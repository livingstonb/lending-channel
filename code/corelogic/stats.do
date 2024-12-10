
#delimit ;

/* Read bank level */
#delimit ;
use "${tempdir}/cleaned_bank_level.dta", clear;
keep if qdate == yq(2022, 4);
merge 1:m rssdid using "${tempdir}/corelogic_aggregated.dta", nogen keep(1 3);
drop if missing(svb_week);
keep if inrange(svb_week, -9, 12);

/* Aggregate bank-level to bhc-level */

gen id_equals_parent = (rssdid == parentid);
egen parent_is_child = max(id_equals_parent), by(parentid);

drop id_equals_parent rssdid name member_fhlbs lei;
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
		res_mort_sold total_lending22 nloans lent conforming_lent;
	
/* HMDA Variables to take weighted mean of */
	local meanvars conforming22 ltv22 mu_linc22 age_coarse22
		debt_to_income22 interest_only22;
	foreach var of local meanvars {;
		replace `var' = `var' * total_lending22;
	};

	local sumvars `sumvars' `meanvars';

/* Variables constant within bhc by date */
	local firstvars qlabel name date member_fhlbs lei cntry_inc_cd parent_is_child;

/* Collapse */
	keep `sumvars' `firstvars' rssdid svb_week;
	collapse (sum) `sumvars' (first) `firstvars', by(rssdid svb_week);

foreach var of local meanvars {;
	replace `var' = `var' / total_lending22;
};

/* Mark-to-market losses, percentages */
gen mtm_2022_loss_pct_assets = mtm_2022_loss_level / assets;
gen mtm_2022_loss_pct_equity = mtm_2022_loss_level / total_equity_capital;

gen bhclevel = 1;

keep if inrange(svb_week, -8, 12);


keep if nloans >= 2;

gen l_lent = log(lent);
gen nonconforming_lent = lent - conforming_lent;
replace nonconforming_lent = . if nonconforming_lent < 0;
gen l_nonconforming = log(nonconforming_lent);
gen unins_leverage = unins_debt / liabilities;
gen l_assets = log(assets);

gen sdate = svb_week + 8;
gen post = (svb_week >= 1);
xtset rssdid sdate;

xtreg l_lent i.sdate c.l_assets##c.post c.age_coarse22##c.post
	c.ltv22##c.post
	c.unins_leverage#i.sdate
	, vce(robust);


assert 0;
/* Add only if rssdid not equal parent? Otherwise already added corelogic */
/* merge 1:m rssdid using "${tempdir}/corelogic_aggregated.dta", nogen keep(1 3); /*
keep if !missing(svb_week);
merge 1:1 rssdid svb_week using "`bhc_corelogic'", nogen keep(1 3); 

foreach var of varlist lent nloans conforming_lent {;
	replace `var' = `var' + bhc_`var' if (parent_is_child == 0) & !missing(`var');
	replace `var' = bhc_`var' if (parent_is_child == 0) & missing(`var');
	drop bhc_`var';
};







#delimit ;
use "${outdir}/cleaned_bank_data.dta", clear;
keep if bhclevel == 1;
keep if bank & domestic;
keep if date == "2022-12-31";

merge m:1 lei using "${tempdir}/hmda_lender_agg_2022.dta", nogen keep(1 3);
merge 1:m rssdid using "${tempdir}/corelogic_aggregated.dta", nogen keep(1 3);

/* Do aggregation... */

/* Aggregate to BHC */

/* Check if some LEIs are holding company level */

local binary_event_indicator 0;

/* Choose event. Variable svb_week is -2 for 2 weeks before SVB failure, -1 for
week before, 0 for week of (week starting 3/9), 1 for week after, etc.
***** options are svb_week OR fr_week */
local event svb_week;

if `binary_event_indicator' {;
	/* Two weeks before is pre-event */
	gen post = 0 if inrange(svb_week, -2, -1);
	/* Weeks 2-3 after is post */
	replace post = 1 if inrange(svb_week, 1, 2);
};
else {;
	
	gen post = 0 if inrange(svb_week, 1, 2);
	replace post = -1 if inrange(svb_week, -2, -1);
	replace post = -2 if inrange(svb_week, -4, -3);
	replace post = -3 if inrange(svb_week, -6, -5);
	replace post = 1 if inrange(svb_week, 3, 4);
	replace post = 2 if inrange(svb_week, 5, 6);
	
	/*
	gen post = .
	forvalues t = -4/4 {
		replace post = `t' if inlist(svb_week, `t')
	}
	*/
};

keep if !missing(rssdid, post, lent);


#delimit ;

/* More aggregation */
collapse (sum) lent nloans conforming_lent (first) branch_density
	(first) assets (first) unins_debt (first) mtm_2022_loss_pct_equity
	(first) debt_to_income22 age_coarse22 conforming22
	ltv22  mu_linc22 svbR, by(rssdid post);
gen conforming_share = conforming_lent / lent;
/* rename parentid rssdid; */
	
keep if nloans > 5;

bysort rssdid: gen N = _N;

gen ncon = lent - conforming_lent;
gen llent = log(lent);
gen lconlent = log(conforming_lent);
gen lncon = log(ncon);
gen lassets = log(assets);
gen lnloans = log(nloans);
gen unins_leverage = unins_debt / assets;
gen lbranch_density = log(branch_density);

xtset rssdid post;


#delimit ;
xtile qtile_bdensity = branch_density if !missing(llent), nquantiles(3);
/* recode qtile_bdensity (1=0) (3=1) (2=.); */
 /* replace qtile_bdensity = qtile_bdensity - 2; */
gen dllent = D.llent;

/*
do "${codedir}/gen_reg_variables.do";
*/


xtile qtile_unins_leverage = unins_leverage if !missing(llent), nquantiles(3);
/* recode qtile_unins_leverage (1=0) (3=1) (2=.); */

/* NEED TO THINK OF APPROPRIATE CONTROLS */
/* Contamination of control group? */

/* bysort rssdid: keep if _N == 7; */
*/

xtset rssdid post;
drop if rssdid < 0;


if `binary_event_indicator' == 1 {;
	#delimit ;
	xtset rssdid post;
	quietly xtreg llent post c.post#c.( lassets debt_to_income22 conforming22 age_coarse22
			ltv22 mu_linc22)
		ib0.post##c.( unins_leverage), fe vce(robust);
};
else {;
	#delimit ;
	replace post = post + 3;
	xtset rssdid post;
	quietly xtreg llent
		c.post#c.(lassets debt_to_income22 conforming22 age_coarse22
			ltv22 mu_linc22)
		ib0.post##c.( branch_density)
		, fe vce(robust);
		
};

/*
tab post, gen(dpost);
forvalues j = 3/6 {;
	gen treat`j' = dpost`j' * branch_density;
};

reg d.llent lassets debt_to_income22 conforming22 age_coarse22
			ltv22 mu_linc22 ib1.post
			treat*, cluster(rssdid);
		*/

estimates;
