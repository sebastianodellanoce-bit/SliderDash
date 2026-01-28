# ⚡ Quick Deploy Guide - Azure App Service

## 🎯 Deployment Rapido (5 minuti)

### 1. Crea App Service in Azure Portal

1. Vai su [portal.azure.com](https://portal.azure.com)
2. **"+ Crea una risorsa"** → Cerca **"Web App"** → **"Crea"**
3. Compila:
   - **Name**: `enpal-streamlit-dashboard` (unico)
   - **Runtime**: Python 3.11 (Linux)
   - **Pricing**: Basic B1 (~$13/mese) o Free F1 (test)

### 2. Configura Variabili d'Ambiente

**Configuration** → **Application settings** → **+ New application setting**:

```
GA_PROPERTY_ID = <il_tuo_property_id>
GA_CREDENTIALS_PATH = /home/site/wwwroot/credentials/service-account-key.json
USE_DEFAULT_CREDENTIALS = false
ANTHROPIC_API_KEY = <la_tua_api_key>
```

### 3. Carica Credenziali

**Advanced Tools** → **Go** (Kudu) → **Debug console** → **CMD**:
- Naviga a `site/wwwroot/`
- Crea cartella `credentials`
- Carica `service-account-key.json`

### 4. Startup Command

**Configuration** → **General settings** → **Startup Command**:
```bash
python -m streamlit run app.py --server.port=${PORT:-8000} --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false
```

### 5. Deploy Codice

**Opzione A: VS Code**
- Installa estensione "Azure App Service"
- Clic destro progetto → **"Deploy to Web App"**

**Opzione B: Git**
- **Deployment Center** → Connetti GitHub/Azure Repos
- Push automatico ad ogni commit

**Opzione C: ZIP**
```bash
zip -r deploy.zip . -x "venv/*" "__pycache__/*" ".git/*"
# Poi carica via Azure Portal → Deployment Center → ZIP Deploy
```

### 6. Testa!

Vai su: `https://<nome-app>.azurewebsites.net`

---

## 🐳 Container Apps (Alternativa)

Se preferisci Container Apps:

1. **Container Apps** → **+ Crea**
2. Usa il `Dockerfile` incluso nel progetto
3. Build e push su Azure Container Registry
4. Configura variabili d'ambiente come sopra

---

## ❗ Problemi Comuni

- **App non parte**: Controlla **Log stream** per errori
- **Modulo mancante**: Verifica `requirements.txt`
- **Credenziali non trovate**: Controlla path in `GA_CREDENTIALS_PATH`

---

Vedi `DEPLOYMENT.md` per la guida completa! 📚

