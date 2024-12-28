"""
This file calls uses all of the python modules, sequentially, to obtain the data we want.
This file need not be used since each of the modules can be called on their own.
"""

from py_mod import crsp
from py_mod import sod
from call_reports_main import call_reports_main
import os

### CRSP STOCK PRICES/RETURNS ###
crsp_df = crsp.crsp_main()
crsp_df.to_csv('../temp/crsp_daily_cleaned.csv')


### SUMMARY OF DEPOSITS ###
year = 2022
(sod_bhc_df, sod_bank_df) = sod.sod_main(year)
sod_bhc_df.to_csv(f"../temp/sod_bhc_level_{year}.csv")
sod_bank_df.to_csv(f"../temp/sod_bank_level_{year}.csv")

### CALL REPORTS ###
# Requires CRSP-FRB crosswalk saved as 'data/bank_crsp_links.csv'
# List of dates of integer form YYYYMMDD
quarters = [331, 630, 930, 1231]
years = [2018, 2019, 2020, 2021, 2022, 2023]
dates = [int(y * 1e4) + q for y in years for q in quarters]
dates.pop()
bhck = False
test_run = False
call_df = call_reports_main(dates, bhck, test_run)
call_df.to_csv(os.path.join('../temp', 'bank_data_cleaned.csv'))
