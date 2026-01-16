"""Data loading functions for the Google Analytics Dashboard."""
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_csv_data(file_path: str) -> pd.DataFrame:
    """Load data from CSV file with caching."""
    path = Path(file_path)
    if not path.exists():
        st.error(f"Data file not found: {file_path}")
        return pd.DataFrame()

    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    return df


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_ga4_data(property_id: str, credentials_path: str = None, use_default_credentials: bool = True) -> pd.DataFrame:
    """Load data from Google Analytics 4 API."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
        import google.auth

        # Initialize client
        if use_default_credentials:
            credentials, project = google.auth.default()
            client = BetaAnalyticsDataClient(credentials=credentials)
        elif credentials_path:
            client = BetaAnalyticsDataClient.from_service_account_file(credentials_path)
        else:
            st.error("No credentials provided for GA4 API")
            return pd.DataFrame()

        # Define date range (last 90 days to avoid timeout)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        # Run the report
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="date"),
                Dimension(name="customEvent:event_action"),
                Dimension(name="sessionCampaignName"),
                Dimension(name="sessionSource"),
                Dimension(name="landingPage"),
            ],
            metrics=[
                Metric(name="eventCount"),
            ],
            date_ranges=[
                DateRange(
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d")
                )
            ],
            limit=250000,  # Increase row limit to get all data
        )

        response = client.run_report(request)

        # Convert to DataFrame
        rows = []
        for row in response.rows:
            rows.append({
                'date': row.dimension_values[0].value,
                'event_action': row.dimension_values[1].value,
                'campaign': row.dimension_values[2].value or '(not set)',
                'channel': row.dimension_values[3].value or '(not set)',
                'url': row.dimension_values[4].value or '(not set)',
                'count': int(row.metric_values[0].value),
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

        return df

    except Exception as e:
        st.error(f"Error loading GA4 data: {str(e)}")
        return pd.DataFrame()


def get_data(
    property_id: str = None,
    credentials_path: str = None,
    use_default_credentials: bool = True
) -> pd.DataFrame:
    """Get data from Google Analytics 4 API."""
    if not property_id:
        st.error("GA4 Property ID is required")
        return pd.DataFrame()
    return load_ga4_data(property_id, credentials_path, use_default_credentials)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_all_event_actions(property_id: str, credentials_path: str = None, use_default_credentials: bool = True) -> list:
    """Get ALL unique event_action values from GA4 (without other dimensions)."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
        import google.auth
        from datetime import datetime, timedelta

        # Initialize client
        if use_default_credentials:
            credentials, project = google.auth.default()
            client = BetaAnalyticsDataClient(credentials=credentials)
        elif credentials_path:
            client = BetaAnalyticsDataClient.from_service_account_file(credentials_path)
        else:
            return []

        # Date range (last 90 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        # Query ONLY event_action dimension
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="customEvent:event_action"),
            ],
            metrics=[
                Metric(name="eventCount"),
            ],
            date_ranges=[
                DateRange(
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d")
                )
            ],
            limit=10000,
        )

        response = client.run_report(request)

        # Extract unique event_action values
        event_actions = []
        for row in response.rows:
            event_actions.append({
                'event_action': row.dimension_values[0].value,
                'total_count': int(row.metric_values[0].value)
            })

        return event_actions

    except Exception as e:
        st.error(f"Error getting event actions: {str(e)}")
        return []


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_all_channels(property_id: str, credentials_path: str = None, use_default_credentials: bool = True) -> list:
    """Get ALL unique channel (sessionSource) values from GA4."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
        import google.auth
        from datetime import datetime, timedelta

        # Initialize client
        if use_default_credentials:
            credentials, project = google.auth.default()
            client = BetaAnalyticsDataClient(credentials=credentials)
        elif credentials_path:
            client = BetaAnalyticsDataClient.from_service_account_file(credentials_path)
        else:
            return []

        # Date range (last 90 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        # Query ONLY sessionSource dimension
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="sessionSource"),
            ],
            metrics=[
                Metric(name="eventCount"),
            ],
            date_ranges=[
                DateRange(
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d")
                )
            ],
            limit=10000,
        )

        response = client.run_report(request)

        # Extract unique channel values
        channels = []
        for row in response.rows:
            channels.append({
                'channel': row.dimension_values[0].value,
                'total_count': int(row.metric_values[0].value)
            })

        return channels

    except Exception as e:
        st.error(f"Error getting channels: {str(e)}")
        return []


def get_unique_campaigns(df: pd.DataFrame) -> list:
    """Get unique campaigns with event counts."""
    if df.empty:
        return []
    campaign_counts = df.groupby('campaign')['count'].sum().sort_values(ascending=False)
    return [(camp, count) for camp, count in campaign_counts.items()]


def get_unique_channels(df: pd.DataFrame) -> list:
    """Get unique channels with event counts."""
    if df.empty:
        return []
    channel_counts = df.groupby('channel')['count'].sum().sort_values(ascending=False)
    return [(channel, count) for channel, count in channel_counts.items()]


def get_unique_urls(df: pd.DataFrame) -> list:
    """Get unique URLs with event counts."""
    if df.empty:
        return []
    url_counts = df.groupby('url')['count'].sum().sort_values(ascending=False)
    return [(url, count) for url, count in url_counts.items()]


def filter_data(
    df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    campaigns: list = None,
    channels: list = None,
    urls: list = None
) -> pd.DataFrame:
    """Filter data based on date range, campaigns, channels, and URLs."""
    if df.empty:
        return df

    filtered = df.copy()

    # Date filter
    filtered = filtered[(filtered['date'] >= start_date) & (filtered['date'] <= end_date)]

    # Campaign filter
    if campaigns:
        filtered = filtered[filtered['campaign'].isin(campaigns)]

    # Channel filter
    if channels:
        filtered = filtered[filtered['channel'].isin(channels)]

    # URL filter
    if urls:
        filtered = filtered[filtered['url'].isin(urls)]

    return filtered


def aggregate_by_event_action(df: pd.DataFrame, url: str = None) -> pd.DataFrame:
    """Aggregate data by event_action with cascade ratio, filtered by landing page."""
    if df.empty:
        return pd.DataFrame(columns=['event_action', 'total_count', 'ratio'])

    # Filter by URL if provided
    filtered_df = df.copy()
    if url:
        filtered_df = filtered_df[filtered_df['url'] == url]

    result = filtered_df.groupby('event_action')['count'].sum().reset_index()
    result.columns = ['event_action', 'total_count']
    result = result.sort_values('total_count', ascending=False).reset_index(drop=True)

    # Limit to first 36 events (include all, even with 0 count)
    result = result.head(36).reset_index(drop=True)

    # Calculate cascade ratio (current row / previous row)
    ratios = []
    for i in range(len(result)):
        if i == 0:
            ratios.append("100%")
        else:
            prev_count = result.iloc[i - 1]['total_count']
            curr_count = result.iloc[i]['total_count']
            if prev_count > 0:
                ratio = (curr_count / prev_count) * 100
                ratios.append(f"{ratio:.1f}%")
            else:
                ratios.append("N/A")

    result['ratio'] = ratios
    return result
