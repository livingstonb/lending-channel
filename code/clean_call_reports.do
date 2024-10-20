clear

import delimited using "${tempdir}/bank_data_cleaned.csv", clear
tempfile bank_level

gen ddate = date(date, "YMD")
format %td ddate

gen qdate = qofd(ddate)
format %tq qdate

#delimit ;
/* Cleaning */
replace id_lei = lei if missing(id_lei);
drop lei;
rename id_lei lei;
replace lei = "" if lei == "0";

/* Commercial banks (200), holding companies (500) */
gen bank = inlist(chtr_type_cd, 200)
			& inlist(insur_pri_cd, 1, 2, 6, 7);
gen domestic = (parent_domestic_ind == "Y") & (domestic_ind == "Y");
drop chtr_type_cd insur_pri_cd *domestic_ind;

gen year = year(ddate);
gen qlabel = string(qdate, "%tq");
drop *hc_ind dt_* cntry_inc_cd ddate nm_lgl;

rename parent_mbr_fhlbs_ind parent_member_fhlbs;
rename mbr_fhlbs_ind member_fhlbs;
rename parent_nm_lgl parentname;

/* Estimates of insured and uninsured debt */
gen ins_deposits = dep_retir_lt250k + dep_nretir_lt250k
	+ (num_dep_retir_gt250k + num_dep_nretir_gt250k) * 250;
gen alt_ins_deposits = dep_retir_lt250k + dep_nretir_lt250k;

/* Other variables */
gen unins_deposits = deposits - ins_deposits;
gen unins_debt = liabilities - ins_deposits;

/* Save bank level */
gen bhclevel = 0;
save "${tempdir}/cleaned_bank_level.dta", replace;

/* Aggregate to BHC */
do "${codedir}/aggregate_bhc.do";
gen bhclevel = 1;
save "${tempdir}/cleaned_bhc_level.dta", replace;

/* Append */
use "${tempdir}/cleaned_bank_level.dta", clear;
append using "${tempdir}/cleaned_bhc_level.dta";

save "${tempdir}/cleaned_bank_bhc_combined.dta", replace;


/* Statistics */
/* drop if assets < 1000000;

merge 1:1 rssdid qdate using "${tempdir}/bhck_for_merge.dta", nogen keep(1 3); */

/* Keep if present in each period */
/*
quietly sum qdate;
scalar tperiods = r(max) - r(min) + 1;
bysort rssdid: drop if _N < tperiods;



tsset rssdid qdate;
gen ldeposits = log(deposits);
gen dldeposits = d.ldeposits;
gen lunins = log(est_unins_deposits);
gen dlunins = d.lunins;
gen lmort = log(retail_mortorig_forsale);
gen dlmort = d.lmort;

xtile qtile_bd = dldeposits, nquantiles(5);
graph bar dlunins, over(qtile_bd) over(qlabel);
*/

/* Regression */


/*
quietly sum qdate;
local quarters = r(max) - r(min) + 1;
bysort rssdid qdate: ;
*/
