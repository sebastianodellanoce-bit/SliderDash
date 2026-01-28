"""Filter components for the Google Analytics Dashboard."""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


def format_count(count: float) -> str:
    """Format count with K/M suffix."""
    if count >= 1_000_000:
        return f"{count/1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count/1_000:.1f}K"
    return str(int(count))


def render_date_filter(df: pd.DataFrame) -> tuple:
    """Render date range filter in sidebar."""
    st.sidebar.subheader("Date Range")

    # Default values based on data, but no restrictions on selection
    if df.empty:
        today = datetime.today()
        default_start = today - timedelta(days=30)
        default_end = today
    else:
        default_start = df['date'].min().date()
        default_end = df['date'].max().date()

    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=default_start,
            format="DD/MM/YYYY"
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=default_end,
            format="DD/MM/YYYY"
        )

    return pd.Timestamp(start_date), pd.Timestamp(end_date)


def render_campaign_filter(campaigns_with_counts: list) -> list:
    """Render campaign multi-select filter in sidebar."""
    st.sidebar.subheader("Campaigns")

    if not campaigns_with_counts:
        st.sidebar.info("No campaigns available")
        return []

    # Create options with counts
    options = [f"{camp} - {format_count(count)} events"
               for camp, count in campaigns_with_counts]
    campaign_names = [camp for camp, _ in campaigns_with_counts]

    selected_options = st.sidebar.multiselect(
        "Select Campaigns",
        options=options,
        default=[],
        placeholder="Search campaigns..."
    )

    # Extract campaign names from selected options
    selected_campaigns = []
    for opt in selected_options:
        for camp, count in campaigns_with_counts:
            if opt.startswith(camp):
                selected_campaigns.append(camp)
                break

    return selected_campaigns


def render_channel_filter(channels_with_counts: list) -> list:
    """Render channel multi-select filter in sidebar."""
    st.sidebar.subheader("Channels")

    if not channels_with_counts:
        st.sidebar.info("No channels available")
        return []

    # Create options with counts
    options = [f"{channel} - {format_count(count)} events"
               for channel, count in channels_with_counts]

    selected_options = st.sidebar.multiselect(
        "Select Channels",
        options=options,
        default=[],
        placeholder="Search channels..."
    )

    # Extract channel names from selected options
    selected_channels = []
    for opt in selected_options:
        for channel, count in channels_with_counts:
            if opt.startswith(channel):
                selected_channels.append(channel)
                break

    return selected_channels


