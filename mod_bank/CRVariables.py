import pandas as pd

class CRVariables(object):

    def __init__(self, dates):
        self.rcon = self.variables_from('rcon')
        self.rcfd = self.variables_from('rcfd')
        self.dates = dates
        self.keys = {'rssd9001': 'rssdid', 'rssd9999': 'date'}
        self.other = {'rssd2017': 'name'}
        self.variables_table = None

    def get_table_name(self, variables):
        tables = dict()
        for var in variables:
            tables[var] = self.variables_table[
                self.variables_table['var'] == 'var']['table']

        return tables

    def variables_from(self, ctab):
        allvars = {
            f'{ctab}f045': f'{ctab}_dep_retir_lt250k',
            f'{ctab}f049': f'{ctab}_dep_nretir_lt250k',
            f'{ctab}a549': f'{ctab}_gsec_le3m',
            f'{ctab}a550': f'{ctab}_gsec_3m1y',
            f'{ctab}a551': f'{ctab}_gsec_1y3y',
            f'{ctab}a552': f'{ctab}_gsec_3y5y',
            f'{ctab}a553': f'{ctab}_gsec_5y15y',
            f'{ctab}a554': f'{ctab}_gsec_ge15y',
            f'{ctab}a555': f'{ctab}_famsec_le3m',
            f'{ctab}a556': f'{ctab}_famsec_3m1y',
            f'{ctab}a557': f'{ctab}_famsec_1y3y',
            f'{ctab}a558': f'{ctab}_famsec_3y5y',
            f'{ctab}a559': f'{ctab}_famsec_5y15y',
            f'{ctab}a560': f'{ctab}_famsec_ge15y',
            f'{ctab}a564': f'{ctab}_flien_le3m',
            f'{ctab}a565': f'{ctab}_flien_3m1y',
            f'{ctab}a566': f'{ctab}_flien_1y3y',
            f'{ctab}a567': f'{ctab}_flien_3y5y',
            f'{ctab}a568': f'{ctab}_flien_5y15y',
            f'{ctab}a569': f'{ctab}_flien_ge15y',
            f'{ctab}a570': f'{ctab}_othll_le3m',
            f'{ctab}a571': f'{ctab}_othll_3my1y',
            f'{ctab}a572': f'{ctab}_othll_1y3y',
            f'{ctab}a573': f'{ctab}_othll_3y5y',
            f'{ctab}a574': f'{ctab}_othll_5y15y',
            f'{ctab}a575': f'{ctab}_othll_ge15y',
            f'{ctab}2200': f'{ctab}_deposits',
            f'{ctab}2170': f'{ctab}_assets',
            f'{ctab}b993': f'{ctab}_repo_liab_ff',
            f'{ctab}b995': f'{ctab}_repo_liab_oth',
            f'{ctab}3190': f'{ctab}_oth_borr_money',
            f'{ctab}3200': f'{ctab}_sub_debt',
            f'{ctab}2213': f'{ctab}_liab_fbk_trans',
            f'{ctab}2236': f'{ctab}_liab_fbk_ntrans',
            f'{ctab}2216': f'{ctab}_liab_foff_trans',
            f'{ctab}2377': f'{ctab}_liab_foff_ntrans',
            }
        return allvars

    def variables_by_table(self, conn):
        tabnames = ['wrds_call_rcon_1', 'wrds_call_rcon_2',
                    'wrds_call_rcfd_1', 'wrds_call_rcfd_2']
        tabs = dict()
        for tabname in tabnames:
            variables = conn.get_table(library='bank', table=tabname,
                                       obs=1).columns.values
            tabs.update({tabname: list(variables)})

        self.variables_table = tabs
