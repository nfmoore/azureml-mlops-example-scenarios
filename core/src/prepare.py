# imports
from argparse import ArgumentParser, Namespace
from typing import Tuple

import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split

from constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET


def main(args: Namespace) -> None:
    # process data
    df = pd.read_csv(args.curated_dataset)
    df_train, df_test = prepare_data(df, args.random_state)

    df_train.to_csv(f"{args.prepared_data_dir}/train.csv", index=False)
    df_test.to_csv(f"{args.prepared_data_dir}/test.csv", index=False)


def prepare_data(df: pd.DataFrame, random_state: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # change data types of features
    df[TARGET] = df[TARGET].replace(
        {"Yes": 1, "No": 0}).astype("str")
    df[CATEGORICAL_FEATURES] = df[CATEGORICAL_FEATURES].astype(
        "str")
    df[NUMERIC_FEATURES] = df[NUMERIC_FEATURES].astype("float")

    # split into train and test datasets
    df_train, df_test = train_test_split(
        df[CATEGORICAL_FEATURES + NUMERIC_FEATURES + TARGET],
        test_size=0.20,
        random_state=random_state
    )

    return df_train, df_test


def parse_args() -> Namespace:
    # setup arg parser
    parser = ArgumentParser("prepare")

    # add arguments
    parser.add_argument("--curated_dataset", type=str)
    parser.add_argument("--prepared_data_dir", type=str)
    parser.add_argument(
        "--random_state", type=lambda x: int(float(x)), default=24)

    # parse args
    args = parser.parse_args()

    return args


# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    with mlflow.start_run():
        main(args)
