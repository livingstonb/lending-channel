
import pandas as pd
from mod_bank import call_reports
from mod_bank import mark_to_market as mtm
import sys
import io
import os


def variables(bhck=False):

    # Variable always shows up with RCON prefix (or this is the version we want)
    vars_rcon = {
        '9224': 'lei',
        '5597': 'est_unins_deposits',
        '2200': 'deposits_domestic_office',
        'f045': 'dep_retir_lt250k',
        'f047': 'dep_retir_gt250k',
        'f048': 'num_dep_retir_gt250k',
        'f049': 'dep_nretir_lt250k',
        'f051': 'dep_nretir_gt250k',
        'f052': 'num_dep_nretir_gt250k',
        '2213': 'liab_fbk_trans',
        '2236': 'liab_fbk_ntrans',
        '2216': 'liab_foff_trans',
        '2377': 'liab_foff_ntrans',
        'a545': 'cons_parent_fdic_cert',
        'g105': 'total_equity_capital',
        '0211': 'treas_htm_amort',
        '0213': 'treas_htm_fval',
        '1286': 'treas_afs_amort',
        '1287': 'treas_afs_fval',
        '3531': 'treas_trading',
        'ht81': 'retail_mortorig_forsale',
        'ht82': 'whlsale_mortorig_forsale',
        'ft04': 'res_mort_sold',
        'ft05': 'res_mort_hfs_or_hft',
        '1754': 'totsec_afs_amort',
        '1771': 'totsec_afs_fval',
        '1772': 'totsec_htm_amort',
        '1766': 'ci_loans_nontrading',
        'f614': 'ci_loans_trading',
        'j454': 'nbfi_loans',
        '1545': 'lns_for_purch_carr_sec',
        'b538': 'cons_cc_loans',
        'b539': 'cons_oth_revolvc_loans',
        'k137': 'cons_auto_loans',
        'k207': 'cons_oth_loans',
        '2122': 'tot_loansleases',
        '2123': 'unearnedinc_loansleases',
    }
    all_vars = {'rcon'+k: v for k, v in vars_rcon.items()}

    # Variable has RCON prefix for 041 filers, RCFD for 031 filers
    vars_rcon_rcfd = {
        '2170': 'assets',
        'b993': 'repo_liab_ff',
        'b995': 'repo_liab_oth',
        '3190': 'oth_borr_money',
        '3200': 'sub_debt',
        '2948': 'liabilities',
        'g105': 'total_equity_capital',
        '0416': 'pledged_securities',
        'g378': 'pledged_ll',
        'jj34': 'htm_securities',
        '1773': 'afs_debt_securities',
        '5369': 'll_hfs',
        'b528': 'll_hfi',
        '3123': 'll_loss_allowance',
        'ja22': 'eq_sec_notftrading',
        '3164': 'mort_servicing_assets',
        'a549': 'gsec_le3m',
        'a550': 'gsec_3m1y',
        'a551': 'gsec_1y3y',
        'a552': 'gsec_3y5y',
        'a553': 'gsec_5y15y',
        'a554': 'gsec_ge15y',
        'a555': 'famsec_le3m',
        'a556': 'famsec_3m1y',
        'a557': 'famsec_1y3y',
        'a558': 'famsec_3y5y',
        'a559': 'famsec_5y15y',
        'a560': 'famsec_ge15y',
        'a564': 'flien_le3m',
        'a565': 'flien_3m1y',
        'a566': 'flien_1y3y',
        'a567': 'flien_3y5y',
        'a568': 'flien_5y15y',
        'a569': 'flien_ge15y',
        'a570': 'othll_le3m',
        'a571': 'othll_3m1y',
        'a572': 'othll_1y3y',
        'a573': 'othll_3y5y',
        'a574': 'othll_5y15y',
        'a575': 'othll_ge15y',
        'g300': 'rmbs_htm_amort_gnma',
        'g301': 'rmbs_htm_fval_gnma',
        'g302': 'rmbs_afs_amort_gnma',
        'g303': 'rmbs_afs_fval_gnma',
        'g304': 'rmbs_htm_amort_fmac',
        'g305': 'rmbs_htm_fval_fmac',
        'g306': 'rmbs_afs_amort_fmac',
        'g307': 'rmbs_afs_fval_fmac',
        'g308': 'rmbs_htm_amort_oth',
        'g309': 'rmbs_htm_fval_oth',
        'g310': 'rmbs_afs_amort_oth',
        'g311': 'rmbs_afs_fval_oth',
        'g379': 'rmbs_trading_agency',
        '3545': 'total_trading_assets',
        'j457': 'unused_comm_ci',
        'j458': 'unused_comm_nbfi',
    }

    for prefix in ['rcon', 'rcfd']:
        all_vars.update(
            {prefix+key: '_'.join((prefix, val)) for key, val in vars_rcon_rcfd.items()})

    other = {
        'rcoa7206': 'rcoa_tier1cap',
        'rcfa7206': 'rcfa_tier1cap',
        'rcoa7204': 'rcoa_levratio',
        'rcfa7204': 'rcoa_levratio',
        'rcfn2200': 'deposits_foreign_office',
        'riadb493': 'net_sec_income',
        'riadb492': 'net_serv_fees',
        'riad4135': 'salaries_and_benefits',
        'riad4217': 'exp_premises_fa',
    }
    all_vars.update(other)

    if bhck:
        all_vars = {
            'bhckjj34': 'htm_securities',
            'bhck1773': 'afs_debt_securities',
            'bhckJA22': 'eq_sec_notftrading',
            'bhck2130': 'inv_unconsol_subsid',
            'bhck2170': 'assets',
            'bhdm6631': 'dom_nointerest_deposits',
            'bhdm6636': 'dom_interest_deposits',
            'bhfn6631': 'fn_nointerest_deposits',
            'bhfn6636': 'fn_interest_deposits',
            'bhck2948': 'liabilities',
            'bhckg105': 'equity_capital',
            'bhck1763': 'dom_ci_loans',
            'bhck1764': 'fn_ci_loans',
            'bhckj458': 'unused_lines_to_nbfis',
            'bhckj454': 'loans_nondep_fi'
        }

    return all_vars


