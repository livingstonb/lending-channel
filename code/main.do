clear


global projdir "/Users/brianlivingston/Library/Mobile Documents/com~apple~CloudDocs/svb_shock"
global datadir "${projdir}/data"
global tempdir "${projdir}/temp"

import delimited using "${tempdir}/bank_data_cleaned.csv", clear

gen ddate = date(date, "YMD")
format %td ddate

gen qdate = qofd(ddate)
format %tq qdate

/* SAMPLE SELECTION */
/* Commercial banks (200), holding companies (500) */
#delimit ;
gen bank = inlist(chtr_type_cd, 200)
			& inlist(insur_pri_cd, 1, 2, 6, 7);
gen domestic = (parent_domestic_ind == "Y") & (domestic_ind == "Y");

keep if bank & domestic;
drop bank domestic;

drop if assets < 100000; /* Assets < $100m */




/* Use entries consolidated by domestic and foreign branches where possible */
foreach var of varlist rcfd_* {;
	local newvar = substr("`var'", 6, .);
	gen `newvar' = `var';
};
foreach var of varlist rcon_* {;
	local newvar = substr("`var'", 6, .);
	cap gen `newvar' = `var';
	replace `newvar' = `var' if missing(`newvar');
};
drop rcon_* rcfd_*;

/* Cleaning */
replace id_lei = lei if missing(id_lei);
drop lei;
rename id_lei lei;

/*
quietly sum qdate;
local quarters = r(max) - r(min) + 1;
bysort rssdid qdate: ;
*/
