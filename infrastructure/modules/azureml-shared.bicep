//********************************************************
// Parameters
//********************************************************

// The location of the resource group. Defaults to the location of the resource group.
param deploymentLocation string = resourceGroup().location

// The name of the Azure Machine Learning registry.
param azureMLRegistryName string

//********************************************************
// Resources
//********************************************************

// Azure Machine Learning Registry
// This resource deploys an Azure Machine Learning registry.
resource r_azureMLRegistry 'Microsoft.MachineLearningServices/registries@2022-10-01-preview' = {
  name: azureMLRegistryName
  location: deploymentLocation
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    regionDetails: [
      {
        location: deploymentLocation
        storageAccountDetails: [
          {
            systemCreatedStorageAccount: {
              storageAccountHnsEnabled: false
              storageAccountType: 'Standard_LRS'
            }
          }
        ]
        acrDetails: [
          {
            systemCreatedAcrAccount: {
              acrAccountSku: 'Premium'
            }
          }
        ]
      }
    ]
  }
}
