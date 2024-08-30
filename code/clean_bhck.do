clear

import delimited "temp/bhck_data_cleaned.csv", clear
drop if missing(assets) | (assets == 0)

egen deposits = rowtotal(*deposits), missing
drop if deposits == 0

gen ddate = date(date, "YMD")
gen qdate = qofd(ddate)
format %td ddate
format %tq qdate

keep rssdid assets liabilities deposits qdate

foreach var of varlist assets liabilities deposits {
	rename `var' bhck_`var'
}

save "${tempdir}/bhck_for_merge.dta", replace
