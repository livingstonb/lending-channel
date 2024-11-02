
/*
#delimit ;
import excel "${datadir}/mcr_panel.xlsx", clear firstrow;
*/


#delimit ;
import excel "C:\Users\akbri\Documents\mcr_data/matching_corelogic_lenders_raw.xlsx",
	clear firstrow;

replace CORELOGIC_NAME = subinstr(CORELOGIC_NAME, "MTG", "Mortgage", .);
replace CORELOGIC_NAME = subinstr(CORELOGIC_NAME, " CORPORATION ", " Corp ", .);
replace CORELOGIC_NAME = subinstr(CORELOGIC_NAME, "FIN'L", "Financial", .);
replace CORELOGIC_NAME = subinstr(CORELOGIC_NAME, "LNDG", "Lending", .);
replace CORELOGIC_NAME = subinstr(CORELOGIC_NAME, " HM ", " Home ", .);
replace CORELOGIC_NAME = subinstr(CORELOGIC_NAME, " FNDG", " Funding", .);
replace CORELOGIC_NAME = subinstr(CORELOGIC_NAME, " GRP", " Group", .);

replace NMLS_NAME = subinstr(NMLS_NAME, " Corporation ", " Corp ", .);

export excel "C:\Users\akbri\Documents\mcr_data/matching_corelogic_lenders_cleaned.xlsx",
	replace firstrow(variables);
