clear

#delimit ;

tempfile alldata;
save "`alldata'", emptyok;

local increment = 1000000;
forvalues range_start = 2(`increment')60000000 {;
	local range_end = `range_start' + `increment' - 1;
	clear;
	di `range_end';
	import delimited "${datadir}/Ratewatch/depositRateData_2020.txt",
		clear rowrange(`range_start':`range_end')  varnames(1)
		stringcols(10);
	if (_N == 0) {;
		use "`alldata'", clear;
		continue, break;
	};
	
	keep if inlist(producttype, "CD", "INTCK", "MM", "SAV");
	keep if inlist(termlength, 0, 1, 3, 6, 9, 12, 24, 36, 60);
	
	drop if inlist(termtype, "D", "Y") | (promo == "Y");
	drop termtype promo;
	
	drop if prd_typ_join != producttype;
	tostring termlength, force replace;
	replace producttype = producttype + termlength + "m" if producttype == "CD";
	
	gen date = date(datesurveyed, "YMD");
	format %td date;
	keep accountnumber product apy date;
	
	append using "`alldata'", force;
	save "`alldata'", replace;
};

/* Next step to drop 3 weeks out of each month? */
