//********************************************************
// Parameters
//********************************************************

// The environment name.
param environmentName string

// The location of the resource group. Defaults to the location of the resource group.
param deploymentLocation string = resourceGroup().location

// The name of the Azure Machine Learning workspace.
param azureMLWorkspaceName string

// The name of the Azure Machine Learning compute cluster.
param azureMlComputeClusterName string = 'cpu-cluster'

// The name of the storage account used by the Azure Machine Learning workspace.
param azureMLStorageAccountName string

// The name of the Key Vault used by the Azure Machine Learning workspace.
param azuremlKeyVaultName string

// The name of the container registry used by the Azure Machine Learning workspace.
param azureMLContainerRegistryName string

// The name of the Application Insights instance used by the Azure Machine Learning workspace.
param azureMLAppInsightsName string

// The name of the Log Analytics workspace used by the Azure Machine Learning workspace.
param logAnalyticsWorkspaceName string

// The name of the Deployment Script used to upload data to the Azure Machine Learning workspace.
param deploymentScriptName string

//********************************************************
// Variables
//********************************************************

// The ID of the Azure RBAC role assigned to the Log Analytics Reader.
var azureRbacLogAnalyticsReaderRoleId = '73c42c96-874c-492b-b04d-ab87d138a893' // Log Analytics Reader

// The tags for the Azure resources created by this module.
var tags = {
  Environment: environmentName
}

//********************************************************
// Resources
//********************************************************

// Azure ML Workspace
// This resource deploys an Azure Machine Learning workspace.
resource r_azureMlWorkspace 'Microsoft.MachineLearningServices/workspaces@2022-05-01' = {
  name: azureMLWorkspaceName
  location: deploymentLocation
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    tier: 'Basic'
    name: 'Basic'
  }
  properties: {
    friendlyName: '${environmentName} Workspace'
    storageAccount: r_azureMlStorageAccount.id
    keyVault: r_azuremlKeyVault.id
    applicationInsights: r_azureMlAppInsights.id
    containerRegistry: r_azureMlContainerRegistry.id
    publicNetworkAccess: 'Enabled'
  }
}

// Azure ML Compute Cluster
// This resource deploys a compute cluster to the Azure Machine Learning workspace.
resource r_azureMlComputeCluster 'Microsoft.MachineLearningServices/workspaces/computes@2021-04-01' = {
  name: '${azureMLWorkspaceName}/${azureMlComputeClusterName}'
  location: deploymentLocation
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    computeType: 'AmlCompute'
    properties: {
      vmSize: 'Standard_DS11_v2'
      vmPriority: 'Dedicated'
      scaleSettings: {
        maxNodeCount: 4
        minNodeCount: 0
      }
    }
  }
  dependsOn: [ r_azureMlWorkspace ]
}

// Azure Key Vault
// This resource deploys an Azure Key Vault instance to store secrets for the Azure Machine Learning workspace.
resource r_azuremlKeyVault 'Microsoft.KeyVault/vaults@2019-09-01' = {
  name: azuremlKeyVaultName
  location: deploymentLocation
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      name: 'standard'
      family: 'A'
    }
    accessPolicies: []
  }
}

// Azure ML Storage Account
// This resource deploys an Azure Storage account to store data for the Azure Machine Learning workspace.
resource r_azureMlStorageAccount 'Microsoft.Storage/storageAccounts@2019-04-01' = {
  name: azureMLStorageAccountName
  location: deploymentLocation
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    encryption: {
      services: {
        blob: {
          enabled: true
        }
        file: {
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    isHnsEnabled: false
  }
}

//Azure ML Container Registry
// This resource deploys an Azure Container Registry instance to store Docker images for the Azure Machine Learning workspace.
resource r_azureMlContainerRegistry 'Microsoft.ContainerRegistry/registries@2019-05-01' = {
  name: azureMLContainerRegistryName
  location: deploymentLocation
  tags: tags
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: true
  }
}

//Azure ML Application Insights
// This resource deploys an Azure Application Insights instance to monitor the Azure Machine Learning workspace.
resource r_azureMlAppInsights 'Microsoft.Insights/components@2020-02-02-preview' = {
  name: azureMLAppInsightsName
  location: deploymentLocation
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Redfield'
    Request_Source: 'IbizaMachineLearningExtension'
    WorkspaceResourceId: r_logAnalyticsWorkspace.id
  }
}

