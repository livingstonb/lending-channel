import pandas as pd
import numpy as np
import os

def link_child_bhc(maindir):
	####################################################################
	# Takes branch rssdid values from SOD and associates them with
	# the appropriate BHC rssdid.
	####################################################################

	# Temp directory for project
	tempdir = os.path.join(maindir, "temp")

	# Table of branch rssdid identifiers from Summary of Deposits (SOD)
	sod_path = os.path.join(tempdir, "sod_rssdid_only.csv")
	sod_table = pd.read_csv(sod_path)
	zero_col = np.zeros((sod_table.shape[0],1),
		dtype = np.int32)
	sod_table['bhc_rssdid'] = zero_col
	sod_table['bhc_name'] = ""

	# Child-parent linking table
	links_path = os.path.join(tempdir, "rssdid_links.csv")
	links = pd.read_csv(links_path)

	# Loop over SOD branches and find top-tier (BHC) parent of each branch
	for i, child in enumerate(sod_table['rssdid'].values):
		recursions = 0
		x = move_up(child, links, recursions)
		if x is not None:
			sod_table['bhc_rssdid'].iat[i] = x['parent_rssdid']
			sod_table['bhc_name'].iat[i] = x['bhc_name'].values[0]

	# Save results
	outfile = os.path.join(tempdir, "branch_bhc_linked.csv")
	sod_table.set_index('rssdid', inplace=True)

	# Compute branches per BHC
	sod_table = compute_branches(sod_table)

	# Save
	sod_table.to_csv(outfile)

		
def move_up(child, links, recursions):
	####################################################################
	# Recursively moves up the ownership hierarchy
	####################################################################
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

def compute_branches(data):
	return data.groupby('bhc_rssdid').agg({
		'bhc_name': 'first',
		'nbranches': 'sum',
		})

if __name__ == "__main__":
	maindir = os.path.dirname(os.getcwd())
	link_child_bhc(maindir)


