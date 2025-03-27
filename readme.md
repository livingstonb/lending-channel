# Readme

## Structure of the Repository

Some of the data, particularly data queried from WRDS, is obtained and first cleaned in Python code, for which the main file is *main.py*. The remaining data are dealth with in Stata. Evertyhing is then merged in Stata (see *main.do*).

## Datasets
The file *main.py* is a good reference to see how each of the python modules are used to obtain different datasets and where they are saved

### Bank Call Reports (from WRDS)
1. Running *code/call_reports_main.py* queries WRDS and produces the main banking dataset ***temp/bank_data_cleaned.csv***
2. Code at the bottom of *code/call_reports_main.py* selects which quarters to query and whether to query the bank tables or BHC tables (BHC option is likely broken). Data issue with 2023Q4 because of banks reporting multiple times
3. The rest of the code in *code/call_reports_main.py* selects variables, calls the query code, and calls code to add variables for 2022 mark-to-market losses

### NIC Data
1. Used to identify bank ownership structure
2. Contains bank attribute variables

### Summary of Deposits (FDIC)
1. Must run *code/py_mod/sod.py* with a particular year, e.g. 2022
2. A subset of SOD years are in the data directory: *data/sod_06_YYYY.csv*
3. Code produces two DataFrames, one at bank-level and one at BHC-level, *temp/sod_bank_level_2022.csv* and *temp/sod_bhc_level_2022.csv*

### CRSP stock prices around events
1. File is *code/py_mod/crsp.py*
2. Queries WRDS and produces the file *temp/crsp_daily_cleaned.csv*
3. To identify the CRSP identifiers attached to the bank (stocks) in our sample we use the CRSP-FRB link provided by the New York Fed: https://www.newyorkfed.org/research/banking_research/crsp-frb.

### LEI-NMLS crosswalk (HMDA-MCR)
Our crosswalk was originally constructed by Erica Jiang. We've used her work with permission and manually matched LEI-NMLS identifiers for additional nonbank lenders.
The file *data/hmda_lei_nmls_crosswalk.dta* is our most up-to-date crosswalk we use for matching, and our added matches can be identified in the separate file *data/erica_cwalk_updates.xlsx*.

## Main Stata file
*main.do* calls additional Stata code to read and clean other datasets (including Corelogic), and then merges data.
1. Before using the MCR data, the do-file produces *output/final_bank_panel.dta*, which is a bank-level panel with variables from a number of different sources
2. Cleans MCR data and produces the final nonbank panel dataset ***output/final_mcr_panel.dta***
3. Generates the file ***temp/wloc_panel_cleaned.dta*** which has each credit line, nonbank-bank-quarter level
4. Generates the file ***output/wloc_bank_level_aggregates.dta*** which takes the bank panel and appends line of credit variables such as number of lines.

## Using the data
To compute shock exposure variables for each nonbank, can use the bank-nonbank connections in ***temp/wloc_panel_cleaned.dta*** to get which banks a nonbank borrows from, then compute an exposure  statistic across these banks using the bank data ***output/wloc_bank_level_aggregates.dta***. Then this measure can be merged into the nonbank panel, ***output/final_mcr_panel.dta***.

To start, one can just merge the credit line data ***temp/wloc_panel_cleaned.dta*** on bank-quarters with the bank data ***output/wloc_bank_level_aggregates.dta*** to bring in any bank variables needed to compute bank shock vulnerability.

### Analysis
The idea so far is to run an event study regressing nonbank originations income on nonbank exposure to shock-affected banks.
