import pandas as pd
from call_reports import link_rssdids


def obtain_bhc_banks():
    links, top_tier = link_rssdids.clean_banking_relationships(
        'data/bank_relationships.csv', 20220630)
    bhcids = link_rssdids.list_bhcids('data/bhck-06302022-wrds.csv')
    tt_bhcids = list(set(top_tier).intersection(set(bhcids)))
    return link_rssdids.call_recursion(links, tt_bhcids)


def read_call_reports(fname, bhc_banks):
    call = pd.read_csv(fname, header=0, index_col='rssdid')
    df = call.merge(bhc_banks, how='left', left_index=True,
                    right_index=True)
    return df

if __name__ == "__main__":
    bhc_banks = obtain_bhc_banks()
    callfile = 'data/call_jun2022.csv'
    df = read_call_reports(callfile, bhc_banks)
    print(df.head())