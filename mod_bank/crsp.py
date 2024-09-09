import pandas as pd
import wrds
import io, sys


def query_dates(dates):
    links = get_bank_permco_links('data/bank_crsp_links.csv',
                                  pd.to_datetime(dates))
    tab_variables = conn.get_table(
        library='crsp', table='dsf', obs=1).columns.values
    query_res = query_wrds(conn, set(links['permco'].values), dates)

    data = query_res.merge(links[['rssdid', 'permco']],
                           how='right', left_on='permco', right_on='permco')
    data = data.drop(['permno', 'permco'], axis=1)

    return data

def get_bank_permco_links(fname, dates):
    df = pd.read_csv(fname, header=0)
    df = df.rename(columns={'RSSD9001': 'rssdid'})
    df['dt_start'] = pd.to_datetime(df['dt_start'])
    df['dt_end'] = pd.to_datetime(df['dt_end'])
    keep = (df['dt_start'] <= dates[0]) & (df['dt_end'] >= dates[1])
    return df[keep][['rssdid', 'permco']]

def query_wrds(conn, permco_list, dates):
    permco_str = ', '.join([str(s) for s in permco_list])

    # Date string
    datestr = f"between '{dates[0]} 00:00:00' and  '{dates[1]} 00:00:00'"

    query_output = conn.raw_sql(
        """select permno, permco, date, ret, shrout, prc, openprc, divamt, facpr
            from crsp.dsf
            where  (permco in (%s))
                and (date %s)""" % (permco_str, datestr),
        date_cols=['date'])
    return query_output


def concatenate(datasets):
    data = pd.concat(datasets, axis=0).reset_index()
    data['strdate'] = data['date'].apply(
        lambda x: f'R{x.strftime("%Y%m%d")}')
    data = data.drop('date', axis=1)
    data['ret'] = data['ret'] + 1.0
    data = data.pivot(index='rssdid', columns='strdate', values='ret')
    return data


if __name__ == "__main__":

    # connect to WRDS
    # Create a string that will serve as our simulated input
    test_input = "blivingston\n\nn\n"

    # Redirect stdin to read from the string
    sys.stdin = io.StringIO(test_input)
    conn = wrds.Connection(username='blivingston')

    data1 = query_dates(['2023-03-08', '2023-03-14'])
    data2 = query_dates(['2023-04-29', '2023-05-03'])
    df = concatenate((data1, data2))
    df.to_csv('temp/crsp_daily_cleaned.csv')