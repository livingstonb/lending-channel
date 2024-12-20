

/*
	Aggregate corelogic lending, by lender, to multiple frequencies
	NOTE: Set up to match on RSSDID so any institutions without
	this indicator, or for which there is no match in crosswalk, will not show
	up in final dataset
*/

#delimit ;
import excel using "${datadir}/corelogic_company_codes_crosswalk.xlsx",
	firstrow clear;
rename corelogic_code lendercompanycode;
keep lendercompanycode rssdid;

tempfile cwalk;
save "`cwalk'", replace;

/* Corelogic */
#delimit ;
clear;
save "${tempdir}/corelogic_aggregated.dta", emptyok replace;

forvalues val = 2022/2023 {;
	/* Read year */
	import delimited using "${datadir}/corelogic_mortgage_`val'.csv",
		clear;
	duplicates drop clip fipscode transactionbatchdate, force;
	replace mortgageamount = mortgageamount / 1000;
	drop transactionbatchdate transactionbatchsequencenumber
		mortgagerecordingdate refinanceloanindicator mortgageloantypecode
		constructionloanindicator constructionloanindicator
		mortgagesequencenumber;
		
	/* Don't need loan identifiers anymore */
	drop clip fipscode;
	
	/* Date variables */
	tostring mortgagedate, replace;
	gen date = date(mortgagedate, "YMD");
	format %td date;
	
	/* Use crosswalk to link corelogic lender codes to bank rssdid */
	merge m:1 lendercompanycode using "`cwalk'", nogen keep(3);
	drop lendercompanycode;
	
	/* Collapse to lender-week frequency */
	gen conformingamt = conformingloanindicator * mortgageamount;
	collapse (count) nloans=mortgageamount (sum) lent=mortgageamount
			conforming_lent=conformingamt
			(first) lenderfullname, by(rssdid date);
	replace lenderfullname = . if rssdid == .;
	
	/* Append previous years and save again */
	append using "${tempdir}/corelogic_aggregated.dta";
	save "${tempdir}/corelogic_aggregated.dta", emptyok replace;
};

/* Deflate using monthly CPI */
gen mdate = mofd(date);
merge m:1 mdate using "${tempdir}/cpi.dta", nogen keep(1 3);
replace lent = lent / cpi;
replace conforming_lent = conforming_lent / cpi;
drop mdate cpi;

order date rssdid lenderfullname lent;
gsort -date -rssdid;
save "${tempdir}/corelogic_aggregated.dta", replace;
