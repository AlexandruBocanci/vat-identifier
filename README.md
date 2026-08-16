# VAT identifier

## Problem definition

This project tests if UK VAT registration numbers can be identified from the open web and matched reliably to Companies House, and whether a HMRC online checker can validate the candidates. The goal is to evaluate coverage, precision, cost and the limitations of a dataset, rather than build a complete dataset.

## Scope and limitations

This project tests VAT discovery with a small sample of active UK companies sourced from Companies House. The testing uses publicly available web sources and a manual verification against HMRC. When a VAT number cannot be found, this counts as a failed discovery attempt, not as evidence that the company is not VAT registered.

- **Candidate:** a VAT-like number extracted from a web source.
- **Verified:** a candidate confirmed as valid by HMRC.
- **Accepted:** a verified number that can be reliably linked to the target company.
- **Ambiguous:** a valid number for which the company association is uncertain.
- **Not found:** no candidate was discovered within the defined search process.

## Sampling methodology

The sample was drawn from the Companies House bulk snapshot as of August 2026. The file had 5,695,465 records and I read the CSV in blocks of 100,000 rows, because the full 2.8 GB file would not fit in memory.

I kept active non-dormant companies which had a company number and company name, leaving me with a dataset of 4,617,014 records to sample from. I took a simple random sample of 50 companies from this population without pre-checking to see if the selected companies had a website or VAT number, using a fixed random seed of 42 to make the sample reproducible.

This sample is from the Companies House population defined above, not the manufacturer's true list of suppliers, which was unavailable.

## Website discovery

For each of the 50 companies, I manually searched for an official website, limiting the process to a maximum of three Google searches per company. I identified 14 possible websites: 5 were confirmed using the company number, 5 were considered probable based on matching names and addresses, and 4 remained unconfirmed because I found no direct evidence linking them to the company. This process took around 3 hours, indicating that company-to-website discovery is a significant issue. This only reports success in website discovery, not VAT registration or VAT-number coverage.

## Results

I ran the extractor against the 14 sites I found. The extractor was able to access 13 of them, while one blocked the request by returning a 403 status code.

The word "VAT" appeared on 4 sites. I found what looked like VAT numbers on 3 of them. The fourth only mentioned VAT returns and did not contain a number.

I checked the 3 candidates using HMRC's online VAT checker and confirmed that all of them were valid. The names returned by HMRC matched the Companies House companies. Two of the HMRC addresses also matched Companies House. For the remaining result, the address was different, but the source website displayed the exact company number next to the VAT number. Based on this evidence, all 3 results were accepted.

The final numbers are:

- possible websites found: 14 / 50
- VAT candidates found: 3 / 50
- valid HMRC results: 3 / 3
- accepted results: 3 / 50
- observed false positives: 0 / 3
- manual website search time across the 50 companies: 148 minutes

This gives me a yield of 6% on the original sample. The website search time works out at around 49 minutes per accepted VAT number.

I observed 0 false positives from 3 accepted results. However, this sample is too small to use as an estimate of the tool's general performance.

The other 47 companies cannot be considered not VAT registered. For these companies, I either could not find a reliable website or the website did not display a VAT number.

## Source research

I manually tested Companies House filings as an alternative way to find the VAT number of 10 companies for which the websites were not successful.

### Companies house filings

