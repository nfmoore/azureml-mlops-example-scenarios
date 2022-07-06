# Example Scenarios: MLOps with Azure Machine Learning

## Overview

MLOps is a set of repeatable, automated, and collaborative workflows with best practices that empower teams of ML professionals to quickly and easily get their machine learning models deployed into production.

This repository provides prescriptive guidance when building, deploying, and monitoring machine learning models with [Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/) in line with MLOps principles and practices.

These example scenarios provided an end-to-end approach for MLOps in Azure based on common inference scenarios. The example scenarios will focus on  [Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning) and [GitHub Actions](https://github.com/features/actions).

> **Note:** the [Azure MLOps (v2) Solution Accelerator](https://github.com/Azure/mlops-v2) is intended to serve as the starting point for MLOps implementation in Azure.

## Getting Started

The example scenarios will focus on classical machine learning problems. The `IBM HR Analytics Employee Attrition & Performance` [dataset](https://www.kaggle.com/pavansubhasht/ibm-hr-analytics-attrition-dataset) available on Kaggle will be used to illistrate each example scenario.

| Example Scenario | Inference Scenario | Description |
| ---------------- | ------------------ | ----------- |
| Real-time Endpoint | Online |  Consume a registered model as a real-time endpoint within Azure Machine Learning for low-latency scenarios. |
| Batch Endpoint | Batch | Consume a registered model as a batch endpoint within Azure Machine Learning for high-throughput scenarios that can be executed within a single Azure Machine Learning workspace. |
| Azure Data Factory / Synapse Pipeline | Batch | Consume a registered model as a batch endpoint within Azure Machine Learning for high-throughput scenarios orchestrated via Azure Data Factory (e.g. copy results to SQL DB). |
| Azure Synapse Dedicated SQL Pool | Batch | Consume a registered model within a SQL Stored Procedure for high-throughput scenarios when loading data into an Azure Synapse Dedicated SQL Pool. |
| Azure Stream Analytics | Streaming | Consume a registered model deployed as a real-time endpoint within an Azure Stream Analytics User Defined Function for processing high-volume data streams. |
| Power BI | Online | Consume a registered model deployed as a real-time endpoint within a Power BI report |

## License

Details on licensing for the project can be found in the [LICENSE](./LICENSE) file.
