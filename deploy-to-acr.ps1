# Script PowerShell per build e push su Azure Container Registry
# Esegui questo script dalla cartella del progetto

param(
    [Parameter(Mandatory=$true)]
    [string]$RegistryName,
    
    [Parameter(Mandatory=$false)]
    [string]$ImageName = "enpal-streamlit",
    
    [Parameter(Mandatory=$false)]
    [string]$Tag = "latest",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = ""
)

Write-Host "🐳 Azure Container Registry Deployment Script" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Verifica Azure CLI
Write-Host "1. Verificando Azure CLI..." -ForegroundColor Yellow
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "   ✅ Azure CLI trovato: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Azure CLI non trovato! Installa da: https://aka.ms/installazurecliwindows" -ForegroundColor Red
    exit 1
}

# Login ad Azure
Write-Host "2. Login ad Azure..." -ForegroundColor Yellow
az account show | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Esegui login..." -ForegroundColor Gray
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ❌ Login fallito!" -ForegroundColor Red
        exit 1
    }
}
Write-Host "   ✅ Autenticato" -ForegroundColor Green

# Login ad ACR
Write-Host "3. Login ad Azure Container Registry: $RegistryName" -ForegroundColor Yellow
az acr login --name $RegistryName
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Login ad ACR fallito! Verifica che il registro esista." -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Login ad ACR riuscito" -ForegroundColor Green

# Verifica che il Dockerfile esista
Write-Host "4. Verificando Dockerfile..." -ForegroundColor Yellow
if (-not (Test-Path "Dockerfile")) {
    Write-Host "   ❌ Dockerfile non trovato nella cartella corrente!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Dockerfile trovato" -ForegroundColor Green

# Build e push
$fullImageName = "$RegistryName.azurecr.io/$ImageName`:$Tag"
Write-Host "5. Building e pushing immagine: $fullImageName" -ForegroundColor Yellow
Write-Host "   Questo potrebbe richiedere 5-15 minuti..." -ForegroundColor Gray
Write-Host ""

az acr build --registry $RegistryName --image "$ImageName`:$Tag" .
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Build/Push fallito!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "   ✅ Build e push completati!" -ForegroundColor Green

# Verifica immagine
Write-Host "6. Verificando immagine nel registro..." -ForegroundColor Yellow
az acr repository show-tags --name $RegistryName --repository $ImageName --output table
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Immagine verificata" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Completato!" -ForegroundColor Green
Write-Host ""
Write-Host "Immagine disponibile su ACR:" -ForegroundColor Cyan
Write-Host "   $fullImageName" -ForegroundColor White
Write-Host ""
Write-Host "Ora puoi usare questa immagine in Azure Container App:" -ForegroundColor Cyan
Write-Host "   - Origine: Registro Azure Container" -ForegroundColor White
Write-Host "   - Registro: $RegistryName" -ForegroundColor White
Write-Host "   - Immagine: $ImageName" -ForegroundColor White
Write-Host "   - Tag: $Tag" -ForegroundColor White
Write-Host ""

