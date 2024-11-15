


save "${output}/corelogic_lending_series.dta", replace emptyok;
forvalues val = 2018/2023 {;
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
	
	/* Aggregate */
	collapse (sum) mortgageamount, by(mdate);
	append using "${tempdir}/corelogic_aggregated.dta";
	save "${output}/corelogic_lending_series.dta", replace;
};

/* Now do % capacity on wloc's */ #delimit ;
/* use "${tempdir}/nmls_wloc_aggregates.dta", clear; */

#delimit ;
import excel using "${datadir}/mcr/wloc_data.xlsx", clear firstrow;
gen ddate = dofc(quarter);
replace ddate = ddate + 65;
replace ddate = lastdayofmonth(ddate);
format %td ddate;
gen mdate = mofd(ddate);
format %tm mdate;

drop if usage < 0;
drop if (usage > limit) | missing(usage);
drop if (limit <= 0) | missing(limit);


/* collapse (mean) usage, by(qdate); */

collapse (sum) usage limit, by(ddate);
replace usage = usage / limit;
gen capacity = 1 - usage;

keep capacity ddate;
export delimited "${outdir}/mcr_wloc_capacity_series.csv", replace;

