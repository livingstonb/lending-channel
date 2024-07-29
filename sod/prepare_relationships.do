
// *** PREPARE RELATIONSHIPS (for python) *** //
* Prepare binary indicator for "Is a BHC"
use "${datadir}/bhck-jun2022.dta", clear
keep rssdid name
rename rssdid parent_rssdid
rename name bhc_name
replace bhc_name = strtrim(bhc_name)
duplicates drop parent_rssdid, force
gen is_bhc = 1

tempfile bhcid
save "`bhcid'"

* Prepare bank relationships
import delimited using "${datadir}/bank_relationships.csv", clear

tostring dt_start, replace
gen date0 = date(dt_start, "YMD")

tostring dt_end, replace
gen date1 = date(dt_end, "YMD")

format %td date0 date1

* Create links table, 06/2022 branches to 06/2022 BHC 
local sod_date = date("20220630", "YMD")
keep if (date0 <= `sod_date') & (date1 >= `sod_date')
keep if (pct_equity > 50) & !missing(pct_equity)
// keep if pct_equity == 100

keep id_rssd_parent id_rssd_offspring
rename id_rssd_parent parent_rssdid
rename id_rssd_offspring rssdid

merge m:1 parent_rssdid using "`bhcid'", nogen keep(1 3)
replace is_bhc = 0 if missing(is_bhc)

order rssdid parent_rssdid is_bhc bhc_name
sort rssdid

* Small number of special cases, will need to evaluate
* bysort rssdid: egen numparents = count(parent_rssdid)

export delimited using "${tempdir}/rssdid_links.csv", replace

