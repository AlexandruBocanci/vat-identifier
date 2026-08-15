import re
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup


# Some sampled websites returned 403 when requests used its default user agent.
headers = {
    "User-Agent": "Mozilla/5.0"
}

# The pilot showed that company details were most likely to appear
# in footers and legal, contact or company-information pages.
page_keywords = [
    "terms",
    "privacy",
    "legal",
    "contact",
    "about",
]

# Requiring an explicit VAT label reduces the risk of extracting
# company numbers, postcodes or telephone numbers.
vat_number_pattern = re.compile(
    r"\bVAT\s*(?:(?:registration|reg\.?)\s*)?"
    r"(?:number|no\.?)\s*[:\-]?\s*"
    r"((?:GB\s*)?\d(?:[\s.-]*\d){8}(?:(?:[\s.-]*\d){3})?)\b",
    re.IGNORECASE,
)


def download_page(url):
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )
    except requests.RequestException:
        return None, url

    if response.status_code != 200:
        return None, response.url

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    return soup, response.url


def get_domain(url):
    domain = urlparse(url).netloc.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


def find_relevant_links(soup, homepage_url):
    homepage_domain = get_domain(homepage_url)
    relevant_links = []

    for link in soup.find_all("a"):
        href = link.get("href")

        if href is None:
            continue

        link_text = link.get_text(
            " ",
            strip=True,
        ).lower()

        href_lower = href.lower()
        is_relevant = False

        for keyword in page_keywords:
            if (
                keyword in link_text
                or keyword in href_lower
            ):
                is_relevant = True
                break

        if is_relevant is False:
            continue

        full_url = urljoin(
            homepage_url,
            href,
        )

        # External links are ignored because their VAT details may
        # belong to a different company.
        if (
            get_domain(full_url) == homepage_domain
            and full_url not in relevant_links
        ):
            relevant_links.append(full_url)

    # The page limit controls request cost and prevents one website
    # from receiving a disproportionate number of requests.
    return relevant_links[:5]


# Reading identifiers as strings preserves leading zeroes in company numbers.
discovery_log = pd.read_csv(
    "data/discovery_log.csv",
    dtype=str,
)

websites = discovery_log[
    discovery_log["website_url"].notna()
].copy()


vat_candidates = []

fetch_failed_count = 0
candidate_company_count = 0
keyword_only_count = 0
vat_not_found_count = 0


for website_index in range(len(websites)):
    company = websites.iloc[website_index]

    company_number = company["company_number"]
    company_name = company["company_name"]
    website_url = company["website_url"]
    website_match = company["website_match"]

    homepage_soup, final_homepage_url = download_page(
        website_url
    )

    if homepage_soup is None:
        fetch_failed_count += 1
        print(f"{company_name}: FETCH_FAILED")
        continue

    relevant_links = find_relevant_links(
        homepage_soup,
        final_homepage_url,
    )

    pages = [
        (final_homepage_url, homepage_soup)
    ]

    for page_url in relevant_links:
        page_soup, final_page_url = download_page(
            page_url
        )

        if page_soup is not None:
            pages.append(
                (final_page_url, page_soup)
            )

    # VAT details often appear in a shared footer, so the same number
    # may be extracted from several pages belonging to one company.
    company_candidates = set()
    vat_keyword_found = False

    for page_url, page_soup in pages:
        page_text = page_soup.get_text(
            " ",
            strip=True,
        )

        # A keyword-only result is tracked separately from an actual
        # candidate, as shown by the page that only mentioned VAT returns.
        if re.search(
            r"\bVAT\b",
            page_text,
            re.IGNORECASE,
        ):
            vat_keyword_found = True

        for candidate_match in vat_number_pattern.finditer(
            page_text
        ):
            candidate_raw = candidate_match.group(1)

            vat_candidate = re.sub(
                r"\D",
                "",
                candidate_raw,
            )

            if vat_candidate in company_candidates:
                continue

            company_candidates.add(vat_candidate)

            context_start = max(
                0,
                candidate_match.start() - 100,
            )

            context_end = min(
                len(page_text),
                candidate_match.end() + 150,
            )

            # A short context provides evidence for manual review without
            # storing or publishing a complete copy of the source page.
            context = page_text[
                context_start:context_end
            ]

            vat_candidates.append({
                "company_number": company_number,
                "company_name": company_name,
                "website_match": website_match,
                "source_page": page_url,
                "vat_candidate": vat_candidate,
                "context": context,
            })

    if len(company_candidates) > 0:
        candidate_company_count += 1
        status = "VAT_CANDIDATE_FOUND"
    elif vat_keyword_found:
        keyword_only_count += 1
        status = "VAT_KEYWORD_ONLY"
    else:
        vat_not_found_count += 1
        status = "VAT_NOT_FOUND"

    print(
        f"{company_name}: {status} "
        f"({len(company_candidates)} candidates)"
    )


candidate_columns = [
    "company_number",
    "company_name",
    "website_match",
    "source_page",
    "vat_candidate",
    "context",
]

candidates_dataframe = pd.DataFrame(
    vat_candidates,
    columns=candidate_columns,
)

candidates_dataframe.to_csv(
    "data/vat_candidates.csv",
    index=False,
)


print("\nExtraction summary:")
print(f"Websites attempted: {len(websites)}")
print(f"Fetch failed: {fetch_failed_count}")
print(f"Companies with candidates: {candidate_company_count}")
print(f"VAT keyword only: {keyword_only_count}")
print(f"VAT not found: {vat_not_found_count}")
print(f"Unique candidates: {len(candidates_dataframe)}")
print("\nSaved data/vat_candidates.csv")