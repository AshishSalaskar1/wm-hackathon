using './main.bicep'

/* =========================================================================
   DEPLOYMENT CONFIGURATION
   ========================================================================= */

param config = {
  resourcePrefix: 'wm'
  environment: 'dev'
  instance: '001'
}

param location = 'swedencentral'  // Supports Azure OpenAI embeddings

param tags = {
  application: 'intelligent-matching'
  environment: 'dev'
  managedBy: 'bicep'
}

/* =========================================================================
   AI SEARCH CONFIGURATION
   ========================================================================= */

param searchSku = 'basic'
param searchReplicaCount = 1
param searchPartitionCount = 1
param searchEnablePublicAccess = true

/* =========================================================================
   AZURE OPENAI CONFIGURATION
   ========================================================================= */

param openAiSku = 'S0'
param openAiEnablePublicAccess = true
param embeddingDeploymentName = 'text-embedding-3-small'
param embeddingModelName = 'text-embedding-3-small'
param embeddingModelVersion = '1'
param embeddingCapacity = 120
param embeddingSkuName = 'GlobalStandard'
