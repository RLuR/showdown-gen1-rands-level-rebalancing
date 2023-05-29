import pandas as pd
from scipy.stats import binomtest
def main():
    data: pd.DataFrame = pd.read_csv("data.txt", sep="\t")
    data['Win %'] = round(data['Win %'].str.rstrip('%').astype('float') / 100.0, 4)

    data = data.apply(lambda row: calculate_generally(row, three_max=False), axis=1)
    data = data.apply(lambda row: calculate_easier_one_level_changes(row), axis=1)

    data = sort(data)
    data.to_csv("result.csv", index=False)

def sort(df):
    upper_half = df[df["Win %"]>0.5]
    lower_half = df[df["Win %"]<=0.5]

    upper_half = upper_half.sort_values(["levelchange", "next_p"], ascending=[True,True])
    lower_half = lower_half.sort_values(["levelchange", "next_p"], ascending=[True,False])

    return pd.concat([upper_half, lower_half], sort=False, ignore_index=True)


def calculate_generally(row, three_max):
    def cutoff_generator():
        cutoff=0
        while True:
            cutoff = cutoff + 0.015
            yield cutoff

    if three_max:
        cutoffs = [0.015, 0.03, 0.045]
    else:
        cutoffs = cutoff_generator()
    p = 0.01
    positive = row["Win %"] > 0.5
    change = 0

    for cutoff in cutoffs:
        if positive:
            significance = binomtest(k=row["Raw wins"], n=row["Times generated"], p=0.5+cutoff, alternative="greater")
        else:
            significance = binomtest(k=row["Raw wins"], n=row["Times generated"], p=0.5-cutoff, alternative="less")

        if significance.pvalue < p:
            change=change-1 if positive else change+1
        else:
            break
    row["levelchange"] = change
    row["next_p"] = round(significance.pvalue,4)
    return row

def calculate_easier_one_level_changes(row):
    # For changes of a single level less strict requirements are given,
    # either 1% deviation with p = 0.01 or 1,5% deviation with p = 0.05

    if row["levelchange"] != 0:
        return row

    positive = row["Win %"] > 0.5
    change = 0
    if positive:
        significance = binomtest(k=row["Raw wins"], n=row["Times generated"], p=0.51, alternative="greater")
    else:
        significance = binomtest(k=row["Raw wins"], n=row["Times generated"], p=0.49, alternative="less")

    if significance.pvalue < 0.01:
        change = change - 1 if positive else change + 1
        row["levelchange"] = change
        return row

    if positive:
        significance = binomtest(k=row["Raw wins"], n=row["Times generated"], p=0.515, alternative="greater")
    else:
        significance = binomtest(k=row["Raw wins"], n=row["Times generated"], p=0.485, alternative="less")

    if significance.pvalue < 0.05:
        change = change - 1 if positive else change + 1
        row["levelchange"] = change
        return row

    return row


if __name__ == "__main__":
    main()