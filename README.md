# VAT identifier

## Problem definition

This project tests if UK VAT registration numbers can be identified from the open web and matched confidentially to Companies House, and whether a HMRC online checker can validate the candidates. The goal is to evaluate coverege, precision, cost and the limitations of a dataset, rather than build a escomplete dataset.

## Scope and limitations

This project tests VAT discovery with a small sample of active UK companies sourced fromCompanies House. The testing uses publicly available web sources and a manual verification against HMRC. When a VAT number cannot be found this counts as a failed attempt at discovery, not that a company isn't VAT registered.

- **Candidate:** a VAT-like number extracted from a web source.
- **Verified:** a candidate confirmed as valid by HMRC.
- **Accepted:** a verified number that can be reliably linked to the target company.
- **Ambiguous:** a valid number for which the company association is uncertain.
- **Not found:** no candidate was discovered within the defined search process.

## Sampling methodology

The sample was drawn from the Companies House bulk snapshot as of August 2026. The file had 5,695,465 records and I read the CSV in blocks of 100,000 rows, because the full 2.8 GB file would not fit in memory.

I kept active non-dormant companies which had a company number and company name, leaving me with a dataset of 4,617,014 records to sample from. I took a simple random sample of 50 companies from this population without pre-checking to see if the selected companies had a website or VAT number, using a fixed random seed of 42 to make the sample reproducible.

This sample is from the Companies House population defined above, not the manufacturer's true list of suppliers, which was unavailable

## Website discovery

For each of the 50 companies, I manually searched for an official website, limiting the process to a maximum of three Google searches per company. I identified 14 possible websites: 4 were confirmed using the company number, 5 were considered probable based on matching names and addresses, and 5 remained unconfirmed because I found no direct evidence linking them to the company. This process took around 3 hours, indicating that company-to-website discovery is a significant issue. This only reports success in website discovery, not VAT registration or VAT-number coverage.

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
