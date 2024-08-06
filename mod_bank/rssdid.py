#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 11:53:35 2024

@author: brianlivingston
"""

import pandas as pd
import numpy as np


def assign_bhcid(df, bhck_fname, relationships_fname, date):

    # (parent, child) table and list of top-tier institutions (no parents)
    links_table, top_tier = get_banking_relationships(relationships_fname, date)

    # list of rssdid's for all BHCs from BHCK file
    bhcids = get_bhcids_from_bhck(bhck_fname)

    # strip out child BHCs
    top_bhcs = list(set(top_tier).intersection(set(bhcids)))

    rssdid_top_bhc_links = get_top_bhc_links(links_table, top_tier)
    df = pd.merge(df, rssdid_top_bhc_links,
                  how='left', on='rssdid').rename(columns={'rssd9999': 'date'})

    bhc_fun = np.vectorize(lambda x: np.isin(x, top_bhcs))
    df['parent_is_bhc'] = bhc_fun(df['parent_rssdid'])
    return df

def get_bhcids_from_bhck(fname):
    """

    Args:
        fname: file path for bhck dataset downloaded from WRDS

    Returns:
        array of rssdid values BHCs
    """
    bhck_table = pd.read_csv(fname, header=0, thousands=',',
                             index_col='RSSD9001', low_memory=False, dtype={'RSSD9001': np.int32})
    return bhck_table.index.values


def get_banking_relationships(fname, date):
    """

    Parameters
    ----------
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
        'ID_RSSD_OFFSPRING': 'rssdid',
        '#ID_RSSD_PARENT': 'parent_rssdid'})

    links_table = links_table[['rssdid', 'parent_rssdid']]
    top_tier = list(set(links_table['parent_rssdid'].values.astype('Int64')
                        ).difference(set(links_table['rssdid'])))

    return links_table, top_tier


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

        df_bhc = pd.DataFrame(results[bhcid], columns=['rssdid'], dtype='Int64')
        df_bhc['bhcid'] = bhcid
        dfls.append(df_bhc)

    df = pd.concat(dfls, axis=0, ignore_index=True)
    df['parent_rssdid'] = df['bhcid'].astype('Int64')

    return df


def down(parent, children, links, recnum):
    recnum += 1
    idx = (links['parent_rssdid'].values == parent)
    rows = links[idx]

    if (rows.size == 0) | (recnum > 100):
        return set()

    found = set(rows['rssdid'].values) - children

    if len(found) > 0:
        children = children.union(found)
        for rssdid in found:
            children = children.union(down(rssdid, children, links, recnum.view()))

    return children

