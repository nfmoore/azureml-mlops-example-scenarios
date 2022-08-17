# Azure Data Factory / Azure Synapse Pipeline Example Scenario

## Solution Overview

### Potential use cases

This approach is best suited for:

- High throughput scenarios
- Enriching data residing in a data lake at a pre-defined frequency as part of a batch scoring scenario
- Integrate Azure Machine Learning batch managed endpoints with a broader set of data stores

### Solution Design

The below diagram shows a high-level design for implementing batch scoring workloads suitable for classical machine learning scenarios using Azure Machine Learning which are orchestrated via Azure Data Factory.

![design](./images/design-adf.png)

The solution consists of the following components:

- **Datastores:** production-grade data used to develop models.
- **Experimentation workstation:** workstation where data scientists can access data, explore data and develop machine learning models.
- **Orchestration:** central solution responsible for triggering pipelines and orchestrating data movement.
- **Artefact repository:** place to store machine learning models and experiment metrics.
- **Training pipeline:** machine learning pipeline job used to build a model artifact for deployment.
- **Model deployment:** managed batch endpoint used to host the model artifact for batch inferencing.
- **Monitoring:** central monitoring solution for application and model logs and metrics. Inference data and data drift metrics are stored here.
- **Data drift pipeline:** pipeline job to calculate data drift metrics based on inference data and model training data.
- **Source control:** solution to track code.
- **Automated workflows:** workflows to automate the build and deployment of different components used in the solution.

> **Note:**
>
> The same Azure Data Factory instance can be shared across many use-cases.

The end-to-end workflow operation consists of:

1. Creating a machine learning model as an output from a pipeline job designed to develop a model artifact for the relevant use case.
2. The model artifact is registered in the model registry and consumed by the batch managed endpoint.
3. When triggered, the batch managed endpoint will consume a data set as an input and produce a data set as an output.
4. An Azure Data Factory pipeline will be used to orchestrate all batch inferencing and data movement. This pipeline will call the batch managed endpoint in Azure Machine Learning and copy the output data set to another destination (e.g. Azure SQL DB or another Azure Data Factory sink).
5. Data drift metrics will be calculated via a pipeline job and sent to Azure Monitor via Application Insights as custom metrics.
6. Alerts can be triggered in Azure Monitor to retain and re-deploy models via triggering a pipeline job designed to develop a model artifact.

> **Note:**
>
> A metadata-driven approach should be adopted for scaling pipelines used for orchestration.
> In this approach Azure Data Factory pipelines will capture logic for generic workflows (e.g. calling a managed batch endpoint and writing data to Azure SQL DB).
>
> When executing each pipeline, metadata will be extracted from a database which will govern the exact managed batch endpoint and sink which will be used by the pipeline.
> These will be passed to the pipeline as parameters.

### Continuous Integration and Continuous Delivery Workflow

The below diagram shows the overall CI/CD process as built with GitHub Actions. This approach consists of three environments consisting of an identical set of resources.

Azure Machine Learning artifacts will follow the build and release process shown in the below diagram.

![design](./images/cicd-batch.png)

Azure Data Factory pipelines will follow the build and release process shown in the below diagram. It's important that the associated Azure Machine Learning artifacts have to be created first in each environment.

![design](./images/cicd-adf.png)

The environments include:

- **Development:** used by developers to build and test their solutions.
- **Staging:** used to test deployments before going to production in a production-like environment. Any integration tests are run in this environment.
- **Production:** used for the final production environment.

> **Note:**
>
> In a metadata-driven approach re-deploying the Azure Data Factory pipelines is not necessary if a separate use-case adopts logic captured in an existing Azure Data Factory pipeline.
> In this approach a new record can be added to the control table in the database which stores metadata for the pipeline.
> For this an updated DACPAC or run scripts using SQLCMD can be used within the CI/CD pipeline.

## Related resources

You might also find these references useful:

- [Use batch endpoints for batch scoring](https://docs.microsoft.com/azure/machine-learning/how-to-use-batch-endpoint)
- [Execute Azure Machine Learning pipelines in Azure Data Factory and Synapse Analytics](https://docs.microsoft.com/azure/data-factory/transform-data-machine-learning-service)
- [Azure Data Factory and Azure Synapse Analytics connector overview](https://docs.microsoft.com/azure/data-factory/connector-overview)
- [Build large-scale data copy pipelines with a metadata-driven approach in copy data tool](https://docs.microsoft.com/azure/data-factory/copy-data-tool-metadata-driven)
- [Deploy a Data-tier Application](https://docs.microsoft.com/sql/relational-databases/data-tier-applications/deploy-a-data-tier-application)
- [CI/CD for Azure SQL Database](https://github.com/Azure-Samples/modern-data-warehouse-dataops/tree/main/single_tech_samples/azuresql)
