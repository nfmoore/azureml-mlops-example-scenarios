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
        "Gender": "Male",
        "Education": "College",
        "EducationField": "Life Sciences",
        "Department": "Research & Development",
        "JobRole": "Research Scientist",
        "JobLevel": "L1",
        "PerformanceRating": "Medium",
        "JobInvolvement": "Medium",
        "JobSatisfaction": "Medium",
        "RelationshipSatisfaction": "Very High",
        "EnvironmentSatisfaction": "Medium",
        "BusinessTravel": "Travel Rarely",
        "OverTime": "Frequently",
        "WorkLifeBalance": "Better",
        "MaritalStatus": "Married",
        "StockOptionLevel": "L1",
        "Age": 34,
        "DistanceFromHome": 1,
        "MonthlyIncome": 3622,
        "NumCompaniesWorked": 1,
        "PercentSalaryHike": 13,
        "TotalWorkingYears": 6,
        "TrainingTimesLastYear": 3,
        "YearsAtCompany": 6,
        "YearsInCurrentRole": 5,
        "YearsSinceLastPromotion": 1,
        "YearsWithCurrManager": 3
    }
]

# define sample response for inference
OUTPUT_SAMPLE = {
    "predictions": [
        0.3364485981308411
    ]
}
