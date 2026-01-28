# Google Analytics Dashboard with Streamlit

A professional, interactive dashboard built with Streamlit that connects to Google Analytics 4 data and enables users to filter, explore, and analyze event actions efficiently.

## Project Objective

Create a responsive, fast, and user-friendly analytics dashboard suitable for business stakeholders and marketing teams, replacing traditional tools like Looker Studio and Excel reports.

## Features

### Advanced Filters (Multi-Select Enabled)
- **Date Range Filter**
  - Calendar picker (Start Date & End Date)
  - DD/MM/YYYY format
  - Monthly navigation
  - Custom date range selection
  - Dynamic filtering on all data

- **Campaign Filter**
  - Multi-select dropdown with search
  - Checkbox selection
  - Event count displayed per campaign
  - Example: (organic) – 231.1K events, National_North_Mobile – 85.9K, etc.

- **Channel Filter**
  - Multi-select dropdown with search
  - Checkbox selection
  - Event count per channel
  - Example: google – 504.1K, outbrain – 163.1K, facebook – 128.5K, etc.

### Data Visualization
- **Dynamic Table**
  - Columns: event_action, total_count
  - Sorting & pagination
  - Live filtering

- **Interactive Charts**
  - Bar charts
  - Line charts
  - Pie charts

- **KPI Cards**
  - Total events count
  - Selected campaigns summary
  - Channel breakdown

### Calculated Metrics
- **Ratio Calculations**
  - Custom formula support
  - Example: Enpal Source Cookie / (not set)
  - Percentage formatting
  - Row-specific display

##  Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend & UI | Streamlit |
| Backend & Logic | Python |
| Data Source | Google Analytics 4 API |
| Data Processing | pandas |
| Visualization | plotly / matplotlib |

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Step 1: Activate Virtual Environment
```powershell
# On Windows
& .\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
```
streamlit==1.52.2
pandas
plotly
matplotlib
google-analytics-data
google-auth-oauthlib
google-auth-httplib2
python-dotenv
```

### 1. Prepare Data
- **Google Analytics 4 API**: Add credentials to `config/.env`

### 2. Run the Dashboard
```bash
python -m streamlit run app.py
```

The dashboard will open at: `http://localhost:8501`

### 3. Use the Dashboard
1. Select date range using the calendar picker
2. Filter campaigns using multi-select dropdown
3. Filter channels using multi-select dropdown
4. View results in the main table
5. Download data as CSV
6. Explore visualizations

## Project Structure

```
.
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── config/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   └── .env.example           # Environment variables template
├── data/
│   └── analytics.csv          # Sample data (CSV)
├── src/
│   ├── __init__.py
│   ├── data_loader.py         # Data loading functions
│   ├── filters.py             # Filter components
│   ├── visualizations.py      # Chart functions
│   ├── metrics.py             # KPI & metric calculations
│   └── utils.py               # Helper utilities
└── assets/
    └── styles.css             # Custom styling (optional)
```

## Configuration

### Using Google Analytics 4 API
1. Create a Google Cloud project
2. Enable Google Analytics 4 API
3. Create a service account and download JSON credentials
4. Add credentials to `config/.env`:
   ```
   GA4_CREDENTIALS_PATH=path/to/credentials.json
   GA4_PROPERTY_ID=your_property_id
   ```
5. Update `src/data_loader.py` to use GA4 API

## Performance Optimization

- **Caching**: API calls and data processing cached with `@st.cache_data()`
- **Lazy Loading**: Data loaded on-demand
- **Efficient Grouping**: Optimized pandas groupby operations
- **Memory Management**: Large datasets handled efficiently
- **Query Optimization**: Minimal data fetching

## Usage Examples

### Filter Data
```
1. Date Range: 01/01/2024 - 31/12/2024
2. Campaigns: Select (organic), National_North_Mobile
3. Channels: Select google, facebook
→ Table updates automatically
```

### View Metrics
- Total events in selected date range
- Top campaigns by event count
- Channel distribution
- Custom ratio calculations

### Export Data
- Click "Download CSV" button
- File saves with timestamp
- Includes all applied filters

## Calculated Metrics

### Example: Ratio Calculation
```
Metric: Enpal Source Cookie / (not set)

Formula:
  Event count (Enpal Source Cookie)
  ────────────────────────────────
  Total event count ((not set))

Result: 45.32%
```

---

**Maintained by**: Zakaria Meziane
**Status**: Production Ready
