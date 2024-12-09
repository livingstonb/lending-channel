
/* Set directory macros */
global projdir "/Users/brianlivingston/Dropbox/NU/Projects/svb-shock"
// global projdir "D:\Dropbox\NU\Projects\svb-shock"
global datadir "${projdir}/data"
global codedir "${projdir}/code"
global tempdir "${projdir}/temp"
global outdir "${projdir}/output"




/* Clean CPI */
#delimit ;
do "${codedir}/clean_cpi.do";

/* HMDA */
 #delimit ;
local year 2022;
do "${codedir}/clean_hmda.do" `year';

/* Corelogic */
#delimit ;
do "${codedir}/corelogic/corelogic_aggregates.do";

/* Call reports, bank level */
 #delimit ;
do "${codedir}/clean_call_reports_to_bank_level.do";

/* Aggregate to BHC-level */
 #delimit ;
do "${codedir}/aggregate_bank_level_to_bhc.do";

/* Aggregate Corelogic to BHC-level */
/* do "${codedir}/aggregate_corelogic_bhc.do"; */

/* Summary of deposits */
#delimit ;
do "${codedir}/clean_sod.do";

/* CRSP daily */
do "${codedir}/clean_crsp_daily.do";

/* Merges */
#delimit ;
use "${tempdir}/cleaned_bank_bhc_combined.dta", clear;
merge m:1 rssdid using "${tempdir}/sod_2021.dta", nogen keep(1 3);
merge m:1 rssdid using "${tempdir}/sod_2022.dta", nogen keep(1 3);
merge m:1 rssdid using "${tempdir}/crsp_daily_cleaned.dta", nogen keep(1 3);
merge m:1 parentid using "${tempdir}/crsp_daily_cleaned.dta",
	nogen keep(1 3 4) update keepusing(svbR frR);
replace name = strtrim(name);

/* Drop (for now) */
drop parent_dt* bhc;
drop if rssdid <= 0;

/* Save */
cap mkdir "${outdir}";
save "${outdir}/cleaned_bank_data.dta", replace;

/* Create more bank variables for nonbank exposure measure */
do "${codedir}/prepare_bank_for_nonbank_merge.do";

/*************************/
/* MCR */

do "${codedir}/mcr/clean_mcr_panel.do";
do "${codedir}/mcr/clean_wloc.do";

use "${tempdir}/wloc_panel_cleaned.dta", clear;
	collapse (sum) limit available usage, by(firm qdate);
	save "${tempdir}/wloc_nonbank_level_aggregates.dta", replace;

do "${codedir}/mcr/save_wloc_bank_level.do";


/*************************/
/* Combined dataset */
do "${codedir}/combine_mcr_wloc_bank.do";