- NORTHERN TURBINE SERVICES LIMITED (SC510079) - I searched the latest accounts filed on May 18th 2026 for the word "VAT", which was not found.
- FRANK KELBIE LIMITED (SC133320) - I searched the latest accounts filed on July 31st 2025 for the word "VAT", which was not found.
- GREATER UPKEEP LIMITED (16788444) - No account filings were available.
- FUSED ELECTRICS LTD (14946172 ) - I searched the latest accounts filed on June 25th 2025 for the word "VAT", which was not found.
- BROUGHTON COMMUNITY ENERGY LIMITED (RS009540) - No account filings were available.
- JC CONSTRUCTION AND SECURITY LTD (16153535) - I searched the latest accounts filed on December 31st 2025 for the word "VAT", which was not found.
- PRESTIGE GLAZING LTD (13557258) - I searched the latest accounts filed on August 31st 2025 for the word "VAT", which was not found.
- GRESLEY HOUSE CARE LIMITED (09243079) - I searched the latest accounts filed on March 31st 2025 for the word "VAT", which was not found.
- NIGEL DAVIES LIMITED (04510236) - I searched the latest accounts filed on March 31st 2025 for the word "VAT", which was not found.
- EDS CONSTRUCT LTD (13093635) - I searched the latest accounts filed on December 31st 2024 for the word "VAT", which was not found.

Accounts documents were available for 8 out of the 10 companies, however none of the 8 documents contained a VAT number, and the other 2 companies had no account filings available. Based on these results, I did not continue along with this method to find companies VAT numbers.

### EORI

I also tried EORI numbers as another way to find VAT numbers, but the official EORI checker can confirm whether an EORI number is valid and may return a company's information. This was only possible if the EORI numbers for each company that I wanted to test were known.
The service is similar to the HMRC VAT checker. It has the same backwards-search limitation, so I did not continue with this method either.

## Proof of concept

The PoC starts with 50 random companies selected by "sampling.py" from the raw csv file which contained over 5.5 million companies. I manually searched for their websites and logged the results in "discovery_log.csv".

For the 14/50 companies with a possible website, "extraction.py" downloads the homepage and follows up with the first 5 internal pages whose links contain any of the following words: "terms", "privacy", "legal", "contact", "about". It converts the HTML code into readable text and searches for any 9 or 12 digit numbers that were placed after words like "VAT Number" or "VAT No." (not case sensitive) since these are the most frequent ones.

The extracted number is cleaned by removing prefixes and spaces (GB 123 456 789 -> 123456789). Duplicate numbers found in multiple components are stored only once. For each company the script keeps the company's number, company's name, company's website match, company's website, company's VAT Number and the context in which the VAT was found.

I verified each candidate manually with HMRC VAT checker and saved the company name and address. After that, I compared them with the website and the Companies House data and accepted the match.

## Production approach

The current process would not scale well for 40,000 suppliers since finding the correct website manually was the most time-consuming step. A search API would reduce the manual work, but since "a wrong number costs more than a missing one" it might return an incorrect domain, since some companies use a domain that is different from their legal name.

For this PoC I used HMRC's online checker manually, since the API access requires an approval process that takes around 2 weeks and could not be completed before the project's deadline. With more time and approved access, the API could automate VAT data verification, reducing the processing time.

A larger version of the process would first match each supplier with its Companies House record. A search API would suggest possible domains based on the company number, name and address from Companies House. The confirmed websites would be scanned only on a few relevant pages like "privacy" or "terms" pages. The HMRC API would be used to verify each extracted VAT candidate. Unclear domain or company matches would eventually be sent for manual review.

Paid company to domain sources and search APIs could help find the websites that I missed manually, however the PoC is too small to estimate how much coverage would improve. The priority would still be accuracy, each website would need to be linked using Companies House evidence, each VAT number verified through HMRC, and uncertain matches reviewed manually.

### Monitoring

In production I would monitor:

- how many companies were matched to a website
- how many websites could not be accessed
- how many websites produced a VAT candidate
- how many candidates were confirmed by HMRC
- how many results were ambiguous or matched a different company
- when each accepted VAT number was last verified

These numbers would help identify whether problems appeared during website discovery, page downloading, VAT extraction or company matching.

## Cost

Using the manual website search time, the process took around 2-3 minutes per company and around 50 minutes for each accepted VAT number. With this rate, 40,000 suppliers would require almost 2,000 hours of manual website search. This is the case if the work is done manually because search APIs and automated website search could reduce time, however some ambiguous cases may require manual review.

