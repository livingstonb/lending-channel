
clear

/***** SELECT OPTIONS *****/
	/* Set 1 to reproduce paper tables */
	local paper_options 0

	/* Select weights for bank shock exposure (usage, limit, equal) */
	local weight_type equal


	#delimit ;

	/* Resets options if paper options were selected */
	if (`paper_options' == 1) {;
		local weight_type usage;
		local latex_file1 using "${outdir}/unins_leverage_nonbank_response.tex";
		local latex_file2 using "${outdir}/all_shockvars_nonbank_response.tex";
		local latex_option booktabs;
	};
	else {;
		local latex_option;
		local latex_file1;
		local latex_file2;
	};

/***** READ IN WLOC DATA FOR MERGE *****/
	#delimit ;
	use "${tempdir}/wloc_panel_cleaned.dta", clear;
	merge m:1 rssdid using "${outdir}/wloc_bank_level_aggregates.dta",
		keep(1 3) keepusing(low_svbR_hat high_svbR_hat svbR_hat branch_density_2021 branch_density_2022
			unins_leverage svbR low_unins_leverage high_unins_leverage lassets low_branch_density_2022
			high_branch_density_2022 high_mtm_2022_loss_pct_equity ins_dep_cov_ratio
			large branch_density_2022_large mtm_2022_loss_pct_equity wloc_l_total_usage) nogen;

	/* Collapse at nonbank-level on credit line variables, using selected weights */
	tempvar weights total_weights;
	if "`weight_type'" == "equal" {;
		gen `weights' = 1 if ((usage > 0) & !missing(usage));
	};
	else {;
		gen `weights' = `weight_type' if (usage > 0) & !missing(usage);
	};
	egen `total_weights' = total(`weights') if qdate == yq(2022, 4), by(firm);
	replace `weights' = `weights' / `total_weights';
	replace `weights' = . if `weights' == 0;

	local collapsevars low_svbR_hat high_svbR_hat svbR_hat branch_density_2021 branch_density_2022
			unins_leverage svbR low_unins_leverage high_unins_leverage lassets low_branch_density_2022
			high_branch_density_2022 ins_dep_cov_ratio
			large branch_density_2022_large mtm_2022_loss_pct_equity wloc_l_total_usage;
	 
	local countvars;
	foreach var of local collapsevars {;
		replace `var' = `var' * `weights';
		local countvars `countvars' (count) count_`var'=`var';
	};

	collapse `countvars' (sum) `collapsevars', by(firm);
	foreach var of local collapsevars {;
		replace `var' = . if count_`var' == 0;
	};
	drop count_*;

	rename lassets bank_lassets;
	rename wloc_l_total_usage bank_wloc_l_total_usage;
	tempfile wlocs;
	save "`wlocs'", replace;

/* Merge MCR panel */
	#delimit ;
	use "${outdir}/final_mcr_panel.dta", clear;
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

label variable unins_leverage "\textbf{Unins Leverage}";
label variable bank_lassets "Avg Bank Size";
label variable branch_density_2022 "\textbf{Branch Density}";
label variable low_branch_density_2022 "0-1 Low Branch Density";
label variable svbR "\textbf{Event Stock Return}";
label variable mtm_2022_loss_pct_equity "\textbf{2022 MtM Losses}";

/* outcome */
local outcome l_orig_inc;

/* treatment */
local exposure_vars std_unins_leverage;

/* controls */
local hmda_control_vars conforming22 age_coarse22 ltv22 debt_to_income22;

local firm_control_vars lassets share_cash nlines msr_share excess_capacity
		share_lt_debt leverage;
		
