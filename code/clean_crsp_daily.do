
#delimit ;

/* Save csv crsp as dta */
import delimited using "${tempdir}/crsp_daily_cleaned.csv", clear;
rename cap market_cap;

foreach var of varlist r2023* {;
	label variable `var' "CRSP close-to-close return";
};
foreach var of varlist idr* {;
	label variable `var' "CRSP intraday return";
};

gen long parentid = rssdid;

save "${tempdir}/crsp_daily_cleaned.dta", replace;
