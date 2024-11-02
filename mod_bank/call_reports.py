#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains main operations to request and clean call reports data.
Created on Fri Jul 26 11:53:35 2024

@author: brianlivingston
"""
import itertools
import re
import pandas as pd
import numpy as np
import wrds
from mod_aux import functions

class Query(object):
    uname = 'blivingston'
    tabnames = ['wrds_call_rcon_1', 'wrds_call_rcon_2', 'wrds_call_rcfd_1', 'wrds_call_rcfd_2',
                'wrds_call_rcoa_1', 'wrds_call_riad_1']
    variables_by_table = dict()
    n_test_data = -1
    gen_test_data = False
    test_data_path = 'temp/test_input'

    def __init__(self, uname, bhck=False, gen_test_data=False):
        self.conn = wrds.Connection(username=uname)
        self.bhck = bhck

        self.gen_test_data = gen_test_data
        if self.gen_test_data:
            self.n_test_data = 100

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

            # Dictionary that links table 'tabname' to a list of selected variables
            # that show up in the WRDS table 'tabname'
            self.variables_by_table.update({tabname: selected_in_tab})

    def query(self, date):
        """
        Query the WRDS tables.
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

            # Limit dataset
            if self.gen_test_data:
                nsample = self.n_test_data
            else:
                nsample = -1

            # Query selected table
            query_this_table = query_one_table(
                self.conn, table_name, variables, date, nsample)
            query_this_table = query_this_table.set_index('rssd9001', drop=True)
            query_this_table.index.name = 'rssdid'

            # Save observation date and names for later, same across loop iterations
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


def query_one_table(conn, table_name, variables, date, n_test_data):
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

    # Generate mall dataset if using for tests
    if n_test_data > 0:
        limstr = f"limit {n_test_data}"
    else:
        limstr = ""

    # Date range string
    datestr = f"between '{date} 00:00:00' and  '{date} 00:00:00'"
    # SQL query
    query_output = conn.raw_sql(
        """select rssd9001, rssd9999, rssd9017, rssdfininstfilingtype, %s
            from bank.%s
            where  rssd9999 %s
            %s""" % (vstr, table_name, datestr, limstr),
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

    # Keep only active relationships valid at date
    date = pd.to_datetime(f'{date}')
    links_table['DT_START'] = links_table['DT_START'].where(
        links_table['DT_START'] != 0, 19000101)
    links_table['DT_END'] = links_table['DT_END'].where(
        links_table['DT_END'] < 99991231, 20501231)
    for var in ['DT_START', 'DT_END']:
        links_table[var] = pd.to_datetime(links_table[var].apply(lambda x: f'{x} 00:00:00'))
    date_mask = (links_table['DT_START'] <= functions.quarter_start_value(date)
                 ) & (links_table['DT_END'] >= date)
    links_table = links_table[date_mask]
    links_table = links_table.rename(columns={
        'ID_RSSD_OFFSPRING': 'rssd9001',
        '#ID_RSSD_PARENT': 'parentid'})

    # Start recursion up the ownership structure
    # Each unique rssdid is treated as a child
    results = np.full((len(children), 2), -10, dtype=np.int64)
    for i, child in enumerate(children):
        parent = move_up(links_table, child)
        # Results from recursion. Row is: [child rssdid, parent rssdid]
        results[i, 0] = child
        results[i, 1] = parent

    final = pd.DataFrame(results, columns=['rssdid', 'parentid'])

    # Add variables
    integer_vars = ['#ID_RSSD', 'DT_OPEN', 'DT_END', 'BHC_IND', 'CHTR_TYPE_CD',
                    'FHC_IND', 'INSUR_PRI_CD', 'IHC_IND',
                    'MBR_FHLBS_IND', 'CNTRY_INC_CD']
    set_ints = {k: 'Int64' for k in integer_vars}
    other_vars = ['ID_LEI', 'NM_LGL', 'DOMESTIC_IND']

    # Merge in parent bank attributes table and then child bank attributes
    for parent in [True, False]:
        # Attr_files are active, and closed banks
        for i, fname_attr in enumerate(attr_files):
            attr_table = pd.read_csv(fname_attr,
                                      usecols=other_vars+integer_vars,
                                      dtype=set_ints)
            attr_table['DT_OPEN'] = attr_table['DT_OPEN'].where(
                attr_table['DT_OPEN'] != 0, 19000101)
            attr_table['DT_END'] = attr_table['DT_END'].where(
                attr_table['DT_END'] < 99991231, 20501231)
            for var in ['DT_OPEN', 'DT_END']:
                attr_table[var] = pd.to_datetime(
                    attr_table[var].apply(lambda x: f'{x} 00:00:00'))
            # Keep only attributes valid for the entire period
            date_mask = (attr_table['DT_OPEN'] <= functions.quarter_start_value(date)
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


def strip_prefixed(variables, prefix):
    return [s.split(prefix)[1] for s in variables]


def account_for_different_ffiec_forms(df):
    df = df.rename(columns={'rssdfininstfilingtype': 'form'})
    column_names = df.columns.tolist()

    # Variables designated with rcon prefix
    rcon_list = [s for s in column_names if s.startswith('rcon_')]
    rcon_names = strip_prefixed(rcon_list, 'rcon_')
    df = df.rename(columns={k: v for k, v in zip(rcon_list, rcon_names)})

    # Replace values with RCFD for 031 filers
    rcfd_list = [s for s in column_names if s.startswith('rcfd_')]
    rcfd_names = strip_prefixed(rcfd_list, 'rcfd_')
    for name in rcon_names:
        if name in rcfd_names:
            df[name] = df[name].mask(df.form == '031', df['rcfd_'+name])
            df = df.drop('rcfd_'+name, axis=1)

    return df


def account_for_ma(df, fpath):
    transf = pd.read_csv(fpath)
    vars = transf.columns.tolist()
    transf = transf.rename(columns={n: n.lower() for n in vars})
    transf = transf.rename(columns={
        'id_rssd_successor': 'event_successor',
        '#id_rssd_predecessor': 'event_predecessor',
    })

    # Tranformation date by quarter
    transf['d_dt_trans'] = pd.to_datetime(transf['d_dt_trans'])
    transf['quarter'] = functions.quarter_end(transf['d_dt_trans'])
    min_date = df['date'].min()
    transf = transf[transf['quarter'] >= min_date]

    # Merge predecessor events
    sel_idx = ['event_predecessor', 'quarter']
    selection = transf[['event_predecessor', 'quarter', 'trnsfm_cd']]
    selection = selection.drop_duplicates(sel_idx)
    selection = selection.rename({'trnsfm_cd': 'event_was_predecessor_cd'})
    df = df.reset_index()
    df = pd.merge(df, selection, left_on=['rssdid', 'date'], right_on=sel_idx, how='left')
    df = df.drop(sel_idx, axis=1)

    # Merge successor events
    sel_idx = ['event_successor', 'quarter']
    selection = transf[sel_idx].drop_duplicates(sel_idx)
    selection['event_was_successor'] = 1
    df = pd.merge(df, selection, left_on=['rssdid', 'date'], right_on=sel_idx, how='left')
    df = df.drop(sel_idx, axis=1)

    return df