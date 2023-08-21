"""Script to run data quality tests"""
from argparse import ArgumentParser, Namespace

import mlflow
import pandas as pd
from constants import CATEGORICAL_FEATURES, TARGET
from deepchecks.tabular import Dataset
from deepchecks.tabular.suites import data_integrity, train_test_validation


def main(args: Namespace) -> None:
    """Generate data quality report"""
    # read data
    df_train = pd.read_csv(f"{args.prepared_data_dir}/train.csv")
    df_test = pd.read_csv(f"{args.prepared_data_dir}/test.csv")

    # initiate dataset objects
    dataset_train = Dataset(
        df_train, cat_features=CATEGORICAL_FEATURES, label=TARGET[0]
    )
    dataset_test = Dataset(df_test, cat_features=CATEGORICAL_FEATURES, label=TARGET[0])

    # run data integrity suite
    data_integrity_suite = data_integrity()
    data_integrity_result = data_integrity_suite.run(dataset_train)

    # run train test validation suite
    train_test_validation_suite = train_test_validation()
    train_test_validation_result = train_test_validation_suite.run(
        dataset_train, dataset_test
    )

    # display test results
    print("data integrity suite result:", data_integrity_result.passed())
    print("train test validation suite result:", train_test_validation_result.passed())

    # save html output
    data_integrity_result.save_as_html("./data_integrity.html")
    train_test_validation_result.save_as_html("./train_test_validation.html")

    # log html output
    mlflow.log_artifact("./data_integrity.html")
    mlflow.log_artifact("./train_test_validation.html")


def parse_args() -> Namespace:
    """Parse command line arguments"""
    # setup arg parser
    parser = ArgumentParser("data_quality")

    # add arguments
    parser.add_argument("--prepared_data_dir", type=str)

    # parse args
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    with mlflow.start_run():
        main(parse_args())
