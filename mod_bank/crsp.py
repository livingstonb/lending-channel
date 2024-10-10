import numpy as np
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
        """select permno, permco, DlyCalDt, DlyPrc, DlyCap, DlyRet, DlyFacPrc, DlyClose, DlyOpen
            from crsp.dsf_v2
            where  (permco in (%s))
                and (DlyCalDt %s)""" % (permco_str, datestr),
        date_cols=['DlyCalDt'])
    return query_output


def concatenate(datasets):
    data = pd.concat(datasets, axis=0).reset_index()
    data = data.rename(columns={
        'dlycaldt': 'date', 'dlyprc': 'prc', 'dlycap': 'cap',
        'dlyret': 'R', 'dlyfacprc': 'pfac', 'dlyclose': 'close',
        'dlyopen': 'open'
    })
    data['R'] = data['R'] + 1.0
    data[data['R'] == -99]['R'] = np.nan
    data['idR'] = data['prc'] / data['open']
    data[(data['prc'] == 0) | (data['open'] == 0)]['idR'] = np.nan
    data[data['prc'] == 0]['prc'] = np.nan
    data = data.rename(columns={'prc': 'p'})

    data['return_labels'] = data['date'].apply(
        lambda x: f'R{x.strftime("%Y%m%d")}')
    data['intraday_labels'] = data['date'].apply(
        lambda x: f'idR{x.strftime("%Y%m%d")}')
    data['price_labels'] = data['date'].apply(
        lambda x: f'p{x.strftime("%Y%m%d")}')

    date0 = min(data['date'])
    cap = data[data['date'] == date0].set_index('rssdid')['cap']
    data = data[data['date'] > date0]
    data = data.drop('date', axis=1)

    returns = data.pivot(index='rssdid', columns='return_labels', values='R')
    intraday = data.pivot(index='rssdid', columns='intraday_labels', values='idR')
    price = data.pivot(index='rssdid', columns='price_labels', values='p')
    df = pd.concat((returns, intraday, price, cap), axis=1)
    return df


if __name__ == "__main__":

    # connect to WRDS
    # Create a string that will serve as our simulated input
    test_input = "blivingston\n\nn\n"

    # Redirect stdin to read from the string
    sys.stdin = io.StringIO(test_input)
    conn = wrds.Connection(username='blivingston')

    data1 = query_dates(['2023-03-07', '2023-03-14'])
    data2 = query_dates(['2023-04-28', '2023-05-03'])
    df = concatenate((data1, data2))
    df.to_csv('temp/crsp_daily_cleaned.csv')