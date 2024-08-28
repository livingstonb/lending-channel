
import pandas as pd
from mod_bank import call_reports
import sys
import io
import os

def variables():
    vars = {
        '9224': 'lei',
        'f045': 'dep_retir_lt250k',
        'f047': 'dep_retir_gt250k',
        'f048': 'num_dep_retir_gt250k',
        'f049': 'dep_nretir_lt250k',
        'f051': 'dep_nretir_gt250k',
        'f052': 'num_dep_nretir_gt250k',
        '5597': 'est_unins_deposits',
        'a545': 'cons_parent_fdic_cert',
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
        'a571': 'othll_3my1y',
        'a572': 'othll_1y3y',
        'a573': 'othll_3y5y',
        'a574': 'othll_5y15y',
        'a575': 'othll_ge15y',
        'a901': 'merger_acq',
        '2200': 'deposits',
        '2170': 'assets',
        'b993': 'repo_liab_ff',
        'b995': 'repo_liab_oth',
        '3190': 'oth_borr_money',
        '3200': 'sub_debt',
        '2948': 'total_liab',
        '2213': 'liab_fbk_trans',
        '2236': 'liab_fbk_ntrans',
        '2216': 'liab_foff_trans',
        '2377': 'liab_foff_ntrans',
        'ht81': 'retail_mortorig_forsale',
        'ht82': 'whlsale_mortorig_forsale',
        'ft04': 'res_mort_sold',
        'ft05': 'res_mort_hfs_or_hft',
        'g105': 'total_equity_capital',
        '0211': 'treas_htm_amort',
        '0213': 'treas_htm_fval',
        '1286': 'treas_afs_amort',
        '1287': 'treas_afs_fval',
        '3531': 'treas_trading',
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
        '1754': 'totsec_afs_amort',
        '1771': 'totsec_afs_fval',
        '1772': 'totsec_htm_amort',
        '1773': 'totsec_htm_fval',
        'jj11': 'loanls_loss_res_amort',
        'jj19': 'loanls_loss_res_bal',
        'jj25': 'htmsec_loss_res_bal',
        '1766': 'ci_loans_nontrading',
        'f614': 'ci_loans_trading',
        '2122': 'all_loansls_htm_hfs',
        '3545': 'total_trading_assets',
    }

    all_vars = dict()
    for prefix in ['rcon', 'rcfd']:
        all_vars.update(
            {prefix+key: '_'.join((prefix, val)) for key, val in vars.items()})

    rcoa = {
        'rcoa8274': 'rcoa_tier1cap',
        'rcoa7204': 'rcoa_levratio',
    }
    all_vars.update(rcoa)

    return all_vars


def get_quarter(date, from_file=False):
    if from_file:
        fpath = 'data/call_jun2022.csv'
        df = pd.read_csv(fpath, header=0, index_col='rssdid')
    else:
        # Create a string that will serve as our simulated input
        test_input = "blivingston\n\nn\n"

        # Redirect stdin to read from the string
        sys.stdin = io.StringIO(test_input)
        cr_query = call_reports.Query('blivingston')

        # Select variables
        vars = variables()
        cr_query.select_variables(vars.keys())

        df = cr_query.query(date)
        vars.update({
            'rssd9001': 'rssdid',
            'rssd9999': 'date',
            'rssd9200': 'state',
            'rssd9017': 'name'
        })
        df = df.rename(columns=vars)

    attr_files = ['data/NIC_attributes_closed.csv', 'data/NIC_attributes_active.csv']
    bhcids = call_reports.assign_topid_up(df, 'data/NIC_relationships.csv', attr_files, date)
    bhcids = bhcids.set_index('rssdid')
    data_quarter = df.drop('rssdid', axis=1).merge(
        bhcids, how='left', left_index=True, right_index=True)
    return data_quarter


if __name__ == "__main__":

    dates = [20220630, 20220930, 20221231, 20230331, 20230630, 20230930]
    qtables = list()
    for date in dates:
        dq = get_quarter(date)
        qtables.append(dq)

    df = pd.concat(qtables)

    fpath = 'temp'
    if not os.path.exists(fpath):
        os.makedirs(fpath)

    df.to_csv(os.path.join('temp', 'bank_data_cleaned.csv'))
