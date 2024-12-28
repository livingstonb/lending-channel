"""
This module uses the WRDS python API to query stock returns and stock prices from CRSP.
As written, query selects dates around the failures of SVB, Signature Bank,
and First Republic Bank.

Data required is CRSP-FRB Link (https://www.newyorkfed.org/research/banking_research/crsp-frb),
saved as 'data/bank_crsp_links.csv'.

Code is expected to be run while working directory is set to main repository directory.
"""

import numpy as np
import pandas as pd
import wrds
import io
import sys

def crsp_main():
    """
    Use login credentials and query selected dates

    Returns
    -------
    DataFrame
        rows: bank rssdids
        columns: daily stock returns and prices

    """
    # Login
    test_input = "blivingston\n\nn\n"
    sys.stdin = io.StringIO(test_input)
    conn = wrds.Connection(username='blivingston')

    # Query two periods separately
    data1 = query_wrds(conn, ['2023-03-07', '2023-03-14'])
    data2 = query_wrds(conn, ['2023-04-28', '2023-05-03'])
    return concatenate((data1, data2))


def query_wrds(conn, dates):
    """

    Parameters
    ----------
    conn
        WRDS connection object
    dates
        date range to query

    Returns
    -------
    DataFrame
        rows: bank rssdids
        columns: daily stock returns and prices

    """

    # Crosswalk between bank rssdids and crsp permco values
    links = get_bank_permco_links('../data/bank_crsp_links.csv',
                                  pd.to_datetime(dates))
    # Convert to comma-separated string
    permco_str = ', '.join([str(s) for s in set(links['permco'].values)])

    # Date string for query
    datestr = f"between '{dates[0]} 00:00:00' and  '{dates[1]} 00:00:00'"

    # SQL query
    query_output = conn.raw_sql(
        """select permno, permco, DlyCalDt, DlyPrc, DlyCap, DlyRet, DlyFacPrc, DlyClose, DlyOpen
            from crsp.dsf_v2
            where  (permco in (%s))
                and (DlyCalDt %s)""" % (permco_str, datestr),
        date_cols=['DlyCalDt'])

    # Merge rssdid's back in and drop crsp identifiers
    data = query_output.merge(links[['rssdid', 'permco']],
                           how='right', left_on='permco', right_on='permco')
    data = data.drop(['permno', 'permco'], axis=1)
    return data


def get_bank_permco_links(fname, dates):
    """

    Parameters
    ----------
    fname
        string, path to rssdid-permco crosswalk
    dates
        list containing two strings of dates

    Returns
    -------
    DataFrame
        rows: entries for rssdid-permco matches
        columns rssdid, permco pairs

    """
    df = pd.read_csv(fname, header=0)
    df = df.rename(columns={'RSSD9001': 'rssdid'})
    df['dt_start'] = pd.to_datetime(df['dt_start'])
    df['dt_end'] = pd.to_datetime(df['dt_end'])
    keep = (df['dt_start'] <= dates[0]) & (df['dt_end'] >= dates[1])
    return df[keep][['rssdid', 'permco']]


def concatenate(datasets):
    """

    Parameters
    ----------
    datasets
        tuple of DataFrames, concatenate data from multiple dates

    Returns
    -------
    DataFrame
        rows: rssdids
        columns: returns and prices by date

    """
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

    df = crsp_main()
    df.to_csv('../temp/crsp_daily_cleaned.csv')