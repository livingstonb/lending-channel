#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 11:53:35 2024

@author: brianlivingston
"""

import os
import pandas as pd


def list_bhcids(fname):
    """

    Args:
        fname: file path for bhck dataset downloaded from WRDS

    Returns:
        array of rssdid values of top-tier BHCs
    """
    bhck_table = pd.read_csv(fname, header=0,
                             index_col='RSSD9001', low_memory=False)
    return bhck_table.index.values


def clean_banking_relationships(fname, date):
    """
    Reads raw FDIC table on banking relationships

    Parameters
    ----------
    date : Extract relationships at this date (integer: YYYYMMDD)

    Returns
    -------
    links_table : DataFrame

    """

    # File location
    links_table = pd.read_csv(
        fname, usecols=['#ID_RSSD_PARENT', 'ID_RSSD_OFFSPRING',
                        'DT_START', 'DT_END', 'PCT_EQUITY'])

    # Keep only active relationships at date
    date_mask = (links_table['DT_START'] < date
                 ) & (links_table['DT_END'] > date)
    links_table = links_table[date_mask]

    # Keep only relationships with > 50% equity ownership
    links_table = links_table[links_table['PCT_EQUITY'] > 50]
    # links_table = links_table[links_table['CTRL_IND'] == 1]

    links_table.drop(['DT_START', 'DT_END', 'PCT_EQUITY'],
                     axis=1, inplace=True)

    links_table.rename(columns={
        'ID_RSSD_OFFSPRING': 'rssdid',
        '#ID_RSSD_PARENT': 'parent_rssdid'}, inplace=True)

    top_tier = list(set(links_table['parent_rssdid'].values
                        ).difference(links_table['rssdid']))

    return links_table, top_tier


def call_recursion(links, bhcids):
    """

    Args:
        links: DataFrame
        bhcids: list of rssdids for BHCs

    Returns:
        dictionary containing bhcid keys, values are subordinate rssdids
    """
    results = dict()

    df = pd.DataFrame(columns=['rssdid', 'bhcid'])
    for bhcid in bhcids:
        results[bhcid] = {bhcid}
        recnum = 0
        found = down(bhcid, results[bhcid], links, recnum)
        results[bhcid] = list(results[bhcid].union(found))

        df_bhc = pd.DataFrame(results[bhcid], columns=['rssdid'])
        df_bhc['bhcid'] = bhcid
        df = df.merge(df_bhc, how='outer')

    return df.set_index('rssdid')


def down(parent, children, links, recnum):
    """
    Recursively moves down the ownership hierarchy
    """
    recnum += 1
    idx = (links['parent_rssdid'].values == parent)
    rows = links[idx]

    if (rows.size == 0) | (recnum > 100):
        return {}

    found = set(rows['rssdid'].values) - children

    if len(found) > 0:
        children = children.union(found)
        for rssdid in found:
            children = children.union(down(rssdid, children, links, recnum))

    return children











def call_files():
    files = {
        "FFIEC CDR Call Schedule RCO 06302022(1 of 2).txt":
            ['RCONF045', 'RCONF049', 'RCON5597'],
        "FFIEC CDR Call Schedule RC 06302022.txt":
            ['RCON2170', 'RCON2200'],
    }
    return files


def get_call(dirs):
    """
    Reads raw call reports

    Returns
    -------
    call_table : DataFrame

    """
    # Read delimited call reports text document

    call_path = dirs.datapath("Call-Reports-06302022")
    files = call_files()
    first = True
    # Loop over files, given quarter
    for key, value in files.items():
        call_file = os.path.join(call_path, key)
        int_table = pd.read_table(
            call_file, sep='\t', header=0, index_col='IDRSSD', low_memory=False)

        int_table = int_table[value]

        if first:
            call_table = int_table
            first = False
            continue
        else:
            # Merge with previous files
            call_table = call_table.merge(int_table, left_index=True, right_index=True)

    # Replace missings with 0 to avoid error
    nanvals = pd.isna(call_table.index)
    index_copy = call_table.index.values
    index_copy[nanvals] = [0]
    call_table.index = index_copy.astype('int')

    return call_table
