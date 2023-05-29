import pandas as pd
from scipy.stats import binomtest
def main():
    data: pd.DataFrame = pd.read_csv("data.txt", sep="\t")
    data['Win %'] = data['Win %'].str.rstrip('%').astype('float') / 100.0
    data = data.apply(lambda row: calculate(row), axis=1)

    data = sort(data)
    data.to_csv("result.csv", index=False)

def sort(df):
    upper_half = df[df["Win %"]>0.5]
    lower_half = df[df["Win %"]<=0.5]

    upper_half = upper_half.sort_values(["levelchange", "next_p"], ascending=[True,True])
    lower_half = lower_half.sort_values(["levelchange", "next_p"], ascending=[True,False])

    return pd.concat([upper_half, lower_half], sort=False, ignore_index=True)


def calculate(row):
    cutoffs = [0.015, 0.03, 0.045]
    p = 0.05
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
    row["next_p"] = significance.pvalue
    return row

if __name__ == "__main__":
    main()