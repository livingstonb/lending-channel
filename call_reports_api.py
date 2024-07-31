
import wrds
import pandas as pd
from mod_bank.CRVariables import CRVariables

def request_call_reports():
    conn = wrds.Connection(username='blivingston')
    return conn


def query(conn, vars):

    apple = conn.raw_sql(
        """select rssd9001, rssd9999, rssd9017
                %s
            from bank.wrds_call_rcon_1
            where rssd9001 = 37
            and rssd9999 > '20210101 00:00:00'"""%vars,
                         date_cols=['rssd9999'])
    return apple


def variables():
    vars = {'rcona555': 'rcon_famsec_le3m',
    'rcona556': 'rcon_famsec_3m1y',
    'rcona557': 'rcon_famsec_1y3y',
    'rcona558': 'rcon_famsec_3y5y',
    'rcona559': 'rcon_famsec_5y15y',
    'rcona560': 'rcon_famsec_ge15y'}
    vstr = ', '.join(list(vars.keys()))
    return vars, vstr

if __name__ == "__main__":
    conn = request_call_reports()
    dates = [20220101, 20230101]
    callvars = CRVariables(dates)

    callvars.variables_by_table(conn)
    vtab = callvars.variables_table

    # Select variables
    vars, vstr = variables()
    q = query(conn, vstr)
    q.rename(columns=vars, inplace=True)