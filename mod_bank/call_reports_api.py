
import wrds
import pandas as pd

def request_call_reports():
    conn = wrds.Connection(username='blivingston')
    return conn


def table_variable_links():
    tabnames = ['wrds_call_rcon_1', 'wrds_call_rcon_2',
                'wrds_call_rcfd_1', 'wrds_call_rcfd_2']
    dfs = []
    for tabname in tabnames:
        variables = conn.get_table(library='bank', table=tabname,
                                   obs=1).columns.values
        df = pd.DataFrame(variables, columns=['var'])
        df['table'] = tabname
        dfs.append(df)

    return pd.concat(dfs, axis=0).reset_index(drop=True)


if __name__ == "__main__":
    conn = request_call_reports()
    tab = table_variable_links()