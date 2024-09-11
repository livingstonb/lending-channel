
#delimit ;

gen log_assets = log(assets);
gen log_deposits = log(deposits);

/* Uninsured debt variables */
gen unins_deposits = deposits - ins_deposits;
gen unins_debt = liabilities - ins_deposits;
gen unins_leverage = unins_debt / assets;
gen log_unins_deposits = log(unins_dep);
gen log_unins_debt = log(unins_debt);

/* Returns */
gen svbR = idr20230309 * r20230310 * r20230313;
gen firstrepR = r20230501 * r20230502 * r20230503;

gen leverage = assets / total_equity_capital;

/* Collateral */
gen pledgeable_securities = htm_securities + afs_debt_securities
	+ eq_sec_notftrading - pledged_securities;
gen pledgeable_loans_leases = ll_hfs + ll_hfi - ll_loss_allowance - pledged_ll;
gen pledgeable_coll = pledgeable_securities * 0.9 + pledgeable_loans_leases * 0.8;
gen log_pledgeable_coll = log(pledgeable_coll);

gen unins_debt_net_of_coll = (unins_debt - pledgeable_coll) / assets;
gen coll_unins_debt_ratio = pledgeable_coll / unins_debt;
gen pledgeable_share = pledgeable_coll /
	(htm_securities + afs_debt_securities + eq_sec_notftrading
		+ ll_hfs + ll_hfi - ll_loss_allowance);

