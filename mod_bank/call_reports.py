#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 11:53:35 2024

@author: brianlivingston
"""

import pandas as pd
import numpy as np
import wrds


def assign_bhcid(df, bhck_fname, relationships_fname, date):

    # (parent, child) table and list of top-tier institutions (no parents)
    links_table, top_tier = get_banking_relationships(relationships_fname, date)

    # list of rssdid's for all BHCs from BHCK file
    bhcids = get_bhcids_from_bhck(bhck_fname)

    # strip out child BHCs
    top_bhcs = list(set(top_tier).intersection(set(bhcids)))

    rssdid_top_bhc_links = get_top_bhc_links(links_table, top_bhcs)
    # bdups = rssdid_top_bhc_links['rssd9001'].duplicated(keep=False)
    # dups = rssdid_top_bhc_links[bdups]['rssd9001']

    # For now, jus get rid of banks with multiple BHC connections
    rssdid_top_bhc_links = rssdid_top_bhc_links.drop_duplicates(subset='rssd9001', keep=False)
    df = df.merge(rssdid_top_bhc_links, on='rssd9001', how='left')

    # rssdid_top_bhc_links = myfun(rssdid_top_bhc_links)
    # df = pd.concat([df, rssdid_top_bhc_links], axis=1)


    bhc_fun = np.vectorize(lambda x: np.isin(x, top_bhcs))
    df['parent_is_bhc'] = bhc_fun(df['parent_rssdid'])
    return df


def myfun(df):
    # Duplicate matches to drop
    cases = list()
    # Grand Valley Bank
    cases.append((df['rssd9001'] == 178851)
                 & (df['parent_rssdid'] == 3695528))
    # First State Bank
    cases.append((df['rssd9001'] == 264455)
                 & (df['parent_rssdid'] == 3035227))
    # Home Savings Bank, ownership by two BHCs (5421413, 5421422)
    cases.append((df['rssd9001'] == 460770)
                 & (df['parent_rssdid'] == 5421413))
    # Commercial Bank, ownership by two FHCs (3793219, 2492485)
    cases.append((df['rssd9001'] == 497039)
                 & (df['parent_rssdid'] == 3793219))
    # Austin Bank, Texas National Association, ownership by (3072660, 3035227)
    cases.append((df['rssd9001'] == 548351)
                 & (df['parent_rssdid'] == 3072660))
    # Capital Bank, ownership by (3072660, 3035227)
    cases.append((df['rssd9001'] == 596156)
                 & (df['parent_rssdid'] == 3072660))
    # Nexbank, ownership by (3864614,4970802)
    cases.append((df['rssd9001'] == 652874)
                 & (df['parent_rssdid'] == 3864614))
    # First State Bank
    cases.append((df['rssd9001'] == 3285246)
                 & (df['parent_rssdid'].isin([1250419, 3285219])))
    # Bank of Lexington
    cases.append((df['rssd9001'] == 3410141)
                 & (df['parent_rssdid'] == 1100309))

    mask = cases.pop()
    for case in cases:
        mask = mask | case
    df = df.drop(df.index[mask])

    return df

def get_banking_relationships(fname, date):
    """

    Parameters
    ----------
    fname : filepath for banking relationships csv
    date : Integer date at which to get relationships, YYYYMMDD

    Returns
    -------
    links_table : DataFrame
    top_tier : list of rssdid's that only appear as parents
    """

    # File location
    links_table = pd.read_csv(
        fname, usecols=['#ID_RSSD_PARENT', 'ID_RSSD_OFFSPRING', 'RELN_LVL',
                        'DT_START', 'DT_END', 'PCT_EQUITY', 'OTHER_BASIS_IND',
                        'CTRL_IND'],
        dtype={'#ID_RSSD_PARENT': 'Int64',
               'ID_RSSD_OFFSPRING': 'Int64'})

    # Keep only active relationships at date
    date_mask = (links_table['DT_START'] <= date
                 ) & (links_table['DT_END'] >= date)
    links_table = links_table[date_mask]

    # Keep only relationships with > 50% equity ownership, or other control
    # mask = (links_table['PCT_EQUITY'] > 50) | (
    #     ('OTHER_BASIS_IND' == 1) & ('RELN_LVL' == 1)
    # )
    mask = links_table['CTRL_IND'] == 1
    links_table = links_table[mask]

    links_table = links_table.rename(columns={
        'ID_RSSD_OFFSPRING': 'rssd9001',
        '#ID_RSSD_PARENT': 'parent_rssdid',
        'PCT_EQUITY': 'pct_equity'})

    links_table = links_table[['rssd9001', 'parent_rssdid']]
    top_tier = list(set(links_table['parent_rssdid'].values.astype('Int64')
                        ).difference(set(links_table['rssd9001'])))

    return links_table, top_tier


def get_bhcids_from_bhck(fname):
    """
    Extracts rssdid's for all bank holding companies, given filepath to BHCK.

    Args:
        fname: file path for bhck dataset downloaded from WRDS

    Returns:
        array of rssdid values BHCs
    """
    bhck_table = pd.read_csv(fname, header=0, thousands=',',
                             index_col='RSSD9001', low_memory=False, dtype={'RSSD9001': np.int32})
    return bhck_table.index.values


def get_top_bhc_links(links, bhcids):
    """

    Args:
        links: DataFrame of bank relationships, 1st col parent, 2nd parent child
        bhcids: list of rssdids for BHCs

    Returns:
        2-column DataFrame (rssdid, top-tier BHC)
    """
    results = dict()

    dfls = list()
    for i, bhcid in enumerate(bhcids):
        results[bhcid] = set()
        recnum = np.array([0], dtype='int32')
        found = down(bhcid, results[bhcid], links, recnum.view())
        results[bhcid] = list(results[bhcid].union(found))

        df_bhc = pd.DataFrame(results[bhcid], columns=['rssd9001'], dtype='Int64')
        df_bhc['bhcid'] = bhcid
        dfls.append(df_bhc)

    df = pd.concat(dfls, axis=0, ignore_index=True)

    df['parent_rssdid'] = df['bhcid'].astype('Int64')
    df = df.drop('bhcid', axis=1)
    df = df.drop_duplicates()

    return df


def down(parent, children, links, recnum):
    recnum += 1
    idx = (links['parent_rssdid'].values == parent)
    rows = links[idx]

    if (rows.size == 0) | (recnum > 100):
        return set()

    found = set(rows['rssd9001'].values) - children

    if len(found) > 0:
        children = children.union(found)
        for rssdid in found:
            children = children.union(down(rssdid, children, links, recnum.view()))

    return children


def request_call_reports(uname):
    conn = wrds.Connection(username=uname)
    return conn


def variables_by_table(conn):
    """
    Requires a connection to WRDS, and returns a dictionary indicating
    which variables can be accessed via which BANK tables in WRDS.

    Args:
        conn: WRDS connection

    Returns:
        tabs: dictionary with entries {'WRDS table name': [all vars in table]}
    """
    tabnames = ['wrds_call_rcon_1', 'wrds_call_rcon_2',
                'wrds_call_rcfd_1', 'wrds_call_rcfd_2']
    tabs = dict()
    for tabname in tabnames:
        variables = conn.get_table(
            library='bank', table=tabname, obs=1).columns.values
        tabs.update({tabname: list(variables)})

    return tabs