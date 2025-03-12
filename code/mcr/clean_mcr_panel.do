/*
	Cleans raw MCR panel, excluding WLOCs except for aggregated usage statistics
	across lines. Saves to firm-quarter level.
	
	Requires aggregated HMDA data and Avery crosswalk, but this can be changed.
	Also, see NOTE below.
*/

#delimit ;

/* NOTE: MUST FIRST USE CODE BELOW AT LEAST ONCE TO SAVE MCR PANEL AS dta!!!
	Just saves time in the future because xlsx with duplicates is very costly
	to read.

	#delimit ;
	import excel using "${datadir}/mcr_panel.xlsx", clear firstrow;
	duplicates drop firm quarter, force;

	save "${tempdir}/mcr/mcr_panel.dta", replace;
*/



/* Aggregate WLOC borrowings (across lines) to nonbank-quarter level */
import excel using "${datadir}/mcr/wloc_data.xlsx", clear firstrow;

replace available = . if (usage < 0) | (usage > limit);
replace usage = . if (usage < 0) | (usage > limit);
replace limit = . if (usage < 0) | (usage > limit);
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


use "${tempdir}/mcr_panel.dta", clear;
merge 1:1 firm quarter using "`wlocs'", keep(1 3);

/* Date variables */
	gen date = dofc(quarter);
	format %td date;
	drop quarter;

	gen quarter = qofd(date);
	format %tq quarter;
	rename quarter qdate;
/*
Merge with with HMDA-LEI crosswalk, Avery, and aggregated annual public
HMDA from earlier.
*/
	merge m:1 firm using "${datadir}/hmda_lei_nmls_crosswalk.dta",
		nogen keep(1 3) keepusing(lei);

	merge m:1 lei using "${datadir}/avery_crosswalk.dta",
		nogen keep(1 3) keepusing(type22 purcd22 appld22 origd22);
	gen imb = (type22 == 40);
		
	merge m:1 lei using "${tempdir}/hmda_lender_agg_2022.dta",
		nogen keep(1 3) keepusing(conforming ltv mu_linc age_coarse
			debt_to_income total_lending);

/* MCR variables */
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
	rename B090 payables_to_unrelated;
	rename B140 oth_lt_payables_to_unrelated;
	rename B217 current_liab;
	rename B219 lt_liab;
	rename B220 liab;
	rename B260 common_stock;
	rename B350 equity;

	rename C100_1 warehousing_int;
	rename C210_1 orig_fees;
	rename C260_1 total_orig_inc;
	rename C650_1 total_serv_noni_income;
	rename C800_1 total_gross_income;

	rename D070_1 total_orig_comp;
	rename D180_1 total_comp;
	rename D500_1 total_nonint_exp;
	rename D510_1 pretax_noi;
	rename D530_1 posttax_noi;

	drop A* B* C* D*;

/* Identifier for listed firms */
	gen listed = 0;
	local public 330511 15622 3030 1071 2285 128231 3274 174457 7706;
	foreach firmno of local public {;
		replace listed = 1 if firm == `firmno';
	};

/* Other variables */
	gen orig_share = total_orig_comp / total_comp;
	gen lassets = log(assets);
	gen balshare = bal_debt_fac / total_orig_inc;
	gen lbalshare = log(balshare);
	gen lorig = log(total_orig_inc);
	gen liquidassets = unrestr_cash + sec_afs + sec_trading;
	gen leverage = equity / assets;

/* Save final mcr panel */
	save "${outdir}/final_mcr_panel.dta", replace;

/* Save unique names for IMBs (for reference) */
	preserve;
	keep if (imb == 1);

	export excel "${tempdir}/mcr_nonbank_nmls_ids.xlsx", replace firstrow(variables);
	restore;


	
	
/*
assert 1 == 0;
/*
	CODE BELOW IS UNUSED. May be informative when we go back to our issue of
	measurement error in warehouse line reporting. Recall: some look off by
	factor of 1000, some look off by arbitrary factor.
*/


#delimit 
import excel using "${datadir}/mcr/wloc_data.xlsx", clear firstrow;

drop if usage < 0;
drop if usage > limit;

gen pct_usage = usage / limit;
gen nlines = 1;

collapse (sum) limit available usage, by(firm quarter);

gen date = dofc(quarter);
format %td date;
drop quarter;

gen quarter = qofd(date);
format %tq quarter;
rename quarter qdate;
drop date;

tempfile wlocs;
save "`wlocs'", replace;

/* */ #delimit ;
use "${outdir}/final_mcr_panel.dta", clear;
keep if (type22 == 40);

drop usage limit available;
merge 1:1 firm qdate using "`wlocs'", nogen keep(1 3);

drop if usage < 0;
drop if usage > limit;
gen pct_usage = usage / limit;

gen share_wloc_facilities = usage / bal_debt_fac;
replace share_wloc_facilities = 1 if (bal_debt_fac == 0) & (usage == 0);

local to_scale
	unrestr_cash sec_afs sec_trading msr assets bal_debt_fac comm_paper
	payables_to_related current_liab adv_fhlb lt_liab liab common_stock equity
	orig_fees total_orig_inc total_serv_noni_income total_orig_comp total_comp
	total_nonint_exp pretax_noi posttax_noi warehousing_int;
foreach var of local to_scale {;
	replace `var' = `var' * 1000 if inrange(share_wloc_facilities, 900, 1100);
	replace share_wloc_facilities = share_wloc_facilities / 1000
		if inrange(share_wloc_facilities, 900, 1100);
};

drop if inrange(share_wloc_facilities, 2, 900);
drop if share_wloc_facilities > 1100;
replace usage = bal_debt_fac if inrange(share_wloc_facilities, 1.001, 2);
*/
