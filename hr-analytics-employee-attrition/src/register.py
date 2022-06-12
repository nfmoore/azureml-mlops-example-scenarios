# imports
import argparse

import mlflow
import pandas as pd
from mlflow.models.signature import infer_signature

from constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES
from pyfunc_model import EmployeeAttritionModel


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser("register")

    # add arguments
    parser.add_argument("--prepared_data_dir", type=str)
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--model_output", type=str)

    # parse args
    args = parser.parse_args()

    return args


def main(args):
    # retreive active run
    run_id = mlflow.active_run().info.run_id

    # create instance of model
    model_artifact = EmployeeAttritionModel(
        columns_categorical=CATEGORICAL_FEATURES,
        columns_numeric=NUMERIC_FEATURES
    )

    # define context and load models
    artifacts_path = args.model_output
    artifacts = {"artifacts_path": artifacts_path}
    # context = PythonModelContext(artifacts)
    # model_artifact.load_context(context)

    # create model signature
    df = pd.read_csv(f"{args.prepared_data_dir}/data.csv")
    model_input = df[CATEGORICAL_FEATURES + NUMERIC_FEATURES].head()
    model_signature = infer_signature(model_input)

    mlflow.pyfunc.log_model(
        artifact_path=args.model_name,
        python_model=model_artifact,
        artifacts=artifacts,
        conda_env="environments/score.yml",
        code_path=["src/pyfunc_model.py"],
        signature=model_signature
    )

    # register model
    model_uri = f'runs:/{run_id}/{args.model_name}'
    mlflow.register_model(model_uri, args.model_name)


if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main
    with mlflow.start_run():
        main(args)
