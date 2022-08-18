//********************************************************
// General Parameters
//********************************************************

@description('Workload Identifier')
param workloadIdentifier string = substring(uniqueString(resourceGroup().id), 0, 6)

@description('Resource Instance')
param resourceInstance string = '001'

//********************************************************
// Resource Config Parameters
//********************************************************

@description('Azure Machine Learning Workspace Name')
param azureMLWorkspaceName string = 'mlw${workloadIdentifier}${resourceInstance}'

@description('Azure Machine Learning Workspace Location')
param azureMLWorkspaceLocation string = resourceGroup().location

@description('Azure Machine Learning Storage Account Name')
param azureMLStorageAccountName string = 'st${workloadIdentifier}${resourceInstance}'

@description('Azure Machine Learning Application Insights Name')
param azureMLAppInsightsName string = 'appi${workloadIdentifier}${resourceInstance}'

@description('Azure Machine Learning Container Registry Name')
param azureMLContainerRegistryName string = 'cr${workloadIdentifier}${resourceInstance}'

@description('Azure Machine Learning Compute Cluster Name')
param azureMlComputeClusterName string = 'cpu-cluster'

@description('Key Vault Name')
param keyVaultName string = 'kv${workloadIdentifier}${resourceInstance}'

@description('Key Vault Location')
param keyVaultLocation string = resourceGroup().location

@description('Log Analytics Workspace Name')
param logAnalyticsWorkspaceName string = 'law${workloadIdentifier}${resourceInstance}'

@description('Log Analytics Workspace Location')
param logAnalyticsWorkspaceLocation string = resourceGroup().location

@description('Deployment Script Name')
param deploymentScriptName string = 'ds${workloadIdentifier}${resourceInstance}'

//********************************************************
// Variables
//********************************************************

var azureRbacLogAnalyticsReaderRoleId = '73c42c96-874c-492b-b04d-ab87d138a893' // Log Analytics Reader

//********************************************************
// Resources
//********************************************************

// User assigned managed identity
// resource r_userAssignedManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = {
//   name: userAssignedManagedIdentityName
//   location: userAssignedManagedIdentityLocation
// }

// Azure ML Key Vault
resource r_keyVault 'Microsoft.KeyVault/vaults@2021-10-01' = {
  name: keyVaultName
  location: keyVaultLocation
  properties: {
    createMode: 'default'
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    enableSoftDelete: true
    enableRbacAuthorization: true
    enablePurgeProtection: true
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
    sku: {
      family: 'A'
      name: 'standard'
    }
    softDeleteRetentionInDays: 7
    tenantId: subscription().tenantId
  }
}

//Azure ML Storage Account
resource r_azureMlStorageAccount 'Microsoft.Storage/storageAccounts@2021-02-01' = {
  name: azureMLStorageAccountName
  location: azureMLWorkspaceLocation
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
  }
}

//Azure ML Application Insights
resource r_azureMlAppInsights 'Microsoft.Insights/components@2020-02-02-preview' = {
  name: azureMLAppInsightsName
  location: azureMLWorkspaceLocation
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

//Azure ML Container Registry
resource r_azureMlContainerRegistry 'Microsoft.ContainerRegistry/registries@2019-05-01' = {
  name: azureMLContainerRegistryName
  location: azureMLWorkspaceLocation
  sku: {
    name: 'Basic'
  }
  properties: {}
}

//Azure Machine Learning Workspace
resource r_azureMlWorkspace 'Microsoft.MachineLearningServices/workspaces@2021-04-01' = {
  name: azureMLWorkspaceName
  location: azureMLWorkspaceLocation
  sku: {
    name: 'basic'
    tier: 'basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: azureMLWorkspaceName
    keyVault: r_keyVault.id
    storageAccount: r_azureMlStorageAccount.id
    applicationInsights: r_azureMlAppInsights.id
    containerRegistry: r_azureMlContainerRegistry.id
  }
}

resource r_azureMlComputeCluster 'Microsoft.MachineLearningServices/workspaces/computes@2021-04-01' = {
  name: '${azureMLWorkspaceName}/${azureMlComputeClusterName}'
  location: azureMLWorkspaceLocation
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

// Deploy Log Analytics Workspace
resource r_logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2020-03-01-preview' = {
  name: logAnalyticsWorkspaceName
  location: logAnalyticsWorkspaceLocation
  properties: {
    retentionInDays: 30
    sku: {
      name: 'PerGB2018'
    }
    workspaceCapping: {
      dailyQuotaGb: 1
    }
  }
}

//********************************************************
// RBAC Role Assignments
//********************************************************

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

resource s_deploymentScript 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
  name: deploymentScriptName
  location: azureMLWorkspaceLocation
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
      SOURCE_CURATED_DATA_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/main/core/data/curated/data.csv'
      SOURCE_INFERENCE_DATA_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/main/core/data/inference/data.csv'
      DESTINATION_CURATED_DATA_PATH='./data/employee-attrition/curated/data.csv'
      DESTINATION_INFERENCE_DATA_PATH='./data/employee-attrition/inference/batch/data.csv'

      curl -o $DESTINATION_CURATED_DATA_PATH $SOURCE_CURATED_DATA_PATH --create-dirs
      curl -o $DESTINATION_INFERENCE_DATA_PATH $SOURCE_INFERENCE_DATA_PATH --create-dirs

      CONTAINER_NAME=$(az storage container list --account-name $AZURE_STORAGE_ACCOUNT --account-key $AZURE_STORAGE_KEY --query "[].name" | grep "azureml-blobstore-*" | tr -d ',' | xargs)
      az storage blob upload-batch --destination $CONTAINER_NAME --account-name $AZURE_STORAGE_ACCOUNT --account-key $AZURE_STORAGE_KEY --destination-path ./data --source ./data
    '''
  }
}

//********************************************************
// Outputs
//********************************************************
