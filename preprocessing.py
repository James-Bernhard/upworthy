"""
Prepare Upworthy data for analysis
by James Bernhard
2023-11-16
"""

import pandas as pd
import numpy as np
from pathlib import Path
from nltk.sentiment import SentimentIntensityAnalyzer
import itertools
import re
import random
import scipy.special
import statsmodels.stats.proportion

input_file = Path("upworthy-archive-confirmatory-packages-03.12.2020.csv")
output_file = Path("df_sentiments.csv")

def compute_nltk_sentiments(headlines: pd.Series) -> pd.Series:
    """
    Put in a sentiment score column, based on nltk sentiment analyzer.
    :param headlines: Series of headlines from Upworthy data
    :return: Series of new sentiments column in it.
    """
    sia = SentimentIntensityAnalyzer()
    sentiments = np.zeros(len(headlines))
    for i in range(len(sentiments)):
        sentiments[i] = sia.polarity_scores(headlines.iloc[i])["compound"]
    return pd.Series(sentiments, index=headlines.index)


def upworthy_to_sentiment(input_file: Path, sentiment_file: Path, remove_zeros: bool = True) -> None:
    """
    Make a sentiment spreadsheet given an Upworthy data file. Removes zero CTR rows, in order to compute logit CTR.
    :param input_file: file of Upworthy data to input data from
    :param sentiment_file: file to output a sentiment spreadsheet (csv file) to
    :return:
    """
    print("Assembling sentiment data file " + sentiment_file.name + "...")
    temp_df = (
        pd.read_csv(input_file, low_memory=False)
        [["clickability_test_id", "headline", "clicks", "impressions", "test_week"]]
        .groupby(by=["clickability_test_id", "headline", "test_week"])[["clicks", "impressions"]]
        .apply(lambda x: x.astype(float).sum()).reset_index()
    )

    # if requested, get rid of those with 0 clicks
    if remove_zeros:
        temp_df = temp_df[temp_df["clicks"] > 0]

    # keep only those with two or more of the same headline
    counts = temp_df["clickability_test_id"].value_counts()
    temp_df = temp_df[temp_df["clickability_test_id"].isin(counts.index[counts.ge(2)])]

    these_tag = re.compile(r"\bthese\b", re.IGNORECASE)
    this_tag = re.compile(r"\bthis\b", re.IGNORECASE)
    that_tag = re.compile(r"\bthat\b", re.IGNORECASE)
    those_tag = re.compile(r"\bthose\b", re.IGNORECASE)
    i_tag = re.compile(r"\bi\b", re.IGNORECASE)
    me_tag = re.compile(r"\bme\b", re.IGNORECASE)
    we_tag = re.compile(r"\bwe\b", re.IGNORECASE)
    us_tag = re.compile(r"\bus\b", re.IGNORECASE)
    you_tag = re.compile(r"\byou\b", re.IGNORECASE)
    he_she_tag = re.compile(r"\bhe\b|\bshe\b", re.IGNORECASE)
    her_him_tag = re.compile(r"\bher\b|\bhim\b", re.IGNORECASE)
    it_tag = re.compile(r"\bit\b", re.IGNORECASE)
    they_tag = re.compile(r"\bthey\b", re.IGNORECASE)
    them_tag = re.compile(r"\bthem\b", re.IGNORECASE)

    temp_df = temp_df.assign(ctr=temp_df["clicks"] / temp_df["impressions"],
                             logit_ctr=lambda x: scipy.special.logit(x["ctr"]),
                             nltk_sentiment=compute_nltk_sentiments(temp_df["headline"]),
                             exclamation=temp_df["headline"].str.contains("!"),
                             question=temp_df["headline"].str.contains("\\?"),
                             headline_length=pd.Series(list(map(len, temp_df["headline"])), index=temp_df.index),
                             caps=temp_df["headline"].str.contains(r"\b[A-Z][A-Z]+\b"),
                             these=temp_df["headline"].str.contains(these_tag),
                             this=temp_df["headline"].str.contains(this_tag),
                             that=temp_df["headline"].str.contains(that_tag),
                             those=temp_df["headline"].str.contains(those_tag),
                             i=temp_df["headline"].str.contains(i_tag),
                             me=temp_df["headline"].str.contains(me_tag),
                             we=temp_df["headline"].str.contains(we_tag),
                             us=temp_df["headline"].str.contains(us_tag),
                             you=temp_df["headline"].str.contains(you_tag),
                             he_she=temp_df["headline"].str.contains(he_she_tag),
                             her_him=temp_df["headline"].str.contains(her_him_tag),
                             it=temp_df["headline"].str.contains(it_tag),
                             they=temp_df["headline"].str.contains(they_tag),
                             them=temp_df["headline"].str.contains(them_tag)
                             )
    temp_df.to_csv(sentiment_file, index=False)
    print("Sentiment data file " + sentiment_file.name + " assembled.\n")


# compile data file for analysis
upworthy_to_sentiment(input_file=input_file, sentiment_file=output_file)


