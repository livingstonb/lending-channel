

#delimit ;

/* Data */
use "${outdir}/cleaned_bank_data.dta", clear;
do "${codedir}/gen_reg_variables.do";

/*
/* Sample selection */
keep if bhclevel;
tsset rssdid qdate;
keep if assets >= 1000;

/* Return regression */
reg r20230310 unins_lev branch_density mtm_2022_loss_pct_equity
	D4.log_unins_dep leverage logassets if date == "2022-12-31", robust;

/* Change in deposits */
reg D.log_unins_dep c.r20230310##c.(L2.unins_lev branch_density mtm_2022_loss_pct_equity
	L2D4.log_unins_dep) if date == "2023-06-30", robust;
	
*/

keep if !bhclevel;
tsset rssdid qdate;
keep if assets >= 100;
keep if bank & domestic;

/* Return regression */
reg D.log_unins_dep L2.unins_lev branch_density mtm_2022_loss_pct_equity
	L2D3.log_unins_dep L2.leverage L2.logassets if date == "2023-06-30", robust;
