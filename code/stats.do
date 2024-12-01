
clear


/* Read in WLOC */
#delimit ;
use "${tempdir}/wloc_panel_cleaned.dta", clear;
merge m:1 rssdid using "${outdir}/wloc_bank_level_aggregates.dta",
	keep(1 3) keepusing(tercile_svbR branch_density unins_leverage) nogen;
/* replace shocked = 0 if missing(shocked); */


egen total_usage = total(usage) if qdate == yq(2022,4), by(firm);
egen total_matched_usage = total(usage) if (qdate == yq(2022,4)) & !missing(usage), by(firm);
gen temp_exposure1 = (usage * (tercile_svbR == 1)) / total_usage if qdate == yq(2022,4);
gen temp_exposure3 = (usage * (tercile_svbR == 3)) / total_usage if qdate == yq(2022,4);
gen temp_branch_density = (branch_density * usage) / total_matched_usage;
gen temp_unins_leverage = (unins_leverage * usage) / total_matched_usage;

collapse (sum) limit available usage temp_exposure1 temp_exposure3
	temp_branch_density temp_unins_leverage, by(firm qdate);
egen exposure = max(temp_exposure1), by(firm);
egen healthy = max(temp_exposure3), by(firm);
egen branch_density = max(temp_branch_density), by(firm);
egen unins_leverage = max(temp_unins_leverage), by(firm);
drop temp_*;

tempfile wlocs;
save "`wlocs'", replace;


/* Merge MCR panel */
#delimit ;
use "${tempdir}/mcr_cleaned.dta", clear;
keep if (type22 == 40);
merge m:1 firm qdate using "`wlocs'", keep(1 3) nogen;

/* Variables */
tsset firm qdate;
gen profitability = total_gross_income / L.assets;
cap drop lassets;
cap drop l_orig_inc;
gen msr_share = msr / assets;
gen lassets = log(assets);
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
xtreg l_orig_inc c.post##c.(L.lassets conforming22 age_coarse22) c.post##c.exposure, fe vce(robust);
*/

/* healthy exposure */
local exposure_vars  unins_leverage;

reg D.l_orig_inc L2.(lassets share_cash nlines msr_share excess_capacity)
	conforming22 age_coarse22 healthy exposure
	if (qdate == yq(2023, 2)), robust;

/* Baseline */
reg D.l_orig_inc L2.lassets `exposure_vars'
	if (qdate == yq(2023, 2)), robust;

	
/* With 2022 HMDA controls */
reg D.l_orig_inc L2.lassets conforming22 age_coarse22 ltv22 debt_to_income22 `exposure_vars'
	if (qdate == yq(2023, 2)), robust;

/* With firm-specific controls */
reg D.l_orig_inc L2.(lassets share_cash nlines msr_share excess_capacity
		leverage)
	`exposure_vars'
	if (qdate == yq(2023, 2)), robust;

/* Kitchen sink */
reg D.l_orig_inc L2.lassets conforming22 age_coarse22 ltv22 debt_to_income22
	L2.(share_cash nlines msr_share excess_capacity leverage)
	`exposure_vars'
	if (qdate == yq(2023, 2)), robust;
