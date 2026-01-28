"""
Google Analytics Dashboard with Streamlit
A professional, interactive dashboard for analyzing Google Analytics 4 data.
"""
import streamlit as st
import pandas as pd
from pathlib import Path

# Import custom modules
from src.data_loader import (
    get_data,
    get_unique_campaigns,
    get_unique_channels,
    get_unique_urls,
    filter_data,
    aggregate_by_event_action,
    get_all_event_actions,
    get_all_channels
)
from src.filters import (
    render_date_filter,
    render_campaign_filter,
    render_channel_filter,
)
from src.visualizations import render_all_comparison_charts
from src.metrics import (
    calculate_leads,
    calculate_start_rate,
    calculate_end_rate,
    calculate_registration_rate,
    calculate_cap_success,
    render_conversion_metrics
)
from src.utils import render_download_button
from src.ai_analysis import render_ai_analysis
from src.report_generator import render_report_section, init_report_session
from config.config import (
    PAGE_TITLE, PAGE_ICON, LAYOUT,
    GA_PROPERTY_ID, GA_CREDENTIALS_PATH, USE_DEFAULT_CREDENTIALS
)

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .comparison-header {
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        padding: 0.5rem;
        background-color: #e8e8e8;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .old-landing {
        background-color: #fff3e0;
    }
    .new-landing {
        background-color: #e3f2fd;
    }
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .header-title {
        font-size: 2rem !important;
        font-weight: bold !important;
        color: #191970 !important;
        margin: 0 !important;
    }
    /* Fixed height for multiselect with scrolling */
    div[data-testid="stMultiSelect"] > div > div {
        max-height: 120px !important;
        overflow-y: auto !important;
    }
    /* Compact button styling */
    .url-buttons {
        display: flex;
        gap: 8px;
        margin-bottom: 8px;
    }
    .url-buttons button {
        flex: 1;
        padding: 0.25rem 0.5rem !important;
        font-size: 0.85rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Header with logo (aligned vertically)
logo_path = Path("assets/enpal-logo.png")
if logo_path.exists():
    import base64
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <div class="header-container">
            <img src="data:image/png;base64,{logo_base64}" width="180">
            <h1 class="header-title">{PAGE_TITLE}</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    st.title(PAGE_TITLE)
st.markdown("---")

# Load data
with st.spinner("Loading GA4 data..."):
    df, _ = get_data(
        property_id=GA_PROPERTY_ID,
        credentials_path=GA_CREDENTIALS_PATH,
        use_default_credentials=USE_DEFAULT_CREDENTIALS
    )

if df.empty:
    st.error("No data available. Please check your data source configuration.")
    st.stop()

# Sidebar filters (Global filters)
st.sidebar.header("Global Filters")

# Date filter
start_date, end_date = render_date_filter(df)

# Get campaigns and channels with counts for the current date range
date_filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
campaigns_with_counts = get_unique_campaigns(date_filtered_df)
channels_with_counts = get_unique_channels(date_filtered_df)
urls_with_counts = get_unique_urls(date_filtered_df)

# Campaign filter
selected_campaigns = render_campaign_filter(campaigns_with_counts)

# Channel filter
selected_channels = render_channel_filter(channels_with_counts)

# Apply global filters (without URL filter - that will be per-column)
base_filtered_df = filter_data(
    df,
    start_date,
    end_date,
    selected_campaigns if selected_campaigns else None,
    selected_channels if selected_channels else None,
    None  # No URL filter at global level
)

# Get URLs available after global filters
available_urls = get_unique_urls(base_filtered_df)
url_options = [url for url, count in available_urls]

# Landing Page Comparison
st.markdown("## Landing Page Comparison")

# Create two columns for comparison
col_old, col_new = st.columns(2)

# Store url_options in session state for callbacks
st.session_state.url_options = url_options

# Callback functions (defined before columns so they capture correctly)
def select_all_old_callback():
    search = st.session_state.get('search_old', '')
    opts = st.session_state.get('url_options', [])
    filtered = [url for url in opts if search.lower() in url.lower()] if search else opts
    # Replace selection with filtered results
    st.session_state.url_filter_old = filtered

def clear_old_callback():
    st.session_state.url_filter_old = []

def select_all_new_callback():
    search = st.session_state.get('search_new', '')
    opts = st.session_state.get('url_options', [])
    filtered = [url for url in opts if search.lower() in url.lower()] if search else opts
    # Replace selection with filtered results
    st.session_state.url_filter_new = filtered

def clear_new_callback():
    st.session_state.url_filter_new = []

# --- OLD LANDING COLUMN ---
with col_old:
    st.markdown('<div class="comparison-header old-landing">🔶 OLD LANDING</div>', unsafe_allow_html=True)

    # Search input for Old Landing
    search_old = st.text_input(
        "Search URLs (Old Landing)",
        key="search_old",
        placeholder="Type to filter (e.g. /ar, /it/fotovoltaico...)"
    )

    # Filter options based on search (for display)
    filtered_options_old = [url for url in url_options if search_old.lower() in url.lower()] if search_old else url_options

    # Select All Matching and Clear buttons (compact layout)
    col_btn1, col_btn2 = st.columns([1, 1], gap="small")
    with col_btn1:
        st.button("Select All", key="select_all_old", on_click=select_all_old_callback, disabled=len(filtered_options_old) == 0, use_container_width=True)
    with col_btn2:
        st.button("Clear", key="clear_old", on_click=clear_old_callback, use_container_width=True)

    # Show count of matching URLs
    if search_old:
        st.caption(f"Found {len(filtered_options_old)} matching URLs")

    # URL multiselect for Old Landing
    selected_urls_old = st.multiselect(
        "Selected URLs (Old Landing)",
        options=url_options,
        default=[],
        key="url_filter_old",
        placeholder="Select URLs or use search above"
    )

    # Filter data for old landing
    if selected_urls_old:
        old_landing_df = base_filtered_df[base_filtered_df['url'].isin(selected_urls_old)]
    else:
        old_landing_df = base_filtered_df.copy()

    # KPIs for Old Landing
    st.markdown("### KPIs")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        leads_old = calculate_leads(old_landing_df)
        st.metric(label="Leads", value=f"{leads_old:,}")

    with kpi_col2:
        start_rate_old = calculate_start_rate(old_landing_df)
        st.metric(label="Start Rate", value=f"{start_rate_old:.2f}%")

    with kpi_col3:
        end_rate_old = calculate_end_rate(old_landing_df)
        st.metric(label="End Rate", value=f"{end_rate_old:.2f}%")

    with kpi_col4:
        reg_rate_old = calculate_registration_rate(old_landing_df)
        st.metric(label="Reg Rate", value=f"{reg_rate_old:.2f}%")
    
    kpi_col5, kpi_col6 = st.columns([2, 2])
    with kpi_col5:
        postcap_success_old = calculate_cap_success(old_landing_df)
        st.metric(label="PostCap Success", value=f"{postcap_success_old:.2f}%")

    # Data table for Old Landing
    st.markdown("### Event Actions")
    event_data_old = aggregate_by_event_action(old_landing_df)

    if not event_data_old.empty:
        render_download_button(event_data_old, key="download_old")
        st.dataframe(event_data_old, width="stretch", hide_index=True)
    else:
        st.info("No data available for selected filters")

# NEW LANDING COLUMN
with col_new:
    st.markdown('<div class="comparison-header new-landing">🔷 NEW LANDING</div>', unsafe_allow_html=True)

    # Search input for New Landing
    search_new = st.text_input(
        "Search URLs (New Landing)",
        key="search_new",
        placeholder="Type to filter (e.g. /ar, /it/fotovoltaico...)"
    )

    # Filter options based on search (for display)
    filtered_options_new = [url for url in url_options if search_new.lower() in url.lower()] if search_new else url_options

    # Select All Matching and Clear buttons (compact layout)
    col_btn3, col_btn4 = st.columns([1, 1], gap="small")
    with col_btn3:
        st.button("Select All", key="select_all_new", on_click=select_all_new_callback, disabled=len(filtered_options_new) == 0, use_container_width=True)
    with col_btn4:
        st.button("Clear", key="clear_new", on_click=clear_new_callback, use_container_width=True)

    # Show count of matching URLs
    if search_new:
        st.caption(f"Found {len(filtered_options_new)} matching URLs")

    # URL multiselect for New Landing
    selected_urls_new = st.multiselect(
        "Selected URLs (New Landing)",
        options=url_options,
        default=[],
        key="url_filter_new",
        placeholder="Select URLs or use search above"
    )

    # Filter data for new landing
    if selected_urls_new:
        new_landing_df = base_filtered_df[base_filtered_df['url'].isin(selected_urls_new)]
    else:
        new_landing_df = base_filtered_df.copy()

    # KPIs for New Landing
    st.markdown("### KPIs")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        leads_new = calculate_leads(new_landing_df)
        st.metric(label="Leads", value=f"{leads_new:,}")

    with kpi_col2:
        start_rate_new = calculate_start_rate(new_landing_df)
        st.metric(label="Start Rate", value=f"{start_rate_new:.2f}%")

    with kpi_col3:
        end_rate_new = calculate_end_rate(new_landing_df)
        st.metric(label="End Rate", value=f"{end_rate_new:.2f}%")

    with kpi_col4:
        reg_rate_new = calculate_registration_rate(new_landing_df)
        st.metric(label="Reg Rate", value=f"{reg_rate_new:.2f}%")
    
    kpi_col5, kpi_col6 = st.columns([2, 2])
    with kpi_col5:
        postcap_success_new = calculate_cap_success(new_landing_df)
        st.metric(label="PostCap Success", value=f"{postcap_success_new:.2f}%")

    # Data table for New Landing
    st.markdown("### Event Actions")
    event_data_new = aggregate_by_event_action(new_landing_df)

    if not event_data_new.empty:
        render_download_button(event_data_new, key="download_new")
        st.dataframe(event_data_new, width="stretch", hide_index=True)
    else:
        st.info("No data available for selected filters")

st.markdown("---")


# AI ANALYSIS SECTION
render_ai_analysis(
    old_landing_df,
    new_landing_df,
    start_date.strftime('%d/%m/%Y'),
    end_date.strftime('%d/%m/%Y')
)

st.markdown("---")


# COMPARISON CHARTS SECTION
st.markdown("## Comparison Charts")
render_all_comparison_charts(old_landing_df, new_landing_df)


# REPORT GENERATOR SECTION

init_report_session()

# Session state per AI analysis
if 'last_ai_analysis' not in st.session_state:
    st.session_state.last_ai_analysis = None

# Filtri per report
filters_info = {
    'campaigns': ', '.join(selected_campaigns[:3]) + ('...' if len(selected_campaigns) > 3 else '') if selected_campaigns else 'All',
    'channels': ', '.join(selected_channels[:3]) + ('...' if len(selected_channels) > 3 else '') if selected_channels else 'All',
    'old_urls': ', '.join(selected_urls_old[:2]) if selected_urls_old else 'All',
    'new_urls': ', '.join(selected_urls_new[:2]) if selected_urls_new else 'All'
}

render_report_section(
    old_df=old_landing_df,
    new_df=new_landing_df,
    old_landing_name=selected_urls_old[0] if selected_urls_old else "OLD Landing (All URLs)",
    new_landing_name=selected_urls_new[0] if selected_urls_new else "NEW Landing (All URLs)",
    date_range=f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
    filters=filters_info,
    ai_analysis=st.session_state.get('last_ai_analysis')
)

# Footer
st.markdown("---")
st.caption("Google Analytics Dashboard - Enpal B.V")
