import numpy as np
import pandas as pd


class MTMConfig:
    treas_index_fpath = 'data/sp_treasury_indexes.csv'
    ishares_etf_fpath = 'data/ishares_etfs.csv'
    end_date = "2022-12-30"


def get_bond_price_changes():
    treasury_prices = read_treasury_prices(MTMConfig.treas_index_fpath)
    yoy_2023Q1_treas = compute_pct_change(treasury_prices, MTMConfig.end_date, 4)

    ishares_prices = read_ishares_prices(MTMConfig.ishares_etf_fpath)
    yoy_2023Q1_etfs = compute_pct_change(ishares_prices, MTMConfig.end_date, 12)

    keys = yoy_2023Q1_etfs.columns.tolist() + yoy_2023Q1_treas.columns.tolist()
    values = np.concatenate(
        (yoy_2023Q1_etfs.values[0, :],
         yoy_2023Q1_treas.values[0, :]))
    dp = {k: v for k, v in zip(keys, values)}
    return dp

def read_treasury_prices(fname):
    """
    Reads S&P treasury indexes from data, returns DataFrame.

    Args:
        fname: filepath for csv with S&P treasury indexes from WRDS

    Returns:
        df: DataFrame
    """
    df = pd.read_csv(fname)
    df['datenum'] = df['caldt'].map(lambda x: str(x).replace('-', ''))
    df['date'] = pd.to_datetime(df['caldt'])
    df = df.set_index('date').sort_values('datenum')

    df = df[[var for var in df.columns.tolist() if 'ind' in var]]
    return df


def read_ishares_prices(fname):
    """

    Args:
        fname: filepath for csv with iShares ETF prices from CRSP

    Returns:

    """
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
    return df


def compute_pct_change(prices, end_dt, periods):
    """

    Args:
        prices: DataFrame, rows of dates and columns are securities
        end_dt: string of form "YYYY-MM-DD"
        periods: number of periods back to compute percent change

    Returns:
        one-row DataFrame of percent price changes, backward "periods"
        from end_dt
    """
    dprice = prices.pct_change(periods=periods)
    pct_dprice = dprice[dprice.index == pd.to_datetime(end_dt)]
    return pct_dprice
