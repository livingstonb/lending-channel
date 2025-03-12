/*
	This code is to be run only after main.py was run. Requires data saved by
	main.py.
	
	Using CPI, HMDA, corelogic, and data obtained from python code, this code
	successively calls other do-files to price several datasets ready for
	final data analysis.
*/


/* Directories */
global projdir "/Users/brianlivingston/Dropbox/NU/Projects/svb-shock"
// global projdir "D:\Dropbox\NU\Projects\svb-shock"
include "${projdir}/code/stata_header.doh"

/* Clean CPI */
#delimit ;
do "${codedir}/clean_cpi.do";

/* HMDA */
 #delimit ;
local year 2022;
do "${codedir}/clean_hmda.do" `year';

/* Aggregate bank Corelogic mortgage lending to bank-day level */
#delimit ;
do "${codedir}/corelogic/aggregate_corelogic_mortgages_banks.do";

/***************** BANK CALL REPORTS/OTHER BANK DATA **************************/

/* Call reports, bank level */
#delimit ;
do "${codedir}/clean_call_reports_to_bank_level.do";

/* Aggregate to BHC-level */
#delimit ;
do "${codedir}/aggregate_bank_level_to_bhc.do";

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

/* Drop */
drop parent_dt* bhc;
drop if rssdid <= 0;

/* Save final bank panel data */
cap mkdir "${outdir}";
save "${outdir}/final_bank_panel.dta", replace;

/***************** MCR ********************************************************/
/*
	Cleans raw MCR data, using WLOCs only to create variables firm-quarter
	aggregates (this is not at firm-wloc-quarter level).
	Saves final panel dataset.
*/
do "${codedir}/mcr/clean_mcr_panel.do";


/*
	First create panel of credit lines at wloc-quarter level.
	
	Then aggregation of pre-shock wloc data (and other bank exposure variables).
	From "final_bank_panel.dta", generates "wloc_bank_level_aggregates.dta"
	which now has WLOC variables that have been aggregated across banks.
*/
do "${codedir}/mcr/clean_wloc.do";
use "${tempdir}/wloc_panel_cleaned.dta", clear;
do "${codedir}/mcr/save_wloc_bank_level.do";


/******************************************************************************/
/* Combined dataset */
/* do "${codedir}/combine_mcr_wloc_bank.do"; */
