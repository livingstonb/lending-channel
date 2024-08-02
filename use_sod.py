from mod_bank import sod

def use_sod():
    df = sod.clean("data/sod_2022.csv")
    return df


if __name__ == "__main__":
    df = use_sod()