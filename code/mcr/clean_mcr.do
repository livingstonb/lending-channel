

#delimit ;

/*
#delimit ;
import excel using "${datadir}/mcr_panel.xlsx", clear firstrow;
duplicates drop firm quarter, force;

save "${tempdir}/mcr/mcr_panel.dta", replace;
*/
use "${tempdir}/mcr_panel.dta", clear;

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
	
merge m:1 lei using "${tempdir}/hmda_lender_agg_2022.dta",
	nogen keep(1 3) keepusing(conforming ltv mu_linc md_linc age_coarse
		debt_to_income total_lending);
	
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

gen leverage = equity / assets;

/* Save unique names */
preserve;
keep firm name_dataAB;
rename name_dataAB name;
duplicates drop firm name, force;
collapse (first) name, by(firm);

export excel "${tempdir}/mcr_nonbank_nmls_ids.xlsx", replace firstrow(variables);
restore;

/* Scatter */


