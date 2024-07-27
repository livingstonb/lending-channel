#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 20:31:44 2024

@author: brianlivingston
"""

import aux
import call_report_fns
import pandas as pd
import numpy as np

def start(bhcid):
	dirs = aux.ProjectDirs()
	
	call_table = call_report_fns.get_call(dirs)
	
	date = 20220630
	links_table = call_report_fns.get_banking_relationships(dirs, date)
	
	
	recursion = call_report_fns.CallRecursion(call_table, links_table)
	results = recursion.search(bhcid)
	return (call_table, results)

if __name__ == "__main__":
	chase = 1039502
	(call_table, rssdids) = start(chase)
	idx = list(rssdids)
	data = np.ones(len(idx))
	
	ser = pd.Series(data, name='matched_rssdid', index=idx)
	matches = call_table.merge(ser, left_index=True, right_index=True)
	insured_deposits = matches['RCONF045'] + matches['RCONF049']
	# convert to double