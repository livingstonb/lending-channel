 
#delimit ;
use "${tempdir}/wloc_panel_cleaned.dta", clear;

/* Aggregate to firm-bank-date */
	collapse (sum) limit available usage, by(rssdid firm qdate);

/* Aggregate and save at bank level */ #delimit ;
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

/* Merge with cleaned call reports data */
	merge 1:m rssdid qdate using "${outdir}/cleaned_bank_data.dta",
		nogen keep(1 3);
	
	keep if bhclevel == 1;
	
	drop v1 form est_unins_deposits dep_retir_lt250k dep_retir_gt250k num_dep_retir_gt250k dep_nretir_lt250k dep_nretir_gt250k num_dep_nretir_gt250k totsec_afs_amort ci_loans_nontrading nbfi_loans lns_for_purch_carr_sec cons_oth_loans repo_liab_ff htm_securities afs_debt_securities ll_hfs ll_hfi ll_loss_allowance eq_sec_notftrading liab_fbk_trans liab_fbk_ntrans liab_foff_trans liab_foff_ntrans cons_parent_fdic_cert treas_htm_amort treas_htm_fval treas_afs_amort treas_afs_fval treas_trading retail_mortorig_forsale whlsale_mortorig_forsale res_mort_hfs_or_hft totsec_afs_fval totsec_htm_amort ci_loans_trading cons_oth_revolvc_loans unearnedinc_loansleases repo_liab_oth oth_borr_money sub_debt unused_comm_ci unused_comm_nbfi rcoa_tier1cap rcoa_levratio net_sec_income net_serv_fees salaries_and_benefits exp_premises_fa parentid parent_chtr_type_cd parent_insur_pri_cd parent_member_fhlbs parentname parent_cntry_inc_cd parent_id_lei member_fhlbs lei mtm_2022_loss_level trnsfm_cd event_was_successor year alt_ins_deposits sod_parentid market_cap;

	
	
/* Bank-level variables */
	#delimit ;
	rename deposits_domestic_office deposits;
	
	gen ldeposits = log(deposits);
	
	tsset rssdid qdate;
	gen dep_growth_1y = D4.ldeposits;
	gen dep_growth_2y = D8.ldeposits;
	gen provides_wloc = !missing(wloc_total_limit);
	gen unins_leverage = unins_debt / assets;
	gen leverage = total_equity_capital / assets;
	gen d_branch_density = (branch_density_2022 - branch_density_2021) / branch_density_2021;
	
	gen included = 1 if (qdate == yq(2022, 4)) & (provides_wloc == 1);
	
/* Estimate SVB return for unlisted banks */
	#delimit ;
	cap drop lassets;
	cap drop svbR_hat;
	gen lassets = log(assets);
	reg svbR c.lassets##c.(lassets branch_density_2021 branch_density_2022 unins_leverage leverage
		mtm_2022_loss_pct_equity dep_growth_1y) L(1/4).lassets if included;
	predict svbR_hat if missing(svbR) & included, xb;
	replace svbR_hat = svbR if !missing(svbR) & included;

/* Quantile dummies */
	foreach var of varlist unins_leverage branch_density_2022 {;
		tempvar temp_tercile;
		xtile `temp_tercile' = `var' if included & !missing(`var'), n(3);
		gen low_`var' = (`temp_tercile' == 1);
		gen high_`var' = (`temp_tercile' == 3);
		drop `temp_tercile';
	};
	
/* For stock return, use percentiles only from actual data */
	quietly _pctile svbR if included, p(33 66);
	local Rthreshold1 = `r(r1)';
	local Rthreshold2 = `r(r2)';
	/* replace svbR_hat = min(svbR_hat, 0); */
	gen low_svbR_hat = (svbR_hat < `Rthreshold1') if !missing(svbR_hat);
	gen high_svbR_hat = (svbR_hat >`Rthreshold2') if !missing(svbR_hat);
	
/* Replace outcomes with bad shock if signature or SVB */
	replace low_svbR_hat = 1 if rssdid == 3076592;
	replace low_svbR_hat = 1 if rssdid == 1031449;
	replace low_svbR_hat = . if (included != 1);
	replace high_svbR_hat = . if (included != 1);
	
/* Save */
	keep if qdate == yq(2022, 4);
	save "${outdir}/wloc_bank_level_aggregates.dta", replace;
	