"""Visualization functions for the Google Analytics Dashboard."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st


def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    """Create a bar chart using Plotly."""
    fig = px.bar(
        df,
        x=x,
        y=y,
        title=title,
        color=y,
        color_continuous_scale="Blues"
    )
    fig.update_layout(
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y.replace('_', ' ').title(),
        showlegend=False
    )
    return fig


def create_line_chart(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    """Create a line chart using Plotly."""
    fig = px.line(
        df,
        x=x,
        y=y,
        title=title,
        markers=True
    )
    fig.update_layout(
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y.replace('_', ' ').title()
    )
    return fig


def create_pie_chart(df: pd.DataFrame, values: str, names: str, title: str) -> go.Figure:
    """Create a pie chart using Plotly."""
    fig = px.pie(
        df,
        values=values,
        names=names,
        title=title,
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


def render_event_bar_chart(df: pd.DataFrame):
    """Render bar chart for event actions."""
    if df.empty:
        st.info("No data available for chart")
        return

    fig = create_bar_chart(df, 'event_action', 'total_count', 'Events by Action')
    st.plotly_chart(fig, width="stretch")


def render_daily_trend_chart(df: pd.DataFrame):
    """Render daily trend line chart."""
    if df.empty:
        st.info("No data available for chart")
        return

    daily_data = df.groupby('date')['count'].sum().reset_index()
    daily_data.columns = ['date', 'total_count']

    fig = create_line_chart(daily_data, 'date', 'total_count', 'Daily Event Trend')
    st.plotly_chart(fig, width="stretch")


def render_channel_pie_chart(df: pd.DataFrame):
    """Render pie chart for channel distribution."""
    if df.empty:
        st.info("No data available for chart")
        return

    channel_data = df.groupby('channel')['count'].sum().reset_index()
    channel_data.columns = ['channel', 'total_count']

    fig = create_pie_chart(channel_data, 'total_count', 'channel', 'Channel Distribution')
    st.plotly_chart(fig, width="stretch")


def render_campaign_bar_chart(df: pd.DataFrame):
    """Render horizontal bar chart for campaigns."""
    if df.empty:
        st.info("No data available for chart")
        return

    campaign_data = df.groupby('campaign')['count'].sum().reset_index()
    campaign_data.columns = ['campaign', 'total_count']
    campaign_data = campaign_data.sort_values('total_count', ascending=True)

    fig = px.bar(
        campaign_data,
        x='total_count',
        y='campaign',
        orientation='h',
        title='Events by Campaign',
        color='total_count',
        color_continuous_scale="Greens"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")
