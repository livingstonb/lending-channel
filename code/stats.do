
clear


/* Read in WLOC */
#delimit ;
use "${tempdir}/wloc_panel_cleaned.dta", clear;
merge m:1 rssdid using "${outdir}/wloc_bank_level_aggregates.dta",
	keep(1 3) keepusing(low_svbR_hat high_svbR_hat svbR_hat branch_density_2021 branch_density_2022
		unins_leverage svbR low_unins_leverage high_unins_leverage lassets) nogen;

/* Collapse at nonbank-level on credit line variables, weighted by usage */
egen total_usage = total(usage) if qdate == yq(2022,4), by(firm);
egen total_matched_usage = total(usage) if (qdate == yq(2022,4)) & !missing(usage), by(firm);
gen wts = usage / total_usage;
gen share = usage;

local collapsevars low_svbR_hat high_svbR_hat svbR_hat branch_density_2021 branch_density_2022
		unins_leverage svbR low_unins_leverage high_unins_leverage lassets;

foreach var of local collapsevars {;
		replace `var' = `var' * wts;
};

collapse (sum) `collapsevars', by(firm);

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

gen post = 1 if (qdate == yq(2023, 2));
replace post = 0 if (qdate == yq(2023, 1));

egen nobs = count(post), by(firm);
drop if nobs != 2;

/*
xtreg l_orig_inc L.lassets conforming22 age_coarse22) c.post##c.exposure, fe vce(robust);
*/

/* outcome */
local outcome l_orig_inc;

/* treatment */
local exposure_vars low_svbR_hat high_svbR_hat;

/* Baseline */
reg D.`outcome' L2.lassets `exposure_vars'
	if (qdate == yq(2023, 2)), robust;

	
/* With 2022 HMDA controls */
reg D.`outcome' L2.lassets conforming22 age_coarse22 ltv22 debt_to_income22 `exposure_vars'
	if (qdate == yq(2023, 2)), robust;

/* With firm-specific controls */
reg D.`outcome' L2.(lassets share_cash nlines msr_share excess_capacity
		share_lt_debt leverage)
	`exposure_vars'
	if (qdate == yq(2023, 2)), robust;

/* Kitchen sink */
reg D.`outcome' L2.lassets conforming22 age_coarse22 ltv22 debt_to_income22
	L2.(share_cash nlines msr_share excess_capacity share_lt_debt leverage)
	`exposure_vars'
	if (qdate == yq(2023, 2)), robust;
