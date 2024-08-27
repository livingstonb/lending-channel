#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 11:53:35 2024

@author: brianlivingston
"""
import re

import pandas as pd
import numpy as np
import wrds


class Query(object):
    uname = 'blivingston'
    tabnames = ['wrds_call_rcon_1', 'wrds_call_rcon_2',
                'wrds_call_rcfd_1', 'wrds_call_rcfd_2']
    variables_by_table = dict()

    def __init__(self, uname):
        self.conn = wrds.Connection(username=uname)

    def select_variables(self, selected):
        """
        Requires a connection to WRDS, and sets a dictionary indicating
        which column names to include for which call report tables

        Args:
            selected: list of variables (column names) to include in query
        """
        for tabname in self.tabnames:
            tab_variables = self.conn.get_table(
                library='bank', table=tabname, obs=1).columns.tolist()
            # Subset of selected variables in tabname
            selected_in_tab = [var for var in selected if var in tab_variables]
            self.variables_by_table.update({tabname: selected_in_tab})

    def query(self, date):
        """

        Args:
            date: integer date, YYYYMMDD

        Returns:
            df_out: DataFrame with query of call reports
        """

        # Query each table separately
        all_queries = list()
        for table_name in self.tabnames:
            variables = self.variables_by_table[table_name]
            if len(variables) == 0:
                continue

            # Query selected table
            query_this_table = query_one_table(
                self.conn, table_name, variables, date)
            query_this_table = query_this_table.set_index('rssd9001', drop=True)
            query_this_table.index.name = 'rssdid'

            # Save observation date and names for later
            dates_names = query_this_table[['rssd9999', 'rssd9017', 'rssd9200']]
            query_this_table = query_this_table.drop(['rssd9999', 'rssd9017', 'rssd9200'], axis=1)

            # Store results
            all_queries.append(query_this_table)

        # Concatenate query results from all tables
        df_out = pd.concat(all_queries, axis=1, join='outer')

        # Add back date, state, and institution names
        colnames = df_out.columns.tolist()
        df_out[['rssd9999', 'rssd9017', 'rssd9200']] = dates_names
        df_out['rssd9001'] = df_out.index.values
        df_out = df_out[['rssd9001', 'rssd9999', 'rssd9017', 'rssd9200'] + colnames]
        return df_out


def query_one_table(conn, table_name, variables, date):
    """

    Args:
        conn: WRDS connection object
        table_name: name of the call report table being queried in WRDS
        variables: list of column names to include in query
        date: integer date, YYYYMMDD

    Returns:
        query_output: DataFrame with query results
    """
    # String to pass to SQL for variable selection
    vstr = ', '.join(variables)
    # Date string
    datestr = f"between '{date} 00:00:00' and  '{date} 00:00:00'"
    # SQL query
    query_output = conn.raw_sql(
        """select rssd9001, rssd9999, rssd9017, rssd9200, %s
            from bank.%s
            where  rssd9999 %s""" % (vstr, table_name, datestr),
        date_cols=['rssd9999'])
    return query_output


def assign_topid_up(df, fname_links, attr_files, date):
    children = df['rssdid'].unique().tolist()

    # (parent, child) table and list of top-tier institutions (no parents)
    links_table = pd.read_csv(fname_links,
                        usecols=['#ID_RSSD_PARENT', 'ID_RSSD_OFFSPRING', 'RELN_LVL',
                                'DT_START', 'DT_END', 'PCT_EQUITY', 'OTHER_BASIS_IND',
                                'CTRL_IND', 'EQUITY_IND'],
                        dtype={'#ID_RSSD_PARENT': 'Int64',
                            'ID_RSSD_OFFSPRING': 'Int64'})

    # Keep only active relationships at date
    date_mask = (links_table['DT_START'] <= date
                 ) & (links_table['DT_END'] >= date)
    links_table = links_table[date_mask]

    links_table = links_table.rename(columns={
        'ID_RSSD_OFFSPRING': 'rssd9001',
        '#ID_RSSD_PARENT': 'parentid'})

    results = np.full((len(children), 2), -10, dtype=np.int64)
    for i, child in enumerate(children):
        parent = move_up(links_table, child)
        results[i, 0] = child
        results[i, 1] = parent

    final = pd.DataFrame(results, columns=['rssdid', 'parentid'])

    # Add top-tier name
    for i, fname_attr in enumerate(attr_files):
        attr_table = pd.read_csv(fname_attr,
                                  usecols=['#ID_RSSD', 'NM_LGL', 'DT_OPEN', 'DT_END',
                                           'BHC_IND', 'CHTR_TYPE_CD', 'CNTRY_CD', 'FHC_IND',
                                           'ID_LEI', 'ID_RSSD_HD_OFF', 'IHC_IND', 'INSUR_PRI_CD'],
                                  dtype={'#ID_RSSD': 'Int64',
                                         'DT_OPEN': 'Int64',
                                         'DT_END': 'Int64',
                                         'BHC_IND': 'Int64',
                                         'CHTR_TYPE_CD': 'Int64',
                                         'FHC_IND': 'Int64',
                                         'INSUR_PRI_CD': 'Int64',
                                         'ID_RSSD_HD_OFF': 'Int64',
                                         'CNTRY_CD': 'Int64',
                                         'IHC_IND': 'Int64'})
        # Keep only active attributes at date
        date_mask = (attr_table['DT_OPEN'] <= date
                     ) & (attr_table['DT_END'] >= date)
        attr_table = attr_table[date_mask].rename(columns={'#ID_RSSD': 'parentid'})

        final = final.merge(attr_table, on='parentid', how='left')
        if i == 1:
            colnames = final.columns.values.tolist()
            for colnm_y in filter(lambda x: x.endswith('_y'), colnames):
                variable = re.match('(.*)_y',colnm_y).groups()[0]
                final[variable] = final[colnm_y].fillna(final[variable+'_x'])
                final = final.drop([colnm_y, variable+'_x'], axis=1)

    return final


def move_up(links_table, child):
    parents = links_table[links_table['rssd9001'] == child]
    if parents.shape[0] == 0:
        return child
    elif parents.shape[0] == 1:
        # Go up again
        return move_up(links_table, parents.iloc[0]['parentid'])
    else:
        # Child maps to multiple parents
        mask = (parents['PCT_EQUITY'] > 50
                ) & (parents['EQUITY_IND'] > 0) & (parents['RELN_LVL'] == 1)
        candidates = parents[mask]
        if candidates.shape[0] == 0:
            return -1
        elif candidates.shape[0] == 1:
            return move_up(links_table, candidates.iloc[0]['parentid'])
        else:
            return -2