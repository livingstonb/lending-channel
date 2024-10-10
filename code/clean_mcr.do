

#delimit ;

/*
%delimit
import excel using "${datadir}/mcr.xlsx", clear firstrow
	datestring(%td);
duplicates drop firm quarter, force;

save "${tempdir}/mcr.dta", replace;
*/
use "${tempdir}/mcr.dta", clear;

gen date = dofc(quarter);
format %td date;
drop quarter;

gen quarter = qofd(date);
format %tq quarter;

gen q4_2023 = (date == mdy(10, 1, 2023));
gen q3_2023 = (date == mdy(7, 1, 2023));
gen q2_2023 = (date == mdy(4, 1, 2023));
gen q1_2023 = (date == mdy(1, 1, 2023));
gen q4_2022 = (date == mdy(10, 1, 2022));
gen q2_2022 = (date == mdy(4, 1, 2022));
gen q3_2019 = (date == mdy(10, 1, 2019));

merge m:1 firm using "${datadir}/hmda_lei_nmls_crosswalk.dta",
	nogen keep(1 3) keepusing(lei);

merge m:1 lei using "${datadir}/avery_crosswalk.dta",
	nogen keep(1 3) keepusing(type22 purcd22 appld22 origd22);
	
/* IMB non-affiliated with depository institution */
keep if (type22 == 40);

sort firm date;

gen servicing_fees = C500_1 + C510_1;

rename A010 unrestr_cash;
rename A034 sec_afs;
rename A036 sec_trading;
rename A160 msr;
rename A240 assets;

rename B010 bal_debt_fac;
rename B060 adv_fhlb;
rename B070 comm_paper;
rename B080 payables_to_related;
rename B217 current_liab;
rename B219 lt_liab;
rename B220 liab;
rename B260 common_stock;
rename B350 equity;

rename C100_1 warehousing_int;
rename C210_1 orig_fees;
rename C260_1 total_orig_inc;
rename C650_1 total_serv_noni_income;

rename D070_1 total_orig_comp;
rename D180_1 total_comp;
rename D500_1 total_nonint_exp;
rename D510_1 pretax_noi;
rename D530_1 posttax_noi;

drop A* B* C* D*;

/* Other variables */
gen orig_share = total_orig_comp / total_comp;
gen lbal_debt_facilities = log(bal_debt_fac);
gen l_orig_inc = log(total_orig_inc);
gen lassets = log(assets);
gen balshare = bal_debt_fac / total_orig_inc;
gen lbalshare = log(balshare);
gen lorig = log(total_orig_inc);

/* gen liquidity = (unrestr_cash + sec_afs) */

/* Look for originators */
gen orig_fee_share_inc = orig_fees / pretax_noi;

/* Check sample size */
tsset firm quarter;
count if q1_2023 & L.q1_2023;

local datevar q1_2023;

gen earnings = D.posttax_noi / L.posttax_noi;
gen lev = equity / assets;

/* 
gen coverage = (unrestr_cash + sec_afs + sec_trading) / 
	(total_nonint_exp / 4 + lt_liab / 4);
*/

gen lcoverage = log(coverage);
replace lcoverage = coverage;

reg lbal_debt_fac total_orig_inc L.bal_debt_fac L.total_orig_inc L2.orig_share;
reg lbal_debt_fac l_orig_inc L.lbal_debt_fac L.l_orig_inc L2.orig_share
	if `datevar';

reg lbalshare L2.lbalshare L2.orig_share L2.lassets L2.coverage if `datevar'
	& L2.coverage < 20, robust;
	
reg D.lorig L2D.lorig L4D.lorig L2.orig_share L2.lassets L4.lcoverage if `datevar'
	, robust;
predict resid if `datevar', residuals;
/*
keep if (resid >-1) | (resid < 1);
*/
twoway scatter resid L2.lcoverage if `datevar';

corr resid L2.lcoverage if `datevar';
