# Integrazione Claude AI per Analisi Dashboard

## Obiettivo
Aggiungere Claude (Anthropic LLM) alla dashboard per analizzare automaticamente i dati in base alle selezioni fatte dall'utente.

---

## Cosa Farà l'AI

### 1. **Confronto Landing Pages**
Quando l'utente seleziona URLs per OLD e NEW landing:
- Analizza le differenze nei KPI (Leads, Start Rate, End Rate, Reg Rate)
- Identifica quale landing performa meglio e perché

### 2. **Identificazione Drop-off**
- Trova dove si perde il maggior numero di utenti nel funnel
- Esempio: "Il drop-off maggiore è tra 'A quale prodotto sei interessato?' e 'Per quale prodotto vuoi scoprire i bonus?' con una perdita del 45%"

### 3. **Analisi Differenze**
- Quale step ha la DIFFERENZA MAGGIORE tra OLD e NEW?
- Il Start Rate è uguale o diverso?
- Dove la NEW landing migliora/peggiora rispetto alla OLD?

### 4. **Insights Concreti**
L'AI fornirà risposte concrete come:
- "La NEW landing ha un Start Rate del 12% vs 8% della OLD, probabilmente grazie a..."
- "Il problema principale è nello step X dove si perdono il 60% degli utenti"
- "Consiglio: migliorare lo step Y che ha il drop-off maggiore"

---

## Implementazione Tecnica

### Step 1: Installare Anthropic SDK
```bash
pip install anthropic
```

### Step 2: Configurare API Key
Aggiungere in `config/.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### Step 3: Creare Modulo AI
Nuovo file `src/ai_analysis.py`:
```python
import anthropic

def analyze_landing_comparison(old_data, new_data, old_kpis, new_kpis):
    """
    Analizza i dati e fornisce insights usando Claude AI.
    """
    # Formatta i dati per il prompt
    # Chiama Claude API
    # Restituisce l'analisi
```

### Step 4: Aggiungere UI nella Dashboard
In `app.py`, aggiungere:
- Bottone "🤖 Analizza con AI"
- Sezione per mostrare l'analisi
- Spinner durante l'elaborazione

---

## Dati che l'AI Riceverà

### KPIs
| Metrica | OLD Landing | NEW Landing |
|---------|-------------|-------------|
| Leads | X | Y |
| Start Rate | X% | Y% |
| End Rate | X% | Y% |
| Reg Rate | X% | Y% |

### Funnel Events (per ogni landing)
| Step | Event Action | Count | Drop-off % |
|------|-------------|-------|------------|
| 1 | Enpal Source Cookie | 100,000 | - |
| 2 | A quale prodotto... | 80,000 | 20% |
| 3 | Per quale prodotto... | 50,000 | 37.5% |
| ... | ... | ... | ... |

### Filtri Applicati
- Date Range: XX/XX/XXXX - XX/XX/XXXX
- Campaigns: [lista]
- Channels: [lista]
- URLs OLD: [lista]
- URLs NEW: [lista]

---

## Esempio di Output AI

```
📊 ANALISI COMPARATIVA LANDING PAGES

🏆 VINCITORE: NEW Landing (+15% conversioni)

📈 PUNTI DI FORZA NEW:
• Start Rate superiore: 12.5% vs 8.2% (+52%)
• Migliore engagement iniziale

⚠️ PROBLEMI IDENTIFICATI:
• DROP-OFF CRITICO: Step "Per quale prodotto vuoi scoprire i bonus?"
  - OLD: 45% drop-off
  - NEW: 48% drop-off (peggiore!)
  
• La NEW landing perde più utenti nello step 3

💡 RACCOMANDAZIONI:
1. Ottimizzare lo step "Per quale prodotto..." nella NEW landing
2. Analizzare perché il form ha un tasso di abbandono alto
3. Considerare A/B test sullo step problematico
```

---

## Costi Stimati
- Claude 3.5 Sonnet: ~$0.003 per analisi (circa 1000 token input + 500 output)
- Budget mensile consigliato: $10-20 per uso moderato

---

## Prossimi Passi
1. [ ] Ottenere API Key da Anthropic (https://console.anthropic.com)
2. [ ] Installare SDK: `pip install anthropic`
3. [ ] Aggiungere API Key al .env
4. [ ] Implementare il modulo AI
5. [ ] Aggiungere UI alla dashboard
6. [ ] Testare con dati reali

---

## Note
- L'analisi è opzionale (bottone da cliccare)
- I dati NON vengono salvati da Anthropic
- L'API Key deve rimanere segreta (non committare nel repo)

