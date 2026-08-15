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