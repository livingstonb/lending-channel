


use "${tempdir}/cleaned_bank_data_corelogic_merged.dta", clear

gen event = wdate - weekly("2023w10", "YW")

keep if !missing(rssdid, wdate, lent)
xtset rssdid wdate

keep if nloans > 5

gen llent = log(lent)
gen lassets = log(assets)

drop if event > 12
tab event, gen(d_event)

replace lassets = round(lassets)

gen post = event >= 2


#delimit ;
xtreg llent d_event2-d_event9 d_event11-d_event18
	if inrange(event, -8, 18), fe vce(robust);


xtile qtile_bdensity = branch_density if !missing(llent), nquantiles(3)
recode qtile_bdensity (1=0) (3=1) (2=.)

#delimit ;
xtreg llent d_event*
	c.(branch_density lassets)#c.d_event*, fe vce(robust);

/*
xtreg llent
	c.branch_density#i.post L(1/4).llent, fe vce(robust);
*/
// This lag is too recent (last week)
