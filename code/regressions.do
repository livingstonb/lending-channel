

#delimit ;

/* Data */
use "${outdir}/cleaned_bank_data.dta", clear;
do "${codedir}/gen_reg_variables.do";


/* Sample selection */
/* 
keep if bhclevel;
*/
tsset rssdid qdate;
keep if assets >= 1000;
keep if bank;
keep if domestic;
drop if bhclevel;

#delimit ;
/* Regressions, change in deposits or originations? */
gen depvar = D.log_unins_deposits if date == "2023-03-31";

table (colname) (command result) if `date',
	command(reg depvar L2.(unins_leverage log_assets)
		)
	command(reg depvar mtm_2022_loss_pct_assets L2.(log_assets)
		);
drop depvar;








/* Return regression */
reg r20230310 unins_lev branch_density mtm_2022_loss_pct_equity
	D4.log_unins_dep leverage logassets if date == "2022-12-31", robust;

/* Change in deposits */
reg D.log_unins_dep c.r20230310##c.(L2.unins_lev branch_density mtm_2022_loss_pct_equity
	L2D4.log_unins_dep) if date == "2023-06-30", robust;
	
*/

/* First stage, return regression */

keep if assets >= 1000;
reg svbR coll_unins_debt_ratio mtm_2022_loss_pct_assets
	 log_assets leverage log_pledgeable_coll if date == "2022-12-31", robust;

duplicates drop rssdid qdate, force;
tsset rssdid qdate;
gen dlog_deposits = D.log_deposits;

keep if (bank & domestic) | bhclevel;
// keep if !missing(svbR);

#delimit ;
cap drop fittedR;
reg svbR
	L(0/3).(branch_density unins_lev coll_unins_debt_ratio mtm_2022_loss_pct_equity
	log_unins_dep log_assets leverage log_pledgeable_coll)
	if date == "2022-12-31";
predict fittedR if date == "2022-12-31", xb;
reg F.dlog_deposits fittedR;
corr F.dlog_deposits fittedR;



// capture program drop one_rep;
program define one_rep;



reg svbR
	branch_density unins_lev coll_unins_debt_ratio mtm_2022_loss_pct_equity
	log_unins_dep log_assets leverage log_pledgeable_coll
	if date == "2022-12-31" & bhclevel;
cap drop fittedR;

predict fittedR if date == "2022-12-31" & !bhclevel, xb;
reg fd_log_deposits fittedR mtm_2022_loss_pct_equity
	branch_density unins_lev if date == "2022-12-31";

end program;

// bootstrap, reps(50) nodrop: one_rep;
//
// restore;

//
// keep if !bhclevel;
// tsset rssdid qdate;
// keep if assets >= 100;
// keep if bank & domestic;
//
// predict fittedR if date == "2022-12-31", xb;
// sum fittedR, detail;
// replace fittedR = r(p5) if fittedR < r(p5);
// replace fittedR = r(p95) if fittedR > r(p95) & !missing(fittedR);
//
// bysort rssdid: egen Rhat = max(fittedR);
// drop fittedR;
// tsset rssdid qdate;
//
// corr Rhat FD2.log_deposits if date == "2023-03-31";

/* Return regression */
/*
reg D.log_unins_dep L2.unins_lev branch_density mtm_2022_loss_pct_equity
	L2D3.log_unins_dep L2.leverage L2.logassets if date == "2023-03-31", robust;
	*/
