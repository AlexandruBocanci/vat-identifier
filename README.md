# VAT identifier

## Problem definition

This project tests if UK VAT registration numbers can be identified from the open web and matched confidentially to Companies House, and whether a HMRC online checker can validate the candidates. The goal is to evaluate coverege, precision, cost and the limitations of a dataset, rather than build a escomplete dataset.

## Scope and limitations

This project tests VAT discovery with a small sample of active UK companies sourced fromCompanies House. The testing uses publicly available web sources and a manual verification against HMRC. When a VAT number cannot be found this counts as a failed attempt at discovery, not that a company isn't VAT registered.