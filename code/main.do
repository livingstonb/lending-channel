
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
use "${tempdir}/cleaned_bank_bhc_combined.dta", clear;
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


/*************************/
/* MCR */

do "${codedir}/mcr/clean_mcr.do";
do "${codedir}/mcr/link_nmls_rssdid.do";

#delimit ;
use "${tempdir}/mcr_cleaned.dta", clear;
merge 1:1 firm qdate using "${tempdir}/nmls_wloc_aggregates.dta", nogen
	keep(3);


/** ****** ** ** */
/* Merge with call reports */
#delimit ;
use "${outdir}/cleaned_bank_data.dta", clear;
drop if bhclevel;
merge 1:1 rssdid qdate using "${tempdir}/corelogic_aggregated.dta", nogen keep(3);

