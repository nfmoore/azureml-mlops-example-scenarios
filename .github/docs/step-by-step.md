# Step-by-Step Setup

> **Note:**
> As with all Azure Deployments, this will incur associated costs. Remember to teardown all related resources after use to avoid unnecessary costs.

## Prerequisites

Before implementing this example scenario the following are needed:

- Azure subscription (contributor or owner)
- GitHub account

## 1. Initial Setup

### 1.1. Deploy Azure Resources

You will need to create an Azure Machine Learning workspace with associated resources for `Staging` and `Production` environments. To assist with this an ARM template has been created to automate the deployment of all necessary resources. Use the `Deploy to Azure` button below to automatically deploy these resources. You will need to do this twice to deploy 2 separate instances for `Staging` and `Production` respectively. Note no settings need to be changed except the `Resource Instance` parameter (e.g. `001` and `002` respectivally).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fnfmoore%2Fazureml-mlops-example-scenarios%2Fmain%2Finfrastructure%2Fmain.json)

Note that the above deployment will also upload the required data sets `core/data/curated/data.csv` and `core/data/inference/data.csv` to the default blob datastore `workspaceblobstore`. These will be used as part of this example scenario.

![1](./images/sbs-1.png)

### 1.2. Create GitHub Repository

Log in to your GitHub account and navigate to the [azureml-mlops-example-scenarios](https://github.com/nfmoore/azureml-mlops-example-scenarios) repository and click `use this template` to create a new repository from this template. Rename the template and leave it public. Use [these](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-repository-from-a-template) instructions for more details about creating a repository from a template.

### 1.3. Configure GitHub Actions Environments

GitHub Environments are used to describe the `Staging` and `Production` deployment targets and will be used to configure protection rules and secrets in this example scenario.

To set up these environments, from the GitHub repository you created in `1.1` click the `Settings` tab in the menu bar. On the new page select `Environments` from the sidebar. Click the `New Environment` button and create an environment with the `Name` of `Staging`. Repeat this to create a second environment with the `Name` of `Production`.

![1](./images/sbs-2.png)

Next, you will configure GitHub Action secrets. These are encrypted environment variables used within GitHub Actions Workflows. Click the `Settings` tab in the menu bar of your GitHub repository and on the new page than select `Secrets` from the sidebar. Click the `New Repository Secret` button to create a new secret and then the `Add Secret` button to create the secret.

![1](./images/sbs-3.png)

You need to create the following secrets in each environment:

| Secret name | How to find secret value |
|:------------|:-------------------------|
| AZURE_CREDENTIALS | A JSON object with details of your Azure Service Principal. [This](https://github.com/marketplace/actions/azure-login#configure-deployment-credentials) document will help you configure a service principal with a secret. The value will look something like: `{ "clientId": "<GUID>", "clientSecret": "<GUID>", "subscriptionId": "<GUID>", "tenantId": "<GUID>", ... }`|
| RESOURCE_GROUP | The name of the resource group that resources are deployed into. |
| WORKSPACE_NAME | The name of the Azure Machine Learning workspace resource. |
| APPLICATION_INSIGHTS_NAME | The name of the Application Insights resource. |
| LOG_ANALYTICS_WORKSPACE_NAME | The name of the Log Analytics workspace resource. |
| ENDPOINT_SUFFIX | A unique suffix with a maximum of 9 characters consisting of letters and numbers. |

Click the `Add Secret` button and create the above secret with associated values from your deployments from `1.1` in both the `Staging` and `Production` environments.

![1](./images/sbs-4.png)

After creating the above secrets for the `Production` environment, you can enable `Required Viewers` before deploying to this environment. This will allow you to specify people or teams that may approve workflow runs when they access this environment. To enable `Required Viewers`, under the `Environment Protection Rules` section, click the checkbox next to `Required Viewers` and search for your GitHub username and select it from the dropdown and click the `Save Protection Rules` button.

![1](./images/sbs-5.png)

## 2. Execute Workflows

> **Note:**
> The `Train and Deploy Model` workflows will deploy both a managed batch endpoint and a managed online endpoint and enable scheduled execution of the `Data Export` and `Data Drift` pipelines periodically.

From your GitHub repository select `Actions` from the menu. From here you will be able to view the GitHub Action implementing the CI/CD pipeline for this example scenario. By default, the workflow in this example scenario is triggered manually within GitHub.

In this example scenario, four workflows have been developed in the `.github/workflows` directory. Reusable sub workflows are in the `.github/templates` directory and are used more than once across one or more workflows. The main workflows in this example scenario are:

- `Code Quality`: workflow implementing regular code scanning on select branches when code is pushed and on a schedule.
- `Create Data Assets`: workflow intended to deploy new data assets to staging and production environments as they are created. Data assets are defined in specification files which trigger the workflow as changes are committed.
- `Create Environments`: workflow intended to deploy new Azure Machine Learning environments to staging and production environments as they are created. Azure Machine Learning environments are defined in specification files which trigger the workflow as changes are committed.
- `Train and Deploy Model`: workflow that trains a model in a staging environment, creates endpoints and deployments referencing the model, runs end-to-end tests, copies model assets to the production environment, and recreates endpoints and deployments in the production environment. Triggering this workflow on a schedule can be used to implement a model retraining process.

To execute the workflow you can manually trigger the workflow in GitHub Actions `Workflows` menu. In the sidebar, you will need to trigger all four workflows. To trigger a workflow, select the workflow then click `Run workflow`. Execute the workflows in the following order:

1. `Code Quality`
2. `Create Data Assets`
3. `Create Environments`
4. `Train and Deploy Model`

![1](./images/sbs-6.png)

Note that the `Train and Deploy Model` workflow depends on `Create Data Assets` and `Create Environments`

![1](./images/sbs-7.png)

Manual approval is required to deploy the Docker container to the `Production` environment. Once the `End to End Testing` job is complete you will be prompted to review the deployment. Click the `Review Deployment` button to give approval and commence the `Upload Model to Production` job. This will need to be repeated for the `Deploy to Production` job. The approver(s) were specified in `1.3` above.

![1](./images/sbs-8.png)

Once the workflow has finished executing all artifacts will have been deployed to both `Staging` and `Production` environments.

![1](./images/sbs-9.png)

### Next Steps

From the `Endpoints` sidebar button in the Azure Machine Learning workspace, you can view the online managed endpoint and batch managed endpoint which have been deployed by the GitHub Actions workflow.

From the `Real-time endpoints` tab, online managed endpoints can be viewed. Different deployments can be tested under the `Test` tab. You can also interact with online managed endpoints using the CLI, SDK, and REST API.

![1](./images/sbs-10.png)

To test batch managed endpoints select the relevant endpoint under the `Batch endpoints` tab and select `Create job`. You will need to configure the job settings, data source, and output location.

![1](./images/sbs-11.png)

The `employee-attrition-inference` data asset can be used for illustrative purposes.

![1](./images/sbs-12.png)

## Related Resources

You might also find these references useful:

- [Using environments for deployment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Understanding GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions)
