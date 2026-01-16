"""KPI and metric calculation functions for the Google Analytics Dashboard."""
import pandas as pd
import streamlit as st


def format_number(num: float) -> str:
    """Format large numbers with K/M suffix."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    return f"{num:,.0f}"


def calculate_total_events(df: pd.DataFrame) -> int:
    """Calculate total event count."""
    if df.empty:
        return 0
    return int(df['count'].sum())


def calculate_unique_campaigns(df: pd.DataFrame) -> int:
    """Calculate number of unique campaigns."""
    if df.empty:
        return 0
    return df['campaign'].nunique()


def calculate_unique_channels(df: pd.DataFrame) -> int:
    """Calculate number of unique channels."""
    if df.empty:
        return 0
    return df['channel'].nunique()


def calculate_unique_events(df: pd.DataFrame) -> int:
    """Calculate number of unique event actions."""
    if df.empty:
        return 0
    return df['event_action'].nunique()


def calculate_ratio(df: pd.DataFrame, event1: str, event2: str) -> float:
    """Calculate ratio between two event actions."""
    if df.empty:
        return 0.0

    # Check if 'event_action' column exists
    if 'event_action' not in df.columns:
        return 0.0

    # Use str.strip() to match events ignoring leading/trailing whitespace
    # Also use str.contains for partial matching to handle whitespace issues
    event1_mask = df['event_action'].str.strip() == event1.strip()
    event2_mask = df['event_action'].str.strip() == event2.strip()
    
    event1_count = df[event1_mask]['count'].sum()
    event2_count = df[event2_mask]['count'].sum()

    if event2_count == 0:
        return 0.0

    return (event1_count / event2_count) * 100


def calculate_leads(df: pd.DataFrame) -> int:
    """Calculate Leads: count of 'slider-success' events."""
    if df.empty:
        return 0
    if 'event_action' in df.columns:
        mask = df['event_action'].str.strip() == 'slider-success'
        return int(df[mask]['count'].sum())
    return 0


def calculate_start_rate(df: pd.DataFrame) -> float:
    """Calculate Start Rate: 'A quale prodotto sei interessato?' / 'Enpal Source Cookie' * 100"""
    return calculate_ratio(df, "A quale prodotto sei interessato?", "Enpal Source Cookie")


def calculate_end_rate(df: pd.DataFrame) -> float:
    """Calculate End Rate: 'slider-success' / 'Per quale prodotto vuoi scoprire i bonus?' * 100"""
    return calculate_ratio(df, "slider-success", "Per quale prodotto vuoi scoprire i bonus?")


def calculate_registration_rate(df: pd.DataFrame) -> float:
    """Calculate Registration Rate: 'slider-success' / 'Enpal Source Cookie' * 100"""
    return calculate_ratio(df, "slider-success", "Enpal Source Cookie")


def render_kpi_cards(df: pd.DataFrame):
    """Render KPI cards at the top of the dashboard."""
    col1, col2, col3 = st.columns(3)

    with col1:
        start_rate = calculate_start_rate(df)
        st.metric(
            label="Start Rate",
            value=f"{start_rate:.2f}%"
        )

    with col2:
        end_rate = calculate_end_rate(df)
        st.metric(
            label="End Rate",
            value=f"{end_rate:.2f}%"
        )

    with col3:
        reg_rate = calculate_registration_rate(df)
        st.metric(
            label="Registration Rate",
            value=f"{reg_rate:.2f}%"
        )


def render_conversion_metrics(df: pd.DataFrame):
    """Render conversion-related metrics."""
    st.subheader("Conversion Metrics")

    if df.empty:
        st.info("No data available for metrics")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Click to submit ratio
        click_to_submit = calculate_ratio(df, 'form_submit', 'button_click')
        st.metric(
            label="Form Submit / Button Click",
            value=f"{click_to_submit:.2f}%"
        )

    with col2:
        # Page view to click ratio
        view_to_click = calculate_ratio(df, 'button_click', 'page_view')
        st.metric(
            label="Button Click / Page View",
            value=f"{view_to_click:.2f}%"
        )
