# Script PowerShell per build e push su Docker Hub
# Esegui questo script dalla cartella del progetto

param(
    [Parameter(Mandatory=$true)]
    [string]$DockerHubUsername,
    
    [Parameter(Mandatory=$false)]
    [string]$ImageName = "enpal-streamlit",
    
    [Parameter(Mandatory=$false)]
    [string]$Tag = "latest"
)

Write-Host "🐳 Docker Hub Deployment Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verifica che Docker sia installato
Write-Host "1. Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "   ✅ Docker trovato: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker non trovato! Installa Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verifica che Docker sia in esecuzione
Write-Host "2. Verificando che Docker sia in esecuzione..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "   ✅ Docker è in esecuzione" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker non è in esecuzione! Avvia Docker Desktop." -ForegroundColor Red
    exit 1
}

# Login a Docker Hub
Write-Host "3. Login a Docker Hub..." -ForegroundColor Yellow
Write-Host "   Inserisci la tua password Docker Hub quando richiesto" -ForegroundColor Gray
docker login -u $DockerHubUsername
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Login fallito!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Login riuscito" -ForegroundColor Green

# Build dell'immagine
$fullImageName = "$DockerHubUsername/$ImageName`:$Tag"
Write-Host "4. Building immagine: $fullImageName" -ForegroundColor Yellow
Write-Host "   Questo potrebbe richiedere 5-10 minuti..." -ForegroundColor Gray
docker build -t $fullImageName .
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Build fallita!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Build completata" -ForegroundColor Green

# Push dell'immagine
Write-Host "5. Pushing immagine su Docker Hub..." -ForegroundColor Yellow
Write-Host "   Questo potrebbe richiedere 5-15 minuti..." -ForegroundColor Gray
docker push $fullImageName
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Push fallito!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Push completato" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Completato!" -ForegroundColor Green
Write-Host ""
Write-Host "Immagine disponibile su Docker Hub:" -ForegroundColor Cyan
Write-Host "   $fullImageName" -ForegroundColor White
Write-Host ""
Write-Host "Ora puoi usare questa immagine in Azure Container App:" -ForegroundColor Cyan
Write-Host "   - Origine: Docker Hub o altri registri" -ForegroundColor White
Write-Host "   - Immagine: $DockerHubUsername/$ImageName" -ForegroundColor White
Write-Host "   - Tag: $Tag" -ForegroundColor White
Write-Host ""

