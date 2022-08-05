# imports
import argparse
import json
import logging

import pandas as pd
from evidently.model_profile import Profile
from evidently.model_profile.sections import (CatTargetDriftProfileSection,
                                              DataDriftProfileSection)
from evidently.pipeline.column_mapping import ColumnMapping
from opencensus.ext.azure.log_exporter import AzureLogHandler

from constants import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES

# Configure logger
LOGGER = logging.getLogger('root')
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(AzureLogHandler())


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser("drift")

    # add arguments
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--reference_data_dir", type=str)
    parser.add_argument("--target_data_dir", type=str)

    # parse args
    args = parser.parse_args()

    return args


def process_data_drift_output(data_drift_metrics):
    # define overall data drift metrics table
    overall_data_drift_metrics = {
        "n_features": data_drift_metrics["n_features"],
        "n_drifted_features": data_drift_metrics["n_drifted_features"],
        "share_drifted_features": data_drift_metrics["share_drifted_features"],
        "dataset_drift": data_drift_metrics["dataset_drift"]
    }

    # define feature data drift metrics table
    feature_data_drift_metrics = []

    # preprocess json output
    for feature in FEATURES:
        feature_data_drift_metrics.append({
            "feature_name": feature,
            "drift_score": data_drift_metrics[feature]["drift_score"],
            "drift_detected": data_drift_metrics[feature]["drift_detected"],
            "feature_type": data_drift_metrics[feature]["feature_type"],
            "stattest_name": data_drift_metrics[feature]["stattest_name"],
        })

    return overall_data_drift_metrics, feature_data_drift_metrics


def main(args):
    try:
        # load datasets
        reference_df = pd.read_csv(f"{args.reference_data_dir}/data.csv")
        target_df = pd.read_csv(f"{args.target_data_dir}/data.csv")

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
            sections=[DataDriftProfileSection(),
                      CatTargetDriftProfileSection()])
        data_drift_profile.calculate(
            reference_df, target_df, column_mapping=column_mapping)

        # convert drift  profile to json
        data_drift_profile_json = json.loads(data_drift_profile.json())

        # process data drift output
        overall_data_drift_metrics, feature_data_drift_metrics = process_data_drift_output(
            data_drift_profile_json["data_drift"]["data"]["metrics"])

        print("Overall data drift metrics:", overall_data_drift_metrics)
        print("Feature data drift metrics:", feature_data_drift_metrics)

        # Log overall drift metrics
        LOGGER.info(json.dumps({
            "model_name": args.model_name,
            "type": "OverallDriftMetrics",
            "data": overall_data_drift_metrics
        }))

        # Log feature drift metrics
        LOGGER.info(json.dumps({
            "model_name": args.model_name,
            "type": "FeatureDriftMetrics",
            "data": feature_data_drift_metrics
        }))

    except Exception as e:
        LOGGER.error(json.dumps({
            "model_name": args.model_name,
            "type": "Exception",
            "error": e
        }), exc_info=e)


if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main
    main(args)
