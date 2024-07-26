import pandas as pd
import numpy as np
import os

class ProjectDirs:
	def __init__(self, codedir=os.getcwd()):
		self.code = codedir
		self.main = os.path.dirname(self.code)
		self.temp = os.path.join(self.main, "temp")
		self.out = os.path.join(self.main, "out")

def get_bhc(data, links):
	"""
	Input : array-like of rssdid's
	"""
	zero_col = np.zeros((data.shape[0],1),
		dtype = np.int32)
	data['bhc_rssdid'] = zero_col
	data['bhc_name'] = ""

	# Loop over rssdid and find top-tier (BHC) parent of each
	for i, child in enumerate(data['rssdid'].values):
		recursions = 0
		x = move_up(child, links, recursions)
		if x is not None:
			data['bhc_rssdid'].iat[i] = x['parent_rssdid']
			data['bhc_name'].iat[i] = x['bhc_name'].values[0]

	return data


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