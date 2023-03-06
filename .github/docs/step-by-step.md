# Step-by-Step Setup

> **Note:**
> As with all Azure Deployments, this will incur associated costs. Remember to teardown all related resources after use to avoid unnecessary costs.

## Prerequisites

Before implementing this example scenario the following are needed:

- Azure subscription (contributor or owner)
- GitHub account

## 1. Initial Setup

> **Estimated setup time:**
> - Azure resource deployments: 20 minutes
> - Configure GitHub environments and secrets: 5 minutes
> - Run all GitHub workflows: 80 minutes

### 1.1. Deploy Azure Resources

You will need to create a resource group for resources associated with **`Staging`** and **`Production`** environments. The same or separate resource groups can be used. 

Once these have been created a service principal must be created with a **`contributor`** role assigned to each resource group.

> **_Note_**: The aim of this demo is to setup a simple proof-of-concept, therefore a single resource group is used. If separate resources groups are required, the following instructions/steps will need adjustment to reflect this. 

![1](./images/01.png)

The following command can be used to create this service principal.

```bash

az ad sp create-for-rbac --name <service-principal-name> --role contributor --scopes /subscriptions/<subscription-id>/resourceGroups/<resource-group-name> --sdk-auth
```

The command should output a JSON object similar to this:

```bash
 {
 "clientId": "<GUID>",
 "clientSecret": "<STRING>",
 "subscriptionId": "<GUID>",
 "tenantId": "<GUID>",
 "resourceManagerEndpointUrl": "<URL>"
 (...)
 }
```

![1](./images/02.png)

> **_Tip_**: Use the [Azure Cloud Shell](https://learn.microsoft.com/azure/cloud-shell/overview)

**Store this JSON object, the `clientId` and `clientSecret` as they will be used in subsequent steps.**

Next an Azure Machine Learning workspace with associated resources for **`Staging`** and **`Production`** environments will need to be created. To assist with this an ARM template has been created to automate the deployment of all necessary resources. 

Use the <kbd>Deploy to Azure</kbd> button below to automatically deploy these resources. You will need to do this twice to deploy 2 separate instances for **`Staging`** and **`Production`** respectively. 
> **_Note_**: No settings need to be changed except the `Resource Instance` parameter (e.g. `001` and `002` respectively).


In the custom deployment you will need to add the **`clientId`** and **`clientSecret`** for the service principal created earlier. In the **`Instance details`** section of the custom, deployment add the **`clientId`** value in the **`servicePrincipalClientId`** field and the **`clientSecret`** value in the **`servicePrincipalSecret`** field.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fnfmoore%2Fazureml-mlops-example-scenarios%2Fmain%2Finfrastructure%2Fmain.json)

![1](./images/03.png)

> **_Note_**: The above deployment will also upload the required data sets and MLTable file specifications found in the `core/data/curated/`, `core/data/inference/batch/`, and `core/data/inference/online/` directories to the default blob datastore `workspaceblobstore`. These will be used as part of this example scenario.

### 1.2. Create GitHub Repository

