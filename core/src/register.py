"""Script to register a machine learning model to mlflow"""
from argparse import ArgumentParser, Namespace

import mlflow
import pandas as pd
from constants import FEATURES
from mlflow.models.signature import infer_signature


def main(args: Namespace) -> None:
    """Register mlflow model in model registry"""
    # load model
    model = mlflow.sklearn.load_model(f"{args.model_output}/model")

    # create model signature
    df_train = pd.read_csv(f"{args.prepared_data_dir}/train.csv")
    model_input = df_train[FEATURES].head()
    model_output = model.predict(model_input)
    model_signature = infer_signature(model_input, model_output)

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        conda_env=args.conda_env,
        signature=model_signature,
        registered_model_name=args.model_name,
    )


def parse_args() -> Namespace:
    """Parse command line arguments"""
    # setup arg parser
    parser = ArgumentParser("register")

    # add arguments
    parser.add_argument("--prepared_data_dir", type=str)
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--model_output", type=str)
    parser.add_argument("--conda_env", type=str)

    # parse args
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    with mlflow.start_run():
        main(parse_args())
