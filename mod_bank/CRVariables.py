import pandas as pd

class CRVariables(object):

    def __init__(self, dates):
        self.variables_table = None

    def variables_by_table(self, conn):
        tabnames = ['wrds_call_rcon_1', 'wrds_call_rcon_2',
                    'wrds_call_rcfd_1', 'wrds_call_rcfd_2']
        tabs = dict()
        for tabname in tabnames:
            variables = conn.get_table(library='bank', table=tabname,
                                       obs=1).columns.values
            tabs.update({tabname: list(variables)})

        self.variables_table = tabs
