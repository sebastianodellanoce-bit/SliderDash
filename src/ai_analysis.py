"""AI-powered analysis using Claude for the Google Analytics Dashboard."""
import anthropic
import pandas as pd
import streamlit as st
from config.config import ANTHROPIC_API_KEY


def get_data_summary(df: pd.DataFrame, landing_type: str) -> dict:
    """Extract key metrics from dataframe for AI analysis."""
    if df.empty:
        return {"landing_type": landing_type, "has_data": False}

    summary = {
        "landing_type": landing_type,
        "has_data": True,
        "total_events": int(df['count'].sum()),
        "unique_campaigns": df['campaign'].nunique() if 'campaign' in df.columns else 0,
        "unique_channels": df['channel'].nunique() if 'channel' in df.columns else 0,
    }

    if 'event_action' in df.columns:
        event_counts = df.groupby('event_action')['count'].sum().to_dict()
        summary["event_breakdown"] = event_counts

        enpal_cookie = event_counts.get("Enpal Source Cookie", 0)
        first_question = event_counts.get("A quale prodotto sei interessato?", 0)
        last_question = event_counts.get("Per quale prodotto vuoi scoprire i bonus?", 0)
        building_type = event_counts.get("Per quale tipo di edificio vuoi scoprire i bonus?", 0)
        slider_success = event_counts.get("slider-success", 0)

        summary["leads"] = slider_success
        summary["start_rate"] = (last_question / enpal_cookie * 100) if enpal_cookie > 0 else 0
        summary["end_rate"] = (slider_success / last_question * 100) if last_question > 0 else 0
        summary["cap_success"] = (slider_success / building_type * 100) if building_type > 0 else 0
        summary["registration_rate"] = (slider_success / enpal_cookie * 100) if enpal_cookie > 0 else 0

        # Calculate ratios between consecutive funnel steps
        summary["step_ratios"] = {}
        sorted_events = sorted(event_counts.items(), key=lambda x: -x[1])
        for i, (event, count) in enumerate(sorted_events):
            if enpal_cookie > 0:
                summary["step_ratios"][event] = {
                    "count": count,
                    "ratio_vs_start": (count / enpal_cookie * 100)
                }

    return summary


def analyze_with_claude(old_data: pd.DataFrame, new_data: pd.DataFrame, start_date: str, end_date: str) -> str:
    """Use Claude to analyze and compare OLD vs NEW landing page performance."""
    if not ANTHROPIC_API_KEY:
        return "Anthropic API key not configured. Please add ANTHROPIC_API_KEY to your .env file."

    old_summary = get_data_summary(old_data, "OLD Landing")
    new_summary = get_data_summary(new_data, "NEW Landing")

    prompt = f"""Sei un analista di dati esperto. Analizza i seguenti dati di Google Analytics confrontando le performance della landing page OLD vs NEW per un funnel slider.

PERIODO DI ANALISI: Dal {start_date} al {end_date}

DATI OLD LANDING PAGE:
{format_summary(old_summary)}

DATI NEW LANDING PAGE:
{format_summary(new_summary)}

ISTRUZIONI IMPORTANTI:
- Analizza TUTTI gli eventi presenti nella lista (event_action), non solo i KPI principali
- Per ogni evento, considera sia il count totale che il ratio rispetto a "Enpal Source Cookie" (punto di partenza del funnel)
- Confronta i numeri assoluti E le percentuali tra OLD e NEW

Fornisci un'analisi COMPLETA in italiano che include:

1. **Confronto KPI Principali**:
   - Leads (slider-success): confronto numeri assoluti e variazione %
   - Start Rate: confronto e variazione %
   - End Rate: confronto e variazione %
   - CAP Success (slider-success / Per quale tipo di edificio vuoi scoprire i bonus?): confronto e variazione %
   - Registration Rate: confronto e variazione %

2. **Analisi Completa del Funnel**:
   - Analizza OGNI evento presente nei dati
   - Per ogni step del funnel, indica: count OLD vs NEW, ratio OLD vs NEW
   - Identifica dove ci sono le differenze maggiori tra le due landing

3. **Drop-off Analysis**:
   - Identifica i passaggi dove si perdono più utenti
   - Calcola il drop-off tra step consecutivi del funnel
   - Evidenzia differenze di drop-off tra OLD e NEW

4. **Conclusione Finale**:
   IMPORTANTE: Termina SEMPRE con una frase conclusiva chiara nel formato:
   "**Nel periodo dal {start_date} al {end_date}, la landing page [OLD/NEW] ha performato meglio perché...**"

   Spiega brevemente il motivo principale (es: più leads, migliore conversion rate, etc.)

Usa tabelle o elenchi puntati per rendere i confronti chiari e leggibili."""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except anthropic.APIError as e:
        return f"Error calling Claude API: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def format_summary(summary: dict) -> str:
    """Format summary dict for the prompt."""
    if not summary.get("has_data", False):
        return f"{summary['landing_type']}: No data available"

    lines = [
        f"Landing Type: {summary['landing_type']}",
        f"Total Events: {summary['total_events']:,}",
        f"Leads (slider-success): {summary.get('leads', 0):,}",
        f"Start Rate: {summary.get('start_rate', 0):.2f}%",
        f"End Rate: {summary.get('end_rate', 0):.2f}%",
        f"CAP Success: {summary.get('cap_success', 0):.2f}%",
        f"Registration Rate: {summary.get('registration_rate', 0):.2f}%",
        f"Unique Campaigns: {summary['unique_campaigns']}",
        f"Unique Channels: {summary['unique_channels']}",
    ]

    if "step_ratios" in summary:
        lines.append("\nComplete Event Breakdown (with ratios vs Enpal Source Cookie):")
        for event, data in sorted(summary["step_ratios"].items(), key=lambda x: -x[1]["count"]):
            lines.append(f"  - {event}: {data['count']:,} (ratio: {data['ratio_vs_start']:.2f}%)")

    return "\n".join(lines)


def render_ai_analysis(old_data: pd.DataFrame, new_data: pd.DataFrame, start_date: str, end_date: str):
    """Render AI analysis section in Streamlit."""
    st.subheader("Analysis")

    if old_data.empty and new_data.empty:
        st.info("No data available for AI analysis. Please adjust your filters.")
        return

    # Custom CSS for dark blue button
    st.markdown("""
    <style>
        div.stButton > button[kind="primary"] {
            background-color: #191970 !important;
            border-color: #191970 !important;
            color: white !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #000080 !important;
            border-color: #000080 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Show previous analysis if exists
    if st.session_state.get('last_ai_analysis'):
        st.markdown(st.session_state.last_ai_analysis)
        if st.button("Run New Analysis", type="secondary"):
            st.session_state.last_ai_analysis = None
            st.rerun()
    else:
        if st.button("Vedi i motivi", type="primary"):
            with st.spinner("Claude sta analizzando i dati..."):
                analysis = analyze_with_claude(old_data, new_data, start_date, end_date)
                st.session_state.last_ai_analysis = analysis
                st.markdown(analysis)
