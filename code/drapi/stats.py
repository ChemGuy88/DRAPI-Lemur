"""
Statistics functions
"""

import pandas as pd


def fiveNumberSummary(series: pd.Series, more=True) -> pd.Series:
    """
    """
    x1 = series.min()
    x2 = series.quantile(.25)
    x3 = series.quantile(.50)
    y3 = series.mean()
    x4 = series.quantile(.75)
    x5 = series.quantile(.90)
    x6 = series.quantile(.95)
    x7 = series.quantile(.99)
    x8 = series.quantile(.999)
    x9 = series.max()
    sumStatsValues1 = [x1, x2, x3, x4, x5, x6, x7, x8, x9]
    sumStatsValues2 = ["", "", y3, "", "", "", "", "", ""]
    fiveNumberSummaryColumns = ["min",
                                "25th ptile",
                                "median",
                                "75th ptile",
                                "max"]
    sumStatsNames1 = ["min",
                      "25th ptile",
                      "median",
                      "75th ptile",
                      "90th ptile",
                      "95th ptile",
                      "99th ptile",
                      "99.9th ptile",
                      "max"]
    sumStatsNames2 = ["",
                      "",
                      "mean",
                      "",
                      "",
                      "",
                      "",
                      "",
                      ""]
    summaryStats = pd.DataFrame([sumStatsNames1, sumStatsValues1, sumStatsValues2, sumStatsNames2]).T
    summaryStats.columns = ["1", "Percentiles", "Means", "2"]
    summaryStats.index = range(1, len(summaryStats) + 1)
    summaryStats[["Percentiles", "Means"]] = summaryStats[["Percentiles", "Means"]].applymap(lambda el: "" if isinstance(el, str) else f"{int(el):,}")

    if more:
        pass
    else:
        summaryStats = summaryStats.set_index("1")
        colsToDrop = [col for col in summaryStats.T.columns if col not in fiveNumberSummaryColumns]
        summaryStats = summaryStats.drop(labels=colsToDrop)
        summaryStats = summaryStats.reset_index()

    summaryStats = summaryStats.rename(columns={"1": "", "2": ""})

    return summaryStats
