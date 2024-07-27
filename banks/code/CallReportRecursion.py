#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 11:53:35 2024

@author: brianlivingston
"""

class CallReportRecursion:
		
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