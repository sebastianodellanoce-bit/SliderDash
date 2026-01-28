"""Visualization functions for the Google Analytics Dashboard."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

# Funnel steps configuration
FUNNEL_STEPS = [
    "Enpal Source Cookie",
    "Per quale prodotto vuoi scoprire i bonus?",
    "Per quale tipo di edificio vuoi scoprire i bonus?",
    "slider-success"
]

FUNNEL_LABELS = [
    "Start",
    "Product Selection",
    "Building Type",
    "Lead (Success)"
]


def get_kpi_data(df: pd.DataFrame) -> dict:
    """Extract KPI values from dataframe."""
    if df.empty or 'event_action' not in df.columns:
        return {
            'Leads': 0,
            'Start Rate': 0,
            'End Rate': 0,
            'Reg Rate': 0,
            'PostCap': 0
        }

    events = df.groupby('event_action')['count'].sum().to_dict()
    enpal = events.get('Enpal Source Cookie', 0)
    bonus = events.get('Per quale prodotto vuoi scoprire i bonus?', 0)
    building = events.get('Per quale tipo di edificio vuoi scoprire i bonus?', 0)
    leads = events.get('slider-success', 0)

    return {
        'Leads': leads,
        'Start Rate': (bonus / enpal * 100) if enpal > 0 else 0,
        'End Rate': (leads / bonus * 100) if bonus > 0 else 0,
        'Reg Rate': (leads / enpal * 100) if enpal > 0 else 0,
        'PostCap': (leads / building * 100) if building > 0 else 0
    }


def get_funnel_data(df: pd.DataFrame) -> dict:
    """Extract funnel step counts from dataframe."""
    if df.empty or 'event_action' not in df.columns:
        return {}

    event_counts = df.groupby('event_action')['count'].sum().to_dict()

    funnel_data = {}
    for step, label in zip(FUNNEL_STEPS, FUNNEL_LABELS):
        count = event_counts.get(step, 0)
        if count == 0:
            for event, cnt in event_counts.items():
                if event.strip() == step.strip():
                    count = cnt
                    break
        funnel_data[label] = count

    return funnel_data


# =============================================================================
# 1. KPI COMPARISON BAR CHART
# =============================================================================
def render_kpi_comparison_chart(old_df: pd.DataFrame, new_df: pd.DataFrame):
    """Bar chart comparing KPIs between Old and New landing pages."""
    old_kpis = get_kpi_data(old_df)
    new_kpis = get_kpi_data(new_df)

    kpi_names = list(old_kpis.keys())

    fig = go.Figure()

    # OLD bars
    fig.add_trace(go.Bar(
        name='OLD Landing',
        x=kpi_names,
        y=list(old_kpis.values()),
        marker_color='#FF6B35',
        text=[f"{v:.1f}" if isinstance(v, float) and v < 1000 else f"{int(v):,}" for v in old_kpis.values()],
        textposition='outside'
    ))

    # NEW bars
    fig.add_trace(go.Bar(
        name='NEW Landing',
        x=kpi_names,
        y=list(new_kpis.values()),
        marker_color='#4ECDC4',
        text=[f"{v:.1f}" if isinstance(v, float) and v < 1000 else f"{int(v):,}" for v in new_kpis.values()],
        textposition='outside'
    ))

    fig.update_layout(
        barmode='group',
        title='KPI Comparison: OLD vs NEW Landing',
        xaxis_title='KPI',
        yaxis_title='Value',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# 2. DAILY TREND LINE CHART (Old vs New)
# =============================================================================
def render_trend_comparison_chart(old_df: pd.DataFrame, new_df: pd.DataFrame):
    """Line chart showing daily trends for Old vs New landing pages."""
    if old_df.empty and new_df.empty:
        st.info("No data available for trend chart")
        return

    fig = go.Figure()

    # OLD trend
    if not old_df.empty:
        old_daily = old_df.groupby('date')['count'].sum().reset_index()
        old_daily = old_daily.sort_values('date')
        fig.add_trace(go.Scatter(
            x=old_daily['date'],
            y=old_daily['count'],
            mode='lines+markers',
            name='OLD Landing',
            line=dict(color='#FF6B35', width=2),
            marker=dict(size=6)
        ))

    # NEW trend
    if not new_df.empty:
        new_daily = new_df.groupby('date')['count'].sum().reset_index()
        new_daily = new_daily.sort_values('date')
        fig.add_trace(go.Scatter(
            x=new_daily['date'],
            y=new_daily['count'],
            mode='lines+markers',
            name='NEW Landing',
            line=dict(color='#4ECDC4', width=2),
            marker=dict(size=6)
        ))

    fig.update_layout(
        title='Daily Trend: OLD vs NEW Landing',
        xaxis_title='Date',
        yaxis_title='Event Count',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# 3. DROP-OFF CHART (Step-to-step retention)
# =============================================================================
def render_dropoff_chart(old_df: pd.DataFrame, new_df: pd.DataFrame):
    """Line chart showing % retention through funnel steps."""
    old_funnel = get_funnel_data(old_df)
    new_funnel = get_funnel_data(new_df)

    if not old_funnel and not new_funnel:
        st.info("No funnel data available")
        return

    # Calculate retention percentages
    old_start = old_funnel.get('Start', 1) or 1
    new_start = new_funnel.get('Start', 1) or 1

    old_retention = [(old_funnel.get(label, 0) / old_start * 100) for label in FUNNEL_LABELS]
    new_retention = [(new_funnel.get(label, 0) / new_start * 100) for label in FUNNEL_LABELS]

    fig = go.Figure()

    # OLD line
    fig.add_trace(go.Scatter(
        x=FUNNEL_LABELS,
        y=old_retention,
        mode='lines+markers+text',
        name='OLD Landing',
        line=dict(color='#FF6B35', width=3),
        marker=dict(size=12),
        text=[f"{v:.1f}%" for v in old_retention],
        textposition="top center"
    ))

    # NEW line
    fig.add_trace(go.Scatter(
        x=FUNNEL_LABELS,
        y=new_retention,
        mode='lines+markers+text',
        name='NEW Landing',
        line=dict(color='#4ECDC4', width=3),
        marker=dict(size=12),
        text=[f"{v:.1f}%" for v in new_retention],
        textposition="bottom center"
    ))

    fig.update_layout(
        title='Drop-off Analysis (% Retention from Start)',
        xaxis_title='Funnel Step',
        yaxis_title='% Retention',
        yaxis=dict(range=[0, 110]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# 4. STACKED BAR - Event Distribution Comparison
# =============================================================================
def render_event_comparison_chart(old_df: pd.DataFrame, new_df: pd.DataFrame):
    """Stacked bar chart comparing top events between Old and New."""
    if old_df.empty and new_df.empty:
        st.info("No data available for event comparison")
        return

    # Get top 10 events from combined data
    all_events = set()
    if not old_df.empty and 'event_action' in old_df.columns:
        old_events = old_df.groupby('event_action')['count'].sum()
        all_events.update(old_events.nlargest(10).index.tolist())
    if not new_df.empty and 'event_action' in new_df.columns:
        new_events = new_df.groupby('event_action')['count'].sum()
        all_events.update(new_events.nlargest(10).index.tolist())

    if not all_events:
        st.info("No event data available")
        return

    # Prepare data
    events_list = list(all_events)[:12]  # Limit to 12 events
    old_counts = []
    new_counts = []

    for event in events_list:
        if not old_df.empty and 'event_action' in old_df.columns:
            old_count = old_df[old_df['event_action'] == event]['count'].sum()
        else:
            old_count = 0
        if not new_df.empty and 'event_action' in new_df.columns:
            new_count = new_df[new_df['event_action'] == event]['count'].sum()
        else:
            new_count = 0
        old_counts.append(old_count)
        new_counts.append(new_count)

    # Shorten event names for display
    short_names = [e[:25] + '...' if len(e) > 25 else e for e in events_list]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='OLD Landing',
        y=short_names,
        x=old_counts,
        orientation='h',
        marker_color='#FF6B35'
    ))

    fig.add_trace(go.Bar(
        name='NEW Landing',
        y=short_names,
        x=new_counts,
        orientation='h',
        marker_color='#4ECDC4'
    ))

    fig.update_layout(
        barmode='group',
        title='Event Distribution: OLD vs NEW',
        xaxis_title='Count',
        yaxis_title='Event Action',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# RENDER ALL COMPARISON CHARTS
# =============================================================================
def render_all_comparison_charts(old_df: pd.DataFrame, new_df: pd.DataFrame):
    """Render all comparison charts in a structured layout."""

    # Row 1: KPI Comparison
    st.subheader("1. KPI Comparison")
    render_kpi_comparison_chart(old_df, new_df)

    st.markdown("---")

    # Row 2: Daily Trend
    st.subheader("2. Daily Trend")
    render_trend_comparison_chart(old_df, new_df)

    st.markdown("---")

    # Row 3: Drop-off Analysis
    st.subheader("3. Drop-off Analysis")
    render_dropoff_chart(old_df, new_df)

    st.markdown("---")

    # Row 4: Event Distribution
    st.subheader("4. Event Distribution")
    render_event_comparison_chart(old_df, new_df)
