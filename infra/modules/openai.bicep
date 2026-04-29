metadata name = 'Azure OpenAI Service'
metadata description = 'Deploys an Azure OpenAI service with a text-embedding-3-small model deployment for semantic matching.'

/* =========================================================================
   PARAMETERS
   ========================================================================= */

@description('Azure OpenAI service name.')
param name string

@description('Azure region for the OpenAI service.')
param location string

@description('Tags to apply to the resource.')
param tags object = {}

@description('Azure OpenAI service SKU.')
@allowed(['S0'])
param sku string

@description('Enable public network access.')
param enablePublicAccess bool

@description('Deployment name for the embedding model.')
param embeddingDeploymentName string

@description('Embedding model name.')
param embeddingModelName string

@description('Embedding model version.')
param embeddingModelVersion string

@description('Embedding deployment capacity (in thousands of tokens per minute).')
@minValue(1)
param embeddingCapacity int

@description('Embedding deployment SKU name.')
@allowed(['Standard', 'GlobalStandard', 'GlobalBatch'])
param embeddingSkuName string = 'GlobalStandard'

/* =========================================================================
   RESOURCES
   ========================================================================= */

resource openAiService 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  tags: tags
  kind: 'OpenAI'
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: sku
  }
  properties: {
    customSubDomainName: name
    publicNetworkAccess: enablePublicAccess ? 'Enabled' : 'Disabled'
    networkAcls: {
      defaultAction: enablePublicAccess ? 'Allow' : 'Deny'
      ipRules: []
      virtualNetworkRules: []
    }
    disableLocalAuth: false
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: openAiService
  name: embeddingDeploymentName
  sku: {
    name: embeddingSkuName
    capacity: embeddingCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: embeddingModelName
      version: embeddingModelVersion
    }
    versionUpgradeOption: 'OnceCurrentVersionExpired'
    raiPolicyName: 'Microsoft.Default'
  }
}

/* =========================================================================
   OUTPUTS
   ========================================================================= */

@description('Azure OpenAI service name.')
output name string = openAiService.name

@description('Azure OpenAI service endpoint.')
output endpoint string = openAiService.properties.endpoint

@description('Azure OpenAI service resource ID.')
output id string = openAiService.id

@description('Azure OpenAI service principal ID (system-assigned managed identity).')
output principalId string = openAiService.identity.principalId

@description('Embedding model deployment name.')
output embeddingDeploymentName string = embeddingDeployment.name
