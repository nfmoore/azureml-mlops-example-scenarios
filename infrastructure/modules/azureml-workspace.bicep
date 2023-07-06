//********************************************************
// Parameters
//********************************************************

// The location of the resource group. Defaults to the location of the resource group.
param deploymentLocation string = resourceGroup().location

// The name of the Azure Machine Learning workspace.
param azureMLWorkspaceName string

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

//********************************************************
// Resources
//********************************************************

// Azure ML Workspace
// This resource deploys an Azure Machine Learning workspace.
resource r_azureMlWorkspace 'Microsoft.MachineLearningServices/workspaces@2022-12-01-preview' = {
  name: azureMLWorkspaceName
  location: deploymentLocation
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    keyVault: r_azuremlKeyVault.id
    storageAccount: r_azureMlStorageAccount.id
    applicationInsights: r_azureMlAppInsights.id
    containerRegistry: r_azureMlContainerRegistry.id
  }
}

// Azure Key Vault
// This resource deploys an Azure Key Vault instance to store secrets for the Azure Machine Learning workspace.
resource r_azuremlKeyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: azuremlKeyVaultName
  location: deploymentLocation
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

// Azure ML Storage Account
// This resource deploys an Azure Storage account to store data for the Azure Machine Learning workspace.
resource r_azureMlStorageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: azureMLStorageAccountName
  location: deploymentLocation
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

//Azure ML Container Registry
// This resource deploys an Azure Container Registry instance to store Docker images for the Azure Machine Learning workspace.
resource r_azureMlContainerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: azureMLContainerRegistryName
  location: deploymentLocation
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

//Azure ML Application Insights
// This resource deploys an Azure Application Insights instance to monitor the Azure Machine Learning workspace.
resource r_azureMlAppInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: azureMLAppInsightsName
  location: deploymentLocation
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: r_logAnalyticsWorkspace.id
    Flow_Type: 'Bluefield'
  }
}

// Log Analytics Workspace
// This resource deploys an Azure Log Analytics workspace to store logs for the Azure Machine Learning workspace.
resource r_logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsWorkspaceName
  location: deploymentLocation
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Disabled'
    workspaceCapping: {
      dailyQuotaGb: 1
    }
  }
}
