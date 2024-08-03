import pandas as pd
from mod_bank import rssdid
from mod_bank import sod

def obtain_bhc_banks():
    links, top_tier = rssdid.get_banking_relationships(
        'data/bank_relationships.csv', 20220630)
    bhcids = rssdid.get_bhcids_from_bhck('data/bhck-06302022-wrds.csv')
    tt_bhcids = list(set(top_tier).intersection(set(bhcids)))
    return rssdid.get_top_bhc_links(links, tt_bhcids)


def read_call_reports(fname, bhc_banks):
    call = pd.read_csv(fname, header=0, index_col='rssdid')
    df = call.merge(bhc_banks, how='left', left_index=True,
                    right_index=True)
    return df


def use_sod():
    df = sod.clean("data/sod_2022.csv")
    return df


if __name__ == "__main__":

    df = pd.read_csv('data/call_jun2022.csv', header=0, index_col='rssdid')
    q = rssdid.assign_bhcid(df,
                            'data/bhck-06302022-wrds.csv', 'data/bank_relationships.csv',
                            20220630)