# Managed Online Endpoint Example Scenario

## Solution Overview

### Potential Use Cases

This approach is best suited for:

- Low-latency and interactive workloads
- Exposing machine learning models as a REST API to integrate with external applications

### Solution Design

The below diagram shows a high-level design for implementing online scoring workloads suitable for classical machine learning scenarios using Azure Machine Learning.

![design](./images/scenarios/design-online.png)

The solution consists of:

- **Datastores:** production-grade data used to develop models.
- **Experimentation workstation:** workstation where data scientists can access data, explore data and develop machine learning models.
- **Training pipeline:** machine learning pipeline job used to build a model artifact for deployment.
- **Model deployment:** managed online endpoint used to host the model artifact for online inferencing.
- **Monitoring:** central monitoring solution for application and model logs and metrics. Inference data and data drift metrics are stored here.
- **Data drift pipeline:** pipeline job to calculate data drift metrics based on inference data and model training data.
- **Data export:** solution to export inference data collected from the managed online endpoint. This can be used to retrain the model or determine data drift.
- **Source control:** solution to track code.
- **Automated workflows:** workflows to automate the build and deployment of different components used in the solution.
- **Machine Learning Registry:** central registry for storing and sharing artifacts (model, environments and components) between workspaces in staging and production from a single location.

The end-to-end workflow operation consists of:

1. Creating a machine learning model as an output from a pipeline job designed to develop a model artifact for the relevant use case.
2. The model artifact is registered in the Machine Learning Registry and consumed by the online managed endpoint.
3. When triggered, the online managed endpoint will consume data within a payload and send a response. This payload will be logged within Azure Monitor.
4. Inference data collected from the request payload can be extracted by an Azure Machine Learning pipeline job by querying Azure Monitor and writing the output to blob storage. These can be used as an input to calculating data drift metrics.
5. Data drift metrics will be calculated via a pipeline job and sent to Azure Monitor via Application Insights as custom metrics.
6. Alerts can be triggered in Azure Monitor to retain and re-deploy models via triggering a pipeline job designed to develop a model artifact.

### Continuous Integration and Continuous Delivery Workflow

The below diagram shows the overall CI/CD process as built with GitHub Actions. This approach consists of three environments consisting of an identical set of resources.

![design](./images/scenarios/cicd-online.png)

The environments include:

- **Development:** used by developers to build and test their solutions.
- **Staging:** used to test deployments before going to production in a production-like environment. Any integration tests are run in this environment.
- **Production:** used for the final production environment.

## Scenario Walkthrough

This section describes the main components of the example scenario that relate to implementing an online scoring scenario with Azure Machine Learning managed online endpoints. Each section will describe the key files and the role they play in the context of the overall solution.

> **Note:**
> For detailed instructions to deploy this example scenario to a personal Azure environment see the [Step-by-Step Setup](./step-by-step.md) section of this repository. This will result in a machine learning model being trained, registered in both environments, deployed as both a managed batch endpoint and a managed online endpoint, and scheduled execution of the `Data Export` and `Data Drift` pipelines periodically.

### Data Assets

A reference to data assets stored within a datastore needs to be created. Two data assets will be created in this example scenario - one for training a model referencing `core/data/credit-card-default/curated/01.csv`, another for model inference referencing `core/data/credit-card-default/inference/batch/01.csv`, and another for data collected from online inference. Azure Machine Learning datasets enable:

- Keep a single copy of data in storage referenced by datasets.
- Seamlessly access data during model training without worrying about connection strings or data paths.
- Share data and collaborate with other users.
- Create different versions of datasets.

### Model Training Pipeline

An Azure Machine Learning environment called `credit-card-default-train` for the model training pipeline will need to be created. An Azure Machine Learning environment specifies the runtime, Python packages, environment variables, and software settings.

To register the environment for the model training pipeline in the Azure Machine Learning workspace execute:

```bash
az ml environment create -f core/environments/train.yml
```

To register the curated data for the model training pipeline in the Azure Machine Learning workspace execute:

```bash
az ml data create -f core/data/credit-card-default/curated.yml
```

The model training pipeline is defined in `core/pipelines/train_model.yml`. It orchestrates the model development process by executing data preprocessing, data quality reporting, model training with hyperparameter tuning, and model registration logic encapsulated in different scripts. These are found in the `core/src` directory. This pipeline can be used to train an initial model and subsequent model version (i.e. retraining).

To create the machine learning model artifact a pipeline job must be triggered by executing:

```bash
az ml job create -f core/pipelines/train_model.yml
```

A byproduct of executing the model training pipeline is a prepared dataset that will be written to the default blob datastore `workspaceblobstore`.

