"""Script for an azureml online deployment"""
import json
import logging
import os
import uuid
from typing import Dict, List

import mlflow
import pandas as pd
from constants import INPUT_SAMPLE, OUTPUT_SAMPLE
from inference_schema.parameter_types.standard_py_parameter_type import \
    StandardPythonParameterType
from inference_schema.schema_decorators import input_schema, output_schema

# define global variables
SERVICE_NAME = None
MODEL = None
LOGGER = logging.getLogger('root')


def init() -> None:
    """Startup event handler to load an MLFLow model."""
    global SERVICE_NAME, MODEL

    # Load MLFlow model
    SERVICE_NAME = "online/" + os.getenv("AZUREML_MODEL_DIR").split('/', 4)[-1]
    MODEL = mlflow.sklearn.load_model(
        os.getenv("AZUREML_MODEL_DIR") + "/model")

    # Log output data
    LOGGER.info(json.dumps({
        "service_name": SERVICE_NAME,
        "type": "InitializeService",
    }))


@input_schema("data", StandardPythonParameterType(INPUT_SAMPLE))
@output_schema(StandardPythonParameterType(OUTPUT_SAMPLE))
def run(data: List[Dict]) -> str:
    """Perform scoring for every invocation of the endpoint"""

    try:
        # Define UUID for the request
        request_id = uuid.uuid4().hex

        # Append datetime column to predictions
        input_df = pd.DataFrame(data)

        # Preprocess payload and get model prediction
        model_output = MODEL.predict_proba(input_df)[:, 1].tolist()

        # Log input data
        LOGGER.info(json.dumps({
            "service_name": SERVICE_NAME,
            "type": "InputData",
            "request_id": request_id,
            "data": input_df.to_json(orient='records'),
        }))

        # Log output data
        LOGGER.info(json.dumps({
            "service_name": SERVICE_NAME,
            "type": "OutputData",
            "request_id": request_id,
            "data": model_output
        }))

        # Make response payload
        response_payload = json.dumps(
            {"predictions": model_output})

        return response_payload

    except Exception as error:
        LOGGER.error(json.dumps({
            "service_name": SERVICE_NAME,
            "type": "Exception",
            "request_id": request_id,
            "error": error
        }), exc_info=error)
