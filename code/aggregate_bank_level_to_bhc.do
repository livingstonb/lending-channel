
#delimit ;
use "${tempdir}/cleaned_bank_level.dta", clear;

/* Aggregate bank-level to bhc-level */

drop rssdid name member_fhlbs lei;
rename parentid rssdid;
rename parentname name;
rename parent_member_fhlbs member_fhlbs;
rename parent_id_lei lei;
rename parent_cntry_inc_cd cntry_inc_cd;

replace lei = "" if lei == "0";

/* Variables to be summed over banks within bhc by quarter */
	local sumvars est_unins_deposits ins_deposits alt_ins_deposits
		assets deposits liabilities mtm_2022_loss_level
		total_equity_capital htm_securities afs_debt_securities
		eq_sec_notftrading pledged_securities unins_deposits
		ll_hfs ll_hfi ll_loss_allowance pledged_ll unins_debt
		res_mort_sold total_lending22;
	
/* HMDA Variables to take weighted mean of */
	local meanvars conforming22 ltv22 mu_linc22 age_coarse22
		debt_to_income22 interest_only22;
	foreach var of local meanvars {;
		replace `var' = `var' * total_lending22;
	};

	local sumvars `sumvars' `meanvars';

/* Variables constant within bhc by quarter */
	local firstvars qlabel name date member_fhlbs lei cntry_inc_cd;

/* Collapse */
	keep `sumvars' `firstvars' rssdid qdate;
	collapse (sum) `sumvars' (first) `firstvars', by(rssdid qdate);

foreach var of local meanvars {;
	replace `var' = `var' / total_lending22;
};

/* Mark-to-market losses, percentages */
gen mtm_2022_loss_pct_assets = mtm_2022_loss_level / assets;
gen mtm_2022_loss_pct_equity = mtm_2022_loss_level / total_equity_capital;

gen bhclevel = 1;
gen parentid = rssdid;

append using "${tempdir}/cleaned_bank_level.dta";
save "${tempdir}/cleaned_bank_bhc_combined.dta", replace;
