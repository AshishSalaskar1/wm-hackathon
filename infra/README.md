# Infrastructure

Bicep templates for deploying Azure AI Search and Azure OpenAI services for the Intelligent Demand-Supply Matching application.

## Architecture

The infrastructure consists of two core Azure services:

| Resource | Purpose | Configuration |
|----------|---------|---------------|
| **Azure AI Search** | Vector indexing and hybrid retrieval (dense + sparse) for supply profiles and job descriptions | Basic SKU, 1 replica, 1 partition, semantic search enabled |
| **Azure OpenAI** | Generate embeddings using text-embedding-3-small model | S0 SKU, 120K TPM capacity |

## Prerequisites

- Azure CLI (`az`) version 2.60 or later
- Azure subscription with permissions to create resources
- Bicep CLI (included with Azure CLI 2.20+)

## Quick Start

### 1. Login to Azure

```bash
az login
az account set --subscription <subscription-id>
```

### 2. Create a resource group

```bash
az group create \
  --name rg-wm-dev-001 \
  --location swedencentral
```

### 3. Deploy the infrastructure

**Using parameter file:**

```bash
az deployment group create \
  --resource-group rg-wm-dev-001 \
  --template-file main.bicep \
  --parameters main.bicepparam
```

**Using inline parameters:**

```bash
az deployment group create \
  --resource-group rg-wm-dev-001 \
  --template-file main.bicep \
  --parameters config='{"resourcePrefix":"wm","environment":"dev","instance":"001"}' \
               location=swedencentral
```

### 4. Retrieve outputs

```bash
az deployment group show \
  --resource-group rg-wm-dev-001 \
  --name main \
  --query properties.outputs
```

## Configuration

### Deployment Configuration

Edit `main.bicepparam` to customize the deployment:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `config.resourcePrefix` | Resource name prefix | `wm` |
| `config.environment` | Environment (dev/test/prod) | `dev` |
| `config.instance` | Instance identifier | `001` |
| `location` | Azure region | `swedencentral` |

### AI Search Configuration

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `searchSku` | AI Search SKU | `basic` | `basic`, `standard`, `standard2`, `standard3`, `storage_optimized_l1`, `storage_optimized_l2` |
| `searchReplicaCount` | Number of replicas | `1` | 1-12 |
| `searchPartitionCount` | Number of partitions | `1` | 1, 2, 3, 4, 6, 12 |
| `searchEnablePublicAccess` | Enable public network access | `true` | `true`, `false` |

### Azure OpenAI Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `openAiSku` | Azure OpenAI SKU | `S0` |
| `embeddingDeploymentName` | Embedding model deployment name | `text-embedding-3-small` |
| `embeddingModelName` | Embedding model name | `text-embedding-3-small` |
| `embeddingModelVersion` | Embedding model version | `1` |
| `embeddingCapacity` | Tokens per minute (thousands) | `120` |
| `openAiEnablePublicAccess` | Enable public network access | `true` |

## Resource Naming Convention

Resources follow Azure naming conventions:

| Resource Type | Pattern | Example |
|---------------|---------|---------|
| AI Search | `srch-{prefix}-{env}-{instance}` | `srch-wm-dev-001` |
| Azure OpenAI | `oai-{prefix}-{env}-{instance}` | `oai-wm-dev-001` |

## Outputs

After deployment, the following outputs are available:

| Output | Description |
|--------|-------------|
| `searchServiceName` | AI Search service name |
| `searchServiceEndpoint` | AI Search HTTPS endpoint |
| `searchServiceId` | AI Search resource ID |
| `openAiServiceName` | Azure OpenAI service name |
| `openAiServiceEndpoint` | Azure OpenAI HTTPS endpoint |
| `openAiServiceId` | Azure OpenAI resource ID |
| `embeddingDeploymentName` | Embedding model deployment name |

## Local Development Setup

After deployment, you need to configure your local environment to connect to the Azure resources.

### 1. Copy Environment Template

```bash
# Copy the example file to create your local .env
cp .env.example .env
```

