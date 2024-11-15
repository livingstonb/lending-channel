#delimit ;

/* Resave Summary of Deposits (FDIC) as dta */


/* Bank-level */
import delimited using "${tempdir}/sod_bank_level_2022.csv", clear;
keep rssdid nbranch branch_density rssdhcr;
destring branch_density, force replace;
gen bhc = 0;

tempfile sod_bank;
save "`sod_bank'";

/* BHC-level */
import delimited using "${tempdir}/sod_bhc_level_2022.csv", clear;
gen rssdhcr = rssdid;
keep rssdid nbranch branch_density;
append using "`sod_bank'";
replace bhc = 1 if missing(bhc);

rename rssdhcr sod_parentid;

/* Save */
save "${tempdir}/sod_2022.dta", replace;
