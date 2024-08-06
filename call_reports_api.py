
import wrds
import pandas as pd
from mod_bank import call_reports


def query(conn, vtab, vars, dates):
    tables = ['wrds_call_rcon_1', 'wrds_call_rcon_2',
              'wrds_call_rcfd_1', 'wrds_call_rcfd_2']

    # Loop over call report tables
    df_tab_list = list()
    for tab in tables:
        # Selected variables in table "tab"
        v_this_table = [v for v in vtab[tab] if v in vars]

        if len(v_this_table) == 0:
            continue

        df_tab = query_one_table(conn, tab, v_this_table, dates)
        df_tab = df_tab.set_index('rssd9001', drop=True)
        df_tab.index.name = 'rssdid'
        dates_names = df_tab[['rssd9999', 'rssd9017']]
        df_tab = df_tab.drop(['rssd9999', 'rssd9017'], axis=1)
        df_tab_list.append(df_tab)

    # Concatenate query results from all tables
    df_out = pd.concat(df_tab_list, axis=1, join='outer')

    # Add back date and institution names
    colnames = df_out.columns.tolist()
    df_out[['rssd9999', 'rssd9017']] = dates_names
    df_out['rssd9001'] = df_out.index.values
    df_out = df_out[['rssd9001', 'rssd9999', 'rssd9017'] + colnames]

    return df_out


def query_one_table(conn, table, vars, date):
    vstr = ', '.join(vars)
    datestr = f"between '{date} 00:00:00' and  '{date} 00:00:00'"
    df = conn.raw_sql(
        """select rssd9001, rssd9999, rssd9017, %s
            from bank.%s
            where  rssd9999 %s"""%(vstr, table, datestr),
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
    dates = [20220630, 20220630]
    date = dates[0]

    from_file = False

    if from_file:
        fpath = 'data/call_jun2022.csv'
        df = pd.read_csv(fpath, header=0, index_col='rssdid')
    else:
        conn = call_reports.request_call_reports('blivingston')

        vtab = call_reports.variables_by_table(conn)

        # Select variables
        vars = variables()
        df = query(conn, vtab, vars, date).rename(columns=vars)

    final = call_reports.assign_bhcid(df,
                            'data/bhck-06302022-wrds.csv', 'data/bank_relationships.csv',
                                      date)