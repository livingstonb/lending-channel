clear


global projdir "/Users/brianlivingston/Library/Mobile Documents/com~apple~CloudDocs/svb_shock"
global datadir "${projdir}/data"
global codedir "${projdir}/code"
global tempdir "${projdir}/temp"

import delimited using "${tempdir}/bank_data_cleaned.csv", clear

gen ddate = date(date, "YMD")
format %td ddate

gen qdate = qofd(ddate)
format %tq qdate

#delimit ;
/* Cleaning */
replace id_lei = lei if missing(id_lei);
drop lei;
rename id_lei lei;


/* Commercial banks (200), holding companies (500) */
gen bank = inlist(chtr_type_cd, 200)
			& inlist(insur_pri_cd, 1, 2, 6, 7);
gen domestic = (parent_domestic_ind == "Y") & (domestic_ind == "Y");
drop chtr_type_cd insur_pri_cd *domestic_ind;

gen year = year(ddate);
gen qlabel = string(qdate, "%tq");
drop *hc_ind id_rssd_hd_off dt_* cntry_inc_cd ddate nm_lgl;

gen member_fhlbs = parent_mbr_fhlbs_ind if !missing(parent_mbr_fhlbs_ind);
rename parent_nm_lgl parentname;
drop parent_*;


/* Estimates of insured and uninsured debt */
gen ins_deposits = dep_retir_lt250k + dep_nretir_lt250k
	+ (num_dep_retir_gt250k + num_dep_nretir_gt250k) * 250;
gen unins_deposits = deposits - ins_deposits;
gen unins_debt = liabilities - ins_deposits;
gen unins_lev = unins_debt / assets;

/* Merge with summary of deposits */
preserve;

import delimited using "temp/sod_bank_level_2022.csv", clear;
keep rssdid nbranch branch_density;

tempfile sod_data;
save "`sod_data'";

restore;
merge m:1 rssdid using "`sod_data'", keep(1 3) nogen;

/* Aggregate to BHC */
do "${codedir}/aggregate_bhc.do";

/* Statistics */
drop if assets < 1000000;

merge 1:1 rssdid qdate using "${tempdir}/bhck_for_merge.dta", nogen keep(1 3);

/* Keep if present in each period */
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

/* Regression */


/*
quietly sum qdate;
local quarters = r(max) - r(min) + 1;
bysort rssdid qdate: ;
*/
