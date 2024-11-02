
global projdir "/Users/brianlivingston/Dropbox/NU/Projects/svb-shock"
// global projdir "D:\Dropbox\NU\Projects\svb-shock"
global datadir "${projdir}/data"
global codedir "${projdir}/code"
global tempdir "${projdir}/temp"
global outdir "${projdir}/output"


#delimit ;

/* Clean CPI */
do "${codedir}/clean_cpi.do";

/* Call reports */
do "${codedir}/clean_call_reports.do";

/* Summary of deposits */
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

/** ****** ** ** */
/* Merge with call reports */
#delimit ;
use "${outdir}/cleaned_bank_data.dta", clear;
drop if bhclevel;
merge 1:1 rssdid qdate using "${tempdir}/corelogic_aggregated.dta", nogen keep(3);

