
global projdir "/Users/brianlivingston/Dropbox/NU/Projects/svb-shock"
global datadir "${projdir}/data"
global codedir "${projdir}/code"
global tempdir "${projdir}/temp"
global outdir "${projdir}/output"


#delimit ;

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
	nogen keep(1 3 4) update keepusing(r2* idr*);
replace name = strtrim(name);

/* Drop (for now) */
drop dep_* num_* famsec* flien* rcon_* gsec* othll* sub_debt* rcfd_* parent_dt*
	bhc;
drop if rssdid <= 0;

/* Save */
cap mkdir "${outdir}";
save "${outdir}/cleaned_bank_data.dta", replace;
