import pandas as pd
import wrds

# TODO: select links that hold across an entire year only (easiest way)

def get_bank_permco_links(fname, date):
    df = pd.read_csv(fname, header=0)
    df = df.rename(columns={'RSSD9001': 'rssdid'})
    df['dt_start'] = pd.to_datetime(df['dt_start'])
    df['dt_end'] = pd.to_datetime(df['dt_end'])
    keep = (df['dt_start'] <= date) & (df['dt_end'] >= date)
    return df[keep][['rssdid', 'permco']]


def query_wrds(conn, permco_list, dates):
    permco_str = ', '.join([str(s) for s in permco_list])

    # Date string
    datestr = f"between '{dates[0]} 00:00:00' and  '{dates[1]} 00:00:00'"

    query_output = conn.raw_sql(
        """select permno, permco, date, ret
            from crsp.msf
            where  (permco in (%s))
                and (date %s)""" % (permco_str, datestr),
        date_cols=['date'])
    return query_output


if __name__ == "__main__":
    dates = ['2022-1-30', '2022-12-31']
    unique_permcos = list()
    for date in dates:
        links = get_bank_permco_links('data/bank_crsp_links.csv',
                                      pd.to_datetime(date))
        unique_permcos.append(set(links['permco']))

    # permcos that appear at each date
    stable_permcos = set.intersection(*unique_permcos)

    # connect to WRDS
    conn = wrds.Connection(username='blivingston')

    tab_variables = conn.get_table(
        library='crsp', table='msf', obs=1).columns.values
    query_res = query_wrds(conn, list(stable_permcos), dates)

    # restrict to listed firms with returns every month
    query_res = query_res.groupby('permno').filter(
        lambda x: (x['ret'].count() == 12))

    query_res['ret'] += 1.0
    cumulative_ret = query_res.groupby('permno').agg(
        {'ret': 'prod', 'permco': 'first'}).reset_index()
    cumulative_ret = cumulative_ret[['permco', 'permno', 'ret']]