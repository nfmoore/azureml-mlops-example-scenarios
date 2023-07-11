//********************************************************
// Parameters
//********************************************************

// Workload identifier used to create unique names for resources.
@description('A unique identifier for the workload.')
@minLength(2)
@maxLength(6)
param workloadIdentifier string = substring(uniqueString(resourceGroup().id), 1, 6)

// Staging environment identifier used to create unique names for resources.
@description('A unique identifier for the staging environment.')
@minLength(2)
@maxLength(8)
param stagingEnvironmentIdentifier string = '001'

// Staging environment name used to create unique names for resources.
@description('A name for the staging environment.')
@minLength(2)
@maxLength(16)
param stagingEnvironmentName string = 'Staging'

// Production environment identifier used to create unique names for resources.
@description('A unique identifier for the production environment.')
@minLength(2)
@maxLength(8)
param productionEnvironmentIdentifier string = '002'

// Production environment name used to create unique names for resources.
@description('A name for the production environment.')
@minLength(2)
@maxLength(16)
param productionEnvironmentName string = 'Production'

// The location of resource deployments. Defaults to the location of the resource group.
@description('The location of resource deployments.')
param deploymentLocation string = resourceGroup().location

// The client ID of the service principal used to authenticate with Azure services.
@description('The client ID of the service principal used to authenticate with Azure services.')
param servicePrincipalClientId string

// The secret for the service principal used to authenticate with Azure services.
@description('The secret for the service principal used to authenticate with Azure services.')
@secure()
param servicePrincipalSecret string

//********************************************************
// Modules
//********************************************************

// Deploy Azure ML Shared Resources
// This module deploys the shared resources for the Azure Machine Learning workspace, such as the asset registry.
module m_azureml_shared 'modules/azureml-shared.bicep' = {
  name: 'deploy_azureml_shared'
  scope: resourceGroup(resourceGroup().name)
  params: {
    deploymentLocation: deploymentLocation
    azureMLRegistryName: 'mlr${workloadIdentifier}'
  }
}

// Deploy Azure ML Workspaces
// This module deploys the Azure Machine Learning workspaces for the staging and production environments.
module m_azureml_workspaces 'modules/azureml-workspace.bicep' = [for environmentIdentifier in [ stagingEnvironmentIdentifier, productionEnvironmentIdentifier ]: {
  name: 'deploy_azureml_workspace_${environmentIdentifier}'
  params: {
    environmentName: ((environmentIdentifier == stagingEnvironmentIdentifier) ? stagingEnvironmentName : productionEnvironmentName)
    deploymentLocation: deploymentLocation
    azureMLWorkspaceName: 'mlw${workloadIdentifier}${environmentIdentifier}'
    azureMLStorageAccountName: 'stmlw${workloadIdentifier}${environmentIdentifier}'
    azuremlKeyVaultName: 'kvmlw${workloadIdentifier}${environmentIdentifier}'
    azureMLContainerRegistryName: 'crmlw${workloadIdentifier}${environmentIdentifier}'
    azureMLAppInsightsName: 'appimlw${workloadIdentifier}${environmentIdentifier}'
    logAnalyticsWorkspaceName: 'lawmlw${workloadIdentifier}${environmentIdentifier}'
    deploymentScriptName: 'ds${workloadIdentifier}${environmentIdentifier}'
  }
}]

//Deploy Data Factories
// This module deploys the Data factories for the staging and production environments.
module m_data_factories 'modules/data-factory.bicep' = [for environmentIdentifier in [ stagingEnvironmentIdentifier, productionEnvironmentIdentifier ]: {
  name: 'deploy_data_factory_${environmentIdentifier}'
  params: {
    deploymentLocation: deploymentLocation
    dataFactoryName: 'df${workloadIdentifier}${environmentIdentifier}'
    dataFactoryKeyVaultName: 'kvdf${workloadIdentifier}${environmentIdentifier}'
    servicePrincipalClientId: servicePrincipalClientId
    servicePrincipalSecret: servicePrincipalSecret
  }
}]
