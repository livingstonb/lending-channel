#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 11:53:35 2024

@author: brianlivingston
"""
import os
import aux
import pandas as pd


class CallReportRecursion:
	
	children = {}
	
	def __init__(self):
		self.set_directories()
	
	def set_directories(self):
		# Call report data
		dirs = aux.ProjectDirs()
		callreports = os.path.join(dirs.data, "Call-Reports-06302022")
		callrcon = os.path.join(callreports, "FFIEC CDR Call Schedule RCO 06302022(1 of 2).txt")
		self.call = pd.read_csv(callrcon, sep='\t', header=[0,1])
		
		# Bank relationships
		links_path = os.path.join(dirs.temp, "rssdid_links.csv")
		self.links = pd.read_csv(links_path)
		
	def search_from_top(self, bhcid):
		recursions = 0
		self.move_down(bhcid, recursions)
		
	def move_down(self, parent, recursions):
		"""
		Recursively moves down the ownership hierarchy
		"""
		recursions += 1
		idx = (self.links['parent_rssdid'].values == parent)
		rows = self.links[idx]
		
		if (rows.size == 0) | (recursions > 50):
			return
		
		additions = rows['rssdid'].values.to_set()
		additions -= self.children
		
		if len(additions) == 0:
			return
		
		self.children.add(additions)
		
		for rssdid in additions:
			self.move_down(rssdid, 1)
		
		
if __name__ == "__main__":
	cr = CallReportRecursion()
	cr.search_from_top(2942690)
	print(cr.children)
# =============================================================================
# 	ids = [2942690]
# 	cols = ["RCONF045", "RCONF049"]
# 	begin(ids, cols)
# =============================================================================
# =============================================================================
# 		results = []
# =============================================================================

# =============================================================================
# 		if row['rssdid'].size == 0:
# 			# No children found
# 			return results
# 		elif row['rssdid'].size == 1:
# 			# End of the branch, return variables
# 			return move_down(pid, links, cols, rec0)
# =============================================================================
