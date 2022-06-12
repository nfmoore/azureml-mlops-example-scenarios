# imports
import argparse
import glob
from distutils.dir_util import copy_tree

import mlflow
import pandas as pd

from constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET_FEATURE


def main(args):
    # read in data
    files = glob.glob(f'{args.raw_data_dir}/*.csv')
    df = pd.concat([pd.read_csv(f) for f in files])

    # process data
    df = process_data(df)
    df.to_csv(f"{args.prepared_data_dir}/data.csv", index=False)


def process_data(df):

    # convert values of `Over18` feature for consistancy
    df["Over18"] = df["Over18"].replace(
        {"Y": "Yes", "N": "No"})

    # change data types of features
    df[TARGET_FEATURE] = df[TARGET_FEATURE].replace(
        {"Yes": 1, "No": 0}).astype("str")
    df[CATEGORICAL_FEATURES] = df[CATEGORICAL_FEATURES].astype(
        "str")
    df[NUMERIC_FEATURES] = df[NUMERIC_FEATURES].astype("float")

    # return data
    return df


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser("prepare")

    # add arguments
    parser.add_argument("--raw_data_dir", type=str)
    parser.add_argument("--prepared_data_dir", type=str)

    # parse args
    args = parser.parse_args()

    # return args
    return args


# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    with mlflow.start_run():
        main(args)
