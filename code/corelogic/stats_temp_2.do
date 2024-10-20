


use "${tempdir}/cleaned_bank_data_corelogic_merged.dta", clear

// gen ddate = dofw(wdate)
// format %td ddate
// gen month = month(ddate)
// gen week = week(ddate)

/* 
gen day = day(ddate)
gen week = mod(week(ddate), 4)
*/

// keep if bank & domestic
merge m:1 lei using "${tempdir}/hmda_lender_agg_2022.dta", nogen keep(1 3)

// gen event = wdate - weekly("2023w10", "YW")
gen event = period - 5

keep if !missing(rssdid, period, lent)
xtset rssdid period

keep if nloans > 4

gen llent = log(lent)
gen lassets = log(assets)
gen lnloans = log(nloans)

drop if event > 3
tab event, gen(d_event)


gen post = (event >= 1) if !missing(event)

#delimit ;
xtile qtile_bdensity = branch_density if !missing(llent), nquantiles(3);
/* recode qtile_bdensity (1=0) (3=1) (2=.); */
replace qtile_bdensity = qtile_bdensity - 2;


do "${codedir}/gen_reg_variables.do";

xtile qtile_unins_leverage = unins_leverage if !missing(llent), nquantiles(3);
/* recode qtile_unins_leverage (1=0) (3=1) (2=.); */

	
#delimit ;
xtreg llent d_event2-d_event4 d_event5-d_event8
	c.post#c.(lassets debt_to_income22 age_coarse22 conforming22)
	c.( branch_density)#c.(d_event2-d_event4 d_event5-d_event8)
	, fe vce(robust);
	

#delimit ;
xtreg llent d_event2-d_event4 d_event5-d_event8
	c.post#c.( lassets debt_to_income22 age_coarse22 conforming22
	unins_leverage )
	, fe vce(robust);

keep if bank;
keep if inlist(period, 7, 4);
replace post = (period == 7);
xtreg llent post c.post#c.(lassets
	debt_to_income22 age_coarse22 conforming22
	lshare_mort_sold qtile_bdensity
	unins_debt_net_of_coll), fe vce(robust);

xtreg llent post c.post#c.(lassets
	debt_to_income22 age_coarse22 conforming22
	lshare_mort_sold qtile_bdensity
	) c.post#c.lassets#c.qtile_bdensity, fe vce(robust);

/*
xtreg llent
	c.branch_density#i.post L(1/4).llent, fe vce(robust);
*/
// This lag is too recent (last week)
