clear

/* Preparation for adding missing LEIs */
	#delimit ;
	import excel using "${datadir}/corelogic_bank_missing_leis.xlsx",
		firstrow clear;
	keep rssdid lei;

	tempfile missing_leis;
	save "`missing_leis'", replace;

/* Now import bank data */
	import delimited using "${tempdir}/bank_data_cleaned.csv", clear;

	gen ddate = date(date, "YMD");
	format %td ddate;

	gen qdate = qofd(ddate);
	format %tq qdate;


/* Cleaning */
	#delimit ;
	replace id_lei = lei if missing(id_lei);
	drop lei;
	rename id_lei lei;
	replace lei = "" if lei == "0";
	
	merge m:1 rssdid using "`missing_leis'", nogen keep(1 3 4) update;

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
	
/* Bring in HMDA */
	merge m:1 lei using "${tempdir}/hmda_lender_agg_2022.dta",
		nogen keep(1 3);

/* Save bank level */
	gen bhclevel = 0;
	save "${tempdir}/cleaned_bank_level.dta", replace;
