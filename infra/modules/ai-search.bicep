metadata name = 'Azure AI Search Service'
metadata description = 'Deploys an Azure AI Search service with configurable SKU, replicas, and partitions for vector and semantic search.'

/* =========================================================================
   PARAMETERS
   ========================================================================= */

@description('AI Search service name.')
param name string

@description('Azure region for the AI Search service.')
param location string

@description('Tags to apply to the resource.')
param tags object = {}

@description('AI Search service SKU.')
@allowed(['basic', 'standard', 'standard2', 'standard3', 'storage_optimized_l1', 'storage_optimized_l2'])
param sku string

@description('Number of search replicas (1-12).')
@minValue(1)
@maxValue(12)
param replicaCount int

@description('Number of search partitions (1, 2, 3, 4, 6, or 12).')
@allowed([1, 2, 3, 4, 6, 12])
param partitionCount int

@description('Enable public network access.')
param enablePublicAccess bool

@description('Enable semantic search (requires standard or higher SKU).')
param enableSemanticSearch bool = true

/* =========================================================================
   RESOURCES
   ========================================================================= */

resource searchService 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: sku
  }
  properties: {
    replicaCount: replicaCount
    partitionCount: partitionCount
    hostingMode: 'default'
    publicNetworkAccess: enablePublicAccess ? 'enabled' : 'disabled'
    networkRuleSet: {
      ipRules: []
    }
    encryptionWithCmk: {
      enforcement: 'Unspecified'
    }
    disableLocalAuth: false
    authOptions: {
      apiKeyOnly: {}
    }
    semanticSearch: enableSemanticSearch ? 'standard' : 'disabled'
  }
}

/* =========================================================================
   OUTPUTS
   ========================================================================= */

@description('AI Search service name.')
output name string = searchService.name

@description('AI Search service endpoint.')
output endpoint string = 'https://${searchService.name}.search.windows.net'

@description('AI Search service resource ID.')
output id string = searchService.id

@description('AI Search service principal ID (system-assigned managed identity).')
output principalId string = searchService.identity.principalId
