
#delimit ;

/* Read CRSP csv, obtained previously from python API as dta */
import delimited using "${tempdir}/crsp_daily_cleaned.csv", clear;
rename cap market_cap;

foreach var of varlist r2023* {;
	label variable `var' "CRSP close-to-close return";
};
foreach var of varlist idr* {;
	label variable `var' "CRSP intraday return";
};

gen long parentid = rssdid;

gen svbR = (p20230313 - p20230308) / p20230308;
gen frR = (p20230502 - p20230428) / p20230428;

drop r20* idr20* p20*;

save "${tempdir}/crsp_daily_cleaned.dta", replace;