The `.env` file is pre-configured with the correct resource names based on your deployment:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://oai-wm-dev-001.openai.azure.com/
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://srch-wm-dev-001.search.windows.net
AZURE_SEARCH_SUPPLY_INDEX=supply-profiles
AZURE_JD_SEARCH_INDEX_NAME=jd-index

# Matching Configuration
RETRIEVAL_STRATEGY=dense
RETRIEVAL_TOP_N=10
MATCH_SCORE_THRESHOLD=70
```

### 2. Setup RBAC Permissions

The application uses **Azure CLI authentication** (no API keys required). Grant yourself the necessary permissions:

**Option A: Use the helper script** (recommended)

```powershell
# Run the RBAC setup script
.\scripts\setup-local-rbac.ps1
```

**Option B: Manual setup**

```powershell
# Get your user object ID
$userObjectId = az ad signed-in-user show --query id -o tsv

# Get your subscription ID
$subscriptionId = az account show --query id -o tsv

# Grant Search Index Data Contributor role
az role assignment create `
  --role "Search Index Data Contributor" `
  --assignee $userObjectId `
  --scope "/subscriptions/$subscriptionId/resourceGroups/rg-wm-dev-001/providers/Microsoft.Search/searchServices/srch-wm-dev-001"

# Grant Cognitive Services OpenAI User role
az role assignment create `
  --role "Cognitive Services OpenAI User" `
  --assignee $userObjectId `
  --scope "/subscriptions/$subscriptionId/resourceGroups/rg-wm-dev-001/providers/Microsoft.CognitiveServices/accounts/oai-wm-dev-001"
```

### 3. Verify Setup

Wait 2-3 minutes for RBAC permissions to propagate, then test connectivity:

```bash
# Verify Azure CLI login
az account show

# Test API connectivity (requires backend running)
curl http://localhost:8000/health
```

## Authentication

Both services use **role-based access control (RBAC)** without API keys:

### Local Development
- Uses **DefaultAzureCredential** from Azure Identity SDK
- Authenticates via Azure CLI (`az login`)
- Requires RBAC roles: `Search Index Data Contributor` and `Cognitive Services OpenAI User`
- No API keys or connection strings needed

### Production Deployment
- Uses **Managed Identity** (automatically configured in Azure Container Apps/App Service)
- Same RBAC roles assigned to the managed identity
- More secure than key-based authentication

## Retrieve Deployment Outputs

Use Azure CLI to retrieve deployment information:

```bash
# View all outputs
az deployment group show \
  --resource-group rg-wm-dev-001 \
  --name main \
  --query properties.outputs

# Get specific values
SEARCH_ENDPOINT=$(az deployment group show \
  --resource-group rg-wm-dev-001 \
  --name main \
  --query properties.outputs.searchServiceEndpoint.value -o tsv)

OPENAI_ENDPOINT=$(az deployment group show \
  --resource-group rg-wm-dev-001 \
  --name main \
  --query properties.outputs.openAiServiceEndpoint.value -o tsv)

echo "Search: $SEARCH_ENDPOINT"
echo "OpenAI: $OPENAI_ENDPOINT"
```

## Clean Up

To delete all deployed resources:

```bash
az group delete \
  --name rg-wm-dev-001 \
  --yes \
  --no-wait
```

## Troubleshooting

### Deployment Failures

Check deployment status:

```bash
az deployment group list \
  --resource-group rg-wm-dev-001 \
  --query "[].{Name:name, State:properties.provisioningState}" \
  --output table
```

View detailed error messages:

```bash
az deployment group show \
  --resource-group rg-wm-dev-001 \
  --name main \
  --query properties.error
```

### Quota Issues

If you encounter quota errors for Azure OpenAI:

1. Check your subscription quota: `az cognitiveservices account list-usage`
2. Request quota increase via Azure Portal
3. Try a different region with available capacity

## Next Steps

1. Deploy the infrastructure using the commands above
2. Configure application environment variables with deployment outputs
3. Set up RBAC roles for the application's managed identity
4. Create AI Search indexes for supply profiles and job descriptions
5. Test the embedding generation and search functionality
