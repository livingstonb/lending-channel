import pandas as pd
from mod_bank import call_reports
from mod_bank import sod

def obtain_bhc_banks():
    links, top_tier = call_reports.clean_banking_relationships(
        'data/bank_relationships.csv', 20220630)
    bhcids = call_reports.list_bhcids('data/bhck-06302022-wrds.csv')
    # tt_bhcids = list(set(top_tier).intersection(set(bhcids)))
    tt_bhcids = top_tier
    return call_reports.call_recursion(links, tt_bhcids)


def read_call_reports(fname, bhc_banks):
    call = pd.read_csv(fname, header=0, index_col='rssdid')
    df = call.merge(bhc_banks, how='left', left_index=True,
                    right_index=True)
    return df


def use_sod():
    df = sod.clean("data/sod_2022.csv")
    return df


if __name__ == "__main__":
    bhc_banks = obtain_bhc_banks()
    callfile = 'data/call_jun2022.csv'
    df = read_call_reports(callfile, bhc_banks)

    df_sod = use_sod()
    aggregate = df.groupby('bhcid')[['deposits', 'd_htm_rmbs_gnma', 'd_htm_rmbs_fnma_fhlmc']].agg('sum')