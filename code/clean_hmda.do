args year;

/* Aggregate public HMDA data by lender, for given year */

#delimit ;

/* File saved as hmda[yyyy].dta in data folder */
use "${datadir}/hmda`year'.dta", clear;

keep action_taken combined_loan_to_value_ratio open_end_line_of_credit
	loan_term hoepa_status conforming_loan_limit interest_only_payment
	income debt_to_income_ratio applicant_age lei derived_dwelling_category
	loan_amount;

/* Action taken variable:
	(1) Loan originated
	(2) Application approved but not accepted
	(3) Application denied
	(4) Application withdrawn by applicant
	(5) File closed for incompleteness
	(6) Purchased loan
	(7) Preapproval request denied
	(8) Preapproval request approved but not accepted
*/
drop if inlist(action_taken, 4, 6, 8);
keep if inlist(derived_dwelling_category, "Single Family (1-4 Units):Site-Built",
	"Single Family (1-4 Units):Manufactured");

/* LTV */
replace combined_loan_to_value_ratio = ""
	if (combined_loan_to_value_ratio == "NA");
destring combined_loan_to_value_ratio, force replace;
rename combined_loan_to_value_ratio ltv;

/* Indicator for sample loan type */
gen loan = 1 if (action_taken == 1);
replace loan = 0 if (open_end_line_of_credit != 2);
#delimit ;
replace loan = 0 if (loan_term != "360");
drop loan_term;

/* High cost loan */
replace hoepa_status = 0 if (hoepa_status == 2);
replace hoepa_status = . if (hoepa_status == 3);
rename hoepa_status high_cost;

/* Conforming/NC */
gen conforming = 1 if (conforming_loan_limit == "C");
replace conforming = 0 if (conforming_loan_limit == "NC");
drop conforming_loan_limit;

/* Interest-only */
replace interest_only_payment = 0 if (interest_only_payment == 2);
replace interest_only_payment = . if (interest_only_payment == 1111);
rename interest_only_payment interest_only;

/* Income */
destring income, force replace;
gen inc_quintile = 1 if (income <= 30);
replace inc_quintile = 2 if inrange(income, 31, 58);
replace inc_quintile = 3 if inrange(income, 59, 94);
replace inc_quintile = 4 if inrange(income, 95, 153);
replace inc_quintile = 5 if (income > 154) & !missing(income);
gen log_income = log(income);

/* Debt-to-income */
replace debt_to_income_ratio = "1"
	if inlist(debt_to_income_ratio, "<20%", "20%-<30%");
replace debt_to_income_ratio = "2" if (debt_to_income_ratio == "30%-<36%");
replace debt_to_income_ratio = "3"
	if inlist(debt_to_income_ratio, "50%-60%", ">60%");
destring debt_to_income_ratio, force replace;
replace debt_to_income_ratio = 2 if inrange(debt_to_income_ratio, 36, 49);
rename debt_to_income_ratio debt_to_income;

/* Age */
gen agecat = 1 if (applicant_age == "<25");
replace agecat = 2 if (applicant_age == "25-34");
replace agecat = 3 if (applicant_age == "35-44");
replace agecat = 4 if (applicant_age == "45-54");
replace agecat = 5 if (applicant_age == "55-64");
replace agecat = 6 if (applicant_age == "65-74");
replace agecat = 7 if (applicant_age == ">74");
rename agecat age_fine;

gen age_group = 1 if (age_fine <= 2);
replace age_group = 2 if inlist(age_fine, 3, 4);
replace age_group = 3 if inlist(age_fine, 5);
replace age_group = 4 if inlist(age_fine, 6, 7);
rename age_group age_coarse;

/* Select sample and aggregate according by LEI, mortgage amount-weighted */
keep if loan == 1;
rename loan total_lending;


#delimit ;
collapse (mean) conforming ltv age_coarse debt_to_income interest_only
	(mean) mu_linc=log_income
	(sum) total_lending [fweight=loan_amount], by(lei);

#delimit ;
foreach var of varlist conforming ltv mu_linc age_coarse debt_to_income
	interest_only total_lending {;
		rename `var' `var'`year';
	};
	
save "${tempdir}/hmda_lender_agg_`year'.dta", replace;
