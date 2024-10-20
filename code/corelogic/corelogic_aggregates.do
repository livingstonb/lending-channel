#delimit ;
/* Merge with rssdid */
import excel using "${datadir}/corelogic_company_codes_crosswalk.xlsx",
	firstrow clear;
rename corelogic_code lendercompanycode;
keep lendercompanycode rssdid;

tempfile cwalk;
save "`cwalk'", replace;


#delimit ;
clear;
save "${tempdir}/corelogic_weekly.dta", emptyok replace;

/* 2022q1 2022q2 2022q3 2022q4  2023q3*/
local quarters 2021q4 2022q1 2022q2 2022q3 2022q4 2023q1 2023q2 ;
foreach val of local quarters {;
	import delimited using "${datadir}/corelogic_mortgage_`val'.csv",
		clear;
	duplicates drop clip fipscode transactionbatchdate, force;
	replace mortgageamount = mortgageamount / 1000;
	tostring mortgagedate, replace;

	gen date = date(mortgagedate, "YMD");
	format %td date;
	
	gen wdate = wofd(date);
	format %tw wdate;
	
	gen mdate = mofd(date);
	format %tm mdate;
	
	gen week = week(date);
	
	/* gen period = .;
	forvalues t = 1/26 {;
		replace period = `t' if inlist(week, 2*(`t'-1)+1, 2*(`t'-1)+2);
	};
	*/
	
	gen period = mdate;
	format %tm period;
	
	merge m:1 lendercompanycode using "`cwalk'", nogen keep(3);
	
	collapse (count) nloans=mortgageamount (sum) lent=mortgageamount
		(first) lenderfullname, by(rssdid period);
	
	append using "${tempdir}/corelogic_weekly.dta";
	
	order period rssdid lenderfullname lent;
	gsort -period -lent;
	save "${tempdir}/corelogic_weekly.dta", emptyok replace;
};

/*
gen period = .
forvalues t = 1/26 {
	replace period = `t' if inlist(week, 2*(`t'-1)+1, 2*(`t'-1)+2)
}
*/

#delimit ;
collapse (sum) nloans (sum) lent
		(first) lenderfullname, by(rssdid period);

order period rssdid lenderfullname lent;
	gsort -period -lent;
save "${tempdir}/corelogic_weekly.dta", emptyok replace;

/* Merge with call reports */
#delimit ;
use "${outdir}/cleaned_bank_data.dta", clear;
keep if qlabel == "2022q3";
duplicates tag rssdid, gen(dup);
drop if (dup > 0) & missing(parentid);
merge 1:m rssdid using "${tempdir}/corelogic_weekly.dta",  nogen keep(3);

save "${tempdir}/cleaned_bank_data_corelogic_merged.dta", replace;
