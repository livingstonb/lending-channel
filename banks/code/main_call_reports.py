#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 20:31:44 2024

@author: brianlivingston
"""

import call_aux
import call_report_fns
import pandas as pd
import numpy as np


def start(bhcids):
    dirs = call_aux.ProjectDirs()

    call_table = call_report_fns.get_call(dirs)

    date = 20220630
    links_table = call_report_fns.get_banking_relationships(dirs, date)

    recursion = call_report_fns.CallRecursion(call_table, links_table)

    results = dict()
    for bhcid in bhcids:
        results[bhcid] = recursion.search(bhcid)

    return call_table, results


if __name__ == "__main__":
    chase = 1039502
    svb = 1031449
    bhcids = [chase, svb]

    (call_table, rssdids) = start(bhcids)

    df = pd.DataFrame()
    for bhcid in bhcids:
        idx = list(rssdids[bhcid])
        data = np.ones(len(idx), dtype=np.int32) * bhcid

        ser = pd.Series(data, name='bhc_rssdid', index=idx)
        matches = call_table.merge(ser, left_index=True, right_index=True)
        df = pd.concat([df, matches])

    variables = {
        'RCONF045': 'dep_retir_lt250k',
        'RCONF049': 'dep_nonretir_lt250k',
        'RCON5597': 'est_unins_deposits',
        'RCON2170': 'assets',
        'RCON2200': 'deposits',
    }
    df.rename(columns=variables, inplace=True)
    keep = [value for key, value in variables.items()]
    keep += ['bhc_rssdid']
    df = df[keep]
    df.index.name = 'rssdid'
