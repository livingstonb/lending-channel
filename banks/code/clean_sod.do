
//////////
// Cleans summary of deposits (SOD) and produces two datasets:
// 1) BHC-level aggregates (deposits, number branches, etc)
// 2) Unique list of branch rssdids
//////////

* Summary of deposits bulk download
import delimited using "${datadir}/sod_2022.csv", clear

* Brach identifier (as opposed to main office)
replace bkmo = 1 - bkmo
rename bkmo nbranches

// BHC-LEVEL AGGREGATES //

* Summary of deposits bulk download
import delimited using "${datadir}/sod_2022.csv", clear

* Brach identifier (as opposed to main office)
replace bkmo = 1 - bkmo
rename bkmo nbranches

* Institutional level (rssdid) deposits
replace depsum = subinstr(depsum, ",", "", .)
destring depsum, replace

#delimit ;
/* Aggregate to institution-level (rssdid) */
collapse (sum) nbranches (sum) depsum
	(first) namehcr (first) rssdhcr, by(rssdid);
/* Aggregate to top-tier BHC-level (rssdhcr) */
collapse (sum) nbranches (sum) depsum (first) namehcr,
	by(rssdhcr);
#delimit cr

// UNIQUE BRANCH IDs //

* Summary of deposits bulk download
import delimited using "${datadir}/sod_2022.csv", clear

* Brach identifier (as opposed to main office)
replace bkmo = 1 - bkmo
rename bkmo nbranches

* Branches only
keep rssdid nbranches
collapse (sum) nbranches, by(rssdid)
export delimited using "${tempdir}/sod_rssdid_only.csv", replace
