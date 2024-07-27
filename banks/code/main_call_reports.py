#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 20:31:44 2024

@author: brianlivingston
"""

import aux
import os
import pandas as pd
from CallReportRecursion import CallReportRecursion

def get_call(dirs):
	"""
	Reads raw call reports

	Returns
	-------
	call_table : DataFrame

	"""
	# Read delimited call reports text document
	
	call_path = dirs.datapath("Call-Reports-06302022")
	call_file = os.path.join(call_path,
						 "FFIEC CDR Call Schedule RCO 06302022(1 of 2).txt")
	call_table = pd.read_table(call_file, sep='\t', header=0, index_col='IDRSSD',
						low_memory=False)
	
	# Replace missings with 0 to avoid error
	nanvals = pd.isna(call_table.index)
	index_copy = call_table.index.values
	index_copy[nanvals] = [0]
	call_table.index = index_copy.astype('int')
	
	return call_table

def get_banking_relationships(date):
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
	   'DT_START', 'DT_END', 'PCT_EQUITY']]
	
	# Keep only active relationships at date
	date_mask = (links_table['DT_START'] < date
			  ) & (links_table['DT_END'] > date) 
	links_table = links_table[date_mask]
	
	# Keep only relationships with > 50% equity ownership
	links_table = links_table[links_table['PCT_EQUITY'] > 50]
	links_table.drop(['DT_START', 'DT_END', 'PCT_EQUITY'],
				  axis=1, inplace=True)
	
	links_table.rename(columns={
		'ID_RSSD_OFFSPRING': 'rssdid',
		'#ID_RSSD_PARENT': 'parent_rssdid'}, inplace=True)
	
	return links_table

if __name__ == "__main__":
	dirs = aux.ProjectDirs()
	call_table = get_call(dirs)
	date = 20220630
	links_table = get_banking_relationships(date)
	
	chase = 1039502
	recursion = CallReportRecursion(call_table, links_table)
	results = recursion.search(chase)
	