Assuming a labour cost of £20 per hour, each manual website search would cost approximately £1 per company, excluding other costs like the search API and better data sources. Considering these, manually checking for all 40,000 suppliers would take approximately 2,000 hours and cost around £40,000.

## Debate topics

### Checksum enumeration

The checksum can be used to remove impossible VAT numbers before checking them with HMRC. A number can have a correct checksum without being a real VAT number. We would still have to check a large number of possible VAT numbers, and then connect every valid candidate to the correct company. This could block the entire process by reaching HMRC's request limits, so I would not use this approach.

### Keeping the dataset updated

For every accepted VAT number, I would store the timestamp when it was last verified, and check the VAT number's validity. This has to be done because companies can change their details or deregister. If after each periodic check a VAT number was no longer valid, I would mark it as inactive, keeping it in the database. I would also repeat the discovery process for companies without a VAT number, because they may become registered later.

### Finding errors at scale

There is no complete dataset to compare against, so I would manually check a random sample of the accepted results. I would compare the information available on the website with the data returned by HMRC and Companies House. This could show if some accepted results are incorrect and since a missing VAT number is safer than a wrong one linked to a different company, any uncertain result would be marked as ambiguous rather than accepted.

### Sources used in a commercial product

I used Google to manually discover company websites, but in an automated production process I would use an approved search API, searching the company name and the number in the same query for better accuracy. I would not use VAT numbers found on unconfirmed websites/sources because the information could be outdated and could be linked to the wrong company.

## Conclusion

This project shows that VAT numbers can be extracted from company websites and linked to Companies House data. However the accepted results from only using the websites to extract the VAT number were only 3 out of 50 or 6% of the companies.

The main problem was finding the correct company website, and even then, the majority of the websites did not provide a VAT number. All 3 candidates were checked and confirmed manually using HMRC VAT checker, with 0/3 false positives observed, however, the sample was too small to estimate an error percentage.

Based on these results, a high-accuracy dataset may be possible, but for a better coverage the project needs automated domain discovery, additional sources and manual review for ambiguous cases before using it at a larger scale.

## Beyond the UK
### Germany

Germany has a similar VAT discovery problem, but company websites may be more useful than in the UK. In Germany, a company is required to provide an easily accessible legal notice called "Impressum". Business websites must include information such as the company identity, register number and VAT if applicable. Because of this, I would search the "Impressum" page for a VAT number, which would not guarantee a result, but could improve coverage and accuracy.

**Source:https://europa.eu/youreurope/business/growing/digitalising/setting-up-business-website/index_en.htm**

Verification would be different from the UK since Germany uses a tax number called "Steuernummer" and the VAT number is called "USt-IdNr". Therefore, failing to find or validate a USt-IdNr would not necessarily mean that the business is not registered for domestic VAT. A candidate could be checked through VIES, but VIES cannot discover a VAT number using the company name, and an invalid response may also mean that the number has not been activated for intra-EU transactions.

**Source:https://www.gtai.de/en/invest/investment-guide/value-added-tax-561538**

Most of the UK pipeline could be reused. The equivalent of Companies House from UK is German Company Register in Germany, the crawler would focus on the Impressum page, and the extractor would search for "USt-IdNr" instead of "VAT". The HMRC verification would be replaced by VIES, and company to domain matching and manual reviews would remain the same.

## Running the project

The full Companies House CSV is not included in this repository because it is approximately 2.8 GB. The generated sample is already included.

To run the sampling process again, download the August 2026 snapshot from the Companies House bulk data page (https://download.companieshouse.gov.uk/en_output.html). Extract `BasicCompanyDataAsOneFile-2026-08-01.csv` and place it inside `data/raw/`.

Run the following commands from the main project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\sampling.py
.\.venv\Scripts\python.exe src\extraction.py
```

The extraction results may change over time because websites can update their content or block automated requests.