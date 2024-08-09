import pandas as pd
import numpy as np


def read(fname, include_hcr=True, save_links_path=None):
    df = pd.read_csv(fname, header=0, encoding='ISO-8859-1', thousands=',',
                     dtype={'BKMO': np.int32, 'RSSDID': np.int32, 'RSSDHCR': np.int32})
    if include_hcr:
        df['NBRANCH'] = 1
    else:
        df['NBRANCH'] = 1 - df['BKMO']

    variables = ['NBRANCH', 'ASSET', 'DEPSUM',
                 'NAMEHCR', 'RSSDID', 'RSSDHCR']
    df = df[variables]
    df = df.rename(columns={v: v.lower() for v in variables})

    # Optionally saves bank-BHC identifier links
    if save_links_path is not None:
        save_bank_bhc_links(df, save_links_path)

    return df


def save_bank_bhc_links(df, save_links_path):
    links = df[['rssdid', 'rssdhcr']].drop_duplicates().set_index('rssdid')
    links.to_csv(save_links_path)


def aggregate(df, savepath=None):
    # Aggregate
    df = df.groupby('rssdhcr').agg({
        'nbranch': 'sum',
        'asset': 'sum',
        'depsum': 'sum',
        'namehcr': 'first',
        'rssdid': lambda x: None,
        })
    df = df.drop(columns=['rssdid']).sort_index()
    df['depsum'] = df['depsum'] * 1000 / 1e9
    df['asset'] = df['asset'] * 1000 / 1e9
    df['branch_density'] = df['nbranch'] / df['depsum']
    df.index.name = 'rssdid'

    if savepath is not None:
        df.to_csv(savepath)

    return df