


#delimit ;
keep parentid qdate assets deposits nbranch retail_mortorig_forsale
	est_unins_deposits qlabel;

collapse (sum) assets (sum) deposits (sum) nbranch
	(sum) retail_mortorig_forsale (sum) est_unins_deposits
	(first) qlabel, by(parentid qdate);


drop if retail_mortorig_forsale == 0;
rename parentid rssdid;

quietly sum qdate;
gen temp_bdensity = nbranch / deposits * 1e5 if qdate == r(min);
bysort rssdid: egen branch_density = max(temp_bdensity);
drop temp_bdensity;
