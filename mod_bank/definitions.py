
import pandas as pd
import numpy as np


def insured_uninsured(df):
    df['insured_deposits'] = df[['rcon_dep_nonretir_lt250k', 'rcon_dep_retir_lt250k']].sum(axis=1)
    df['uninsured_deposits'] = df['deposits'] - df['insured_deposits']

    # Other uninsured funding
    uninsured_funding = ['rcon_repo_liab_ff', 'rcon_repo_liab_oth', 'rcon_sub_debt'
                         'rcon_oth_borr_money', 'rcon_sub_debt', 'rcon_liab_fbk_trans',
                         'rcon_liab_fbk_ntrans', 'rcon_liab_foff_trans', 'rcon_liab_foff_ntrans']
    df['uninsured_debt'] = df[['uninsured_deposits'] + uninsured_funding].sum(axis=1)
    df['uninsured_leverage'] = df['uninsured_debt'].values / df['rcon_assets'].values

    return df
