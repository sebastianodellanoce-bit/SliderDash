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
from src.visualizations import (
    render_event_bar_chart,
    render_daily_trend_chart,
    render_channel_pie_chart,
    render_campaign_bar_chart
)
from src.metrics import (
    calculate_leads,
    calculate_start_rate,
    calculate_end_rate,
    calculate_registration_rate,
    render_conversion_metrics
)
from src.utils import render_download_button, render_data_table
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
    df = get_data(
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

# =============================================================================
# DEBUG: Show data info
# =============================================================================
with st.expander("Debug: View Data Info"):
    st.write(f"**Selected Date Range:** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
    st.write(f"**Total rows in raw data:** {len(df)}")
    st.write(f"**Rows after date filter:** {len(base_filtered_df)}")
    st.write(f"**Date range in raw data:** {df['date'].min().strftime('%d/%m/%Y')} - {df['date'].max().strftime('%d/%m/%Y')}")

    st.write("---")
    st.write("**Columns in DataFrame:**", df.columns.tolist())

    st.write("---")
    st.write("**Sample of raw data (first 50 rows):**")
    st.dataframe(df.head(50))

    st.write("---")
    st.write("**All unique event_action values (from current data):**")
    if 'event_action' in df.columns:
        unique_events = df.groupby('event_action')['count'].sum().sort_values(ascending=False)
        st.write(f"Total unique event_action values in current data: {len(unique_events)}")
        st.dataframe(unique_events.reset_index())

    st.write("---")
    st.write("**ALL event_action values from GA4 (direct query without other dimensions):**")
    all_events = get_all_event_actions(
        property_id=GA_PROPERTY_ID,
        credentials_path=GA_CREDENTIALS_PATH,
        use_default_credentials=USE_DEFAULT_CREDENTIALS
    )
    if all_events:
        all_events_df = pd.DataFrame(all_events).sort_values('total_count', ascending=False)
        st.write(f"**TOTAL unique event_action values in GA4: {len(all_events_df)}**")
        st.dataframe(all_events_df, hide_index=True)

    st.write("---")
    st.write("**ALL channels (sessionSource) from GA4 (direct query):**")
    all_channels = get_all_channels(
        property_id=GA_PROPERTY_ID,
        credentials_path=GA_CREDENTIALS_PATH,
        use_default_credentials=USE_DEFAULT_CREDENTIALS
    )
    if all_channels:
        all_channels_df = pd.DataFrame(all_channels).sort_values('total_count', ascending=False)
        st.write(f"**TOTAL unique channels in GA4: {len(all_channels_df)}**")
        st.dataframe(all_channels_df, hide_index=True)

    st.write("---")
    st.write("**All unique URLs (landing pages):**")
    if 'url' in df.columns:
        unique_urls = df.groupby('url')['count'].sum().sort_values(ascending=False)
        st.write(f"Total unique URLs: {len(unique_urls)}")
        st.dataframe(unique_urls.head(50).reset_index())

    st.write("---")
    st.write("Checking specific events for KPI calculation:")
    for event in ["A quale prodotto sei interessato?", "Enpal Source Cookie", "Per quale prodotto vuoi scoprire i bonus?", "slider-success"]:
        if 'event_action' in df.columns:
            count = df[df['event_action'].str.strip() == event]['count'].sum()
        else:
            count = 0
        st.write(f"'{event}': {count:,}")

# =============================================================================
# COMPARISON VIEW - Two side-by-side columns
# =============================================================================
st.markdown("## Landing Page Comparison")

# Create two columns for comparison
col_old, col_new = st.columns(2)

# --- OLD LANDING COLUMN ---
with col_old:
    st.markdown('<div class="comparison-header old-landing">🔶 OLD LANDING</div>', unsafe_allow_html=True)

    # URL filter for Old Landing (with search built-in)
    selected_urls_old = st.multiselect(
        "Select URLs (Old Landing)",
        options=url_options,
        default=[],
        key="url_filter_old",
        placeholder="Type to search URLs (e.g. /ar, /it/fotovoltaico...)"
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
        # Temporary debug
        if 'event_action' in old_landing_df.columns:
            e1 = old_landing_df[old_landing_df['event_action'].str.strip() == "A quale prodotto sei interessato?"]['count'].sum()
            e2 = old_landing_df[old_landing_df['event_action'].str.strip() == "Enpal Source Cookie"]['count'].sum()
            st.caption(f"{e1:,} / {e2:,}")

    with kpi_col3:
        end_rate_old = calculate_end_rate(old_landing_df)
        st.metric(label="End Rate", value=f"{end_rate_old:.2f}%")

    with kpi_col4:
        reg_rate_old = calculate_registration_rate(old_landing_df)
        st.metric(label="Reg Rate", value=f"{reg_rate_old:.2f}%")

    # Data table for Old Landing
    st.markdown("### Event Actions")
    event_data_old = aggregate_by_event_action(old_landing_df)

    if not event_data_old.empty:
        render_download_button(event_data_old, key="download_old")
        st.dataframe(event_data_old, width="stretch", hide_index=True)
    else:
        st.info("No data available for selected filters")

# --- NEW LANDING COLUMN ---
with col_new:
    st.markdown('<div class="comparison-header new-landing">🔷 NEW LANDING</div>', unsafe_allow_html=True)

    # URL filter for New Landing (with search built-in)
    selected_urls_new = st.multiselect(
        "Select URLs (New Landing)",
        options=url_options,
        default=[],
        key="url_filter_new",
        placeholder="Type to search URLs (e.g. /ar, /it/fotovoltaico...)"
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
        # Temporary debug
        if 'event_action' in new_landing_df.columns:
            e1 = new_landing_df[new_landing_df['event_action'].str.strip() == "A quale prodotto sei interessato?"]['count'].sum()
            e2 = new_landing_df[new_landing_df['event_action'].str.strip() == "Enpal Source Cookie"]['count'].sum()
            st.caption(f"{e1:,} / {e2:,}")

    with kpi_col3:
        end_rate_new = calculate_end_rate(new_landing_df)
        st.metric(label="End Rate", value=f"{end_rate_new:.2f}%")

    with kpi_col4:
        reg_rate_new = calculate_registration_rate(new_landing_df)
        st.metric(label="Reg Rate", value=f"{reg_rate_new:.2f}%")

    # Data table for New Landing
    st.markdown("### Event Actions")
    event_data_new = aggregate_by_event_action(new_landing_df)

    if not event_data_new.empty:
        render_download_button(event_data_new, key="download_new")
        st.dataframe(event_data_new, width="stretch", hide_index=True)
    else:
        st.info("No data available for selected filters")

st.markdown("---")

# =============================================================================
# ADDITIONAL TABS (Charts and Metrics)
# =============================================================================
tab1, tab2 = st.tabs(["Charts", "Metrics"])

with tab1:
    # Charts using all filtered data (base_filtered_df)
    event_data_all = aggregate_by_event_action(base_filtered_df)

    col1, col2 = st.columns(2)

    with col1:
        render_event_bar_chart(event_data_all)

    with col2:
        render_channel_pie_chart(base_filtered_df)

    col3, col4 = st.columns(2)

    with col3:
        render_daily_trend_chart(base_filtered_df)

    with col4:
        render_campaign_bar_chart(base_filtered_df)

with tab2:
    # Conversion metrics
    render_conversion_metrics(base_filtered_df)

    st.markdown("---")

    # Additional stats
    st.subheader("Data Summary")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Date Range:**")
        st.write(f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")

    with col2:
        st.write("**Selected Campaigns:**")
        if selected_campaigns:
            for camp in selected_campaigns:
                st.write(f"- {camp}")
        else:
            st.write("All campaigns")

    with col3:
        st.write("**Selected Channels:**")
        if selected_channels:
            for ch in selected_channels:
                st.write(f"- {ch}")
        else:
            st.write("All channels")

# Footer
st.markdown("---")
st.caption("Google Analytics Dashboard - Enpal B.V")
