

#delimit ;
twoway (line newlistings_zillow mdate) (line newlistings_corelogic mdate),
	legend(label(1 "Zillow") label(2 "Corelogic")) ytitle("New Listings")
	graphregion(color(white)) bgcolor(white) xtitle("Month");
	
graph export "${tempdir}/new_listings.png", replace;
sum newlistings_corelogic newlistings_zillow, detail;
