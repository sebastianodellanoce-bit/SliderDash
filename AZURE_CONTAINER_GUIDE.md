# 🐳 Guida Completa Azure Container Apps - Per Principianti

## 📚 Cos'è un Container?

Pensa a un container come a una **scatola** che contiene:
- Il tuo codice Python
- Tutte le librerie necessarie (pandas, streamlit, etc.)
- Le configurazioni
- **Tutto quello che serve per far funzionare l'app**

Questa "scatola" può essere spostata ovunque e funzionerà sempre allo stesso modo!

---

## 🔓 Immagine PUBBLICA vs 🔒 PRIVATA

### Immagine PUBBLICA (Docker Hub)
- ✅ **Gratuita** e facile da usare
- ✅ Chiunque può vedere/scaricare la tua immagine
- ✅ Non serve configurare autenticazione
- ⚠️ **Attenzione**: Non mettere mai credenziali/secrets nell'immagine pubblica!

**Quando usarla:**
- Per test e sviluppo
- Se non hai dati sensibili nel container
- Per iniziare velocemente

### Immagine PRIVATA (Azure Container Registry)
- ✅ **Sicura**: solo tu puoi accedere
- ✅ Puoi mettere credenziali (ma meglio usarle come variabili d'ambiente)
- ✅ Integrazione perfetta con Azure
- 💰 Costa qualche euro al mese (circa $5-10)

**Quando usarla:**
- Per produzione
- Se hai dati sensibili
- Per progetti aziendali

---

## 🎯 Per la Tua Situazione (Prima Volta)

**Ti consiglio: INIZIA CON DOCKER HUB (PUBBLICA)** perché:
1. È più semplice
2. È gratuita
3. Puoi imparare senza costi
4. Puoi sempre passare a privata dopo

---

## 🚀 Guida Passo-Passo Completa

### STEP 1: Prepara il Dockerfile (Già Fatto! ✅)

Il file `Dockerfile` è già nel tuo progetto. Controlla che esista.

### STEP 2: Crea Account Docker Hub (Se Non Ce L'Hai)

1. Vai su [hub.docker.com](https://hub.docker.com)
2. Clicca **"Sign Up"** (Registrati)
3. Crea account gratuito
4. Verifica email

### STEP 3: Build dell'Immagine Docker (Locale)

Apri PowerShell o Terminale nella cartella del progetto:

```bash
# Sostituisci "tuousername" con il tuo username Docker Hub
docker build -t tuousername/enpal-streamlit:latest .
```

**Cosa fa questo comando:**
- `docker build` = costruisce l'immagine
- `-t tuousername/enpal-streamlit:latest` = dà un nome all'immagine
- `.` = usa il Dockerfile nella cartella corrente

**Tempo:** 5-10 minuti la prima volta (scarica tutto)

### STEP 4: Test Locale (Opzionale ma Consigliato)

```bash
# Avvia il container localmente per testare
docker run -p 8000:8000 tuousername/enpal-streamlit:latest
```

Poi apri browser: `http://localhost:8000`

Se funziona, premi `Ctrl+C` per fermarlo.

### STEP 5: Push su Docker Hub

```bash
# Login a Docker Hub
docker login
# Inserisci username e password

# Push dell'immagine
docker push tuousername/enpal-streamlit:latest
```

**Tempo:** 5-15 minuti (carica l'immagine)

### STEP 6: Configura Azure Container App

Nel form Azure che hai aperto:

1. **Origine immagine**: Seleziona **"Docker Hub o altri registri"**
2. **Immagine**: Inserisci `tuousername/enpal-streamlit`
3. **Tag**: Inserisci `latest`
4. **Autenticazione**: Lascia vuoto (pubblica = no auth)

### STEP 7: Aggiungi Variabili d'Ambiente

Nella sezione "Variabili di ambiente", clicca **"+ Aggiungi"** e aggiungi:

| Nome | Valore |
|------|--------|
| `GA_PROPERTY_ID` | `<il_tuo_property_id>` |
| `GA_CREDENTIALS_PATH` | `/app/credentials/service-account-key.json` |
| `USE_DEFAULT_CREDENTIALS` | `false` |
| `ANTHROPIC_API_KEY` | `<la_tua_api_key>` |

### STEP 8: Configura Risorse

- **CPU e memoria**: Cambia a **"0.5 core CPU, 1.0 Gi di memoria"** (minimo per Streamlit)

### STEP 9: Tab "In ingresso" (Ingress)

Quando vai al prossimo tab:
- ✅ **Abilita ingresso**: Sì
- **Esposizione**: Pubblica
- **Porta**: `8000`

### STEP 10: Credenziali GA4

**IMPORTANTE**: Il file `service-account-key.json` NON deve essere nell'immagine Docker!

**Opzione A: Volume Mount (Consigliato)**
- Nel tab "Contenitore", sezione "Volumi"
- Monta il file delle credenziali come volume

**Opzione B: Upload Dopo il Deploy**
- Dopo che l'app è creata, puoi caricare il file via Azure Portal

---

## 🔄 Se Vuoi Usare Immagine PRIVATA (Azure Container Registry)

### Creare ACR

1. Azure Portal → **"+ Crea una risorsa"**
2. Cerca **"Container Registry"**
3. Clicca **"Crea"**
4. Compila:
   - **Nome**: `acrenpal` (deve essere unico globalmente)
   - **Resource Group**: stesso del Container App
   - **SKU**: Basic ($5/mese)
   - **Admin user**: Abilita (per semplicità)

### Build e Push su ACR

```bash
# Login ad Azure
az login

# Login ad ACR
az acr login --name acrenpal

# Build e push (fa tutto in una volta!)
az acr build --registry acrenpal --image enpal-streamlit:latest .
```

### Configurare nel Form Azure

1. **Origine immagine**: **"Registro Azure Container"**
2. **Registro**: Seleziona `acrenpal`
3. **Immagine**: `enpal-streamlit`
4. **Tag**: `latest`
5. **Autenticazione**: **"Identità gestita"** (più sicuro)

---

## ❓ Domande Frequenti

### Q: Devo pagare per Docker Hub?
**A:** No, è gratuito per immagini pubbliche.

### Q: Quanto costa Azure Container Registry?
**A:** Basic tier = ~$5/mese. Gratuito per i primi 30 giorni.

### Q: Posso cambiare da pubblica a privata dopo?
**A:** Sì! Puoi sempre ricreare l'immagine in ACR.

### Q: Le credenziali sono sicure nell'immagine pubblica?
**A:** NO! Non mettere mai credenziali nell'immagine. Usa sempre variabili d'ambiente.

### Q: Quanto tempo ci vuole?
**A:** 
- Setup iniziale: 30-60 minuti
- Build immagine: 5-10 minuti
- Push: 5-15 minuti
- Deploy Azure: 5-10 minuti

---

## 🎯 Checklist Completa

- [ ] Account Docker Hub creato
- [ ] Docker installato e funzionante
- [ ] Immagine buildata localmente
- [ ] Immagine testata localmente (opzionale)
- [ ] Immagine pushato su Docker Hub
- [ ] Variabili d'ambiente configurate in Azure
- [ ] Risorse CPU/Memoria impostate (min 0.5/1.0)
- [ ] Ingress abilitato (porta 8000)
- [ ] Credenziali GA4 caricate (via volume o upload)

---

## 🆘 Problemi Comuni

### "Cannot connect to Docker daemon"
**Soluzione:** Avvia Docker Desktop (Windows/Mac) o Docker service (Linux)

### "denied: requested access to the resource is denied"
**Soluzione:** Fai `docker login` prima del push

### "No space left on device"
**Soluzione:** Pulisci immagini vecchie: `docker system prune -a`

### "Port already in use"
**Soluzione:** Cambia porta o ferma il container esistente

---

## 📞 Prossimi Passi

1. **Ora**: Inizia con Docker Hub (pubblica) per imparare
2. **Dopo**: Se tutto funziona, considera ACR (privata) per produzione
3. **Sempre**: Usa variabili d'ambiente per i secrets, mai nell'immagine!

---

**Buona fortuna! 🚀**