Log in to your GitHub account and navigate to the [azureml-mlops-example-scenarios](https://github.com/nfmoore/azureml-mlops-example-scenarios) repository and click <kbd>Use this Template</kbd> to create a new repository from this template. Rename the template and leave it public. Ensure you click <kbd>Include all branches</kbd> to copy all branches from the repository and not just main. 
Use [these](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-repository-from-a-template) instructions for more details about creating a repository from a template.

### 1.3. Configure GitHub Actions Environments

GitHub Environments are used to describe the **`Staging`** and **`Production`** deployment targets and will be used to configure protection rules and secrets in this example scenario.

To set up these environments, from the GitHub repository you created in `1.1` click the **`Settings`** tab in the menu bar. 

On the new page select **`Environments`** from the sidebar. Click the <kbd>New Environment</kbd> button and create an environment with the `Name` of **`Staging`**. Repeat this to create a second environment with the `Name` of **`Production`**.

![1](./images/04.png)

Next, you will configure GitHub Action secrets. These are encrypted environment variables used within GitHub Actions Workflows. 

Click the **`Settings`** tab in the menu bar of your GitHub repository and on the new page then select **`Secrets`** from the sidebar. Click the <kbd>New Repository Secret</kbd> button to create a new secret and then the <kbd>Add Secret</kbd> button to create the secret.

![1](./images/05.png)

You need to create the following secrets in each environment:

| Secret name | How to find secret value | Secret type |
|:------------|:-------------------------|:------------|
| AZURE_CREDENTIALS | A JSON object with details of your Azure Service Principal. [This](https://github.com/marketplace/actions/azure-login#configure-deployment-credentials) document will help you configure a service principal with a secret. The value will look something like: `{ "clientId": "<GUID>", "clientSecret": "<GUID>", "subscriptionId": "<GUID>", "tenantId": "<GUID>", ... }`| Repository |
| RESOURCE_GROUP | The name of the resource group that resources are deployed into. | Repository |
| WORKLOAD_IDENTIFIER | The 6 random characters common to each resource in your resource group. This is from the custom deployment. For example, `sw9g3m`. | Repository |
| RESOURCE_INSTANCE | The final value common to each resource in your resource group. This is from the custom deployment. For example, `001`.| Environment |

Click the <kbd>Add Secret</kbd> button and create the above secret with associated values from your deployments from `1.1` in both the **`Staging`** and **`Production`** environments.

![1](./images/06.png)

This secret configuration can be checked via **Setting > Secrets and Variables > Actions** (as shown below). 

![1](./images/AML_Source.png)

After creating the above secrets for the **`Production`** environment, you can enable **`Required Viewers`** before deploying to this environment. 
- This will allow you to specify people or teams that may approve workflow runs when they access this environment.
-  
To enable **`Required Viewers`**, under the **`Environment Protection Rules`** section, click the checkbox next to **`Required Viewers`** and search for your GitHub username and select it from the dropdown and click the <kbd>Save Protection Rules</kbd> button.

![1](./images/07.png)

## 2. Execute Workflows

> **Note:**
> The `Deploy Model to Online Endpoint` and `Deploy Model to Batch Endpoint` workflows will enable scheduled execution of the `Data Export` and `Data Drift` pipelines periodically.

From your GitHub repository select **`Actions`** from the menu. From here you will be able to view the GitHub Action implementing the CI/CD pipeline for this example scenario. By default, the workflow in this example scenario is triggered manually within GitHub.

In this example scenario, four workflows have been developed in the `.github/workflows` directory. Reusable sub workflows are in the `.github/templates` directory and are used more than once across one or more workflows. The main workflows in this example scenario are:

- `Code Quality`: workflow implementing regular code scanning on select branches when code is pushed and on a schedule.
- `Build Data Assets`: workflow intended to deploy new data assets to staging and production environments as they are created. Data assets are defined in specification files that trigger the workflow as changes are committed.
- `Build Environments`: workflow intended to deploy new Azure Machine Learning environments to staging and production environments as they are created. Azure Machine Learning environments are defined in specification files that trigger the workflow as changes are committed.
- `Build Model`: workflow that trains a model in a staging environment. Triggering this workflow on a schedule can be used to implement a model retraining process.
- `Deploy Model to Online Endpoint`: create an online endpoint and deployments referencing the model, runs end-to-end tests, copy model assets to the production environment, and recreate the online endpoint and deployments in the production environment. This workflow is triggered automatically upon completion of the `Build Model` workflow.
- `Deploy Model to Batch Endpoint`: create a batch endpoint and deployments referencing the model, copy model assets to the production environment, and recreates the batch endpoint and deployments in the production environment. This workflow is triggered automatically upon completion of the `Build Model` workflow.
- `Build Azure Data Factory`: workflow that builds the data factory template.
- `Deploy to Azure Data Factory`: workflow that deploys the data factory template. This workflow is triggered automatically upon completion of the `Build Azure Data Factory` workflow.

To execute the workflow you can manually trigger the workflow in GitHub Actions **`Workflows`** menu. In the sidebar, you will need to trigger all four workflows. To trigger a workflow, select the workflow then click **`Run workflow`**. Execute the workflows in the following order:

1. `Code Quality`
2. `Build Data Assets`
3. `Build Environments`
4. `Build Model`
5. `Build Azure Data Factory`

![1](./images/08.png)

Manual approval is required to deploy artifacts to the **`Production`** environment. When prompted, click the **`Review Deployment`** button to give approval, adding notes as required.

![1](./images/09.png)

![1](./images/10.png)

> **_Note_**: The `Build Model` workflow depends on `Deploy Data Assets` and `Deploy Environments` workflows.

![1](./images/11.png)

![1](./images/12.png)

Once the `Build Model` workflow completes the following workflows will be automatically executed:

1. `Deploy Model for Batch Inference`
2. `Deploy Model for Online Inference`

Once the `Build Azure Data Factory` workflow completes the `Deploy to Azure Data Factory` workflow will be automatically executed.

![1](./images/13.png)

> **Note:**
>
> If you do not want to deploy a model to an online or batch managed endpoint as part of this proof-of-concept you can cancel the `Deploy Model for Online Inference` or `Deploy Model for Batch Inference` workflow respectively.
>
>If you do not want to highlight Azure Data Factory integration as part of this proof-of-concept you do not need to run the `Build Azure Data Factory` workflow

Manual approval is required to deploy artifacts to the **`Production`** environment. When prompted, click the <kdb>Review Deployment</kdb> button to give approval and commence the `Upload Model to Production` job. 

This will need to be repeated for the `Deploy to Production` job across both the `Deploy Model for Batch Inference` workflow and `Deploy Model for Online Inference` workflow. The approver(s) were specified in `1.3` above.

![1](./images/14.png)

![1](./images/16.png)

Once the workflow has finished executing all artifacts will have been deployed to both **`Staging`** and **`Production`** environments.

![1](./images/15.png)

![1](./images/17.png)

![1](./images/18.png)

### Next Steps

From the <kbd>Endpoints</kbd> sidebar button in the Azure Machine Learning workspace, you can view the online managed endpoint and batch managed endpoint which have been deployed by the GitHub Actions workflow.

From the **`Real-time endpoints`** tab, online managed endpoints can be viewed. Different deployments can be tested under the **`Test`** tab. You can also interact with online managed endpoints using the CLI, SDK, and REST API.

![1](./images/19.png)

To test batch managed endpoints select the relevant endpoint under the **`Batch endpoints`** tab and select **`Create job`**. You will need to configure the job settings, data source, and output location.

![1](./images/20.png)

The `employee-attrition-inference-batch` data asset can be used for illustrative purposes.

![1](./images/22.png)

Monitoring can be performend from the managed online endpoint or Azure Monitor can be used to monitor metrics collected from the deployments as discussed in the [Batch Managed Endpoint](./.github/docs/batch-endpoint.md) and [Online Managed Endpoint](./.github/docs/online-endpoint.md) sections of the documentation.

![1](./images/21.png)

## Resource Clean-Up

There are two main tasks required to clean-up this deemo;
1. Delete the Azure Resoure Group
2. Delete the service principal

### Delete the Resource Group

From the Azure portal, navigate to the demo resource group and select <kbd>Delete resource group</kbd> toolbar button. This will then prompt a confirmation screen, requiring the reourse group name to be entered and the <kbd>Delete</kbd> button to be selected.

This will process will take 5/10mins to complete, it can be montiored via the <kbd>Notification</kbd> toolbar button, represented by the :bell: on the blue stripe. 

### Delete the Service Principle

From the Azure - Cloud CLI, run the following command with your service principal ID in bash.

```bash

az ad sp delete --id <service-principal-name>
```

## Related Resources

You might also find these references useful:

- [Using environments for deployment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Understanding GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions)
