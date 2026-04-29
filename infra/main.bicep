metadata name = 'Intelligent Demand-Supply Matching Infrastructure'
metadata description = 'Deploys Azure AI Search and Azure OpenAI for semantic matching workload.'

/* =========================================================================
   IMPORTS
   ========================================================================= */

import { DeploymentConfig } from './types.bicep'

/* =========================================================================
   PARAMETERS
   ========================================================================= */

@description('Common deployment configuration.')
param config DeploymentConfig

@description('Azure region for resources. Defaults to resource group location.')
param location string = resourceGroup().location

@description('Tags to apply to all resources.')
param tags object = {}

/* =========================================================================
   AI SEARCH PARAMETERS
   ========================================================================= */

@description('AI Search service SKU.')
@allowed(['basic', 'standard', 'standard2', 'standard3', 'storage_optimized_l1', 'storage_optimized_l2'])
param searchSku string = 'basic'

@description('Number of search replicas (1-12).')
@minValue(1)
@maxValue(12)
param searchReplicaCount int = 1

@description('Number of search partitions (1, 2, 3, 4, 6, or 12).')
@allowed([1, 2, 3, 4, 6, 12])
param searchPartitionCount int = 1

@description('Enable public network access for AI Search.')
param searchEnablePublicAccess bool = true

/* =========================================================================
   AZURE OPENAI PARAMETERS
   ========================================================================= */

@description('Azure OpenAI service SKU.')
@allowed(['S0'])
param openAiSku string = 'S0'

@description('Enable public network access for Azure OpenAI.')
param openAiEnablePublicAccess bool = true

@description('Deployment name for the embedding model.')
param embeddingDeploymentName string = 'text-embedding-3-small'

@description('Embedding model name.')
param embeddingModelName string = 'text-embedding-3-small'

@description('Embedding model version.')
param embeddingModelVersion string = '1'

@description('Embedding deployment capacity (in thousands of tokens per minute).')
@minValue(1)
param embeddingCapacity int = 120

@description('Embedding deployment SKU name.')
@allowed(['Standard', 'GlobalStandard', 'GlobalBatch'])
param embeddingSkuName string = 'GlobalStandard'

/* =========================================================================
   MODULES
   ========================================================================= */

module aiSearch './modules/ai-search.bicep' = {
  name: 'deploy-ai-search'
  params: {
    name: 'srch-${config.resourcePrefix}-${config.environment}-${config.instance}'
    location: location
    tags: tags
    sku: searchSku
    replicaCount: searchReplicaCount
    partitionCount: searchPartitionCount
    enablePublicAccess: searchEnablePublicAccess
  }
}

module openAi './modules/openai.bicep' = {
  name: 'deploy-openai'
  params: {
    name: 'oai-${config.resourcePrefix}-${config.environment}-${config.instance}'
    location: location
    tags: tags
    sku: openAiSku
    enablePublicAccess: openAiEnablePublicAccess
    embeddingDeploymentName: embeddingDeploymentName
    embeddingModelName: embeddingModelName
    embeddingModelVersion: embeddingModelVersion
    embeddingCapacity: embeddingCapacity
    embeddingSkuName: embeddingSkuName
  }
}

/* =========================================================================
   OUTPUTS
   ========================================================================= */

@description('AI Search service name.')
output searchServiceName string = aiSearch.outputs.name

@description('AI Search service endpoint.')
output searchServiceEndpoint string = aiSearch.outputs.endpoint

@description('AI Search service resource ID.')
output searchServiceId string = aiSearch.outputs.id

@description('Azure OpenAI service name.')
output openAiServiceName string = openAi.outputs.name

@description('Azure OpenAI service endpoint.')
output openAiServiceEndpoint string = openAi.outputs.endpoint

@description('Azure OpenAI service resource ID.')
output openAiServiceId string = openAi.outputs.id

@description('Embedding model deployment name.')
output embeddingDeploymentName string = openAi.outputs.embeddingDeploymentName
