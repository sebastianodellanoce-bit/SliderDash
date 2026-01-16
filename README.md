# Google Analytics Dashboard with Streamlit

A professional, interactive dashboard built with Streamlit that connects to Google Analytics 4 data and enables users to filter, explore, and analyze event actions efficiently.

## 🎯 Project Objective

Create a responsive, fast, and user-friendly analytics dashboard suitable for business stakeholders and marketing teams, replacing traditional tools like Looker Studio and Excel reports.

## 📋 Features

### Advanced Filters (Multi-Select Enabled)
- **📅 Date Range Filter**
  - Calendar picker (Start Date & End Date)
  - DD/MM/YYYY format
  - Monthly navigation
  - Custom date range selection
  - Dynamic filtering on all data

- **🎯 Campaign Filter**
  - Multi-select dropdown with search
  - Checkbox selection
  - Event count displayed per campaign
  - Example: (organic) – 231.1K events, National_North_Mobile – 85.9K, etc.

- **🌐 Channel Filter**
  - Multi-select dropdown with search
  - Checkbox selection
  - Event count per channel
  - Example: google – 504.1K, outbrain – 163.1K, facebook – 128.5K, etc.

### Data Visualization
- **📊 Dynamic Table**
  - Columns: event_action, total_count
  - Sorting & pagination
  - Live filtering
  - CSV export functionality

- **📈 Interactive Charts**
  - Bar charts
  - Line charts
  - Pie charts

- **🎨 KPI Cards**
  - Total events count
  - Selected campaigns summary
  - Channel breakdown

### Calculated Metrics
- **Ratio Calculations**
  - Custom formula support
  - Example: Enpal Source Cookie / (not set)
  - Percentage formatting
  - Row-specific display

## 🛠 Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend & UI | Streamlit |
| Backend & Logic | Python |
| Data Source | Google Analytics 4 API / CSV / BigQuery |
| Data Processing | pandas |
| Visualization | plotly / matplotlib |
| Analytics API | google-analytics-data (optional) |

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Step 1: Activate Virtual Environment
```powershell
# On Windows
& .\venv\Scripts\Activate.ps1

# On macOS/Linux
source venv/bin/activate
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

## 🚀 Quick Start

### 1. Prepare Data
Choose one of the following:
- **CSV File**: Place sample data in `data/analytics.csv`
- **Google Analytics 4 API**: Add credentials to `config/.env`
- **BigQuery Export**: Configure connection in `config/config.py`

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

## 📁 Project Structure

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

## ⚙️ Configuration

### Using CSV Data (Default)
1. Place CSV file in `data/` folder
2. Ensure columns: `event_action`, `campaign`, `channel`, `count`, `date`
3. Run app.py

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

### Using BigQuery
1. Set up Google Cloud BigQuery project
2. Export GA4 data to BigQuery
3. Configure connection in `config/config.py`
4. Update `src/data_loader.py` accordingly

## 🎨 UI/UX Features

- ✅ Clean layout with columns & sections
- ✅ Sticky sidebar filters
- ✅ KPI cards for quick insights
- ✅ Loading spinners during data fetch
- ✅ Error handling & user feedback
- ✅ Responsive design
- ✅ Multi-select with search capability
- ✅ Calendar date picker
- ✅ Dynamic table with sorting

## 🔧 Streamlit Functional Requirements

The dashboard includes:
- `st.sidebar` for filter panel
- `st.multiselect()` with search functionality
- `st.date_input()` for date filtering
- `st.dataframe()` for interactive tables
- `st.cache_data()` for performance optimization
- Interactive charts using Plotly
- Error handling with `st.error()` / `st.warning()`
- Progress indicators with `st.spinner()`

## ⚡ Performance Optimization

- **Caching**: API calls and data processing cached with `@st.cache_data()`
- **Lazy Loading**: Data loaded on-demand
- **Efficient Grouping**: Optimized pandas groupby operations
- **Memory Management**: Large datasets handled efficiently
- **Query Optimization**: Minimal data fetching

## 🌐 Deployment

### Streamlit Cloud (Recommended)
1. Push project to GitHub
2. Connect repository to Streamlit Cloud
3. Set environment variables in deployment
4. Dashboard auto-deploys on push

### Docker Deployment
```bash
docker build -t ga-dashboard .
docker run -p 8501:8501 ga-dashboard
```

### Private Server
1. Install Streamlit on server
2. Clone repository
3. Configure authentication
4. Use process manager (PM2, systemd)
5. Set up reverse proxy (Nginx)

## 🔐 Google Analytics API Setup

### Step 1: Create Service Account
```bash
1. Go to Google Cloud Console
2. Create new project
3. Enable Google Analytics 4 API
4. Create Service Account
5. Generate JSON key
```

### Step 2: Add to GA4 Property
```bash
1. Copy service account email
2. Add to GA4 property as Editor
3. Wait for permissions to sync
```

### Step 3: Use in Dashboard
```python
# In .env
GA4_CREDENTIALS_PATH=credentials.json
GA4_PROPERTY_ID=123456789
```

## 📊 Usage Examples

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

## 📈 Calculated Metrics

### Example: Ratio Calculation
```
Metric: Enpal Source Cookie / (not set)

Formula:
  Event count (Enpal Source Cookie)
  ────────────────────────────────
  Total event count ((not set))

Result: 45.32%
```

## ✨ Bonus Features (Optional)

- 🔐 User authentication (OAuth2)
- 💾 Saved filter views
- 🔄 Auto-refresh every X minutes
- 📄 PDF export with charts
- 🌙 Dark mode toggle
- 📊 Custom metric builder
- 📬 Email scheduled reports
- 🎯 Goal tracking
- 🔗 Shareable filter links

## 🚨 Troubleshooting

### Issue: "Streamlit not found"
```bash
python -m streamlit run app.py
```

### Issue: Permission denied on .exe
```bash
python -m streamlit run app.py
# or restart terminal with admin privileges
```

### Issue: Data not loading
- Check CSV file exists in `data/` folder
- Verify columns match expected format
- Check API credentials if using GA4
- Review logs for error messages

### Issue: Dashboard slow
- Clear cache: `streamlit cache clear`
- Check date range (narrow if needed)
- Verify sufficient system resources
- Consider data sampling for large datasets

## 📝 License

Proprietary - Enpal B.V

## 👥 Support

For issues or feature requests, contact the development team.

## 🔄 Version History

- **v1.0.0** (2026-01-14): Initial release
  - Core filters (Date, Campaign, Channel)
  - Interactive table
  - Basic visualizations
  - CSV export

---

**Last Updated**: January 14, 2026  
**Maintained by**: Development Team  
**Status**: Production Ready ✅
#   S l i d e r D a s h  
 