def get_quarter(date, from_file=False, bhck=False):
    if from_file:
        fpath = 'data/call_jun2022.csv'
        df = pd.read_csv(fpath, header=0, index_col='rssdid')
    else:
        # Create a string that will serve as our simulated input
        test_input = "blivingston\n\nn\n"

        # Redirect stdin to read from the string
        sys.stdin = io.StringIO(test_input)
        cr_query = call_reports.Query('blivingston', bhck=bhck)

        # Select variables
        vars = variables(bhck)
        cr_query.select_variables(vars.keys())

        df = cr_query.query(date)
        vars.update({
            'rssd9001': 'rssdid',
            'rssd9999': 'date',
            'rssd9017': 'name'
        })
        df = df.rename(columns=vars)

    if bhck:
        data_quarter = df.drop('rssdid', axis=1)
    else:
        attr_files = ['data/NIC_attributes_closed.csv', 'data/NIC_attributes_active.csv']
        bhcids = call_reports.assign_topid_up(df, 'data/NIC_relationships.csv', attr_files, date)
        bhcids = bhcids.set_index('rssdid')
        data_quarter = df.drop('rssdid', axis=1).merge(
            bhcids, how='left', left_index=True, right_index=True)
    return data_quarter


def startswith_anyof(variables, prefixes):
    vars_found = []
    for pre in prefixes:
        vars_found += [v for v in variables if v.startswith(pre)]

    return vars_found

if __name__ == "__main__":

    quarters = [331, 630, 930, 1231]
    years = [2018, 2019, 2020, 2021, 2022, 2023]

    # for y in years:
    #     for q in quarters:
    #         dates.append(int(y * 1e4) + q)
    # dates.pop()

    dates = [20210331]

    # dates = [20210331, 20211231, 20220331, 20220630, 20220930,
    # 20221231, 20230331, 20230630, 20230930]
    bhck = False

    qtables = list()
    for date in dates:
        dq = get_quarter(date, bhck=bhck)
        qtables.append(dq)

    df = pd.concat(qtables)
    df = call_reports.account_for_different_ffiec_forms(df)
    losses = mtm.compute_losses(df)
    df = df.merge(losses, how='left', left_index=True, right_index=True)

    # Drop repricing variables
    prefixes = ['gsec', 'flien', 'famsec', 'othll']
    repricing_vars = startswith_anyof(df.columns.tolist(), prefixes)
    df = df.drop(repricing_vars, axis=1)
    df = df.drop([k for k in df.columns.tolist() if k.startswith('rmbs_')], axis=1)

    fpath = 'temp'
    if not os.path.exists(fpath):
        os.makedirs(fpath)

    if bhck:
        pathname = 'bhck_data_cleaned.csv'
    else:
        pathname = 'bank_data_cleaned.csv'
    df.to_csv(os.path.join('temp', pathname))


