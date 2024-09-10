
#delimit ;

/* Generate variables */

gen logassets = log(assets);
gen log_dep = log(deposits);
gen log_unins_dep = log(unins_dep);
gen svbR = r20230310 * r20230313 * r20230314;
gen firstrepR = r20230501 * r20230502 * r20230503;

gen leverage = assets / total_equity_capital;
