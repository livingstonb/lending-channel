from mod_bank import sod

def use_sod():
    sod_filepath = "data/sod_2022.csv"
    links_savepath = "temp/sod_bank_bhc_links.csv"
    df = sod.clean(sod_filepath, links_savepath)
    return df


if __name__ == "__main__":
    df = use_sod()