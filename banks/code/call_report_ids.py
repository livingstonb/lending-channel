"""
Given BHC rssdid, aggregate bank-level variables
"""

import pandas as pd
import aux
import os

def begin(ids, cols):
	# Call report data
	dirs = aux.ProjectDirs()
	callreports = os.path.join(dirs.data, "Call-Reports-06302022")
# 	callrcon = os.path.join(callreports, "FFIEC CDR Call Schedule RCO 06302022(1 of 2).txt")
	callrcon = os.path.join(callreports, "FFIEC CDR Call Schedule POR 06302022.txt")
	df = pd.read_csv(callrcon, sep='\t', header=[0,1])
	
	# Bank relationships
	links_path = os.path.join(dirs.temp, "rssdid_links.csv")
	links = pd.read_csv(links_path)
	return df

# =============================================================================
# 	for id in ids:
# 		recursions = 0
# 		x = move_down(id, links, df, cols, recursions)
# =============================================================================
		
		
# =============================================================================
# def move_down(parent, links, cols, recursions):
# 	"""
# 	Recursively moves down the ownership hierarchy
# 	"""
# 	row = links[links['parent_rssdid'].values == parent]
# 	recursions += 1
# 	
# 	results = []
# 
# 	if row['rssdid'].size == 0:
# 		# No children found
# 		return results
# 	elif row['rssdid'].size == 1:
# 		# End of the branch, return variables
# 		return move_down(pid, links, cols, rec0)
# 	elif recursions < 50:
# 		# Multiple branches, recurse on each one
# 		for i, pid in enumerate(row['rssdid'].values):
# 			rec0 = 1
# 			z = move_down(pid, links, cols, rec0)
# 			results.append(z)
# 		return results
# 	else:
# 		# Circular pattern in hierarchy
# 		return None
# 
# =============================================================================
if __name__ == "__main__":
	ids = [2942690]
	cols = ["RCONF045", "RCONF049"]
	df = begin(ids, cols)