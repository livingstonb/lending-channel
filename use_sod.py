from mod_bank import sod


def use_sod(year):
    sod_filepath = f"data/sod_06_{year}.csv"
    links_savepath = f"temp/sod_bank_bhc_links_{year}.csv"
    df = sod.read(sod_filepath, save_links_path=links_savepath)

    df_bhc = sod.aggregate_to_bhc(df, f"temp/sod_bhc_level_{year}.csv")
    df_bank = sod.aggregate_to_bank(df, f"temp/sod_bank_level_{year}.csv")

if __name__ == "__main__":
    for year in [2021]:
        use_sod(year)
