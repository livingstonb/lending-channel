
// *** CLEAN SOD *** //
import delimited using "${datadir}/sod_2022.csv", clear
// save "${tempdir}/sod.dta", replace

* Clean variables
replace bkmo = 1 - bkmo
rename bkmo isbranch

* Branches only
keep rssdid isbranch
collapse (sum) nbranches=isbranch, by(rssdid)
export delimited using "${tempdir}/sod_rssdid_only.csv", replace
