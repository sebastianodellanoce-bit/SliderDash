"""
Report Generator Module
Generates cumulative PDF/HTML reports with executive summaries and charts.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime
import base64
from typing import Optional


# Funnel steps for drop-off analysis
FUNNEL_STEPS_ORDER = [
    ("Enpal Source Cookie", "Entry Point"),
    ("Per quale prodotto vuoi scoprire i bonus?", "Prodotto/Bonus"),
    ("Per quale tipo di edificio vuoi scoprire i bonus?", "Tipo Edificio"),
    ("Qual è l'indirizzo dell'edificio?", "Indirizzo"),
    ("Quando hai intenzione di acquistare il tuo prossimo sistema energetico?", "Decisione"),
    ("Qual è il tuo nome?", "Nome"),
    ("Qual è il tuo indirizzo email?", "Email"),
    ("Qual è il tuo numero di telefono?", "Telefono"),
    ("slider-success", "Lead Completato")
]


def init_report_session():
    """Initialize session state for cumulative reports."""
    if 'report_analyses' not in st.session_state:
        st.session_state.report_analyses = []
    if 'report_created_at' not in st.session_state:
        st.session_state.report_created_at = datetime.now().strftime("%Y-%m-%d %H:%M")


def clear_report():
    """Clear all analyses from the report."""
    st.session_state.report_analyses = []
    st.session_state.report_created_at = datetime.now().strftime("%Y-%m-%d %H:%M")


def fig_to_base64(fig: go.Figure, width: int = 800, height: int = 400) -> str:
    """Convert Plotly figure to base64 encoded PNG image."""
    try:
        img_bytes = pio.to_image(fig, format="png", width=width, height=height)
        return base64.b64encode(img_bytes).decode()
    except Exception:
        return None


def calculate_funnel_metrics(df: pd.DataFrame) -> dict:
    """Calculate detailed funnel metrics including drop-offs."""
    if df.empty or 'event_action' not in df.columns:
        return {}

    events = df.groupby('event_action')['count'].sum().to_dict()

    funnel_data = []
    prev_count = None

    for event_name, label in FUNNEL_STEPS_ORDER:
        count = events.get(event_name, 0)
        if count == 0:
            # Try with stripped whitespace
            for e, c in events.items():
                if e.strip() == event_name.strip():
                    count = c
                    break

        if count > 0 or prev_count is not None:
            drop_off = 0
            drop_off_pct = 0
            if prev_count and prev_count > 0:
                drop_off = prev_count - count
                drop_off_pct = (drop_off / prev_count) * 100

            funnel_data.append({
                'step': label,
                'event': event_name,
                'count': count,
                'drop_off': drop_off,
                'drop_off_pct': drop_off_pct
            })
            prev_count = count

    return funnel_data


def identify_critical_steps(old_funnel: list, new_funnel: list) -> list:
    """Identify the top 3 critical steps where most users are lost."""
    critical_steps = []

    # Combine data for comparison
    old_dict = {f['step']: f for f in old_funnel}
    new_dict = {f['step']: f for f in new_funnel}

    for step in old_dict:
        if step in new_dict and step != "Entry Point":
            old_drop = old_dict[step]['drop_off_pct']
            new_drop = new_dict[step]['drop_off_pct']

            critical_steps.append({
                'step': step,
                'old_drop_off': old_drop,
                'new_drop_off': new_drop,
                'difference': old_drop - new_drop,  # Positive = OLD worse
                'severity': max(old_drop, new_drop)
            })

    # Sort by severity (highest drop-off first)
    critical_steps.sort(key=lambda x: x['severity'], reverse=True)

    return critical_steps[:3]


def generate_executive_summary(
    old_df: pd.DataFrame,
    new_df: pd.DataFrame,
    old_name: str,
    new_name: str,
    date_range: str
) -> dict:
    """
    Generate a clear executive summary with:
    - Winner determination
    - Key metrics comparison
    - Critical funnel steps
    - Final recommendation
    """

    # Calculate KPIs
    def calc_kpis(df):
        if df.empty or 'event_action' not in df.columns:
            return {'leads': 0, 'start_rate': 0, 'end_rate': 0, 'cap_success': 0, 'reg_rate': 0, 'volume': 0}

        events = df.groupby('event_action')['count'].sum().to_dict()
        enpal = events.get('Enpal Source Cookie', 0)
        bonus = events.get('Per quale prodotto vuoi scoprire i bonus?', 0)
        building = events.get('Per quale tipo di edificio vuoi scoprire i bonus?', 0)
        leads = events.get('slider-success', 0)

        return {
            'leads': leads,
            'start_rate': round((bonus / enpal * 100), 2) if enpal > 0 else 0,
            'end_rate': round((leads / bonus * 100), 2) if bonus > 0 else 0,
            'cap_success': round((leads / building * 100), 2) if building > 0 else 0,
            'reg_rate': round((leads / enpal * 100), 2) if enpal > 0 else 0,
            'volume': enpal
        }

    old_kpis = calc_kpis(old_df)
    new_kpis = calc_kpis(new_df)

    # Calculate funnel metrics
    old_funnel = calculate_funnel_metrics(old_df)
    new_funnel = calculate_funnel_metrics(new_df)

    # Identify critical steps
    critical_steps = identify_critical_steps(old_funnel, new_funnel)

    # Determine winner
    score_old = 0
    score_new = 0

    # Compare metrics (weighted)
    if new_kpis['leads'] > old_kpis['leads']:
        score_new += 3  # Leads are most important
    else:
        score_old += 3

    if new_kpis['reg_rate'] > old_kpis['reg_rate']:
        score_new += 2
    else:
        score_old += 2

    if new_kpis['end_rate'] > old_kpis['end_rate']:
        score_new += 1
    else:
        score_old += 1

    if new_kpis['cap_success'] > old_kpis['cap_success']:
        score_new += 1
    else:
        score_old += 1

    winner = "NEW" if score_new > score_old else "OLD"
    winner_name = new_name if winner == "NEW" else old_name
    loser_name = old_name if winner == "NEW" else new_name

    # Calculate improvements
    leads_diff = new_kpis['leads'] - old_kpis['leads']
    leads_pct = ((new_kpis['leads'] / old_kpis['leads']) - 1) * 100 if old_kpis['leads'] > 0 else 0
    reg_rate_diff = new_kpis['reg_rate'] - old_kpis['reg_rate']

    # Determine main reasons (short)
    reasons = []
    if winner == "NEW":
        if leads_diff > 0:
            reasons.append(f"+{leads_diff:,} leads ({leads_pct:+.1f}%)")
        if reg_rate_diff > 0:
            reasons.append(f"Registration rate +{reg_rate_diff:.2f}pp")
        if new_kpis['end_rate'] > old_kpis['end_rate']:
            reasons.append(f"Migliore End Rate ({new_kpis['end_rate']:.1f}% vs {old_kpis['end_rate']:.1f}%)")
    else:
        if leads_diff < 0:
            reasons.append(f"+{-leads_diff:,} leads")
        if reg_rate_diff < 0:
            reasons.append(f"Registration rate +{-reg_rate_diff:.2f}pp")

    # Generate detailed explanation (motivo)
    explanation_parts = []

    if winner == "NEW":
        # NEW is better
        if leads_diff > 0:
            explanation_parts.append(f"ha generato {leads_diff:,} leads in più ({new_kpis['leads']:,} vs {old_kpis['leads']:,})")

        if reg_rate_diff > 0.5:
            explanation_parts.append(f"ha un tasso di conversione superiore ({new_kpis['reg_rate']:.2f}% vs {old_kpis['reg_rate']:.2f}%)")

        if new_kpis['end_rate'] > old_kpis['end_rate'] + 5:
            explanation_parts.append(f"converte meglio gli utenti che iniziano il funnel (End Rate: {new_kpis['end_rate']:.1f}% vs {old_kpis['end_rate']:.1f}%)")

        if new_kpis['cap_success'] > old_kpis['cap_success'] + 5:
            explanation_parts.append(f"ha un CAP Success migliore ({new_kpis['cap_success']:.1f}% vs {old_kpis['cap_success']:.1f}%)")

        # Check volume difference
        if old_kpis['volume'] > new_kpis['volume'] * 1.5:
            explanation_parts.append(f"nonostante abbia ricevuto meno traffico ({new_kpis['volume']:,} vs {old_kpis['volume']:,} visite)")

        winner_explanation = f"La landing NEW ha performato meglio perché {', '.join(explanation_parts)}." if explanation_parts else "La landing NEW ha mostrato performance complessive migliori."
    else:
        # OLD is better
        if leads_diff < 0:
            explanation_parts.append(f"ha generato {-leads_diff:,} leads in più ({old_kpis['leads']:,} vs {new_kpis['leads']:,})")

        if reg_rate_diff < -0.5:
            explanation_parts.append(f"ha un tasso di conversione superiore ({old_kpis['reg_rate']:.2f}% vs {new_kpis['reg_rate']:.2f}%)")

        if old_kpis['end_rate'] > new_kpis['end_rate'] + 5:
            explanation_parts.append(f"converte meglio gli utenti che iniziano il funnel (End Rate: {old_kpis['end_rate']:.1f}% vs {new_kpis['end_rate']:.1f}%)")

        winner_explanation = f"La landing OLD ha performato meglio perché {', '.join(explanation_parts)}." if explanation_parts else "La landing OLD ha mostrato performance complessive migliori."

    # Generate funnel problem explanation
    funnel_explanation = ""
    if critical_steps:
        worst_step = critical_steps[0]
        if worst_step['old_drop_off'] > worst_step['new_drop_off'] + 10:
            funnel_explanation = f"Il problema principale della OLD è nello step '{worst_step['step']}' dove perde il {worst_step['old_drop_off']:.1f}% degli utenti (vs {worst_step['new_drop_off']:.1f}% della NEW)."
        elif worst_step['new_drop_off'] > worst_step['old_drop_off'] + 10:
            funnel_explanation = f"Il problema principale della NEW è nello step '{worst_step['step']}' dove perde il {worst_step['new_drop_off']:.1f}% degli utenti (vs {worst_step['old_drop_off']:.1f}% della OLD)."
        else:
            funnel_explanation = f"Entrambe le landing hanno drop-off significativi nello step '{worst_step['step']}' (OLD: {worst_step['old_drop_off']:.1f}%, NEW: {worst_step['new_drop_off']:.1f}%)."

    # Build problems identified
    problems = []
    for cs in critical_steps:
        if cs['old_drop_off'] > cs['new_drop_off'] and cs['difference'] > 5:
            problems.append({
                'step': cs['step'],
                'issue': f"OLD perde {cs['old_drop_off']:.1f}% degli utenti vs {cs['new_drop_off']:.1f}% di NEW",
                'impact': 'alto' if cs['old_drop_off'] > 50 else 'medio'
            })
        elif cs['new_drop_off'] > cs['old_drop_off'] and cs['difference'] < -5:
            problems.append({
                'step': cs['step'],
                'issue': f"NEW perde {cs['new_drop_off']:.1f}% degli utenti vs {cs['old_drop_off']:.1f}% di OLD",
                'impact': 'alto' if cs['new_drop_off'] > 50 else 'medio'
            })
        else:
            problems.append({
                'step': cs['step'],
                'issue': f"Drop-off simile: OLD {cs['old_drop_off']:.1f}% vs NEW {cs['new_drop_off']:.1f}%",
                'impact': 'basso'
            })

    return {
        'date_range': date_range,
        'old_name': old_name,
        'new_name': new_name,
        'winner': winner,
        'winner_name': winner_name,
        'loser_name': loser_name,
        'score': {'old': score_old, 'new': score_new},
        'old_kpis': old_kpis,
        'new_kpis': new_kpis,
        'leads_diff': leads_diff,
        'leads_pct': leads_pct,
        'reg_rate_diff': reg_rate_diff,
        'reasons': reasons,
        'critical_steps': critical_steps,
        'problems': problems,
        'winner_explanation': winner_explanation,
        'funnel_explanation': funnel_explanation,
        'recommendation': f"MANTENERE {winner} LANDING" if abs(score_new - score_old) >= 2 else "RICHIEDE ULTERIORE ANALISI"
    }


def create_kpi_comparison_fig(old_df: pd.DataFrame, new_df: pd.DataFrame) -> go.Figure:
    """Create KPI comparison bar chart figure."""
    def calc_kpis(df):
        if df.empty or 'event_action' not in df.columns:
            return {'Leads': 0, 'Start Rate': 0, 'End Rate': 0, 'CAP Success': 0, 'Reg Rate': 0}

        events = df.groupby('event_action')['count'].sum().to_dict()
        enpal = events.get('Enpal Source Cookie', 0)
        bonus = events.get('Per quale prodotto vuoi scoprire i bonus?', 0)
        building = events.get('Per quale tipo di edificio vuoi scoprire i bonus?', 0)
        leads = events.get('slider-success', 0)

        return {
            'Leads': leads,
            'Start Rate': (bonus / enpal * 100) if enpal > 0 else 0,
            'End Rate': (leads / bonus * 100) if bonus > 0 else 0,
            'CAP Success': (leads / building * 100) if building > 0 else 0,
            'Reg Rate': (leads / enpal * 100) if enpal > 0 else 0,
        }

    old_kpis = calc_kpis(old_df)
    new_kpis = calc_kpis(new_df)
    kpi_names = list(old_kpis.keys())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='OLD Landing',
        x=kpi_names,
        y=list(old_kpis.values()),
        marker_color='#FF6B35',
        text=[f"{v:.1f}" for v in old_kpis.values()],
        textposition='outside'
    ))
    fig.add_trace(go.Bar(
        name='NEW Landing',
        x=kpi_names,
        y=list(new_kpis.values()),
        marker_color='#4ECDC4',
        text=[f"{v:.1f}" for v in new_kpis.values()],
        textposition='outside'
    ))
    fig.update_layout(
        barmode='group',
        title='KPI Comparison',
        height=350,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def add_analysis_to_report(
    analysis_name: str,
    date_range: str,
    old_landing_name: str,
    new_landing_name: str,
    old_df: pd.DataFrame,
    new_df: pd.DataFrame,
    filters_applied: Optional[dict] = None
):
    """Add a new analysis to the cumulative report with executive summary."""
    init_report_session()

    # Generate executive summary
    summary = generate_executive_summary(
        old_df, new_df,
        old_landing_name, new_landing_name,
        date_range
    )

    # Generate chart
    kpi_chart = create_kpi_comparison_fig(old_df, new_df)
    kpi_chart_b64 = fig_to_base64(kpi_chart) if kpi_chart else None

    analysis_entry = {
        'id': len(st.session_state.report_analyses) + 1,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'analysis_name': analysis_name,
        'date_range': date_range,
        'summary': summary,
        'filters': filters_applied or {},
        'chart': kpi_chart_b64
    }

    st.session_state.report_analyses.append(analysis_entry)
    return len(st.session_state.report_analyses)


def generate_html_report() -> str:
    """Generate clean HTML report with executive summaries."""
    init_report_session()

    if not st.session_state.report_analyses:
        return "<html><body><h1>No analyses to report</h1></body></html>"

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Landing Page Analysis Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 30px;
        }}

        .report {{ max-width: 900px; margin: 0 auto; }}

        .header {{
            background: linear-gradient(135deg, #191970 0%, #000080 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }}

        .header h1 {{ font-size: 24px; margin-bottom: 5px; }}
        .header .meta {{ opacity: 0.8; font-size: 14px; }}

        .analysis {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}

        .analysis-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}

        .analysis-title {{ font-size: 18px; font-weight: 600; color: #191970; }}
        .analysis-date {{ font-size: 13px; color: #888; }}

        .winner-box {{
            background: linear-gradient(135deg, #4ECDC4 0%, #44B3AA 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}

        .winner-box.old {{ background: linear-gradient(135deg, #FF6B35 0%, #E5552A 100%); }}

        .winner-label {{ font-size: 12px; text-transform: uppercase; opacity: 0.9; }}
        .winner-name {{ font-size: 22px; font-weight: 700; margin: 5px 0; }}
        .winner-reason {{ font-size: 14px; opacity: 0.9; }}

        .kpi-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
        }}

        .kpi-card {{
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e8e8e8;
        }}

        .kpi-card.old {{ border-left: 4px solid #FF6B35; }}
        .kpi-card.new {{ border-left: 4px solid #4ECDC4; }}

        .kpi-card h4 {{
            font-size: 13px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}

        .kpi-card .url-label {{
            font-size: 11px;
            color: #333;
            font-weight: 500;
            word-break: break-all;
            margin-bottom: 12px;
            padding: 8px;
            background: #f8f8f8;
            border-radius: 4px;
            text-transform: none;
        }}

        .kpi-row {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            font-size: 13px;
        }}

        .kpi-value {{ font-weight: 600; }}

        .problems-section {{
            background: #FFF8E1;
            border: 1px solid #FFE082;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}

        .problems-section h4 {{
            color: #F57C00;
            margin-bottom: 15px;
            font-size: 14px;
        }}

        .problem-item {{
            padding: 10px;
            background: white;
            border-radius: 6px;
            margin-bottom: 10px;
            border-left: 3px solid #FF9800;
        }}

        .problem-step {{ font-weight: 600; color: #333; }}
        .problem-desc {{ font-size: 13px; color: #666; margin-top: 5px; }}

        .recommendation {{
            background: #E8F5E9;
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin-top: 20px;
        }}

        .recommendation h4 {{
            color: #2E7D32;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}

        .recommendation .action {{
            font-size: 20px;
            font-weight: 700;
            color: #1B5E20;
        }}

        .motivo-section {{
            background: #E3F2FD;
            border: 1px solid #90CAF9;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}

        .motivo-section h4 {{
            color: #1565C0;
            margin-bottom: 12px;
            font-size: 14px;
        }}

        .motivo-text {{
            font-size: 14px;
            color: #333;
            line-height: 1.7;
        }}

        .motivo-text p {{
            margin-bottom: 10px;
        }}

        .motivo-text p:last-child {{
            margin-bottom: 0;
        }}

        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}

        .chart-container img {{
            max-width: 100%;
            border-radius: 8px;
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            color: #888;
            font-size: 12px;
        }}

        @media print {{
            body {{ padding: 10px; background: white; }}
            .analysis {{ page-break-inside: avoid; box-shadow: none; border: 1px solid #ddd; }}
        }}
    </style>
</head>
<body>
    <div class="report">
        <div class="header">
            <h1>Landing Page Analysis Report</h1>
            <p class="meta">Generato: {datetime.now().strftime("%d/%m/%Y %H:%M")} | Analisi: {len(st.session_state.report_analyses)}</p>
        </div>
"""

    for analysis in st.session_state.report_analyses:
        s = analysis['summary']
        winner_class = "old" if s['winner'] == "OLD" else ""

        html_content += f"""
        <div class="analysis">
            <div class="analysis-header">
                <span class="analysis-title">#{analysis['id']} - {analysis['analysis_name']}</span>
                <span class="analysis-date">{s['date_range']}</span>
            </div>

            <div class="winner-box {winner_class}">
                <div class="winner-label">Vincitore</div>
                <div class="winner-name">{s['winner']} LANDING</div>
                <div class="winner-reason">{' | '.join(s['reasons'][:2]) if s['reasons'] else 'Performance complessiva migliore'}</div>
            </div>

            <div class="kpi-comparison">
                <div class="kpi-card old">
                    <h4>OLD LANDING</h4>
                    <div class="url-label">{s['old_name']}</div>
                    <div class="kpi-row"><span>Leads</span><span class="kpi-value">{s['old_kpis']['leads']:,}</span></div>
                    <div class="kpi-row"><span>Volume</span><span class="kpi-value">{s['old_kpis']['volume']:,}</span></div>
                    <div class="kpi-row"><span>Reg Rate</span><span class="kpi-value">{s['old_kpis']['reg_rate']}%</span></div>
                    <div class="kpi-row"><span>End Rate</span><span class="kpi-value">{s['old_kpis']['end_rate']}%</span></div>
                    <div class="kpi-row"><span>CAP Success</span><span class="kpi-value">{s['old_kpis']['cap_success']}%</span></div>
                </div>
                <div class="kpi-card new">
                    <h4>NEW LANDING</h4>
                    <div class="url-label">{s['new_name']}</div>
                    <div class="kpi-row"><span>Leads</span><span class="kpi-value">{s['new_kpis']['leads']:,}</span></div>
                    <div class="kpi-row"><span>Volume</span><span class="kpi-value">{s['new_kpis']['volume']:,}</span></div>
                    <div class="kpi-row"><span>Reg Rate</span><span class="kpi-value">{s['new_kpis']['reg_rate']}%</span></div>
                    <div class="kpi-row"><span>End Rate</span><span class="kpi-value">{s['new_kpis']['end_rate']}%</span></div>
                    <div class="kpi-row"><span>CAP Success</span><span class="kpi-value">{s['new_kpis']['cap_success']}%</span></div>
                </div>
            </div>

            <div class="motivo-section">
                <h4>Motivo</h4>
                <div class="motivo-text">
                    <p>{s['winner_explanation']}</p>
                    {f"<p>{s['funnel_explanation']}</p>" if s['funnel_explanation'] else ""}
                </div>
            </div>
"""

        # Add problems section
        if s['problems']:
            html_content += """
            <div class="problems-section">
                <h4>Step Critici del Funnel (Dove si perdono utenti)</h4>
"""
            for p in s['problems']:
                html_content += f"""
                <div class="problem-item">
                    <div class="problem-step">{p['step']}</div>
                    <div class="problem-desc">{p['issue']}</div>
                </div>
"""
            html_content += "</div>"

        # Add chart if available
        if analysis.get('chart'):
            html_content += f"""
            <div class="chart-container">
                <img src="data:image/png;base64,{analysis['chart']}" alt="KPI Chart">
            </div>
"""

        # Add recommendation
        html_content += f"""
            <div class="recommendation">
                <h4>Raccomandazione Finale</h4>
                <div class="action">{s['recommendation']}</div>
            </div>
        </div>
"""

    html_content += """
        <div class="footer">
            <p>Enpal Landing Page Analytics | Report automatico</p>
        </div>
    </div>
</body>
</html>
"""

    return html_content