### Managed Online Endpoint Deployment

Once the model has been developed and the model artifact has been registered in the Azure Machine Learning workspace a managed online endpoint can be created. Managed online endpoints simplify the process of hosting machine learning models by exposing an HTTPS endpoint that clients can call to receive the inferencing (scoring) output of a trained model. When deploying MLflow model scoring code and an execution environment is auto-generated. This approach is not adopted in this example scenario in favour of developing a custom scoring script defined in `core/src/online_score.py` to incorporate custom logging. This custom logging will be used to collect inference data contained in the request payload. This will facilitate monitoring of data drift once this data is extracted and processed.

To deploy the managed online endpoint an endpoint must first be created. An endpoint is an HTTPS endpoint that clients can call to receive the inferencing (scoring) output of a trained model. It provides:

- Authentication using "key & token" based auth
- SSL termination
- A stable scoring URI (endpoint-name.region.inference.ml.azure.com)

An endpoint can be created by executing:

```bash
az ml online-endpoint create -f core/deploy/online/endpoint.yml
```

Next, a deployment must be created for the endpoint. A deployment is a set of resources required for hosting the model that does the actual inferencing. Note that a single endpoint can contain multiple deployments.

An environment called `credit-card-default-score` must be created to support the deployments by executing:

```bash
az ml environment create -f core/environments/score.yml
```

A deployment can be created by executing:

```bash
az ml online-deployment create -f core/deploy/online/deployment.yml
```

To evoke the online endpoint several options exist including CLI, REST, or manually via the workspace UI.

```bash
ENDPOINT_NAME=credit-card-default-oe

az ml online-endpoint invoke --name $ENDPOINT_NAME --request-file core/deploy/online/sample.json
```