/* standardize */
	gen included = 1;
	replace included = . if missing(D.l_orig_inc);
	replace included = . if qdate != yq(2023, 2);

	local other_std_variables unins_leverage bank_lassets branch_density_2022
		mtm_2022_loss_pct_equity svbR bank_wloc_l_total_usage;

	foreach var of local other_std_variables {;
		quietly: sum `var' if included;
		gen std_`var' = (`var' - `r(mean)') / `r(sd)';
		local lbl : variable label `var';
		label variable std_`var' "`lbl'";
	};

	local std_hmda_control_vars;
	foreach var of local hmda_control_vars {;
		quietly: sum `var' if included;
		gen std_`var' = (`var' - `r(mean)') / `r(sd)';
		local std_hmda_control_vars `std_hmda_control_vars' std_`var';
	};

	local std_firm_control_vars;
	foreach var of local firm_control_vars {;
		quietly: sum L2.`var' if included;
		gen std_`var' = (L2.`var' - `r(mean)') / `r(sd)';
		local std_firm_control_vars `std_firm_control_vars' std_`var';
	};

*********** ADD CONTROLS ***********

	/* Baseline */
	estimates clear;
	eststo: quietly reg D.`outcome' `exposure_vars'
		if (qdate == yq(2023, 2)), robust;
	estadd local nonbank_controls "No";
	estadd local hmda_controls "No";
		
	/* Add bank log assets */
	eststo: quietly reg D.`outcome'
		std_bank_lassets
		`exposure_vars'
		if (qdate == yq(2023, 2)), robust;
	estadd local nonbank_controls "No";
	estadd local hmda_controls "No";
		
	/* With firm-specific controls */
	eststo: quietly reg D.`outcome'
		`std_firm_control_vars'
		std_bank_lassets 
		`exposure_vars'
		if (qdate == yq(2023, 2)), robust;
	estadd local nonbank_controls "Yes";
	estadd local hmda_controls "No";
		
	/* With 2022 HMDA controls */
	eststo: quietly reg D.`outcome'
			`std_firm_control_vars'
			`std_hmda_control_vars'
			std_bank_lassets `exposure_vars'
		if (qdate == yq(2023, 2)), robust;
	estadd local nonbank_controls "Yes";
	estadd local hmda_controls "Yes";

	esttab `latex_file1',
		noconst b se label r2 nomtitles obslast
		star(* 0.10 ** 0.05 *** 0.01) nonotes replace `latex_option'
		scalars("nonbank_controls Bal Sheet Controls"
			"hmda_controls HMDA Controls")
		addnotes("Robust standard errors in parentheses")
		keep(`exposure_vars' std_bank_lassets);
	estimates clear;


*********** TRY ONE MAIN VARIABLE AT A TIME ***********

/* UNINS LEVERAGE */
estimates clear;
eststo: quietly reg D.`outcome' std_unins_leverage
		`std_firm_control_vars'
		`std_hmda_control_vars'
		std_bank_lassets
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";
estadd local bsize_controls "Yes";
	
/* BRANCH DENSITY */
eststo: quietly reg D.`outcome' std_branch_density_2022
		`std_firm_control_vars'
		`std_hmda_control_vars'
		std_bank_lassets
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";
estadd local bsize_controls "Yes";
	
/* MtM losses 2022 */
eststo: quietly reg D.`outcome' std_mtm_2022_loss_pct_equity
		`std_firm_control_vars'
		`std_hmda_control_vars'
		std_bank_lassets
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";
estadd local bsize_controls "Yes";
	
/* Stock return */
eststo: quietly reg D.`outcome' std_svbR
		`std_firm_control_vars'
		`std_hmda_control_vars'
		std_bank_lassets
		if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";
estadd local bsize_controls "Yes";

/* All */
eststo: quietly reg D.`outcome' std_unins_leverage std_branch_density_2022
	std_mtm_2022_loss_pct_equity std_svbR
		`std_firm_control_vars'
		`std_hmda_control_vars'
		std_bank_lassets
	if (qdate == yq(2023, 2)), robust;
estadd local nonbank_controls "Yes";
estadd local hmda_controls "Yes";
estadd local bsize_controls "Yes";

esttab `latex_file2',
	noconst b not label r2 nomtitles obslast
	star(* 0.10 ** 0.05 *** 0.01) nonotes replace `latex_option'
	scalars("nonbank_controls Bal Sheet Controls"
		"hmda_controls HMDA Controls" "bsize_controls Bank Size Control")
	keep(std_unins_leverage std_branch_density_2022 std_mtm_2022_loss_pct_equity std_svbR);
estimates clear;
