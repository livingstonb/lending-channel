# Given a list of rssdid values, these functions
# produce a table containing the rssdid, the top-tier
# BHC if applicable, and the name of the BHC

import os
import pandas as pd
import bankagg

def main():
	dirs = {}
	dirs['main'] = os.path.dirname(os.getcwd())
	dirs['temp'] = os.path.join(dirs['main'], "temp")

	rssdids_path = os.path.join(dirs['temp'], "sod_rssdid_only.csv")
	rssdids = pd.read_csv(rssdids_path)

	links_path = os.path.join(dirs['temp'], "rssdid_links.csv")
	links = pd.read_csv(links_path)

	return bankagg.get_bhc(rssdids, links)
	
def statistics(data):
	z = data.groupby('bhc_rssdid').agg({
		'bhc_name': 'first',
		'nbranches': 'sum',
		})
	return z

def export(data):
	dirs = {}
	dirs['main'] = os.path.dirname(os.getcwd())
	dirs['temp'] = os.path.join(dirs['main'], "temp")
	data.to_csv(os.path.join(dirs['temp'], 'links.csv'))

if __name__ == "__main__":
	data = main()
	export(data)
	statistics(data)