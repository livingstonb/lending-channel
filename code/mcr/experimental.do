

#delimit ;
use "${tempdir}/mcr_cleaned.dta", clear;
merge 1:1 firm qdate using "${tempdir}/nmls_wloc_aggregates.dta", nogen
	keep(3);
gen post = 0 if (date == mdy(10,01,2022));
replace post = 1 if (date == m dy(01,01,2023));
drop if missing(post);

keep if total_orig_inc > 0;

gen parity = usage / bal_debt_fac;
keep if inrange(parity, 0.4, 1.2);
gen ratio = total_orig_inc / usage;

gen liquid = (unrestr_cash + sec_afs + sec_trading) / current_liab;

gen profitability = pretax_noi / equity;
quietly sum profitability;
gen norm_noi = profitability / max(abs(r(max)),abs(r(min)));
replace norm_noi = atanh(norm_noi);

xtset firm post;
reg ratio l.ratio l.assets l.nlines l.leverage;
predict resid if post == 1, residuals;

scatter resid norm_noi;
