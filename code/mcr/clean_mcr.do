

#delimit ;

/* Read in WLOC */
import excel using "${datadir}/mcr/wloc_data.xlsx", clear firstrow;

gen pct_usage = usage / limit;
gen nlines = 1;

collapse (sum) nlines limit available usage
	(mean) mu_limit=limit mu_available=available mu_usage=usage mu_pct_usage=pct_usage
	(p50) med_limit=limit med_available=available med_usage=usage med_pct_usage=pct_usage
	(sd) sd_limit=limit sd_available=available sd_usage=usage sd_pct_usage=pct_usage,
		by(firm quarter);

gen rel_sd_available = sd_available / mu_available;
gen rel_sd_usage = sd_usage / mu_usage;
gen rel_sd_limit = sd_limit / mu_limit;

tempfile wlocs;
save "`wlocs'", replace;


/*
#delimit ;
import excel using "${datadir}/mcr_panel.xlsx", clear firstrow;
duplicates drop firm quarter, force;

save "${tempdir}/mcr/mcr_panel.dta", replace;
*/
use "${tempdir}/mcr_panel.dta", clear;
merge 1:1 firm quarter using "`wlocs'", keep(1 3);

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

/* Listed companies */
gen listed = 0;
local public 330511 15622 3030 1071 2285 128231 3274 174457 7706;
foreach firmno of local public {;
	replace listed = 1 if firm == `firmno';
};

/* Other variables */

gen orig_share = total_orig_comp / total_comp;
gen lbal_debt_facilities = log(bal_debt_fac);
gen l_orig_inc = log(total_orig_inc);
gen lassets = log(assets);
gen balshare = bal_debt_fac / total_orig_inc;
gen lbalshare = log(balshare);
gen lorig = log(total_orig_inc);

gen leverage = equity / assets;

save "${tempdir}/mcr_cleaned.dta", replace

/* Save unique names */
preserve;

/* IMB non-affiliated with depository institution */
keep if (type22 == 40);

keep firm name_dataAB;
rename name_dataAB name;
duplicates drop firm name, force;
collapse (first) name, by(firm);



export excel "${tempdir}/mcr_nonbank_nmls_ids.xlsx", replace firstrow(variables);
restore;

/* Scatter */


