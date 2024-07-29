"""
Given a list of rssdid values, these functions
produce a table containing the rssdid, the top-tier
BHC if applicable, and the name of the BHC
"""

import os
import pandas as pd
import call_aux

def main(dirs):

	rssdids_path = os.path.join(dirs.temp, "sod_rssdid_only.csv")
	rssdids = pd.read_csv(rssdids_path)

	links_path = os.path.join(dirs.temp, "rssdid_links.csv")
	links = pd.read_csv(links_path)

	return call_aux.get_bhc(rssdids, links)
	
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

def export(data, dirs):
	data.to_csv(os.path.join(dirs.temp, 'links.csv'))

if __name__ == "__main__":
	projdirs = call_aux.ProjectDirs()
	data = main(projdirs)
	export(data, projdirs)
	statistics(data)