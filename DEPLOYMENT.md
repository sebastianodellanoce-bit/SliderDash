# 🚀 Azure Deployment Guide - Streamlit Dashboard

Guida completa per deployare la dashboard Streamlit su Azure App Service.

---

## 📋 Prerequisiti

1. **Account Azure** attivo
2. **Azure CLI** installato (opzionale, ma consigliato)
3. **Git** per il deployment
4. **Credenziali GA4** già configurate localmente

---

## 🎯 Opzione 1: Azure App Service (Consigliato)

### Step 1: Creare App Service nel Portale Azure

1. Vai su [Azure Portal](https://portal.azure.com)
2. Clicca **"+ Crea una risorsa"** (Create a resource)
3. Cerca **"Web App"** o **"App Service"**
4. Clicca **"Crea"** (Create)

### Step 2: Configurare l'App Service

**Basics Tab:**
- **Subscription**: Seleziona la tua subscription
- **Resource Group**: Crea nuovo o usa esistente
- **Name**: `enpal-streamlit-dashboard` (deve essere unico)
- **Publish**: **Code**
- **Runtime stack**: **Python 3.11** o **Python 3.12**
- **Operating System**: **Linux**
- **Region**: Scegli la regione più vicina (es. West Europe)

**Pricing Tier:**
- **Free (F1)** - Per test (limitato)
- **Basic (B1)** - ~$13/mese (consigliato per produzione)
- **Standard (S1)** - ~$70/mese (più potenza)

Clicca **"Review + create"** → **"Create"**

### Step 3: Configurare le Variabili d'Ambiente

1. Vai alla tua App Service creata
2. Nel menu sinistro, vai su **"Configuration"** → **"Application settings"**
3. Clicca **"+ New application setting"** e aggiungi:

```
GA_PROPERTY_ID = il_tuo_property_id
GA_CREDENTIALS_PATH = /home/site/wwwroot/credentials/service-account-key.json
USE_DEFAULT_CREDENTIALS = false
ANTHROPIC_API_KEY = la_tua_api_key_anthropic
```

4. Clicca **"Save"**

### Step 4: Caricare il File di Credenziali

**Opzione A: Via Azure Portal (Kudu)**
1. Vai su **"Advanced Tools"** → **"Go"** (si apre Kudu)
2. Vai su **"Debug console"** → **"CMD"**
3. Naviga a `site/wwwroot/`
4. Crea cartella `credentials` se non esiste
5. Carica `service-account-key.json` nella cartella `credentials/`

**Opzione B: Via FTP**
1. Vai su **"Deployment Center"** → **"FTPS credentials"**
2. Usa un client FTP (FileZilla) per caricare il file

**Opzione C: Via Azure CLI**
```bash
az webapp deployment source config-zip \
  --resource-group <resource-group-name> \
  --name <app-name> \
  --src credentials.zip
```

### Step 5: Configurare il Startup Command

1. Vai su **"Configuration"** → **"General settings"**
2. In **"Startup Command"**, inserisci:
```bash
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
```

3. Clicca **"Save"**

### Step 6: Deployare il Codice

**Opzione A: Via Git (GitHub/Azure DevOps)**
1. Vai su **"Deployment Center"**
2. Scegli **"GitHub"** o **"Azure Repos"**
3. Connetti il tuo repository
4. Azure farà automaticamente il deploy ad ogni push

**Opzione B: Via Azure CLI**
```bash
# Login
az login

# Deploy
az webapp up \
  --name enpal-streamlit-dashboard \
  --resource-group <resource-group-name> \
  --runtime "PYTHON:3.11"
```

**Opzione C: Via VS Code Extension**
1. Installa estensione **"Azure App Service"** in VS Code
2. Clicca destro sulla cartella del progetto
3. Seleziona **"Deploy to Web App"**

**Opzione D: Via ZIP Deploy**
```bash
# Crea ZIP (escludi venv, __pycache__, etc.)
zip -r deploy.zip . -x "venv/*" "__pycache__/*" "*.pyc" ".git/*"

# Deploy
az webapp deployment source config-zip \
  --resource-group <resource-group-name> \
  --name <app-name> \
  --src deploy.zip
```

### Step 7: Verificare il Deployment

1. Vai su **"Overview"** nella tua App Service
2. Clicca sull'URL (es. `https://enpal-streamlit-dashboard.azurewebsites.net`)
3. La dashboard dovrebbe essere accessibile!

---

## 🐳 Opzione 2: Azure Container Apps (Alternativa)

Se preferisci usare Container Apps (come mostrato nella schermata):

### Step 1: Creare Container App

1. Nel portale Azure, vai su **"Container Apps"**
2. Clicca **"+ Crea"** (Create)
3. Compila i campi:
   - **Name**: `enpal-streamlit-dashboard`
   - **Resource Group**: Crea nuovo o usa esistente
   - **Container Apps Environment**: Crea nuovo

### Step 2: Creare Dockerfile

Crea un file `Dockerfile` nella root del progetto:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0", "--server.headless=true"]
```

### Step 3: Build e Push Container

```bash
# Build
docker build -t enpal-streamlit:latest .

# Tag per Azure Container Registry
docker tag enpal-streamlit:latest <registry>.azurecr.io/enpal-streamlit:latest

# Push
docker push <registry>.azurecr.io/enpal-streamlit:latest
```

### Step 4: Configurare Container App

1. Nella configurazione del Container App, imposta:
   - **Image**: `<registry>.azurecr.io/enpal-streamlit:latest`
   - **Port**: `8000`
   - **Environment Variables**: Come sopra

---

## 🔧 Troubleshooting

### Problema: App non si avvia
- Controlla i **logs** in **"Log stream"** o **"Logs"**
- Verifica che il **Startup Command** sia corretto
- Controlla che tutte le variabili d'ambiente siano impostate

### Problema: Errore "Module not found"
- Verifica che `requirements.txt` contenga tutte le dipendenze
- Controlla i **deployment logs** per errori di installazione

### Problema: Credenziali GA4 non trovate
- Verifica il path: `/home/site/wwwroot/credentials/service-account-key.json`
- Assicurati che il file sia stato caricato correttamente

### Problema: Porta non corretta
- Azure App Service usa la porta definita dalla variabile `PORT`
- Modifica `startup.sh` per usare: `--server.port=${PORT:-8000}`

---

## 📝 Note Importanti

1. **Sicurezza**: Non committare mai `credentials/service-account-key.json` nel repository
2. **Costi**: Il tier Free ha limitazioni (CPU, memoria, timeout)
3. **Scaling**: Puoi configurare auto-scaling in **"Scale out"**
4. **Custom Domain**: Puoi aggiungere un dominio personalizzato in **"Custom domains"**

---

## 🔗 Link Utili

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Streamlit Deployment Guide](https://docs.streamlit.io/deploy)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)

---

## ✅ Checklist Pre-Deployment

- [ ] `.gitignore` protegge le credenziali
- [ ] `requirements.txt` è aggiornato
- [ ] Variabili d'ambiente configurate in Azure
- [ ] File `service-account-key.json` caricato
- [ ] Startup command configurato
- [ ] Testato localmente prima del deploy

---

**Buon deployment! 🚀**