def render_report_section(
    old_df: pd.DataFrame,
    new_df: pd.DataFrame,
    old_landing_name: str,
    new_landing_name: str,
    date_range: str,
    filters: dict,
    ai_analysis: Optional[str] = None
):
    """Render the report generation UI section."""
    init_report_session()

    st.markdown("---")
    st.subheader("Report Generator")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write(f"**Analisi nel report:** {len(st.session_state.report_analyses)}")

        if st.session_state.report_analyses:
            with st.expander("Vedi analisi salvate"):
                for a in st.session_state.report_analyses:
                    winner = a['summary']['winner']
                    st.write(f"• **#{a['id']}** - {a['analysis_name']} → Vincitore: **{winner}**")

    with col2:
        # Use date_range in key to reset when dates change
        analysis_name = st.text_input(
            "Nome Analisi",
            value=f"Analisi {date_range}",
            key=f"analysis_name_{date_range}"
        )

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("Aggiungi al Report", type="primary", use_container_width=True):
            count = add_analysis_to_report(
                analysis_name=analysis_name,
                date_range=date_range,
                old_landing_name=old_landing_name or "OLD Landing",
                new_landing_name=new_landing_name or "NEW Landing",
                old_df=old_df,
                new_df=new_df,
                filters_applied=filters
            )
            st.success(f"Analisi #{count} aggiunta!")
            st.rerun()

    with col_btn2:
        if st.session_state.report_analyses:
            html_report = generate_html_report()
            st.download_button(
                label="Scarica Report",
                data=html_report,
                file_name=f"landing_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html",
                use_container_width=True
            )

    with col_btn3:
        if st.session_state.report_analyses:
            if st.button("Cancella", use_container_width=True):
                clear_report()
                st.info("Report cancellato!")
                st.rerun()

    with st.expander("Come funziona"):
        st.markdown("""
        1. **Applica filtri** e seleziona le landing da confrontare
        2. Clicca **"Aggiungi al Report"** per salvare questa analisi
        3. **Ripeti** con filtri diversi per aggiungere più confronti
        4. Clicca **"Scarica Report"** per ottenere il file HTML
        5. Apri nel browser e **stampa come PDF** se necessario

        **Il report include:**
        - Vincitore chiaro (OLD o NEW)
        - KPI confrontati
        - Step critici del funnel dove si perdono utenti
        - Raccomandazione finale
        """)
