#!/bin/bash

# Azure App Service startup script for Streamlit
# Uses PORT environment variable if available (Azure provides this), otherwise defaults to 8000
PORT=${PORT:-8000}
python -m streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false
