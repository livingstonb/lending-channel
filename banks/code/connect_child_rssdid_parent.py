import pandas as pd
import numpy as np
import os

def myfun(maindir):
	tempdir = os.path.join(maindir, "temp")

	# List of branch identifiers from Summary of Deposits (SOD)
	sod_path = os.path.join(tempdir, "sod_rssdid_only.csv")
	sod_table = pd.read_csv(sod_path)

	# Child-parent linking table
	links_path = os.path.join(tempdir, "rssdid_links.csv")
	links = pd.read_csv(links_path)

	zero_col = np.zeros((sod_table.size),
		dtype = np.int32)
	sod_table['bhc_rssdid'] = zero_col

	for i, child in enumerate(sod_table['rssdid'].values):
		# parent = int(links[links['rssdid']==int(child)]['parent_rssdid'].values)
		# get parent
		recursions = 0
		sod_table['bhc_rssdid'].iat[i] = move_up(child, links, recursions)

	print(sod_table.head())

	outfile = os.path.join(tempdir, "branch_bhc_linked.csv")
	sod_table.set_index('rssdid', inplace=True)

	sod_table.to_csv(outfile)

		
def move_up(child, links, recursions):
	row = links[links['rssdid'] == child]
	recursions += 1

	if row['parent_rssdid'].size == 0:
		return -1
	elif int(row['is_bhc'].values) == 1:
		return int(row['parent_rssdid'].values)
	elif recursions < 50:
		return move_up(child, links, recursions)
	else:
		return -2

# def binarysearch(arr):


if __name__ == "__main__":
	maindir = os.path.dirname(os.getcwd())
	myfun(maindir)


