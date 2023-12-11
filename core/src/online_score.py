"""Script for an azureml online deployment"""
import json
import logging
import os
import uuid
from typing import Dict, List

import mlflow
import pandas as pd
from azureml.ai.monitoring import Collector
from constants import INPUT_SAMPLE, OUTPUT_SAMPLE
from inference_schema.parameter_types.standard_py_parameter_type import \
    StandardPythonParameterType
from inference_schema.schema_decorators import input_schema, output_schema

# define global variables
SERVICE_NAME = None
MODEL = None
LOGGER = logging.getLogger("root")
INPUTS_COLLECTOR = None
OUTPUTS_COLLECTOR = None
INPUTS_OUTPUTS_COLLECTOR = None

def init() -> None:
    """Startup event handler to load an MLFLow model."""
    global SERVICE_NAME, MODEL, INPUTS_COLLECTOR, OUTPUTS_COLLECTOR, INPUTS_OUTPUTS_COLLECTOR

    # instantiate collectors
    INPUTS_COLLECTOR = Collector(name="model_inputs")
    OUTPUTS_COLLECTOR = Collector(name="model_outputs")
    INPUTS_OUTPUTS_COLLECTOR = Collector(name="model_inputs_outputs")

    # Load MLFlow model
    SERVICE_NAME = "online/" + os.getenv("AZUREML_MODEL_DIR").split("/", 4)[-1]
    MODEL = mlflow.sklearn.load_model(os.getenv("AZUREML_MODEL_DIR") + "/model")

    # Log output data
    LOGGER.info(
        json.dumps(
            {
                "service_name": SERVICE_NAME,
                "type": "InitializeService",
            }
        )
    )


@input_schema("data", StandardPythonParameterType(INPUT_SAMPLE))
@output_schema(StandardPythonParameterType(OUTPUT_SAMPLE))
def run(data: List[Dict]) -> str:
    """Perform scoring for every invocation of the endpoint"""

    try:
        # Append datetime column to predictions
        input_df = pd.DataFrame(data)

        # Preprocess payload and get model prediction
        model_output = MODEL.predict_proba(input_df)[:, 1].tolist()
        output_df = pd.DataFrame(model_output, columns=["predictions"])

        # --- Custom Monitoring / Data Collection ---

        # Define UUID for the request
        request_id = uuid.uuid4().hex

        # Log input data
        LOGGER.info(
            json.dumps(
                {
                    "service_name": SERVICE_NAME,
                    "type": "InputData",
                    "request_id": request_id,
                    "data": input_df.to_json(orient="records"),
                }
            )
        )

        # Log output data
        LOGGER.info(
            json.dumps(
                {
                    "service_name": SERVICE_NAME,
                    "type": "OutputData",
                    "request_id": request_id,
                    "data": model_output,
                }
            )
        )

        # Make response payload
        response_payload = json.dumps({"predictions": model_output})

        # ----------------------------------

        # --- Azure ML Native Data Collection ---

        # collect inputs data
        context = INPUTS_COLLECTOR.collect(input_df)

        # collect outputs data
        OUTPUTS_COLLECTOR.collect(output_df, context)

        # create a dataframe with inputs/outputs joined - this creates a URI folder (not mltable)
        input_output_df = input_df.join(output_df)

        # collect both your inputs and output
        INPUTS_OUTPUTS_COLLECTOR.collect(input_output_df, context)

        # ----------------------------------

        return response_payload

    except Exception as error:
        LOGGER.error(
            json.dumps(
                {
                    "service_name": SERVICE_NAME,
                    "type": "Exception",
                    "request_id": request_id,
                    "error": error,
                }
            ),
            exc_info=error,
        )
