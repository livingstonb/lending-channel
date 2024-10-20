

#delimit ;
clear;
save "${tempdir}/corelogic_lenders.dta", emptyok replace;

local quarters 2022q1 2022q2 2022q3 2022q4 2023q1 2023q2 2023q3;
foreach val of local quarters {;
	import delimited using "${datadir}/corelogic_mortgage_`val'.csv",
		clear;
	duplicates drop clip fipscode transactionbatchdate, force;
	replace mortgageamount = mortgageamount / 1000;
	collapse (count) nloans=mortgageamount (sum) lent=mortgageamount
		(first) lenderfullname, by(lendercompanycode);
	gen quarter = "`val'";
	append using "${tempdir}/corelogic_lenders.dta";
	
	order quarter lendercompanycode lenderfullname lent;
	gsort -quarter -lent;
	save "${tempdir}/corelogic_lenders.dta", emptyok replace;
};

#delimit ;
/* Merge with rssdid */
import excel using "${datadir}/corelogic_company_codes_crosswalk.xlsx",
	firstrow clear;
rename corelogic_code lendercompanycode;
keep lendercompanycode rssdid;
merge 1:m lendercompanycode using "${tempdir}/corelogic_lenders.dta", nogen
	keep(3);
drop if missing(rssdid);

gen qdate = quarterly(quarter, "YQ");
format %tq qdate;

/* Sum over repeated banks */
drop lendercompanycode quarter;
collapse (sum) lent (sum) nloans, by(rssdid qdate);

/* Save */
save "${tempdir}/corelogic_aggregated.dta", replace;
