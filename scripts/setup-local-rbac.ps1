# ============================================================================
# Grant RBAC Permissions for Local Development
# ============================================================================
# This script grants your user account the necessary RBAC permissions to
# access Azure AI Search and Azure OpenAI services using Azure CLI authentication.
#
# Prerequisites:
# - Azure CLI installed and logged in (az login)
# - Contributor or Owner role on the resource group
#
# Usage:
#   .\scripts\setup-local-rbac.ps1
# ============================================================================

param(
    [string]$SubscriptionId = "",
    [string]$ResourceGroup = "rg-wm-dev-001",
    [string]$SearchServiceName = "srch-wm-dev-001",
    [string]$OpenAiServiceName = "oai-wm-dev-001"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Setting up RBAC permissions for local development" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Get subscription ID if not provided
if ([string]::IsNullOrWhiteSpace($SubscriptionId)) {
    Write-Host "Getting current subscription..." -ForegroundColor Yellow
    $SubscriptionId = az account show --query id -o tsv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to get subscription ID. Please run 'az login' first."
        exit 1
    }
    Write-Host "Using subscription: $SubscriptionId" -ForegroundColor Green
    Write-Host ""
}

# Get current user's object ID
Write-Host "Getting your user object ID..." -ForegroundColor Yellow
$userObjectId = az ad signed-in-user show --query id -o tsv
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to get user object ID. Please ensure you're logged in with 'az login'."
    exit 1
}
Write-Host "User Object ID: $userObjectId" -ForegroundColor Green
Write-Host ""

# Build resource scopes
$searchScope = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.Search/searchServices/$SearchServiceName"
$openAiScope = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.CognitiveServices/accounts/$OpenAiServiceName"

# Grant Search Index Data Contributor role
Write-Host "Granting 'Search Index Data Contributor' role..." -ForegroundColor Yellow
az role assignment create `
    --role "Search Index Data Contributor" `
    --assignee $userObjectId `
    --scope $searchScope `
    --output none

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Search Index Data Contributor role granted" -ForegroundColor Green
} else {
    Write-Host "⚠ Role may already be assigned or you don't have permission to grant it" -ForegroundColor Yellow
}
Write-Host ""

# Grant Cognitive Services OpenAI User role
Write-Host "Granting 'Cognitive Services OpenAI User' role..." -ForegroundColor Yellow
az role assignment create `
    --role "Cognitive Services OpenAI User" `
    --assignee $userObjectId `
    --scope $openAiScope `
    --output none

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Cognitive Services OpenAI User role granted" -ForegroundColor Green
} else {
    Write-Host "⚠ Role may already be assigned or you don't have permission to grant it" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "RBAC setup complete!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify your .env file has the correct endpoints" -ForegroundColor White
Write-Host "2. Wait 2-3 minutes for RBAC permissions to propagate" -ForegroundColor White
Write-Host "3. Start your application with: uv run fastapi dev src/backend/api/main.py" -ForegroundColor White
Write-Host ""
