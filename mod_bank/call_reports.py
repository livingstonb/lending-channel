#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 11:53:35 2024

@author: brianlivingston
"""
import itertools
import re

import pandas as pd
import numpy as np
import wrds


class Query(object):
    uname = 'blivingston'
    tabnames = ['wrds_call_rcon_1', 'wrds_call_rcon_2', 'wrds_call_rcfd_1', 'wrds_call_rcfd_2',
                'wrds_call_rcoa_1']
    variables_by_table = dict()

    def __init__(self, uname, bhck=False):
        self.conn = wrds.Connection(username=uname)
        self.bhck = bhck
        if bhck:
            self.tabnames = ['wrds_holding_bhck_1', 'wrds_holding_bhck_2',
                             'wrds_holding_other_1']

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

        # Variables that show up in multiple tables (don't want merge issues)
        if self.bhck:
            common_vars = ['rssd9999', 'rssd9017']
        else:
            common_vars = ['rssd9999', 'rssd9017', 'rssdfininstfilingtype']

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
            dates_names = query_this_table[common_vars]
            query_this_table = query_this_table.drop(common_vars, axis=1)

            # Store results
            all_queries.append(query_this_table)

        # Concatenate query results from all tables
        df_out = pd.concat(all_queries, axis=1, join='outer')

        # Add back date, state, and institution names
        colnames = df_out.columns.tolist()
        df_out[common_vars] = dates_names
        df_out['rssd9001'] = df_out.index.values
        df_out = df_out[['rssd9001'] + common_vars + colnames]
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
        """select rssd9001, rssd9999, rssd9017, rssdfininstfilingtype, %s
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
    integer_vars = ['#ID_RSSD', 'DT_OPEN', 'DT_END', 'BHC_IND', 'CHTR_TYPE_CD',
                    'FHC_IND', 'INSUR_PRI_CD', 'ID_RSSD_HD_OFF', 'IHC_IND',
                    'MBR_FHLBS_IND', 'CNTRY_INC_CD']
    other_vars = ['ID_LEI', 'NM_LGL', 'DOMESTIC_IND']
    set_ints = {k: 'Int64' for k in integer_vars}

    for parent in [True, False]:
        for i, fname_attr in enumerate(attr_files):
            attr_table = pd.read_csv(fname_attr,
                                      usecols=other_vars+integer_vars,
                                      dtype=set_ints)
            # Keep only active attributes at date
            date_mask = (attr_table['DT_OPEN'] <= date
                         ) & (attr_table['DT_END'] >= date)

            if parent:
                # Merge for top tier parent
                attr_table = attr_table[date_mask].rename(columns={'#ID_RSSD': 'parentid'})
                final = final.merge(attr_table, on='parentid', how='left')
            else:
                # Merge for bank
                attr_table = attr_table[date_mask].rename(columns={'#ID_RSSD': 'rssdid'})
                final = final.merge(attr_table, on='rssdid', how='left')

            if i == 1:
                colnames = final.columns.values.tolist()
                for colnm_y in filter(lambda x: x.endswith('_y'), colnames):
                    variable = re.match('(.*)_y', colnm_y).groups()[0]
                    final[variable] = final[colnm_y].fillna(final[variable+'_x'])
                    final = final.drop([colnm_y, variable+'_x'], axis=1)

        if parent:
            colnames = {x: 'parent_'+x.lower() for x in other_vars+integer_vars}
        else:
            colnames = {x: x.lower() for x in other_vars + integer_vars}

        final = final.rename(columns=colnames)
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


def account_for_different_ffiec_forms(df):
    variables = df.columns.names.tolist()

    df = df.rename(columns={'rssdfininstfilingtype': 'form'})

    # Variables reported in rcfd for FFIEC 031 not rcon
    categories = ['famsec', 'gsec', 'othll']
    maturities = ['le3m', '3m1y', '1y3y', '3y5y', '5y15y', 'ge15y']
    rcfd_variables = ['_'.join(i) for i in itertools.product(categories, maturities)]
    rcfd_variables.extend(['assets', 'liabilities', 'sub_debt',
                           'total_equity_capital'])

    # Drop prefix and replace rcon value with rcfd value for 031 filers
    df = df.rename(columns={'rcon_' + x: x for x in rcfd_variables})
    for varname in rcfd_variables:
        df[varname] = df.where(df['form'] != 31, df['rcfd_' + varname])

    # rcfd_flien variables don't exist, just rename rcon
    flien_variables = ['flien_' + x for x in maturities]
    df = df.rename(columns={'rcon_' + x: x for x in flien_variables})
