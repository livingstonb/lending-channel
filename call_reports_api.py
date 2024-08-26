
import wrds
import pandas as pd
from mod_bank import call_reports
import sys
import io

def variables():
    vars = {
    'rcon9224': 'rcon_lei',
    'rconf045': 'rcon_dep_retir_lt250k',
    'rconf049': 'rcon_dep_nretir_lt250k',
    'rcona549': 'rcon_gsec_le3m',
    'rcona550': 'rcon_gsec_3m1y',
    'rcona551': 'rcon_gsec_1y3y',
    'rcona552': 'rcon_gsec_3y5y',
    'rcona553': 'rcon_gsec_5y15y',
    'rcona554': 'rcon_gsec_ge15y',
    'rcona555': 'rcon_famsec_le3m',
    'rcona556': 'rcon_famsec_3m1y',
    'rcona557': 'rcon_famsec_1y3y',
    'rcona558': 'rcon_famsec_3y5y',
    'rcona559': 'rcon_famsec_5y15y',
    'rcona560': 'rcon_famsec_ge15y',
    'rcona564': 'rcon_flien_le3m',
    'rcona565': 'rcon_flien_3m1y',
    'rcona566': 'rcon_flien_1y3y',
    'rcona567': 'rcon_flien_3y5y',
    'rcona568': 'rcon_flien_5y15y',
    'rcona569': 'rcon_flien_ge15y',
    'rcona570': 'rcon_othll_le3m',
    'rcona571': 'rcon_othll_3my1y',
    'rcona572': 'rcon_othll_1y3y',
    'rcona573': 'rcon_othll_3y5y',
    'rcona574': 'rcon_othll_5y15y',
    'rcona575': 'rcon_othll_ge15y',
    'rcon2200': 'rcon_deposits',
    'rcon2170': 'rcon_assets',
    'rconb993': 'rcon_repo_liab_ff',
    'rconb995': 'rcon_repo_liab_oth',
    'rcon3190': 'rcon_oth_borr_money',
    'rcon3200': 'rcon_sub_debt',
    'rcon2213': 'rcon_liab_fbk_trans',
    'rcon2236': 'rcon_liab_fbk_ntrans',
    'rcon2216': 'rcon_liab_foff_trans',
    'rcon2377': 'rcon_liab_foff_ntrans',
    'rcfd2200': 'rcfd_deposits',
    'rcfd2170': 'rcfd_assets',
    }
    return vars

if __name__ == "__main__":

    dates = [20220630, 20220630]
    date = dates[0]

    from_file = False

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

    # final = call_reports.assign_bhcid(df,
    #                         'data/bhck-06302022-wrds.csv', 'data/NIC_relationships.csv',
    #                                   date)

    bhcids = call_reports.assign_topid_up(df, 'data/NIC_relationships.csv', 20220630)
    bhcids = bhcids.set_index('rssdid')
    final = df.drop('rssdid', axis=1).merge(bhcids, how='left', left_index=True, right_index=True)