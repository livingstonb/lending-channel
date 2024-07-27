#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 11:53:35 2024

@author: brianlivingston
"""

import os
import pandas as pd


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


def get_banking_relationships(dirs, date):
    """
    Reads raw FDIC table on banking relationships

    Parameters
    ----------
    date : Extract relationships at this date
        DESCRIPTION.

    Returns
    -------
    links_table : DataFrame

    """

    # File location
    links_file = dirs.datapath("bank_relationships.csv")
    links_table = pd.read_csv(links_file)
    links_table = links_table[
        ['#ID_RSSD_PARENT', 'ID_RSSD_OFFSPRING',
         'DT_START', 'DT_END', 'PCT_EQUITY', 'CTRL_IND']]

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

    return links_table


class CallRecursion:

    def __init__(self, call_table, links_table):
        self.call = call_table
        self.links = links_table

    def search(self, bhcid):
        recursions = 0
        return self.move_down(bhcid, recursions)

    def move_down(self, parent, recursions, sel=set()):
        """
        Recursively moves down the ownership hierarchy
        """
        recursions += 1
        idx = (self.links['parent_rssdid'].values == parent)
        rows = self.links[idx]

        if (rows.size == 0) | (recursions > 50):
            return sel

        additions = set(rows['rssdid'].values) - sel

        if len(additions) > 0:
            sel = sel.union(additions)
            for rssdid in additions:
                sel = sel.union(self.move_down(rssdid, 1, sel))

        return sel
