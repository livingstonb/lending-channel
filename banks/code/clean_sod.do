
// *** CLEAN SOD *** //
import delimited using "${datadir}/sod_2022.csv", clear
save "${tempdir}/sod.dta", replace

import delimited using "${datadir}/sod_2022_1.csv", clear
append using "${tempdir}/sod.dta"
save "${tempdir}/sod.dta", replace

import delimited using "${datadir}/sod_2022_2.csv", clear
append using "${tempdir}/sod_rssdid.dta"
save "${tempdir}/sod.dta", replace

* Save only list of unique rssdid
keep rssdid
duplicates drop rssdid, force
export delimited using "${tempdir}/sod_rssdid_only.csv", replace