// Log Analytics Workspace
// This resource deploys an Azure Log Analytics workspace to store logs for the Azure Machine Learning workspace.
resource r_logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2020-08-01' = {
  name: logAnalyticsWorkspaceName
  location: deploymentLocation
  tags: tags
  properties: {}
}

//********************************************************
// RBAC Role Assignments
//********************************************************

// This resource deploys an Azure role assignment for the Azure Machine Learning compute cluster to read logs from the Azure Log Analytics workspace.
resource r_azureMlComputeClusterLogAnalyticsWorkspaceAssignment 'Microsoft.Authorization/roleAssignments@2020-08-01-preview' = {
  name: guid(azureMlComputeClusterName, logAnalyticsWorkspaceName, 'Log Analytics Reader')
  scope: r_logAnalyticsWorkspace
  properties: {
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', azureRbacLogAnalyticsReaderRoleId)
    principalId: r_azureMlComputeCluster.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

//********************************************************
// Deployment Scripts
//********************************************************

// Deployment Script
// The resource executes a script that is used to upload data to the Azure Machine Learning workspace.
resource s_deploymentScript 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
  name: deploymentScriptName
  location: deploymentLocation
  kind: 'AzureCLI'
  properties: {
    azCliVersion: '2.30.0'
    timeout: 'PT5M'
    retentionInterval: 'PT1H'
    environmentVariables: [
      {
        name: 'AZURE_STORAGE_ACCOUNT'
        value: r_azureMlStorageAccount.name
      }
      {
        name: 'AZURE_STORAGE_KEY'
        secureValue: r_azureMlStorageAccount.listKeys().keys[0].value
      }
    ]
    scriptContent: '''
      # Upload data to data store

      SOURCE_CURATED_DATA_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/development/core/data/curated/01.csv'
      SOURCE_BATCH_INFERENCE_DATA_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/development/core/data/inference/batch/01.csv'
      DESTINATION_CURATED_DATA_PATH='./data/uci-credit-card-default/curated/01.csv'
      DESTINATION_BATCH_INFERENCE_DATA_PATH='./data/uci-credit-card-default/inference/batch/01.csv'

      SOURCE_CURATED_MLTABLE_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/development/core/data/curated/MLTable'
      SOURCE_BATCH_INFERENCE_MLTABLE_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/development/core/data/inference/batch/MLTable'
      SOURCE_ONLINE_INFERENCE_MLTABLE_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/development/core/data/inference/online/MLTable'
      DESTINATION_CURATED_MLTABLE_PATH='./data/uci-credit-card-default/curated/MLTable'
      DESTINATION_BATCH_INFERENCE_MLTABLE_PATH='./data/uci-credit-card-default/inference/batch/MLTable'
      DESTINATION_ONLINE_INFERENCE_MLTABLE_PATH='./data/uci-credit-card-default/inference/online/MLTable'

      curl -o $DESTINATION_CURATED_DATA_PATH $SOURCE_CURATED_DATA_PATH --create-dirs
      curl -o $DESTINATION_BATCH_INFERENCE_DATA_PATH $SOURCE_BATCH_INFERENCE_DATA_PATH --create-dirs

      curl -o $DESTINATION_CURATED_MLTABLE_PATH $SOURCE_CURATED_MLTABLE_PATH --create-dirs
      curl -o $DESTINATION_BATCH_INFERENCE_MLTABLE_PATH $SOURCE_BATCH_INFERENCE_MLTABLE_PATH --create-dirs
      curl -o $DESTINATION_ONLINE_INFERENCE_MLTABLE_PATH $SOURCE_ONLINE_INFERENCE_MLTABLE_PATH --create-dirs

      CONTAINER_NAME=$(az storage container list --account-name $AZURE_STORAGE_ACCOUNT --account-key $AZURE_STORAGE_KEY --query "[].name" | grep "azureml-blobstore-*" | tr -d ',' | xargs)
      az storage blob upload-batch --destination $CONTAINER_NAME --account-name $AZURE_STORAGE_ACCOUNT --account-key $AZURE_STORAGE_KEY --destination-path ./data --source ./data

      '''
  }
}
