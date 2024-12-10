
clear


/* Read in WLOC */
#delimit ;
use "${tempdir}/wloc_panel_cleaned.dta", clear;
merge m:1 rssdid using "${outdir}/wloc_bank_level_aggregates.dta",
	keep(1 3) keepusing(low_svbR_hat high_svbR_hat svbR_hat branch_density_2021 branch_density_2022
		unins_leverage svbR low_unins_leverage high_unins_leverage lassets low_branch_density_2022
		high_branch_density_2022 high_mtm_2022_loss_pct_equity ins_dep_cov_ratio
		large branch_density_2022_large mtm_2022_loss_pct_equity) nogen;

/* Collapse at nonbank-level on credit line variables, weighted by usage */
egen total_usage = total(usage) if qdate == yq(2022,4), by(firm);
egen total_matched_usage = total(usage) if (qdate == yq(2022,4)) & !missing(usage), by(firm);
gen wts = usage / total_usage;
replace wts = . if wts == 0;
gen share = usage;

local collapsevars low_svbR_hat high_svbR_hat svbR_hat branch_density_2021 branch_density_2022
		unins_leverage svbR low_unins_leverage high_unins_leverage lassets low_branch_density_2022
		high_branch_density_2022 ins_dep_cov_ratio
		large branch_density_2022_large mtm_2022_loss_pct_equity;
 
local countvars;
foreach var of local collapsevars {;
	replace `var' = `var' * wts;
	local countvars `countvars' (count) count_`var'=`var';
};

collapse `countvars' (sum) `collapsevars', by(firm);

foreach var of local collapsevars {;
	replace `var' = . if count_`var' == 0;
};

/*
collapse (mean) low_svbR_hat high_svbR_hat svbR_hat branch_density_2021 branch_density_2022
		unins_leverage svbR low_unins_leverage high_unins_leverage lassets
		(first) total_usage [aweight=wts], by(firm); */


rename lassets bank_lassets;
tempfile wlocs;
save "`wlocs'", replace;

/* Merge MCR panel */
#delimit ;
use "${tempdir}/mcr_cleaned.dta", clear;
merge m:1 firm using "`wlocs'", keep(1 3) nogen;
keep if (type22 == 40);

/* Variables */
tsset firm qdate;
gen profitability = total_gross_income / L.assets;
gen msr_share = msr / assets;
gen share_cash = unrestr_cash / assets;
gen l_orig_fees = log(orig_fees);
gen l_orig_inc = log(total_orig_inc);
gen excess_capacity = available / limit;
gen share_lt_debt = lt_liab / liab;
gen typical_usage = usage / assets;

gen post = 1 if (qdate == yq(2023, 2));
replace post = 0 if (qdate == yq(2023, 1));

egen nobs = count(post), by(firm);
drop if nobs != 2;

label variable unins_leverage "\textbf{Unins Lev}";
label variable bank_lassets "Size Banks";
label variable branch_density_2022 "\textbf{Branch Density}";
label variable low_branch_density_2022 "0-1 Low Branch Density";
label variable svbR "\textbf{Event Stock Return}";
label variable mtm_2022_loss_pct_equity "\textbf{2022 MtM Losses}";

/* outcome */
local outcome l_orig_inc;

/* treatment */
local exposure_vars unins_leverage;

/* controls */
local hmda_control_vars conforming22 age_coarse22 ltv22 debt_to_income22;

*********** ADD CONTROLS ***********

/* Baseline */
estimates clear;
eststo: quietly reg D.`outcome' `exposure_vars'
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "No";
estadd local hmda_controls "No";
	
/* Add bank log assets */
eststo: quietly reg D.`outcome' bank_lassets `exposure_vars'
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "No";
estadd local hmda_controls "No";
	
/* With firm-specific controls */
eststo: quietly reg D.`outcome' L2.(lassets share_cash nlines msr_share excess_capacity
		share_lt_debt leverage)
	bank_lassets `exposure_vars'
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "No";
	
/* With 2022 HMDA controls */
eststo: quietly reg D.`outcome' L2.(lassets share_cash nlines msr_share excess_capacity
		share_lt_debt leverage)
		`hmda_control_vars'
		bank_lassets `exposure_vars'
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";

esttab using "${outdir}/unins_leverage_nonbank_response.tex",
	noconst beta t label r2 nomtitles obslast
	star(* 0.10 ** 0.05 *** 0.01) nonotes replace booktabs
	scalars("nonbank_controls Bal Sheet Controls"
		"hmda_controls HMDA Controls")
	addnotes("Robust std errors in parentheses")
	keep(`exposure_vars' bank_lassets);
estimates clear;


*********** TRY ONE MAIN VARIABLE AT A TIME ***********

/* UNINS LEVERAGE */
estimates clear;
eststo: quietly reg D.`outcome' unins_leverage
		L2.(lassets share_cash nlines msr_share excess_capacity
		share_lt_debt leverage)
		`hmda_control_vars'
		bank_lassets
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";
estadd local bsize_controls "Yes";
	
/* BRANCH DENSITY */
eststo: quietly reg D.`outcome' branch_density_2022
		L2.(lassets share_cash nlines msr_share excess_capacity
		share_lt_debt leverage)
		`hmda_control_vars'
		bank_lassets
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";
estadd local bsize_controls "Yes";
	
/* MtM losses 2022 */
eststo: quietly reg D.`outcome' mtm_2022_loss_pct_equity
	L2.(lassets share_cash nlines msr_share excess_capacity
		share_lt_debt leverage)
		`hmda_control_vars'
		bank_lassets
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";
estadd local bsize_controls "Yes";
	
/* Stock return */
eststo: quietly reg D.`outcome' svbR
	L2.(lassets share_cash nlines msr_share excess_capacity
		share_lt_debt leverage)
		`hmda_control_vars'
		bank_lassets
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";
estadd local bsize_controls "Yes";

/* All */
eststo: quietly reg D.`outcome' unins_leverage branch_density_2022
	mtm_2022_loss_pct_equity svbR
	L2.(lassets share_cash nlines msr_share excess_capacity
		share_lt_debt leverage)
		`hmda_control_vars'
		bank_lassets
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";
estadd local bsize_controls "Yes";

esttab using "${outdir}/all_shockvars_nonbank_response.tex",
	noconst beta not label r2 nomtitles obslast
	star(* 0.10 ** 0.05 *** 0.01) nonotes replace booktabs
	scalars("nonbank_controls Bal Sheet Controls"
		"hmda_controls HMDA Controls" "bsize_controls Bank Size Control")
	keep(unins_leverage branch_density_2022 mtm_2022_loss_pct_equity svbR);
estimates clear;
