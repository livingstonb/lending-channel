import pandas as pd
import numpy as np
import os

def move_up(child, links, recursions):
	"""
	Recursively moves up the ownership hierarchy
	"""
	row = links[links['rssdid'].values == child]
	recursions += 1

	if row['parent_rssdid'].size == 0:
		# No apparent association with FR Y-9C-reporting BHC
		return None
	elif int(row['is_bhc'].values) == 1:
		# Found the BHC
		return row
	elif recursions < 50:
		# Move up again
		child = int(row['parent_rssdid'])
		return move_up(child, links, recursions)
	else:
		# Circular pattern in hierarchy
		return None