import numpy as np
import pandas as pd


def read_treasury_prices(fname):
    df = pd.read_csv(fname)
    df['datenum'] = df['caldt'].map(lambda x: str(x).replace('-', ''))
    df['date'] = pd.to_datetime(df['caldt'])
    df = df.set_index('date').sort_values('datenum')

    df = df[[var for var in df.columns.tolist() if 'ind' in var]]
    df = df.pct_change(periods=4)
    return df


def read_ishares_prices(fname):
    df = pd.read_csv(fname)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    df = df.pivot(columns='TICKER', values='PRC')

    secs = {'SHY': 'treas_etf_1y3y',
            'IEF': 'treas_etf_7y10y',
            'TLH': 'treas_etf_10y20y',
            'TLT': 'treas_etf_g20y',
            'MBB': 'mbs_etf',
            }
    df = df.rename(columns=secs)
    df = df.pct_change(periods=12)

    return df


if __name__ == "__main__":
    # ishares_rmbs_permno = 92886
    # crsp_a_indexes.crsp

    treasury_path = 'data/sp_treasury_indexes.csv'
    treasury_prices = read_treasury_prices(treasury_path)
    yoy_2023Q1_treas = treasury_prices[
        treasury_prices.index == pd.to_datetime("2022-12-30")]

    ishares_path = 'data/ishares_etfs.csv'
    ishares_prices = read_ishares_prices(ishares_path)
    yoy_2023Q1_etfs = ishares_prices[
        ishares_prices.index == pd.to_datetime("2022-12-30")]

    keys = yoy_2023Q1_etfs.columns.tolist(
        ) + yoy_2023Q1_treas.columns.tolist()
    values = np.concatenate(
        (yoy_2023Q1_etfs.values[0,:],
         yoy_2023Q1_treas.values[0,:]))
    dp = {k: v for k, v in zip(keys, values)}
