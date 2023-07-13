"""Script to develop a machine learning model from input data"""
from argparse import ArgumentParser, Namespace
from distutils.dir_util import copy_tree
from typing import Dict, Union

import mlflow
import pandas as pd
from constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def main(args: Namespace) -> None:
    """Develop an sklearn model and use mlflow to log metrics"""
    # enable auto logging
    mlflow.sklearn.autolog()

    # setup parameters
    params = {
        "n_estimators": args.n_estimators,
        "max_depth": args.max_depth,
        "criterion": args.criterion,
        "random_state": args.random_state,
    }

    # read data
    df_train = pd.read_csv(f"{args.prepared_data_dir}/train.csv")
    df_test = pd.read_csv(f"{args.prepared_data_dir}/test.csv")

    # seperate features and target variables
    x_train, y_train = (
        df_train[CATEGORICAL_FEATURES + NUMERIC_FEATURES],
        df_train[TARGET],
    )
    x_test, y_test = df_test[CATEGORICAL_FEATURES + NUMERIC_FEATURES], df_test[TARGET]

    # train model
    estimator = make_classifer_pipeline(params)
    estimator.fit(x_train, y_train.values.ravel())

    # calculate evaluation metrics
    y_pred = estimator.predict(x_test)
    validation_accuracy_score = accuracy_score(y_test.values.ravel(), y_pred)
    validation_roc_auc_score = roc_auc_score(y_test.values.ravel(), y_pred)
    validation_f1_score = f1_score(y_test.values.ravel(), y_pred)
    validation_precision_score = precision_score(y_test.values.ravel(), y_pred)
    validation_recall_score = recall_score(y_test.values.ravel(), y_pred)

    # log evaluation metrics
    mlflow.log_metric("validation_accuracy_score", validation_accuracy_score)
    mlflow.log_metric("validation_roc_auc_score", validation_roc_auc_score)
    mlflow.log_metric("validation_f1_score", validation_f1_score)
    mlflow.log_metric("validation_precision_score", validation_precision_score)
    mlflow.log_metric("validation_recall_score", validation_recall_score)

    # save models
    mlflow.sklearn.save_model(estimator, "model")

    # copy model artifact to directory
    to_directory = args.model_output
    copy_tree("model", f"{to_directory}/model")


def make_classifer_pipeline(params: Dict[str, Union[str, int]]) -> Pipeline:
    """Create sklearn pipeline to apply transforms and a final estimator"""
    # categorical features transformations
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            (
                "ohe",
                OneHotEncoder(
                    handle_unknown="ignore",
                ),
            ),
        ]
    )

    # numeric features transformations
    numeric_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median"))]
    )

    # preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )

    # model training pipeline
    classifer_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(**params, n_jobs=-1)),
        ]
    )

    return classifer_pipeline


def parse_args() -> Namespace:
    """Parse command line arguments"""
    # setup arg parser
    parser = ArgumentParser("train")

    # add arguments
    parser.add_argument("--prepared_data_dir", type=str)
    parser.add_argument("--model_output", type=str)
    parser.add_argument("--random_state", type=lambda x: int(float(x)), default=24)
    parser.add_argument("--n_estimators", type=lambda x: int(float(x)), default=500)
    parser.add_argument("--max_depth", type=lambda x: int(float(x)), default=10)
    parser.add_argument("--criterion", type=str, default="gini")

    # parse args
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    with mlflow.start_run():
        main(parse_args())
