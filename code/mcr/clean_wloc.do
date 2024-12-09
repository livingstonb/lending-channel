
/* Hand-matched rssdid values for name partials from MCR */
	#delimit ;
	import excel using "${datadir}/mcr/bank_name_conversion.xlsx", clear firstrow;
	drop if missing(MCR);
	keep MCR FedName rssdid date1 date2;
	format %td date1;

/* Extend date to 2024 for entries likely prematurely cut off at 2022 */
	local change_date2
		1094640 1074156 1073757 2349815 5006575 4284536 4191465 3838727
		1026632 1032473 1037003 1039502 1068025 1068191 1069778 1070345
		1082067 1097025 1107184 1109599 1111435 1117512 1119794 1120754
		1199563 1199844 1491641 1562859 1951350 2017673 2016340 3218543
		2132932 2162966 2277860 2380443 2706735 2784920 3025385 3333790
		3587146 3650152 3838857 3840029 3852022 4347208 4389329 4517298
		3559844 1275216;
	foreach id of local change_date2 {;
		replace date2 = mdy(12,31,2024) if rssdid == `id';
	};

	replace date1 = mdy(3,31,2012) if rssdid == 3559844;
	drop if missing(rssdid);
	drop if missing(date1) | missing(date2);

	drop FedName;
	rename MCR name_stub;
	sort name_stub;
	levelsof name_stub, local(stubs);

	#delimit ;
	bysort name_stub: egen date_min = min(date1);
	bysort name_stub: egen date_max = max(date2);
	replace date1 = date_min;
	replace date2 = date_max;
	drop date_m*;
	duplicates drop name_stub, force;
	reshape long date, i(name_stub) j(t);
	drop t;

	gen qdate = qofd(date);
	format %tq qdate;

/* Fill in missing between-dates */
	egen groupid = group(name_stub);
	xtset groupid qdate;
	tsfill, full;
	by groupid (qdate): replace rssdid = rssdid[_n-1] if _n > 1;
	by groupid (qdate): replace name_stub = name_stub[_n-1] if _n > 1;
	drop date groupid;
	drop if missing(rssdid);

/* Save panel of names, rssdids, dates */
	save "${tempdir}/bank_name_conversion_cleaned.dta", replace;

/* Read WLOC data to match to banks */
	#delimit ;
	import excel using "${datadir}/mcr/wloc_data.xlsx", clear firstrow;

	gen name_stub = "";
	foreach stub of local stubs {;
		
		replace name_stub = `"`stub'"' if  (strpos(NameID, `"`stub'"') > 0) & (name_stub == "");
		replace name_stub = `"`stub'"' if NameID == `"`stub'"';

	};

	gen ddate = dofc(quarter);
	drop quarter;
	gen qdate = qofd(ddate);
	format %tq qdate;

/* Merge in saved rssdid from above */
	merge m:1 name_stub qdate using "${tempdir}/bank_name_conversion_cleaned.dta",
		nogen keep(1 3) keepusing(rssdid);
	keep firm limit available usage rssdid qdate;

/* Weird cases */
	drop if ((usage < 0) | (usage > limit)) & !missing(usage, limit);

/* Save */
	save "${tempdir}/wloc_panel_cleaned.dta", replace;
	
/* Aggregate and save at nonbank level also */
	collapse (sum) limit available usage, by(firm qdate);
	save "${tempdir}/wloc_nonbank_level_aggregates.dta", replace;
