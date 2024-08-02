
import wrds
import pandas as pd

def request_call_reports():
    conn = wrds.Connection(username='blivingston')
    return conn


def variables_by_table(conn):
    tabnames = ['wrds_call_rcon_1', 'wrds_call_rcon_2',
                'wrds_call_rcfd_1', 'wrds_call_rcfd_2']
    tabs = dict()
    for tabname in tabnames:
        variables = conn.get_table(library='bank', table=tabname,
                                   obs=1).columns.values
        tabs.update({tabname: list(variables)})

    return tabs

def query(conn, vtab, vars, cates):
    tables = ['wrds_call_rcon_1', 'wrds_call_rcon_2',
              'wrds_call_rcfd_1', 'wrds_call_rcfd_2']
    for i, tab in enumerate(tables):
        v_this_table = [v for v in vtab[tab] if v in vars]
        if len(v_this_table) == 0:
            continue

        if i == 0:
            qt = query_one_table(conn, tab, v_this_table, dates)
        else:
            xt = query_one_table(conn, tab, v_this_table, dates)
            icols = ['rssd9001', 'rssd9999']
            qt = qt.merge(xt, how='outer', on=icols)
    return qt


def query_one_table(conn, table, vars, dates):
    vstr = ', '.join(vars)
    datestr = f"between '{dates[0]} 00:00:00' and  '{dates[1]} 00:00:00'"
    df = conn.raw_sql(
        """select rssd9001, rssd9999, rssd9017, %s
            from bank.%s
            where rssd9001 < 10000
                and rssd9999 %s"""%(vstr, table, datestr),
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

    vtab = variables_by_table(conn)

    # Select variables
    vars = variables()
    q = query(conn, vtab, vars, dates)
    q.rename(columns=vars, inplace=True)