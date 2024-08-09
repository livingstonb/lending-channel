from mod_bank import sod


def use_sod():
    sod_filepath = "data/sod_2022.csv"
    links_savepath = "temp/sod_bank_bhc_links.csv"
    df = sod.read(sod_filepath, save_links_path=links_savepath)

    sod_output_savepath = "temp/sod_nbranches.csv"
    df = sod.aggregate(df, sod_output_savepath)
    return df


if __name__ == "__main__":
    df = use_sod()