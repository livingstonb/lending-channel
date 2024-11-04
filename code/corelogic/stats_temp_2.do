


use "${tempdir}/cleaned_bank_data_corelogic_merged.dta", clear


merge m:1 lei using "${tempdir}/hmda_lender_agg_2022.dta", nogen keep(1 3)

local binary_event_indicator 0

/* Choose event. Variable svb_week is -2 for 2 weeks before SVB failure, -1 for
week before, 0 for week of (week starting 3/9), 1 for week after, etc.
***** options are svb_week OR fr_week */
local event svb_week

if `binary_event_indicator' {
	// Two weeks before is pre-event
	gen post = 0 if inrange(svb_week, -2, -1)
	// Weeks 2-3 after is post
	replace post = 1 if inrange(svb_week, 1, 2)
}
else {
	
	gen post = 0 if inrange(svb_week, 1, 2)
	replace post = -1 if inrange(svb_week, -2, -1)
	replace post = -2 if inrange(svb_week, -4, -3)
	replace post = -3 if inrange(svb_week, -6, -5)
	replace post = 1 if inrange(svb_week, 3, 4)
	replace post = 2 if inrange(svb_week, 5, 6)
	
	/*
	gen post = .
	forvalues t = -4/4 {
		replace post = `t' if inlist(svb_week, `t')
	}
	*/
}

keep if !missing(rssdid, post, lent)


#delimit ;

/* More aggregation */
collapse (sum) lent (sum) nloans (first) branch_density
	(first) assets (first) unins_debt (first) mtm_2022_loss_pct_equity
	(first) debt_to_income22 age_coarse22 conforming22, by(rssdid post);
	
keep if nloans > 5;

bysort rssdid: gen N = _N;
keep if N == 6;


gen llent = log(lent);
gen lassets = log(assets);
gen lnloans = log(nloans);
gen unins_leverage = unins_debt / assets;
gen lbranch_density = log(branch_density);

xtset rssdid post;

/*
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


if `binary_event_indicator' {;
	#delimit ;
	xtreg llent post i.post#c.( debt_to_income22 conforming22 lassets age_coarse22)
		i.post#c.unins_leverage, fe vce(robust);
};
else {;
	#delimit ;
	replace post = post + 3;
	xtset rssdid post;
	xtreg llent
		c.post#c.(lassets)
		ib0.post##c.( branch_density)
		, fe vce(robust);
};

/*
#delimit
xtdidregress (llent debt_to_income22 conforming22 lassets age_coarse22)
	(unins_leverage, continuous), group(rssdid) time(post);
 */
 
/*
 #delimit ;
xtreg llent i(0/5).post c.post#c.( debt_to_income22 conforming22 lassets age_coarse22)
	i(0/4).post#c.( branch_density), fe vce(robust);
*/

/*
replace post = post + 2;
tab post, gen(dpost);
xtset rssdid post;
#delimit ;
xtreg llent i.post c.post#c.(lassets debt_to_income22 age_coarse22 conforming22)
	c.(dpost1-dpost6)#c.branch_density, fe vce(robust);

*/

