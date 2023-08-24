# Example Scenarios: MLOps with Azure Machine Learning

## :books: Overview

MLOps is a set of repeatable, automated, and collaborative workflows with best practices that empower teams of ML professionals to quickly and easily get their machine learning models deployed into production.

This repository provides prescriptive guidance when building, deploying, and monitoring machine learning models with [Azure Machine Learning](https://docs.microsoft.com/azure/machine-learning/) in line with MLOps principles and practices.

These example scenarios provided an end-to-end approach for MLOps in Azure based on common inference scenarios. The example scenarios will focus on [Azure Machine Learning](https://docs.microsoft.com/azure/machine-learning) and [GitHub Actions](https://github.com/features/actions).

> **Note:** the [Azure MLOps (v2) Solution Accelerator](https://github.com/Azure/mlops-v2) is intended to serve as the starting point for MLOps implementation in Azure.

## :computer: Getting Started

This repository contains several example scenarios for productionising models using Azure Machine Learning. Two approaches are considered:

- **Standalone:** where services consuming models are operated entirely within Azure Machine Learning.
- **Native integrations:** where services consuming models within Azure Machine Learning are integrated within other services within Azure via out-of-the-box integrations.

Users of Azure Machine Learning might choose to integrate with other services available within Azure to better align with existing workflows, enable new inference scenarios, or gain greater flexibility.

All example scenarios will focus on classical machine learning problems. An adapted version of the `UCI Credit Card Client Default` [dataset](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) will be used to illustrate each example scenario.

### Setup

Detailed instructions for deploying this proof-of-concept are outlined in the [Step-by-Step Setup](.github/docs/step-by-step.md) section of this repository. This proof-of-concept will illustrate how to:

- Manage and version machine learning models, environments, and datasets within Azure Machine Learning.
- Promote a machine learning model to downstream environments.
- Deploy models to managed endpoints for batch and online inference scenarios.
- Deploy a data factory pipeline to orchestrate workflows consuming a batch-managed endpoint.
- Develop build and deployment workflows for the different inference scenarios.
- Collect and process inference data to detect data drift.
- Monitor workloads for usage, performance and data drift.

### Standalone deployments within Azure Machine Learning

| Example Scenario | Inference Scenario | Description |
| ---------------- | ------------------ | ----------- |
| [Batch Managed Endpoint](./.github/docs/batch-endpoint.md) | Batch | Consume a registered model as a batch managed endpoint within Azure Machine Learning for high-throughput scenarios that can be executed within a single Azure Machine Learning workspace. |
| [Online Managed Endpoint](./.github/docs/online-endpoint.md) | Online | Consume a registered model as an online managed endpoint within Azure Machine Learning for low-latency scenarios. |

### Native integrations between Azure services and deployments within Azure Machine Learning

| Example Scenario | Inference Scenario | Description |
| ---------------- | ------------------ | ----------- |
| [Azure Data Factory / Synapse Pipeline](./.github/docs/data-factory-pipeline.md) | Batch | Consume a registered model as a batch managed endpoint within Azure Machine Learning for high-throughput scenarios orchestrated via Azure Data Factory or Azure Synapse Pipelines. |
| [Power BI](./.github/docs/powerbi.md) | Online | Consume a registered model deployed as an online managed endpoint within a Power BI report |
| [Azure Stream Analytics](./.github/docs/stream-analytics.md) | Streaming | Consume a registered model deployed as an online managed endpoint within an Azure Stream Analytics User Defined Function for processing high-volume data streams. |

## :balance_scale: License

Details on licensing for the project can be found in the [LICENSE](./LICENSE) file.
