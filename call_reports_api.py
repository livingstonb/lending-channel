
import wrds

from mod_bank import rssdid


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
    vars = {
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
    conn = request_call_reports()
    dates = [20220630, 20220630]

    vtab = variables_by_table(conn)

    # Select variables
    vars = variables()
    q = query(conn, vtab, vars, dates)
    q = q.rename(columns=vars)
    df = q.rename(columns={'rssd9001': 'rssdid'})
    final = rssdid.assign_bhcid(df,
                            'data/bhck-06302022-wrds.csv', 'data/bank_relationships.csv',
                            dates[0])