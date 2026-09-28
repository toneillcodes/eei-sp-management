# eei-sp-management
EEI Service Provider management scripts written in Python

* Export service provider entries with `export-all-sp.py`
* Import service provider entries with `create-all-sp.py`
* Federate service providers with `federate-all-sp.py`

List claims found in each file
```
grep -Pzo '<LocalClaim>\s*<ClaimUri>\K.*?(?=<\/ClaimUri>)' *.xml | tr '\0' '\n'
```
List unique claims found across the files
```
grep -Pzo '<LocalClaim>\s*<ClaimUri>\K.*?(?=<\/ClaimUri>)' *.xml | tr '\0' '\n'
```