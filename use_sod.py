from banking_procs import sod_fns


def use_sod():
    df = sod_fns.clean("data/sod_2022.csv")
    return df


if __name__ == "__main__":
    df = use_sod()