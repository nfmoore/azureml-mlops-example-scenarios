//********************************************************
// Parameters
//********************************************************

// The location of the resource group. Defaults to the location of the resource group.
param deploymentLocation string = resourceGroup().location

// The name of the Azure Data Factory.
param dataFactoryName string

// The name of the Key Vault used to store the service principal secret.
param dataFactoryKeyVaultName string

// The client ID of the service principal used to authenticate with Azure services.
param servicePrincipalClientId string

// Determines whether to add repository configuration to the data factory. Defaults to false.
param addRepositoryConfiguration bool = false

// The name of the repository account to use for the data factory.
param repositoryAccountName string = ''

// The name of the repository to use for the data factory.
param dataFactoryRepositoryName string = ''

// The name of the collaboration branch to use for the data factory.
param collaborationBranch string = ''

// The root folder for the repository.
param rootFolder string = ''

// The secret for the service principal used to authenticate with Azure services.
@secure()
param servicePrincipalSecret string

//********************************************************
// Resources
//********************************************************

// Azure Data Factory
// This resource deploys an Azure Data Factory instance with optional repository configuration.
resource r_dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: dataFactoryName
  location: deploymentLocation
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
// This resource deploys an Azure Key Vault instance to store the service principal secret for the Azure Data Factory.
resource r_dataFactoryKeyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: dataFactoryKeyVaultName
  location: deploymentLocation
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

// Azure Data Factory Key Vault Client ID Secret
// This resource creates a secret in the Azure Key Vault to store the client ID for the service principal used to authenticate with Azure services.
resource r_dataFactoryKeyVaultSecret_clientId 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = {
  parent: r_dataFactoryKeyVault
  name: 'clientId'
  properties: {
    value: servicePrincipalClientId
  }
}

// Azure Data Factory Key Vault Client Secret Secret
// This resource creates a secret in the Azure Key Vault to store the client secret for the service principal used to authenticate with Azure services.
resource r_dataFactoryKeyVaultSecret_clientSecret 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = {
  parent: r_dataFactoryKeyVault
  name: 'clientSecret'
  properties: {
    value: servicePrincipalSecret
  }
}
