import numpy as np
import pandas as pd
from pandas.tseries.offsets import DateOffset


class MTMConfig:
    treas_index_fpath = '../data/sp_treasury_indexes.csv'
    ishares_etf_fpath = '../data/ishares_etfs.csv'
    sp_treasury_index_fpath = '../data/sp_treasury_bond_index.csv'
    end_date = pd.to_datetime("2022-12-31") # 2022-12-31


def compute_losses(df):
    df = df[df.date == MTMConfig.end_date - DateOffset(years=1)]
    dp = get_bond_price_changes()

    d_treas_prices = [
        dp['t90ind'],
        (dp['t90ind'] + dp['b1ind']) / 2.0,
        dp['b2ind'],
        (dp['b2ind'] + dp['b5ind']) / 2.0,
        dp['b10ind'],
        dp['b20ind'],
    ]
    periods = ['le3m', '3m1y', '1y3y', '3y5y', '5y15y', 'ge15y']

    # MBS repricing
    loss = []

    rmbs_multiplier = (1 - dp['mbs_etf']) / (1 - dp['treasury_index'])
    rmbs_loss = (df[f'famsec_{periods[0]}']
                 + df[f'flien_{periods[0]}']) * (1 - d_treas_prices[0])
    for i in range(1, 6):
        rmbs_loss += (df[f'famsec_{periods[i]}']
                     + df[f'flien_{periods[i]}']) * (1 - d_treas_prices[i])
    rmbs_loss = rmbs_loss * rmbs_multiplier

    # Treasury and other securities repricing
    other_sec_loss = (df[f'othll_{periods[0]}']
                      + df[f'gsec_{periods[0]}']) * d_treas_prices[0]
    for i in range(1, 6):
        other_sec_loss += (df[f'othll_{periods[i]}']
                            + df[f'gsec_{periods[i]}']) * d_treas_prices[i]

    level_loss = rmbs_loss + other_sec_loss
    level_loss.name = 'mtm_2022_loss_level'
    pct_assets_loss = level_loss / df['assets']
    pct_assets_loss.name = 'mtm_2022_loss_pct_assets'
    pct_equity_loss = level_loss / df['total_equity_capital']
    pct_equity_loss.name = 'mtm_2022_loss_pct_equity'

    # est_assets = df['assets'] + level_loss
    # est_assets.name = 'mtm_2022q4_assets'

    loss.extend([level_loss, pct_assets_loss, pct_equity_loss])

    loss = pd.concat(loss, axis=1)
    return loss


def get_bond_price_changes():
    treasury_prices = read_treasury_prices(MTMConfig.treas_index_fpath)
    ishares_prices = read_ishares_prices(MTMConfig.ishares_etf_fpath)
    sp_treas_index = read_sp_treasury_index(MTMConfig.sp_treasury_index_fpath)

    df = pd.concat((treasury_prices, ishares_prices, sp_treas_index), axis=1)
    D12_df = df / df.shift(12)
    pchange = D12_df[df.index == MTMConfig.end_date]

    dp = dict()
    for key in pchange.columns.tolist():
        dp[key] = pchange[key].values[0]
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
    df = df.resample('M', label='right', convention='end', closed='right').agg('last')
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
            'SPMB': 'mbs_etf',
            }
    df = df.rename(columns=secs)
    df = df.drop(['MBB'], axis=1)
    df = df.resample('M', label='right', convention='end', closed='right').agg('last')
    return df.abs()


def read_sp_treasury_index(fname):
    df = pd.read_csv(fname)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    df = df.resample('M', label='right', convention='end', closed='right').agg('last')
    return df


if __name__ == "__main__":
    dp = get_bond_price_changes()
    # compute_losses()