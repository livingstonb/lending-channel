import pandas as pd


def links_table(fname, date):
    df = pd.read_csv(fname, header=0)
    df = df.rename(columns={'RSSD9001': 'rssdid'})
    df['dt_start'] = pd.to_datetime(df['dt_start'])
    df['dt_end'] = pd.to_datetime(df['dt_end'])
    keep = (df['dt_start'] <= date) & (df['dt_end'] >= date)
    return df[keep][['rssdid', 'permco']]


if __name__ == "__main__":
    date = pd.to_datetime('2022-03-30')
    df = links_table('data/bank_crsp_links.csv', date)