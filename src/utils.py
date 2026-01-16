"""Utility functions for the Google Analytics Dashboard."""
import pandas as pd
import streamlit as st
from datetime import datetime


def get_csv_download_link(df: pd.DataFrame, filename: str = "export") -> bytes:
    """Convert dataframe to CSV bytes for download."""
    return df.to_csv(index=False).encode('utf-8')


def render_download_button(df: pd.DataFrame, key: str = "download"):
    """Render CSV download button."""
    if df.empty:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analytics_export_{timestamp}.csv"

    csv_data = get_csv_download_link(df)

    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        key=key
    )


def render_data_table(df: pd.DataFrame, title: str = "Data"):
    """Render interactive data table."""
    st.subheader(title)

    if df.empty:
        st.info("No data available")
        return

    # Display with sorting enabled
    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )
