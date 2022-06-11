import os

import joblib
import mlflow.pyfunc
import numpy as np
from alibi_detect.utils.saving import load_detector


class EmployeeAttritionModel(mlflow.pyfunc.PythonModel):
    def __init__(self, columns_categorical, columns_numeric):
        self.columns_categorical = columns_categorical
        self.columns_numeric = columns_numeric
        self.drift_column_names = columns_categorical + columns_numeric

    def load_context(self, context):
        self.classifier = joblib.load(os.path.join(
            context.artifacts["artifacts_path"], "model/model.pkl"))
        self.drift_model = load_detector(os.path.join(
            context.artifacts["artifacts_path"], "drift"))
        self.outlier_model = load_detector(os.path.join(
            context.artifacts["artifacts_path"], "outlier"))

    def generate_output(self, model_predictions: np.array, drift_output, outlier_output):
        return {
            "classifier__predictions": model_predictions.tolist(),
            "drift__threshold": drift_output["data"]["threshold"],
            "drift__is_drift": dict(zip(self.columns_categorical + self.columns_numeric, drift_output["data"]["is_drift"].tolist())),
            "drift__p_value": dict(zip(self.columns_categorical + self.columns_numeric, drift_output["data"]["p_val"].tolist())),
            "drift__magnitude": dict(zip(self.columns_categorical + self.columns_numeric, (1 - drift_output["data"]["p_val"]).tolist())),
            "outliers__is_outlier": dict(zip(self.columns_numeric, outlier_output["data"]["is_outlier"].tolist())),
        }

    def predict(self, context, model_input):
        # Generate predictions, drift results, and  outlier results
        predictions = self.classifier.predict_proba(model_input)[:, 1]
        drift_output = self.drift_model.predict(
            model_input[self.drift_column_names].values, drift_type="feature", return_p_val=True, return_distance=True)
        outlier_output = self.outlier_model.predict(
            model_input[self.columns_numeric].values)

        return self.generate_output(predictions, drift_output, outlier_output)
