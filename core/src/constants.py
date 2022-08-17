"""Constants used as a reference by different scripts"""
# define target column
TARGET = ["Attrition"]

# define categorical feature columns
CATEGORICAL_FEATURES = [
    "BusinessTravel",
    "Department",
    "EducationField",
    "Gender",
    "JobRole",
    "MaritalStatus",
    "OverTime",
]

# define numeric feature columns
NUMERIC_FEATURES = [
    "Age",
    "DailyRate",
    "DistanceFromHome",
    "Education",
    "EmployeeNumber",
    "EnvironmentSatisfaction",
    "HourlyRate",
    "JobInvolvement",
    "JobLevel",
    "JobSatisfaction",
    "MonthlyIncome",
    "MonthlyRate",
    "NumCompaniesWorked",
    "PercentSalaryHike",
    "PerformanceRating",
    "RelationshipSatisfaction",
    "StockOptionLevel",
    "TotalWorkingYears",
    "TrainingTimesLastYear",
    "WorkLifeBalance",
    "YearsAtCompany",
    "YearsInCurrentRole",
    "YearsSinceLastPromotion",
    "YearsWithCurrManager",
]

# define all features
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# define sample data for inference
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

# define sample response for inference
OUTPUT_SAMPLE = {"probability": [0.26883566156891225]}
