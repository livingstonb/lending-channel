

/* AGGREGATES TO MONTHLY */

local agg_bhc 1

#delimit ;
/* Prepare crosswalk between corelogic lender codes and rssdid */
import excel using "${datadir}/corelogic_company_codes_crosswalk.xlsx",
	firstrow clear;
rename corelogic_code lendercompanycode;
keep lendercompanycode rssdid;

tempfile cwalk;
save "`cwalk'", replace;

/* Aggregate to BHC */
#delimit ;
use "${outdir}/cleaned_bank_data.dta", clear;
keep if qlabel == "2022q4";
keep rssdid parentid;
drop if parentid < 0;
replace parentid = rssdid  if missing(parentid);
duplicates drop rssdid parentid, force;

tempfile rssdid_parent_cwalk;
save "`rssdid_parent_cwalk'", replace;

/* Add missing LEIs */
import excel using "${datadir}/corelogic_bank_missing_leis.xlsx",
	firstrow clear;
keep rssdid lei;

if "`agg_bhc'" == "1" {;
	merge 1:1 rssdid using "`rssdid_parent_cwalk'", nogen keep(1 3);
	drop rssdid;
	rename parentid rssdid;
};

tempfile missing_leis;
save "`missing_leis'", replace;

/* Corelogic */
#delimit ;
clear;
save "${tempdir}/corelogic_aggregated.dta", emptyok replace;

/* 2021q4 2022q1 2022q2 2022q3 2022q4 2023q1 2023q2 */
local quarters 2022q4 2023q1 2023q2 ;
forvalues val = 2022/2023 {;
	/* Import quarter */
	import delimited using "${datadir}/corelogic_mortgage_`val'.csv",
		clear;
	duplicates drop clip fipscode transactionbatchdate, force;
	replace mortgageamount = mortgageamount / 1000;
	
	/* Date variables */
	tostring mortgagedate, replace;

	gen date = date(mortgagedate, "YMD");
	format %td date;
	
	gen wdate = wofd(date);
	format %tw wdate;
	
	gen mdate = mofd(date);
	format %tm mdate;
	
	/* Put event at beginning of event week */
	gen svb_week = floor((date - mdy(3,9,2023)) / 7);
	gen fr_week = floor((date - mdy(5,1,2023)) / 7);
	
	/* Deflate using monthly CPI */
	merge m:1 mdate using "${tempdir}/cpi.dta", nogen keep(1 3);
	replace mortgageamount = mortgageamount / cpi;
	
	/* Use crosswalk to link corelogic lender codes to bank rssdid */
	merge m:1 lendercompanycode using "`cwalk'", nogen keep(3);
	
	local aggvars mdate wdate svb_week fr_week;
	
	if "`agg_bhc'" == "1" {;
		merge m:1 rssdid using "`rssdid_parent_cwalk'", nogen keep(1 3)
			keepusing(parentid);
		drop rssdid;
		rename parentid rssdid;
	};
	
	/* Aggregate to bank-period */
	foreach var of local aggvars {;
		preserve;
		collapse (count) nloans=mortgageamount (sum) lent=mortgageamount
			(first) lenderfullname, by(rssdid `var');
		append using "${tempdir}/corelogic_aggregated.dta";
		save "${tempdir}/corelogic_aggregated.dta", emptyok replace;
		restore;
	};
};

/* Aggregate again for loans that show up in different data update */
foreach var of local aggvars {;
		preserve;
		collapse (count) nloans=mortgageamount (sum) lent=mortgageamount
			(first) lenderfullname, by(rssdid `var');
		append using "${tempdir}/corelogic_aggregated.dta";
		save "${tempdir}/corelogic_aggregated.dta", emptyok replace;
		restore;
	};
	
use "${tempdir}/corelogic_aggregated.dta", clear;
order mdate rssdid lenderfullname lent;
gsort -mdate -lent;
save "${tempdir}/corelogic_aggregated.dta", emptyok replace;

/* Merge with call reports */
#delimit ;
use "${outdir}/cleaned_bank_data.dta", clear;
keep if qlabel == "2022q4";
duplicates tag rssdid, gen(dup);
drop if (dup > 0) & missing(parentid);

merge 1:m rssdid using "${tempdir}/corelogic_aggregated.dta",  nogen keep(3);
merge m:1 rssdid using "`missing_leis'", nogen keep(1 3 4) update;

save "${tempdir}/cleaned_bank_data_corelogic_merged.dta", replace;
