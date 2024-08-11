
# TODO: merge in table of closed banks
# TODO: use ID_RSSD_HD_OFF to merge lower-branch attributes with headquarters if HQ doesn't show up?
# TODO: move on to routine that computes ownership

import pandas as pd


def merge_nic_tables(date):

    tables = {
        'attributes': 'data/NIC_attributes_active.csv',
        'relationships': 'data/NIC_relationships.csv'
    }
    nic_dfs = dict()
    for k, v in tables.items():
        nic_dfs[k] = read_nic_table(v, date)

    relns = nic_dfs['relationships'].rename(
        columns={'ID_RSSD_OFFSPRING': 'rssdid',
                 '#PARENT_ID_RSSD': 'parentid'})
    attr = nic_dfs['attributes'].rename(columns={'#ID_RSSD': 'rssdid'})

    # Sample selection and merge
    # attr = sample_selection(attr)
    # df = attr.merge(relns, on='rssdid', how='left', validate='1:m')

    print("hello")
    return relns

def read_nic_table(fpath, date):
    df = pd.read_csv(fpath, low_memory=False)
    date_mask = (df['DT_START'] < date
                 ) & (df['DT_END'] > date)
    df = df[date_mask].drop(['DT_END', 'DT_START', 'D_DT_END', 'D_DT_START'], axis=1)
    return df


def sample_selection(df):

    # Insured institutions (excluding state-only insured, value 4)
    insured_institutions = [1, 2, 6, 7]
    df = df[df['INSUR_PRI_CD'].apply(lambda x: x in insured_institutions)]

    # Must be chartered as a commercial bank (note savings bank 300, S&L 310, holding company 500)
    charter_types = [200, 300, 310, 500]
    df = df[df['CHTR_TYPE_CD'].apply(lambda x: x in charter_types)]

    # Within the US
    df = df[df['STATE_CD'].apply(lambda x: (x > 0) & (x < 57))]

    return df


class Traversal(object):

    def __init__(self, links):
        for rssd in links['rssdid'].unique():


    def traverse_up(links, attr, child):
        parents = links[links['rssdid'] == child]
        if parents.shape[0] == 0:
            return [child]
        # elif parents.shape[0] == 1:
        #     return parents['parentid'].tolist()

        candidates = parents[parents['pct_equity'] > 50]
        if candidates.shape[0] == 0:
            return [child]
        elif candidates.shape[0] == 1:
            return candidates['parentid'].tolist()
        elif candidates.shape[0] > 1:
            return [-1]



# class OwnershipTree(object):
#
#     def traverse(self, child):
#
# class Node(object):

if __name__ == "__main__":
    merge_nic_tables(20220630)

    trav = Traversal()
