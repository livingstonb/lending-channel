

use "${tempdir}/cleaned_bank_data_corelogic_merged.dta", clear
merge m:1 lei using "${tempdir}/hmda_lender_agg_2022.dta", nogen keep(1 3)
gen event = period - 5

keep if !missing(rssdid, period, lent)

keep if nloans > 3

gen llent = log(lent)
gen lassets = log(assets)
gen lnloans = log(nloans)

#delimit ;
xtile qtile_bdensity = branch_density if !missing(llent), nquantiles(3);
/* recode qtile_bdensity (1=0) (3=1) (2=.);
replace qtile_bdensity = qtile_bdensity - 2; */


do "${codedir}/gen_reg_variables.do";

xtset rssdid period;
/* gen dllent = D.llent; */

keep if bank & domestic;

/*
gen valid_in_event = !missing(llent) if (event == 0);
by rssdid: egen isvalid = max(valid_in_event);
keep if isvalid == 1;
*/


quietly reg llent i.period;
predict resid, residuals;

collapse (mean) llent, by(qtile_bdensity period);
xtset qtile_bdensity period ;
gen dllent = llent;

#delimit
twoway  (line dllent period if qtile_bdensity == 1)
	(line dllent period if qtile_bdensity == 2)
	(line dllent period if qtile_bdensity == 3),
	legend(label(1 "Lowest") label(2 "Middle") label(3 "Highest (least run-prone)"))
	bgcolor(white) graphregion(color(white))
	ytitle("Mean log lending, monthly")
	title("Lending by tercile of branch density");




replace dlending = D.dlending;

twoway  (line dlending period if qtile_bdensity == 1)
	(line dlending period if qtile_bdensity == 2)
	(line dlending period if qtile_bdensity == 3),
	legend(label(1 "Lowest") label(2 "Middle") label(3 "Highest"));

