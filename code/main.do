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

/* SAMPLE SELECTION */
/* Commercial banks (200) and holding companies (500) */
#delimit ;
gen bank = inlist(CHTR_TYPE_CD, 200, 500)
			& inlist(INSUR_PRI_CD, 1, 2, 6, 7);
