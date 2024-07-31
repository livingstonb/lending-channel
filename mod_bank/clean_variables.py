
import pandas as pd
import numpy as np


def newvars(df):
    df['insured_deposits'] = df[['dep_nonretir_lt250k', 'dep_retir_lt250k']].sum(axis=1)
    df['uninsured_deposits'] = df['deposits'] - df['insured_deposits']