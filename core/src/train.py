# imports
import argparse
from distutils.dir_util import copy_tree

import mlflow
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET


def main(args):
    # enable auto logging
    mlflow.autolog()

    # setup parameters
    params = {
        "n_estimators": args.n_estimators,
        "max_depth": args.max_depth,
        "criterion": args.criterion,
        "random_state": args.random_state,
    }

    # read in data
    df = pd.read_csv(f"{args.prepared_data_dir}/data.csv")

    # split into train and test datasets
    X_train, X_test, y_train, y_test = train_test_split(
        df[CATEGORICAL_FEATURES + NUMERIC_FEATURES],
        df[TARGET],
        test_size=0.20,
        random_state=args.random_state
    )

    # build models
    classification_model = train_classification_model(
        params, X_train, X_test, y_train, y_test)

    # save models
    mlflow.sklearn.save_model(classification_model, "model")

    # copy model artifact to directory
    to_directory = args.model_output
    copy_tree("model", f"{to_directory}/model")


def train_classification_model(params, X_train, X_test, y_train, y_test):
    # train model
    estimator = make_classifer_pipeline(params)
    estimator = estimator.fit(X_train, y_train.values.ravel())

    # evaluate model performance
    metrics = mlflow.sklearn.eval_and_log_metrics(
        estimator, X_test, y_test.values.ravel(), prefix="validation_")
    mlflow.log_metrics(metrics)

    return estimator


def make_classifer_pipeline(params):
    # categorical features transformations
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("ohe", OneHotEncoder())]
    )

    # numeric features transformations
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median"))]
    )

    # preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )

    # model training pipeline
    classifer_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(**params, n_jobs=-1))
    ])

    return classifer_pipeline


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser("train")

    # add arguments
    parser.add_argument("--prepared_data_dir", type=str)
    parser.add_argument("--model_output", type=str)
    parser.add_argument(
        "--random_state", type=lambda x: int(float(x)), default=24)
    parser.add_argument(
        "--n_estimators", type=lambda x: int(float(x)), default=500)
    parser.add_argument(
        "--max_depth", type=lambda x: int(float(x)), default=10)
    parser.add_argument("--criterion", type=str, default="gini")

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
