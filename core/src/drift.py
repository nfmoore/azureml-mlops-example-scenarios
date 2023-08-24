"""Script to calculate data drift metrics for a baseline and target dataset"""
import json
import logging
from argparse import ArgumentParser, Namespace
from typing import Dict, Tuple

import mltable
from constants import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES
from evidently.model_profile import Profile
from evidently.model_profile.sections import (
    CatTargetDriftProfileSection,
    DataDriftProfileSection,
)
from evidently.pipeline.column_mapping import ColumnMapping
from opencensus.ext.azure.log_exporter import AzureLogHandler


def main(args: Namespace, log: logging.Logger) -> None:
    """Calculate data drift metrics and send to app insights"""
    try:
        # load datasets
        reference_tbl = mltable.load(args.reference_data)
        target_tbl = mltable.load(args.target_data)

        reference_df = reference_tbl.to_pandas_dataframe()
        target_df = target_tbl.to_pandas_dataframe()

        # change data types of features
        reference_df[CATEGORICAL_FEATURES] = reference_df[CATEGORICAL_FEATURES].astype(
            "str"
        )
        reference_df[NUMERIC_FEATURES] = reference_df[NUMERIC_FEATURES].astype("float")
        target_df[CATEGORICAL_FEATURES] = target_df[CATEGORICAL_FEATURES].astype("str")
        target_df[NUMERIC_FEATURES] = target_df[NUMERIC_FEATURES].astype("float")

        # define column mapping for evidently
        column_mapping = ColumnMapping()
        column_mapping.target = None
        column_mapping.prediction = None
        column_mapping.id = None
        column_mapping.datetime = None
        column_mapping.numerical_features = NUMERIC_FEATURES
        column_mapping.categorical_features = CATEGORICAL_FEATURES

        # generate data drift profile
        data_drift_profile = Profile(
            sections=[DataDriftProfileSection(), CatTargetDriftProfileSection()]
        )
        data_drift_profile.calculate(
            reference_df, target_df, column_mapping=column_mapping
        )

        # convert drift  profile to json
        data_drift_profile_json = json.loads(data_drift_profile.json())
        print(data_drift_profile_json)

        # process data drift output
        overall_metrics, feature_metrics = process_data_drift_output(
            data_drift_profile_json["data_drift"]["data"]["metrics"]
        )

        print("Overall data drift metrics:", overall_metrics)
        print("Feature data drift metrics:", feature_metrics)

        # Log overall drift metrics
        log.info(
            json.dumps(
                {
                    "model_name": args.model_name,
                    "type": "OverallDriftMetrics",
                    "data": overall_metrics,
                }
            )
        )

        # Log feature drift metrics
        log.info(
            json.dumps(
                {
                    "model_name": args.model_name,
                    "type": "FeatureDriftMetrics",
                    "data": feature_metrics,
                }
            )
        )

    except Exception as error:
        log.error(
            json.dumps(
                {"model_name": args.model_name, "type": "Exception", "error": error}
            ),
            exc_info=error,
        )


def process_data_drift_output(data_drift_metrics: Dict) -> Tuple[Dict, Dict]:
    """Preprocess data drift output from evidently"""
    # define overall data drift metrics table
    overall_metrics = {
        "n_features": data_drift_metrics["n_features"],
        "n_drifted_features": data_drift_metrics["n_drifted_features"],
        "share_drifted_features": data_drift_metrics["share_drifted_features"],
        "dataset_drift": data_drift_metrics["dataset_drift"],
    }

    # define feature data drift metrics table
    feature_metrics = []

    # preprocess json output
    for feature in FEATURES:
        feature_metrics.append(
            {
                "feature_name": feature,
                "drift_score": data_drift_metrics[feature]["drift_score"],
                "drift_detected": data_drift_metrics[feature]["drift_detected"],
                "feature_type": data_drift_metrics[feature]["feature_type"],
                "stattest_name": data_drift_metrics[feature]["stattest_name"],
            }
        )

    return overall_metrics, feature_metrics


def parse_args() -> Namespace:
    """Parse command line arguments"""
    # setup arg parser
    parser = ArgumentParser("drift")

    # add arguments
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--reference_data", type=str)
    parser.add_argument("--target_data", type=str)

    # parse args
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    # parse script arguments
    script_arguments = parse_args()

    # Configure logger
    logger = logging.getLogger("root")
    logger.setLevel(logging.INFO)
    logger.addHandler(AzureLogHandler())

    main(script_arguments, logger)
