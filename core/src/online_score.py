import json
import logging
import os
import uuid
from typing import Dict, List

import mlflow
import pandas as pd
from inference_schema.parameter_types.standard_py_parameter_type import \
    StandardPythonParameterType
from inference_schema.schema_decorators import input_schema, output_schema

# Define sample data
INPUT_SAMPLE = [
    {
        "BusinessTravel": "Travel_Rarely",
        "Department": "Research & Development",
        "EducationField": "Medical",
        "Gender": "Male",
        "JobRole": "Manager",
        "MaritalStatus": "Married",
        "OverTime": "No",
        "Age": 36,
        "DailyRate": 989,
        "DistanceFromHome": 8,
        "Education": 1,
        "EmployeeNumber": 253,
        "EnvironmentSatisfaction": 4,
        "HourlyRate": 46,
        "JobInvolvement": 3,
        "JobLevel": 5,
        "JobSatisfaction": 3,
        "MonthlyIncome": 19033,
        "MonthlyRate": 6499,
        "NumCompaniesWorked": 1,
        "PercentSalaryHike": 14,
        "PerformanceRating": 3,
        "RelationshipSatisfaction": 2,
        "StockOptionLevel": 1,
        "TotalWorkingYears": 14,
        "TrainingTimesLastYear": 3,
        "WorkLifeBalance": 2,
        "YearsAtCompany": 3,
        "YearsInCurrentRole": 3,
        "YearsSinceLastPromotion": 3,
        "YearsWithCurrManager": 1
    }
]

OUTPUT_SAMPLE = {"probability": [0.26883566156891225]}


# Configure logger
LOGGER = logging.getLogger('root')


def init() -> None:
    """
    A startup event handler to load an MLFLow model.
    """
    global SERVICE_NAME
    global MODEL

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
    """
    Function performing scoring for every invocation of the endpoint.
    Parameters:
        request (List[Dict]): Web service request containing inference data.
    Returns:
        response_payload (str): JSON string containing model predictions
        and drift / outlier results for monitoring.
    """

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

    except Exception as e:
        LOGGER.error(json.dumps({
            "service_name": SERVICE_NAME,
            "type": "Exception",
            "request_id": request_id,
            "error": e
        }), exc_info=e)
