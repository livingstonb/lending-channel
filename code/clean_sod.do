#delimit ;

/* Resave Summary of Deposits (FDIC) as dta */

local year 2022;

/* Bank-level */
import delimited using "${tempdir}/sod_bank_level_`year'.csv", clear;
keep rssdid nbranch branch_density rssdhcr;
destring branch_density, force replace;
gen bhc = 0;

tempfile sod_bank;
save "`sod_bank'";

/* BHC-level */
import delimited using "${tempdir}/sod_bhc_level_`year'.csv", clear;
gen rssdhcr = rssdid;
keep rssdid nbranch branch_density;
append using "`sod_bank'";
replace bhc = 1 if missing(bhc);

rename rssdhcr sod_parentid;
rename nbranch nbranch_`year';
rename branch_density branch_density_`year';

/* Save */
save "${tempdir}/sod_`year'.dta", replace;
