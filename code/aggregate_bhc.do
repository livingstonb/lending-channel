

#delimit ;

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
	res_mort_sold;
	
local sumexpr;
foreach var of local sumvars {;
	local sumexpr `sumexpr' (sum) `var';
};

/* Variables constant within bhc by quarter */
local firstvars qlabel name date member_fhlbs lei cntry_inc_cd;

local firstexpr;
foreach var of local firstvars {;
	local firstexpr `firstexpr' (first) `var';
};

/* Collapse */
keep `sumvars' `firstvars' rssdid qdate;
collapse `sumexpr' `firstexpr', by(rssdid qdate);

/* Mark-to-market losses, percentages */
gen mtm_2022_loss_pct_assets = mtm_2022_loss_level / assets;
gen mtm_2022_loss_pct_equity = mtm_2022_loss_level / total_equity_capital;


/* 
quietly sum qdate;
gen temp_bdensity = nbranch / deposits * 1e5 if qdate == r(min);
bysort rssdid: egen branch_density = max(temp_bdensity);
drop temp_bdensity;
*/
