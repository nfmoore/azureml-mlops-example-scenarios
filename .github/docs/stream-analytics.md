# Azure Stream Analytics Example Scenario

## Solution Overview

### Potential use cases

This approach is best suited for:

- High throughput low latency scenarios

### Solution Design

The below diagram shows a high-level design for implementing online scoring for streaming workloads suitable for classical machine learning scenarios using Azure Machine Learning and Azure Stream Analytics.

![design](./images/scenarios/design-streaming.png)

The solution consists of the following components:

- **Datastores:** production-grade data used to develop models.
- **Experimentation workstation:** workstation where data scientists can access data, explore data and develop machine learning models.
- **Orchestration:** central solution responsible for triggering pipelines and orchestrating data movement.
- **Training pipeline:** machine learning pipeline job used to build a model artifact for deployment.
- **Model deployment:** managed online endpoint used to host the model artifact for online inferencing.
- **Streaming services:** data streams will be consumed and processed using the managed online endpoint.
- **Monitoring:** central monitoring solution for application and model logs and metrics. Inference data and data drift metrics are stored here.
- **Data drift pipeline:** pipeline job to calculate data drift metrics based on inference data and model training data.
- **Data export:** solution to export inference data collected from the managed online endpoint. This can be used to retrain the model or determine data drift.
- **Source control:** solution to track code.
- **Automated workflows:** workflows to automate the build and deployment of different components used in the solution.
- **Machine Learning Registry:** central registry for storing and sharing artifacts (model, environments and components) between workspaces in staging and production from a single location.

The end-to-end workflow operation consists of:

1. Creating a machine learning model as an output from a pipeline job designed to develop a model artifact for the relevant use case.
2. The model artifact is registered in the Machine Learning Registry and consumed by the online managed endpoint.
3. Data streams will be accepted by Azure Event Hub and sent to Azure Stream Analytics for processing. Azure Stream Analytics will consume the online managed endpoint to generate predictions for incoming data.
4. When the online managed endpoint is triggered, the data within the request payload will be logged within Azure Monitor.
5. Inference data collected from the request payload can be extracted by an Azure Logic App by querying Azure Monitor and writing the output to blob storage. These can be used as an input to calculating data drift metrics.
6. Data drift metrics will be calculated via a pipeline job and sent to Azure Monitor via Application Insights as custom metrics.
7. Alerts can be triggered in Azure Monitor to retain and re-deploy models via triggering a pipeline job designed to develop a model artifact.

### Continuous Integration and Continuous Delivery Workflow

The below diagram shows the overall CI/CD process as built with GitHub Actions. This approach consists of three environments consisting of an identical set of resources.

Azure Machine Learning artifacts will follow the build and release process shown in the below diagram.

![design](./images/scenarios/cicd-online.png)

Azure Stream Analytics will follow the build and release process shown in the below diagram. It's important that the associated Azure Machine Learning artifacts have to be created first in each environment.

![design](./images/scenarios/cicd-streaming.png)

The environments include:

- **Development:** used by developers to build and test their solutions.
- **Staging:** used to test deployments before going to production in a production-like environment. Any integration tests are run in this environment.
- **Production:** used for the final production environment.

## Related Resources

You might also find these references useful:

- [Integrate Azure Stream Analytics with Azure Machine Learning](https://docs.microsoft.com/azure/stream-analytics/machine-learning-udf)
- [Continuous integration and deployment (CI/CD) for Azure Stream Analytics](https://docs.microsoft.com/azure/stream-analytics/cicd-overview)
- [CI/CD for Azure Stream Analytics](https://github.com/Azure-Samples/modern-data-warehouse-dataops/tree/main/single_tech_samples/streamanalytics)
- [Azure Machine Learning registry](https://learn.microsoft.com/azure/machine-learning/how-to-share-models-pipelines-across-workspaces-with-registries?tabs=cli)
