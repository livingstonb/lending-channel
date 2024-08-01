
import wrds
import pandas as pd
from mod_bank.CRVariables import CRVariables

def request_call_reports():
    conn = wrds.Connection(username='blivingston')
    return conn


def query(conn, vtab, vars):
    tables = ['wrds_call_rcon_1', 'wrds_call_rcon_2',
              'wrds_call_rcfd_1', 'wrds_call_rcfd_2']
    for i, tab in enumerate(tables):
        v_this_table = [v for v in vtab[tab] if v in vars]
        if len(v_this_table) == 0:
            continue

        if i == 0:
            qt = query_one_table(conn, tab, v_this_table)
        else:
            xt = query_one_table(conn, tab, v_this_table)
            icols = ['rssd9001', 'rssd9999']
            qt = qt.merge(xt, how='outer', on=icols)
    return qt


def query_one_table(conn, table, vars):
    vstr = ', '.join(vars)
    df = conn.raw_sql(
        """select rssd9001, rssd9999, rssd9017, %s
            from bank.%s
            where rssd9001 < 10000
                and rssd9999 = '20210630 00:00:00'"""%(vstr, table),
                         date_cols=['rssd9999'])
    return df


def variables():
    vars = {'rcona555': 'rcon_famsec_le3m',
    'rcona556': 'rcon_famsec_3m1y',
    'rcona557': 'rcon_famsec_1y3y',
    'rcona558': 'rcon_famsec_3y5y',
    'rcona559': 'rcon_famsec_5y15y',
    'rcona560': 'rcon_famsec_ge15y',
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
    conn = request_call_reports()
    dates = [20220101, 20230101]
    callvars = CRVariables(dates)

    callvars.variables_by_table(conn)
    vtab = callvars.variables_table

    # Select variables
    vars = variables()
    q = query(conn, vtab, vars)
    q.rename(columns=vars, inplace=True)