The following resource available [here](https://docs.microsoft.com/azure/machine-learning/how-to-deploy-managed-online-endpoints) provides more information about managed online endpoints.

> **Tip:**
> This example scenario can be extended by implementing a safe rollout which allows for gradually upgrading to a new version of the model in a new deployment from the currently running version in deployment. Learn more about implementing this concept [here](https://github.com/rsethur/saferollout)

### Data Drift Pipeline

Data drift is one of the top reasons model accuracy degrades over time. For machine learning models, data drift is the change in model input data that leads to model performance degradation. Monitoring data drift helps detect these model performance issues.

Causes of data drift include:

- Upstream process changes, such as a sensor being replaced that changes the units of measurement from inches to centimetres.
- Data quality issues, such as a broken sensor always reading 0.
- Natural drift in the data, such as mean temperature changing with the seasons.
- Change in the relation between features, or covariate shift.

To calculate data drift Evidently AI, an open-source framework to evaluate, test, and monitor ML models, is used.

In this example scenario, a data drift pipeline job will be triggered and metrics will be calculated and sent to Azure Monitor via Application Insights as custom metrics. The model data drift pipeline is defined in `core/pipelines/data_drift.yml`. This pipeline can be triggered on a re-occurring schedule whenever data drift metrics need to be calculated.

First, an environment called `credit-card-default-drift` for the data drift pipeline must be created by executing:

```bash
az ml environment create -f core/environments/drift.yml
```

Next, the data drift pipeline job can be triggered by executing:

```bash
az ml job create -f core/pipelines/data_drift.yml
```

### Model Monitoring

Azure Monitor is used as the central solution for collecting, analysing, and acting on telemetry within this example scenario. With Azure Monitor, logs can be analysed via Log Analytics, visualisations can be created from metrics, and alerts can be configured.

The data drift pipeline generates logs for the overall level of data drift and the level of data drift for each feature between the baseline and target data sets. The baseline data set can be thought of the data set used to develop the machine learning model and the inference data set can be thought of the data set which has been consumed by the model to make predictions over a given time period.

Using the Log Analytics workspace logs collected from the data drift pipeline through Azure Application Insights can be analysed to monitor data drift to ensure models are performing well.

To view overall data drift metrics the following query can be executed in Log Analytics:

```kql
traces
| where message has 'credit-card-default' and message has 'OverallDriftMetrics'
| project timestamp, data=parse_json(tostring(message)).data
| evaluate bag_unpack(data)
```

To view feature level data drift metrics the following query can be executed in Log Analytics:

```kql
traces
| where message has 'credit-card-default' and message has 'FeatureDriftMetrics'
| project timestamp, data=parse_json(tostring(message)).data
| mv-expand data
| evaluate bag_unpack(data)
```

In addition to data drift custom logs emitted from the managed online endpoint can be analysed using the Log Analytics workspace logs. To filter and parse inference data the following query can be executed in Log Analytics:

```kql
AmlOnlineEndpointConsoleLog
| where TimeGenerated > ago (1d)
| where Message has 'online/credit-card-default/1' and Message has 'InputData'
| project TimeGenerated, ResponsePayload=split(Message, '|')
| project TimeGenerated, InputData=parse_json(tostring(ResponsePayload[-1])).data
| project TimeGenerated, InputData=parse_json(tostring(InputData))
| mv-expand InputData
| evaluate bag_unpack(InputData)
```

This pipeline will be triggered as part of an Azure Machine Learning pipeline schedule.

### Data Export

To effectively monitor data drift and re-train models in online inference scenarios inference data must be collected and transformed from the web service. This is different from batch inference scenarios where data will likely be available upfront. This complicates model monitoring and re-training slightly since an additional process is required.

In this example scenario a job pipeline defined in `core/pipelines/data_export.yml` is used to query data from a Log Analytics workspace in Azure Monitor and send data to Azure Storage which can be consumed by the data drift pipeline for calculating data drift metrics and the model training pipeline for model retraining scenarios.

First, to capture custom logs from the online managed endpoint diagnostic settings must be configured to collect logs from the online managed endpoint and send them to a Log Analytics workspace. The following resource available [here](https://docs.microsoft.com/azure/machine-learning/how-to-monitor-online-endpoints#logs) can be used to learn how to configure this.

Once logs have been collected, to filter and parse inference data from custom logs the following query can be executed in Log Analytics:

```kql
AmlOnlineEndpointConsoleLog
| where TimeGenerated > ago (1d)
| where Message has 'online/credit-card-default/1' and Message has 'InputData'
| project TimeGenerated, ResponsePayload=split(Message, '|')
| project TimeGenerated, InputData=parse_json(tostring(ResponsePayload[-1])).data
| project TimeGenerated, InputData=parse_json(tostring(InputData))
| mv-expand InputData
| evaluate bag_unpack(InputData)
```

This pipeline will be triggered as part of an Azure Machine Learning pipeline schedule.

### Automated Model Training, Deployment, and Monitoring

To automatically build all assets and deploy them to staging and production environments GitHub Actions is used. GitHub Actions is a continuous integration and continuous delivery (CI/CD) platform that allows for the creation of automated build, test, and deployment pipelines. Workflows can be created that build and test every pull recommendation to a repository or deploy merged pull requests to production.

With GitHub Actions and establishing similar workflows, machine learning teams can build their levels of maturity operationalising machine learning models (MLOps). Some goals of implementing MLOps for machine learning projects include:

- Automated deployment of machine learning models to production.
- Creating secured, reproducible and scalable machine learning workflows.
- Manage models and capture data lineage.
- Enable continuous delivery with IaC and CI/CD pipelines.
- Monitor performance and feedback information from models.
- Providing compliance, security, and cost tools for machine learning development.
- Increasing collaboration and experimentation.

In this example scenario, four workflows have been developed in the `.github/workflows` directory. Reusable sub workflows are in the `.github/templates` directory and are used more than once across one or more workflows. The main workflows in this example scenario are:

- **Code Quality:** implementing regular code scanning on select branches when code is pushed and on a schedule.
- **Create Data Assets:** workflow intended to deploy new data assets to staging and production environments as they are created. Data assets are defined in specification files which trigger the workflow as changes are committed.
- **Create Environments:** workflow intended to deploy new Azure Machine Learning environments to staging and production environments as they are created. Azure Machine Learning environments are defined in specification files which trigger the workflow as changes are committed.
- **Build Model:** a workflow that trains a model in a staging environment and registers a model artifact to the workflow. This workflow will automatically trigger the `Deploy Model for Online Inference` workflow upon completion. Triggering this workflow on a schedule can be used to implement a model retraining process.
- **Deploy Model for Online Inference:** a workflow that creates endpoints and deployments referencing the model in the staging environment, runs end-to-end tests, copies model assets to the production environment, and recreates endpoints and deployments in the production environment.

## Related Resources

You might also find these references useful:

- [Deploy and score a machine learning model by using an online endpoint](https://docs.microsoft.com/azure/machine-learning/how-to-deploy-managed-online-endpoints)
- [Monitor online endpoints](https://docs.microsoft.com/azure/machine-learning/how-to-monitor-online-endpoints)
- [Safe rollout of ML models using Azure ML Managed Online Endpoints](https://github.com/rsethur/saferollout)
- [Azure Machine Learning registry](https://learn.microsoft.com/azure/machine-learning/how-to-share-models-pipelines-across-workspaces-with-registries?tabs=cli)
