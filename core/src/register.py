# imports
from argparse import ArgumentParser, Namespace

import mlflow
import pandas as pd
from mlflow.models.signature import infer_signature

from constants import FEATURES


def main(args: Namespace) -> None:
    # load model
    model = mlflow.sklearn.load_model(f"{args.model_output}/model")

    # create model signature
    df = pd.read_csv(f"{args.prepared_data_dir}/train.csv")
    model_input = df[FEATURES].head()
    model_output = model.predict(model_input)
    model_signature = infer_signature(model_input, model_output)

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        conda_env=args.conda_env,
        signature=model_signature,
        registered_model_name=args.model_name
    )


def parse_args() -> Namespace:
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
    # parse args
    args = parse_args()

    # run main
    with mlflow.start_run():
        main(args)
