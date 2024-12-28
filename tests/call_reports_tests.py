from code.mod_bank import call_reports


def assign_topid_up(df):
    date = 20221231
    attr_files = ['data/NIC_attributes_closed.csv', 'data/NIC_attributes_active.csv']
    bhcids = call_reports.assign_topid_up(df, 'data/NIC_relationships.csv', attr_files, date)