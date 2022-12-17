//********************************************************
// General Parameters
//********************************************************

@description('Workload Identifier')
param workloadIdentifier string = substring(uniqueString(resourceGroup().id), 0, 6)

@description('Resource Instance')
param resourceInstance string = '001'

@description('Service Principal Client Id')
param servicePrincipalClientId string

@secure()
@description('Service Principal Secret')
param servicePrincipalSecret string

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

@description('Azure Machine Learning Key Vault Name')
param azuremlKeyVaultName string = 'kvmlw${workloadIdentifier}${resourceInstance}'

@description('Azure Machine Learning Key Vault Location')
param azuremlKeyVaultLocation string = resourceGroup().location

@description('Log Analytics Workspace Name')
param logAnalyticsWorkspaceName string = 'law${workloadIdentifier}${resourceInstance}'

@description('Log Analytics Workspace Location')
param logAnalyticsWorkspaceLocation string = resourceGroup().location

@description('Deployment Script Name')
param deploymentScriptName string = 'ds${workloadIdentifier}${resourceInstance}'

// @description('Azure ML Registry Name')
// param azureMLRegistryName string = 'mlr${workloadIdentifier}'

// @description('Azure ML Registry Primary Location')
// param azureMLRegistryPrimaryLocation string = resourceGroup().location

// @description('Deploy Azure ML Registry')
// param deployAzureMLRegistry bool = true

@description('Azure Data Factory Name')
param dataFactoryName string = 'adf${workloadIdentifier}${resourceInstance}'

@description('Azure Data Factory Location')
param dataFactoryLocation string = resourceGroup().location

@description('Azure Data Factory Location')
param addRepositoryConfiguration bool = false // only add for development environment

@description('Azure Data Factory Repository Name')
param dataFactoryRepositoryName string = ''

@description('Repository Account Name')
param repositoryAccountName string = ''

@description('Azure Data Factory Collaboration Branch')
param collaborationBranch string = 'main'

@description('Azure Data Factory Root Folder')
param rootFolder string = 'adf'

@description('Azure Data Factory Key Vault Name')
param dataFactoryKeyVaultName string = 'kvadf${workloadIdentifier}${resourceInstance}'

@description('Azure Data Factory Key Vault Location')
param dataFactoryKeyVaultLocation string = resourceGroup().location

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
resource r_azuremlKeyVault 'Microsoft.KeyVault/vaults@2021-10-01' = {
  name: azuremlKeyVaultName
  location: azuremlKeyVaultLocation
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
    keyVault: r_azuremlKeyVault.id
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

// Deploy Azure Machine Learning Registry
// resource r_azureMLRegistry 'Microsoft.MachineLearningServices/registries@2022-10-01-preview' = if (deployAzureMLRegistry) {
//   name: azureMLRegistryName
//   location: azureMLRegistryPrimaryLocation
//   identity: {
//     type: 'SystemAssigned'
//   }
//   properties: {
//     managedResourceGroup: {
//       resourceId: 'string'
//     }
//     regionDetails: [
//       {
//         acrDetails: [
//           {
//             systemCreatedAcrAccount: {
//               acrAccountSku: 'Premium'
//             }
//           }
//         ]
//         location: azureMLRegistryPrimaryLocation
//         storageAccountDetails: [
//           {
//             systemCreatedStorageAccount: {
//               storageAccountHnsEnabled: false
//               storageAccountType: 'Standard_GRS'
//             }
//           }
//         ]
//       }
//     ]
//   }
// }

// Azure Data Factory
resource r_dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: dataFactoryName
  location: dataFactoryLocation
  properties: {
    repoConfiguration: addRepositoryConfiguration ? {
      accountName: repositoryAccountName
      repositoryName: dataFactoryRepositoryName
      collaborationBranch: collaborationBranch
      rootFolder: rootFolder
      type: 'FactoryGitHubConfiguration'
    } : {}
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// Azure Data Factory Key Vault
resource r_dataFactoryKeyVault 'Microsoft.KeyVault/vaults@2021-10-01' = {
  name: dataFactoryKeyVaultName
  location: dataFactoryKeyVaultLocation
  properties: {
    createMode: 'default'
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    enableSoftDelete: true
    enableRbacAuthorization: false
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
    accessPolicies: [
      {
        objectId: r_dataFactory.identity.principalId
        tenantId: subscription().tenantId
        permissions: {
          secrets: [
            'get'
            'list'
          ]
        }
      }
    ]
  }
}

resource r_dataFactoryKeyVaultSecret_clientId 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: r_dataFactoryKeyVault
  name: 'client-id'
  properties: {
    value: servicePrincipalClientId
  }
}

resource r_dataFactoryKeyVaultSecret_clientSecret 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: r_dataFactoryKeyVault
  name: 'client-secret'
  properties: {
    value: servicePrincipalSecret
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
      # Upload data to data store

      SOURCE_CURATED_DATA_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/main/core/data/curated/01.csv'
      SOURCE_BATCH_INFERENCE_DATA_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/main/core/data/inference/batch/01.csv'
      DESTINATION_CURATED_DATA_PATH='./data/employee-attrition/curated/01.csv'
      DESTINATION_BATCH_INFERENCE_DATA_PATH='./data/employee-attrition/inference/batch/01.csv'

      SOURCE_CURATED_MLTABLE_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/main/core/data/curated/MLTable'
      SOURCE_BATCH_INFERENCE_MLTABLE_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/main/core/data/inference/batch/MLTable'
      SOURCE_ONLINE_INFERENCE_MLTABLE_PATH='https://raw.githubusercontent.com/nfmoore/azureml-mlops-example-scenarios/main/core/data/inference/online/MLTable'
      DESTINATION_CURATED_MLTABLE_PATH='./data/employee-attrition/curated/MLTable'
      DESTINATION_BATCH_INFERENCE_MLTABLE_PATH='./data/employee-attrition/inference/batch/MLTable'
      DESTINATION_ONLINE_INFERENCE_MLTABLE_PATH='./data/employee-attrition/inference/online/MLTable'

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

//********************************************************
// Outputs
//********************************************************
