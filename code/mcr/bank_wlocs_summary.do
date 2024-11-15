

#delimit ;
use "${outdir}/bank_wloc_data.dta", clear;
keep if !missing(wloc_num_recipients);

order name wloc_*;
gsort -wloc_total_usage;
