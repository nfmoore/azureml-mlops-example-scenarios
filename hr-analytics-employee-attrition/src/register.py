# imports
import argparse
import os

import mlflow

from constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES
from pyfunc_model import EmployeeAttritionModel


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser("register")

    # add arguments
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
    # model_input = df_attrition[columns_categorical + columns_numeric].head()
    # model_output = model_artifact.predict(context, model_input)
    # model_output_formatted = np.array(list(model_output.items()), dtype=object)
    # signature = infer_signature(model_input, model_output_formatted)

    # load model and log to job
    # model = mlflow.sklearn.load_model(args.model_artifact)
    # mlflow.sklearn.log_model(model, args.model_name)

    # mlflow_conda_env = {
    #     'name': args.model_name,
    #     'channels': ["defaults"],
    #     'dependencies': [
    #         "python=3.8.10",
    #         {
    #             "pip": [
    #                 "alibi-detect==0.8.1",
    #                 "mlflow-skinny==1.21.0",
    #                 "scikit-learn",
    #                 "numpy==1.19.2",
    #                 "pandas==1.2.4",
    #                 "scikit-learn==0.24.1"
    #             ]
    #         }
    #     ]
    # }

    mlflow.pyfunc.log_model(
        artifact_path=args.model_name,
        python_model=model_artifact,
        artifacts=artifacts,
        conda_env="environments/score.yml",
        code_path=["src/pyfunc_model.py"]
        # signature=signature
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
