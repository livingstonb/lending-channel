 
#delimit ;
use "${tempdir}/wloc_panel_cleaned.dta", clear;
drop if missing(rssdid, firm);

/* Given firm, probability that it shows up next period? */
egen pair = group(firm rssdid);

collapse (sum) limit usage available (first) pair, by(firm rssdid qdate);
gen relationship = 1;

drop if missing(pair);
tsset pair qdate;


forvalues k = 1/12 {;
	local kp = `k' + 1;
	bysort pair (qdate): gen rel_F`k' = (F`k'.relationship == 1) | (F`kp'.relationship == 1);
	bysort firm (qdate): egen temp_some_pair = max(rel_F`k');
	gen firm_exists_F`k' = 1 if (temp_some_pair == 1);
	replace rel_F`k' = 0 if missing(rel_F`k');
	replace rel_F`k' = . if (firm_exists_F`k' != 1);
	drop temp_some_pair;
};

/* 2019 */
forvalues k = 1/12 {;
	quietly: sum rel_F`k' if qdate == yq(2019, 1);
	di "`r(mean)'";
};

keep rel_F* qdate;
gen date = dofq(qdate);
gen year = year(date);
gen quarter = quarter(date);
drop date;
export delimited using "${tempdir}/bank_nonbank_rel_transitions.csv", replace;
