"""Constants used as a reference by different scripts"""

# define target column
TARGET = ["default_payment_next_month"]

# define categorical feature columns
CATEGORICAL_FEATURES = [
    "sex",
    "education",
    "marriage",
    "repayment_status_1",
    "repayment_status_2",
    "repayment_status_3",
    "repayment_status_4",
    "repayment_status_5",
    "repayment_status_6",
]

# define numeric feature columns
NUMERIC_FEATURES = [
    "credit_limit",
    "age",
    "bill_amount_1",
    "bill_amount_2",
    "bill_amount_3",
    "bill_amount_4",
    "bill_amount_5",
    "bill_amount_6",
    "payment_amount_1",
    "payment_amount_2",
    "payment_amount_3",
    "payment_amount_4",
    "payment_amount_5",
    "payment_amount_6",
]

# define all features
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# define sample data for inference
INPUT_SAMPLE = [
    {
        "sex": "male",
        "education": "university",
        "marriage": "married",
        "repayment_status_1": "duly_paid",
        "repayment_status_2": "duly_paid",
        "repayment_status_3": "duly_paid",
        "repayment_status_4": "duly_paid",
        "repayment_status_5": "no_delay",
        "repayment_status_6": "no_delay",
        "credit_limit": 18000.0,
        "age": 33.0,
        "bill_amount_1": 764.95,
        "bill_amount_2": 2221.95,
        "bill_amount_3": 1131.85,
        "bill_amount_4": 5074.85,
        "bill_amount_5": 3448.0,
        "bill_amount_6": 1419.95,
        "payment_amount_1": 2236.5,
        "payment_amount_2": 1137.55,
        "payment_amount_3": 5084.55,
        "payment_amount_4": 111.65,
        "payment_amount_5": 306.9,
        "payment_amount_6": 805.65,
    }
]

# define sample response for inference
OUTPUT_SAMPLE = {"predictions": [0.02]}
