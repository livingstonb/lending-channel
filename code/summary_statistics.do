
#delimit ;

/* Data */
use "${outdir}/cleaned_bank_data.dta", clear;
do "${codedir}/gen_reg_variables.do";

#delimit ;
gen sample = (assets >= 1000) & bank & domestic;
drop if bhclevel;
tsset rssdid qdate;

keep if sample;

gen log_nbfi_loans = log(unused_comm_nbfi);
gen dlog_nbfi_loans = D.log_nbfi_loans;

reg dlog_nbfi_loans L2.dlog_nbfi_loans L.(log_assets)
	if date == "2023-03-31";
predict resid, residuals;

twoway scatter resid branch_density if branch_density < 50;

// reg D.lonbfi_loans L2.nbfi_loans if date == "2023-03-31";
