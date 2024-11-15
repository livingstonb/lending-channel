

/* Aggregate corelogic lending, by lender, to multiple frequencies
	NOTE: Set up to match on RSSDID so any institutions without
	this indicator, or for which there is no match in crosswalk, will not show
	up in final dataset
*/

local agg_bhc 0

#delimit ;
/* Prepare crosswalk between corelogic lender codes and rssdid (bank-level only)
	TODO: Set up BHC matching
*/
import excel using "${datadir}/corelogic_company_codes_crosswalk.xlsx",
	firstrow clear;
rename corelogic_code lendercompanycode;
keep lendercompanycode rssdid;

tempfile cwalk;
save "`cwalk'", replace;

/* 
/* Crosswalk from bank id to parent id */
#delimit ;
use "${outdir}/cleaned_bank_data.dta", clear;
keep if qlabel == "2022q4";
keep rssdid parentid;
drop if parentid < 0;
replace parentid = rssdid  if missing(parentid);
duplicates drop rssdid parentid, force;

tempfile rssdid_parent_cwalk;
save "`rssdid_parent_cwalk'", replace;
*/

/*
if "`agg_bhc'" == "1" {;
	merge 1:1 rssdid using "`rssdid_parent_cwalk'", nogen keep(1 3);
	drop rssdid;
	rename parentid rssdid;
};
*/

/* Corelogic */
#delimit ;
clear;
save "${tempdir}/corelogic_aggregated.dta", emptyok replace;

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
	gen conformingamt = conformingloanindicator * mortgageamount;
	
	/* Use crosswalk to link corelogic lender codes to bank rssdid */
	merge m:1 lendercompanycode using "`cwalk'", nogen keep(3);
	
	/* Different frequencies */
	local aggvars mdate wdate svb_week fr_week;
	
	if "`agg_bhc'" == "1" {;
		merge m:1 rssdid using "`rssdid_parent_cwalk'", nogen keep(1 3)
			keepusing(parentid);
		drop rssdid;
		rename parentid rssdid;
	};
	
	merge m:1 lendercompanycode using "`cwalk'", nogen keep(1 3);
	drop lendercompanycode;
	
	/* Aggregate to bank-period, for each different frequency */
	foreach var of local aggvars {;
		preserve;
		collapse (count) nloans=mortgageamount (sum) lent=mortgageamount
			conforming_lent=conformingamt
			(mean) conforming_share=conformingloanindicator
			(first) lenderfullname, by(rssdid `var');
		append using "${tempdir}/corelogic_aggregated.dta";
		save "${tempdir}/corelogic_aggregated.dta", emptyok replace;
		restore;
	};
};

/*
/* Aggregate again for loans that show up in different data update */
foreach var of local aggvars {;
		preserve;
		collapse (count) nloans=mortgageamount (sum) lent=mortgageamount
			(first) lenderfullname, by(rssdid `var');
		append using "${tempdir}/corelogic_aggregated.dta";
		save "${tempdir}/corelogic_aggregated.dta", emptyok replace;
		restore;
	};
*/
	
use "${tempdir}/corelogic_aggregated.dta", clear;

order mdate rssdid lenderfullname lent;
gsort -mdate -lent;
save "${tempdir}/corelogic_aggregated.dta", replace;
