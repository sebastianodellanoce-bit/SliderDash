"""KPI and metric calculation functions for the Google Analytics Dashboard."""
import pandas as pd
import streamlit as st


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
    """Calculate Start Rate: 'Per quale prodotto vuoi scoprire i bonus?' / 'Enpal Source Cookie' * 100"""
    return calculate_ratio(df, "Per quale prodotto vuoi scoprire i bonus?", "Enpal Source Cookie")


def calculate_end_rate(df: pd.DataFrame) -> float:
    """Calculate End Rate: 'slider-success' / 'Per quale prodotto vuoi scoprire i bonus?' * 100"""
    return calculate_ratio(df, "slider-success", "Per quale prodotto vuoi scoprire i bonus?")


def calculate_registration_rate(df: pd.DataFrame) -> float:
    """Calculate Registration Rate: 'slider-success' / 'Enpal Source Cookie' * 100"""
    return calculate_ratio(df, "slider-success", "Enpal Source Cookie")


def calculate_cap_success(df: pd.DataFrame) -> float:
    """Calculate CAP Success: 'slider-success' / 'Per quale tipo di edificio vuoi scoprire i bonus?' * 100"""
    return calculate_ratio(df, "slider-success", "Per quale tipo di edificio vuoi scoprire i bonus?")


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
