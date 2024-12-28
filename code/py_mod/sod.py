"""
Reads annual FDIC summary of deposits data from csv and aggregates to bank- and bhc-level.
Used to compute branch density = branches / total deposits and depends on input data
saved as 'data/sod_06_YYYY.csv' downloaded from the FDIC Bankfind Suite.

Code is expected to be run while working directory is set to main repository directory.
"""


import pandas as pd
import numpy as np


def sod_main(year):
    sod_filepath = f"../data/sod_06_{year}.csv"
    links_savepath = f"../temp/sod_bank_bhc_links_{year}.csv"
    df = read(sod_filepath, save_links_path=links_savepath)

    df_bhc = aggregate_to_bhc(df)
    df_bank = aggregate_to_bank(df)
    return df_bhc, df_bank


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


def aggregate_to_bhc(df):
    # Aggregate
    df = df[df['rssdhcr'] > 0]
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
    return df


def aggregate_to_bank(df, savepath=None):
    # Aggregate
    df = df.groupby('rssdid').agg({
        'nbranch': 'sum',
        'asset': 'sum',
        'depsum': 'sum',
        'namehcr': 'first',
        'rssdhcr': 'first',
        })
    df = df.sort_index()
    df['depsum'] = df['depsum'] * 1000 / 1e9
    df['asset'] = df['asset'] * 1000 / 1e9
    df['branch_density'] = df['nbranch'] / df['depsum']
    df.index.name = 'rssdid'
    return df


if __name__ == "__main__":
    (sod_bhc_2022_df, sod_bank_2022_df) = sod_main(2022)
    # sod_bhc_2022_df.to_csv("temp/sod_bhc_level_{year}.csv")
    # sod_bank_2022_df.to_csv("temp/sod_bank_level_{year}.csv")