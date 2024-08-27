clear


global projdir "/Users/brianlivingston/Library/Mobile Documents/com~apple~CloudDocs/svb_shock"
global datadir "${projdir}/data"
global tempdir "${projdir}/temp"

import delimited using "${tempdir}/bank_data_cleaned.csv", clear

gen ddate = date(date, "YMD")
format %td ddate

gen qdate = qofd(ddate)
format %tq qdate

/* Drop global banks */
keep if missing(rcfd_assets)
