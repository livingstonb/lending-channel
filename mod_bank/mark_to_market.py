import numpy as np
import pandas as pd


class MTMConfig:
    treas_index_fpath = 'data/sp_treasury_indexes.csv'
    ishares_etf_fpath = 'data/ishares_etfs.csv'
    sp_treasury_index_fpath = 'data/sp_treasury_bond_index.csv'
    end_date = "2022-12-31"


def compute_losses(df):
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

    # Use 2022Q1 values
    df = df[df.date == pd.to_datetime("2021-12-31")]

    # MBS repricing
    loss = []

    rmbs_multiplier = dp['mbs_etf'] / dp['treasury_index']
    rmbs_loss = (df[f'famsec_{periods[0]}']
                 + df[f'flien_{periods[0]}']) * d_treas_prices[0]
    for i in range(1, 6):
        rmbs_loss += (df[f'famsec_{periods[i]}']
                     + df[f'flien_{periods[i]}']) * d_treas_prices[i]
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
    yoy_2023Q1_treas = compute_pct_change(treasury_prices, MTMConfig.end_date, 4)

    ishares_prices = read_ishares_prices(MTMConfig.ishares_etf_fpath)
    yoy_2023Q1_etfs = compute_pct_change(ishares_prices, MTMConfig.end_date, 4)

    sp_treas_index = read_sp_treasury_index(MTMConfig.sp_treasury_index_fpath)
    yoy_2023Q1_spind = compute_pct_change(sp_treas_index, MTMConfig.end_date, 4)

    keys = yoy_2023Q1_etfs.columns.tolist(
        ) + yoy_2023Q1_treas.columns.tolist(
        ) + yoy_2023Q1_spind.columns.tolist()
    values = np.concatenate(
        (yoy_2023Q1_etfs.values[0, :],
         yoy_2023Q1_treas.values[0, :],
         yoy_2023Q1_spind.values[0, :]
         ))
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


def read_sp_treasury_index(fname):
    df = pd.read_csv(fname)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()

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
    prices = prices.resample('Q-DEC', label='right', convention='end',
                     closed='right').agg('last')
    dprice = prices.pct_change(periods=periods)
    pct_dprice = dprice[dprice.index == pd.to_datetime(end_dt)]
    return pct_dprice


if __name__ == "__main__":
    dp = get_bond_price_changes()
    # compute_losses()