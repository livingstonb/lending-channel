
#delimit ;
/* Prepare CPI */
import delimited using "${datadir}/CPIAUCSL.csv", varnames(1) clear;
gen ddate = date(date, "YMD");
gen mdate = mofd(ddate);
format %tm mdate;
drop ddate date;
rename cpiaucsl cpi;

levelsof cpi if mdate == monthly("2023m1", "YM"), local(cpi2023m1);
replace cpi = cpi / `cpi2023m1';

save "${tempdir}/cpi.dta", replace;
