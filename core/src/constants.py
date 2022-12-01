"""Constants used as a reference by different scripts"""
# define target column
TARGET = ["Attrition"]

# define categorical feature columns
CATEGORICAL_FEATURES = [
    "Gender",
    "Education",
    "EducationField",
    "Department",
    "JobRole",
    "JobLevel",
    "PerformanceRating",
    "JobInvolvement",
    "JobSatisfaction",
    "RelationshipSatisfaction",
    "EnvironmentSatisfaction",
    "BusinessTravel",
    "OverTime",
    "WorkLifeBalance",
    "MaritalStatus",
    "StockOptionLevel"
]

# define numeric feature columns
NUMERIC_FEATURES = [
    "Age",
    "DistanceFromHome",
    "MonthlyIncome",
    "NumCompaniesWorked",
    "PercentSalaryHike",
    "TotalWorkingYears",
    "TrainingTimesLastYear",
    "YearsAtCompany",
    "YearsInCurrentRole",
    "YearsSinceLastPromotion",
    "YearsWithCurrManager"
]

# define all features
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# define sample data for inference
INPUT_SAMPLE = [
    {
        "EmployeeNumber": 1,
        "Gender": "Female", "Education":
        "College",
        "EducationField": "Life Sciences",
        "Department": "Sales", "JobRole": "Sales Executive",
        "JobLevel": 2,
        "PerformanceRating": "High",
        "JobInvolvement": "High",
        "JobSatisfaction": "High",
        "RelationshipSatisfaction": "Low",
        "EnvironmentSatisfaction": "Medium",
        "BusinessTravel": "Travel_Rarely",
        "OverTime": "Yes",
        "WorkLifeBalance": "Bad",
        "MaritalStatus": "Single",
        "StockOptionLevel": "L0",
        "Age": 41,
        "DailyRate": 1102,
        "DistanceFromHome": 1,
        "HourlyRate": 94,
        "MonthlyIncome": 5993,
        "MonthlyRate": 19479,
        "NumCompaniesWorked": 8,
        "PercentSalaryHike": 11,
        "TotalWorkingYears": 8,
        "TrainingTimesLastYear": 0,
        "YearsAtCompany": 6,
        "YearsInCurrentRole": 4,
        "YearsSinceLastPromotion": 0,
        "YearsWithCurrManager": 5
    }
]

# define sample response for inference
OUTPUT_SAMPLE = {"probability": [0.26883566156891225]}
