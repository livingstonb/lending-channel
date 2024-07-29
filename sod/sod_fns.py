import pandas as pd


def clean(fname):
    df = pd.read_csv(fname, header=0, encoding='ISO-8859-1')
    df['NBRANCH'] = 1 - df['BKMO']
    variables = ['NBRANCH', 'ASSET', 'DEPSUM',
                 'NAMEHCR', 'RSSDID', 'RSSDHCR']
    df = df[variables]
    df.rename(columns={v: v.lower() for v in variables}, inplace=True)

    df = df.groupby('rssdhcr').agg({
        'nbranch': 'sum',
        'asset': 'sum',
        'depsum': 'sum',
        'namehcr': 'first',
        'rssdid': lambda x: None,
        })
    return df
