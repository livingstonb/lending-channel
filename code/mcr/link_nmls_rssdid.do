

#delimit ;
import excel using "${datadir}/mcr/bank_name_conversion.xlsx", clear firstrow;
drop if missing(MCR);
keep MCR FedName rssdid date1 date2;
format %td date1;

local change_date2
	1094640 1074156 1073757 2349815 5006575 4284536 4191465 3838727
	1026632 1032473 1037003 1039502 1068025 1068191 1069778 1070345
	1082067 1097025 1107184 1109599 1111435 1117512 1119794 1120754
	1199563 1199844 1491641 1562859 1951350 2017673 2016340 3218543
	2132932 2162966 2277860 2380443 2706735 2784920 3025385 3333790
	3587146 3650152 3838857 3840029 3852022 4347208 4389329 4517298
	3559844 1275216;
foreach id of local change_date2 {;
	replace date2 = mdy(12,31,2024) if rssdid == `id';
};

replace date1 = mdy(3,31,2012) if rssdid == 3559844;
drop if missing(rssdid);
drop if missing(date1) | missing(date2);

drop FedName;
rename MCR name_stub;
sort name_stub;
levelsof name_stub, local(stubs);

/*
export excel "${tempdir}/bank_name_conversion_cleaned.xlsx",
	replace firstrow(variables);
*/


/* WLOC data */
#delimit ;
bysort name_stub: egen date_min = min(date1);
bysort name_stub: egen date_max = max(date2);
replace date1 = date_min;
replace date2 = date_max;
drop date_m*;
duplicates drop name_stub, force;
reshape long date, i(name_stub) j(t);
drop t;

gen qdate = qofd(date);
format %tq qdate;

egen groupid = group(name_stub);
xtset groupid qdate;
tsfill, full;
by groupid (qdate): replace rssdid = rssdid[_n-1] if _n > 1;
by groupid (qdate): replace name_stub = name_stub[_n-1] if _n > 1;
drop date groupid;
drop if missing(rssdid);

save "${tempdir}/bank_name_conversion_cleaned.dta", replace;

import excel using "${datadir}/mcr/wloc_data.xlsx", clear firstrow;

gen name_stub = "";
foreach stub of local stubs {;
	replace name_stub = `"`stub'"' if
		(strpos(NameID, `"`stub'"') > 0) & (name_stub == "");
};

gen ddate = dofc(quarter);
drop quarter;
gen qdate = qofd(ddate);
format %tq qdate;

merge m:1 name_stub qdate using "${tempdir}/bank_name_conversion_cleaned.dta",
	nogen keep(1 3) keepusing(rssdid);
	
/*
gen observed = !missing(rssdid);
collapse (sum) usage, by(observed);
sort observed;
di usage[2] / (usage[2] + usage[1]);
*/
	
/* Clean up */
drop if missing(rssdid);
drop name_stub ddate NameID;

keep firm limit available usage rssdid qdate;

/* FOR NOW DROP THESE */
drop if usage < 0;

/* Aggregate bank lending to same firm */
collapse (sum) limit (sum) available (sum) usage, by(rssdid firm qdate);

/* Save at firm level */
preserve;
collapse (sum) limit available usage, by(firm qdate);
save "${tempdir}/nmls_wloc_aggregates.dta", replace;
restore;

/* Collapse on rssdid to do bank-level analysis */ #delimit ;
collapse (count) wloc_num_recipients=firm
	(sum) wloc_total_limit=limit
	(mean) wloc_avg_limit=limit
	(sd) wloc_sd_limit=limit
	(sum) wloc_total_available=available
	(mean) wloc_avg_available=available
	(sd) wloc_sd_available=available
	(sum) wloc_total_usage=usage
	(mean) wloc_avg_usage=usage
	(sd) wloc_sd_usage=usage, by(rssdid qdate);

merge 1:m rssdid qdate using "${outdir}/cleaned_bank_data.dta",
	nogen keep(1 2 3 4);
	

keep if qdate == quarterly("2022q4", "YQ");
keep if bhclevel == 1;

drop v1 form est_unins_deposits dep_retir_lt250k dep_retir_gt250k num_dep_retir_gt250k dep_nretir_lt250k dep_nretir_gt250k num_dep_nretir_gt250k totsec_afs_amort ci_loans_nontrading nbfi_loans lns_for_purch_carr_sec cons_oth_loans repo_liab_ff htm_securities afs_debt_securities ll_hfs ll_hfi ll_loss_allowance eq_sec_notftrading liab_fbk_trans liab_fbk_ntrans liab_foff_trans liab_foff_ntrans cons_parent_fdic_cert treas_htm_amort treas_htm_fval treas_afs_amort treas_afs_fval treas_trading retail_mortorig_forsale whlsale_mortorig_forsale res_mort_hfs_or_hft totsec_afs_fval totsec_htm_amort ci_loans_trading cons_oth_revolvc_loans unearnedinc_loansleases repo_liab_oth oth_borr_money sub_debt unused_comm_ci unused_comm_nbfi rcoa_tier1cap rcoa_levratio net_sec_income net_serv_fees salaries_and_benefits exp_premises_fa parentid parent_chtr_type_cd parent_insur_pri_cd parent_member_fhlbs parentname parent_cntry_inc_cd parent_id_lei member_fhlbs lei mtm_2022_loss_level trnsfm_cd event_was_successor year alt_ins_deposits sod_parentid market_cap;

#delimit ;
gen provides_wloc = !missing(wloc_total_limit);
gen unins_leverage = unins_debt / assets;
gen leverage = total_equity_capital / assets;

save "${outputdir}/bank_wloc_data.dta", replace;
