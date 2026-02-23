"""
Plotly chart generation for the drug discovery dashboard.
All charts return JSON-serialisable dicts (Plotly figures).
"""

import json
import plotly
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ── Brand palette ──────────────────────────────────────────────────────────────
BG       = "#0a0e1a"
PAPER_BG = "#0f1424"
GRID     = "#1e2640"
ACCENT1  = "#00ff88"   # phosphor green
ACCENT2  = "#00ccff"   # electric blue
ACCENT3  = "#ff6b6b"   # alert red
ACCENT4  = "#ffaa00"   # amber
TEXT     = "#c8d4f0"
FONT     = "DM Mono, monospace"

LAYOUT_BASE = dict(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=BG,
    font=dict(family=FONT, color=TEXT, size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
)


def fig_to_json(fig) -> str:
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


# ── Dashboard Charts ────────────────────────────────────────────────────────────

def property_distribution_chart(compounds: list) -> str:
    """Scatter of MW vs LogP colored by drug-likeness."""
    df = pd.DataFrame(compounds)
    df["Drug-Like"] = df["drug_like"].map({1: "Drug-Like", 0: "Non Drug-Like"})

    fig = go.Figure()
    for label, color in [("Drug-Like", ACCENT1), ("Non Drug-Like", ACCENT3)]:
        sub = df[df["Drug-Like"] == label]
        fig.add_trace(go.Scatter(
            x=sub["mw"], y=sub["logp"],
            mode="markers",
            name=label,
            text=sub["name"],
            hovertemplate="<b>%{text}</b><br>MW: %{x:.1f}<br>LogP: %{y:.2f}<extra></extra>",
            marker=dict(
                color=color, size=10, opacity=0.85,
                line=dict(color="rgba(255,255,255,0.2)", width=1)
            ),
        ))

    # Lipinski boundary
    fig.add_shape(type="rect", x0=0, x1=500, y0=-float("inf"), y1=5,
                  fillcolor="rgba(0,255,136,0.04)", line=dict(color=ACCENT1, width=1, dash="dot"))
    fig.add_annotation(x=490, y=4.7, text="Ro5 Zone", showarrow=False,
                       font=dict(color=ACCENT1, size=10))

    fig.update_layout(**LAYOUT_BASE, title="MW vs LogP — Chemical Space",
                      xaxis_title="Molecular Weight (Da)", yaxis_title="LogP",
                      legend=dict(bgcolor="rgba(0,0,0,0)"))
    return fig_to_json(fig)


def qed_distribution_chart(compounds: list) -> str:
    """Histogram of QED scores."""
    qeds = [c["qed"] for c in compounds]
    fig = go.Figure(go.Histogram(
        x=qeds, nbinsx=12,
        marker=dict(
            color=qeds,
            colorscale=[[0, ACCENT3], [0.5, ACCENT4], [1, ACCENT1]],
            line=dict(color="rgba(0,0,0,0.3)", width=1),
        ),
    ))
    fig.update_layout(**LAYOUT_BASE, title="QED Score Distribution",
                      xaxis_title="QED (0=least drug-like, 1=most)",
                      yaxis_title="Count", showlegend=False)
    return fig_to_json(fig)


def bioactivity_heatmap(compounds: list) -> str:
    """Heatmap of bioactivity IC50 (pIC50 scale) by compound × property."""
    df = pd.DataFrame(compounds)
    df["pIC50"] = -np.log10(df["ic50_nm"] * 1e-9)
    df["pIC50"] = df["pIC50"].clip(3, 12).round(2)

    props = ["mw", "logp", "hbd", "hba", "tpsa", "qed"]
    heat_data = df[props].T
    heat_data.columns = df["name"]

    # Normalise each row 0-1
    normed = heat_data.apply(lambda row: (row - row.min()) / (row.max() - row.min() + 1e-9), axis=1)

    fig = go.Figure(go.Heatmap(
        z=normed.values,
        x=heat_data.columns.tolist(),
        y=props,
        colorscale=[[0, "#0a0e1a"], [0.5, "#0057a8"], [1, ACCENT1]],
        showscale=True,
        hovertemplate="Compound: %{x}<br>Property: %{y}<br>Normalised: %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE, title="Normalised Molecular Property Heatmap",
        xaxis=dict(tickangle=-45, gridcolor=GRID),
        height=360,
    )
    return fig_to_json(fig)


def radar_chart(radar_data: dict, name: str = "Query Molecule") -> str:
    """Spider/radar chart of normalised drug-like properties."""
    categories = list(radar_data.keys())
    values = list(radar_data.values())
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values_closed, theta=categories_closed,
        fill="toself",
        fillcolor="rgba(0,255,136,0.15)",
        line=dict(color=ACCENT1, width=2),
        marker=dict(color=ACCENT1, size=6),
        name=name,
    ))
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=PAPER_BG,
        font=dict(family=FONT, color=TEXT),
        polar=dict(
            bgcolor=BG,
            radialaxis=dict(visible=True, range=[0, 1], gridcolor=GRID,
                            tickfont=dict(color=TEXT, size=9)),
            angularaxis=dict(gridcolor=GRID, tickfont=dict(color=ACCENT2)),
        ),
        margin=dict(l=60, r=60, t=40, b=40),
        title=f"Drug-likeness Profile — {name}",
        showlegend=False,
    )
    return fig_to_json(fig)


def admet_gauge_chart(admet_scores: dict) -> str:
    """Multiple gauge charts as subplots for ADMET properties."""
    from plotly.subplots import make_subplots

    props = list(admet_scores.items())
    n = len(props)

    fig = make_subplots(
        rows=2, cols=3, subplot_titles=[p[0] for p in props],
        specs=[[{"type": "indicator"}] * 3, [{"type": "indicator"}] * 3],
    )

    positions = [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3)]
    for i, (prop, val) in enumerate(props[:6]):
        row, col = positions[i]
        color = ACCENT1 if val >= 0.6 else (ACCENT4 if val >= 0.35 else ACCENT3)
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=round(val * 100, 1),
            number=dict(suffix="%", font=dict(color=color, size=18)),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor=TEXT, tickwidth=1),
                bar=dict(color=color, thickness=0.6),
                bgcolor=GRID,
                borderwidth=1, bordercolor=GRID,
                steps=[
                    dict(range=[0, 35], color="#1a0a0a"),
                    dict(range=[35, 60], color="#1a1200"),
                    dict(range=[60, 100], color="#001a0d"),
                ],
            ),
        ), row=row, col=col)

    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        font=dict(family=FONT, color=TEXT),
        height=380,
        margin=dict(l=20, r=20, t=50, b=10),
        title="ADMET Profile",
    )
    return fig_to_json(fig)


def screening_scatter(df: pd.DataFrame) -> str:
    """Scatter plot for virtual screening results: Docking Score vs QED."""
    color_vals = df.get("score", [0.5] * len(df))
    if hasattr(color_vals, 'tolist'):
        color_vals = color_vals.tolist()

    fig = go.Figure(go.Scatter(
        x=df["qed"], y=df["score"],
        mode="markers",
        text=df["name"],
        hovertemplate="<b>%{text}</b><br>QED: %{x:.3f}<br>Score: %{y:.3f}<extra></extra>",
        marker=dict(
            size=10,
            color=df["score"],
            colorscale=[[0, ACCENT3], [0.5, ACCENT4], [1, ACCENT1]],
            showscale=True,
            colorbar=dict(title="Score", tickfont=dict(color=TEXT)),
            line=dict(color="rgba(255,255,255,0.15)", width=1),
        ),
    ))
    fig.update_layout(
        **LAYOUT_BASE, title="Virtual Screening — Score vs QED",
        xaxis_title="QED (drug-likeness)",
        yaxis_title="Composite Screening Score",
    )
    return fig_to_json(fig)


def feature_importance_chart(feature_names: list, importances: list) -> str:
    """Horizontal bar chart for ML feature importances."""
    sorted_pairs = sorted(zip(importances, feature_names))
    vals, names = zip(*sorted_pairs)

    fig = go.Figure(go.Bar(
        x=list(vals), y=list(names), orientation="h",
        marker=dict(
            color=list(vals),
            colorscale=[[0, ACCENT2], [1, ACCENT1]],
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        hovertemplate="%{y}: %{x:.3f}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE, title="Feature Importance",
        xaxis_title="Importance", yaxis_title="",
        height=300,
    )
    return fig_to_json(fig)


def probability_gauge(probability: float, label: str) -> str:
    """Single gauge for drug-likeness probability."""
    color = ACCENT1 if probability >= 0.6 else (ACCENT4 if probability >= 0.4 else ACCENT3)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(probability * 100, 1),
        number=dict(suffix="%", font=dict(color=color, family=FONT, size=36)),
        delta=dict(reference=50, valueformat=".1f"),
        title=dict(text=f"Drug-Likeness Probability<br><b>{label}</b>",
                   font=dict(color=TEXT, family=FONT, size=14)),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor=TEXT),
            bar=dict(color=color, thickness=0.7),
            bgcolor=GRID,
            borderwidth=2, bordercolor=GRID,
            steps=[
                dict(range=[0, 40], color="#1a0a0a"),
                dict(range=[40, 60], color="#1a1200"),
                dict(range=[60, 100], color="#001a0d"),
            ],
            threshold=dict(line=dict(color=ACCENT2, width=3), thickness=0.8, value=60),
        ),
    ))
    fig.update_layout(
        paper_bgcolor=PAPER_BG, font=dict(family=FONT, color=TEXT),
        height=280, margin=dict(l=30, r=30, t=60, b=10),
    )
    return fig_to_json(fig)


def tpsa_vs_mw_chart(compounds: list) -> str:
    df = pd.DataFrame(compounds)
    df["Drug-Like"] = df["drug_like"].map({1: "Yes", 0: "No"})

    fig = go.Figure()
    for label, color in [("Yes", ACCENT1), ("No", ACCENT3)]:
        sub = df[df["Drug-Like"] == label]
        fig.add_trace(go.Scatter(
            x=sub["mw"], y=sub["tpsa"],
            mode="markers", name=f"Drug-Like: {label}",
            text=sub["name"],
            hovertemplate="<b>%{text}</b><br>MW: %{x:.1f}<br>TPSA: %{y:.1f} Å²<extra></extra>",
            marker=dict(color=color, size=9, opacity=0.85,
                        line=dict(color="rgba(255,255,255,0.2)", width=1)),
        ))
    fig.add_hline(y=140, line=dict(color=ACCENT4, dash="dot", width=1),
                  annotation_text="TPSA = 140 Å²", annotation_position="bottom right",
                  annotation_font=dict(color=ACCENT4, size=10))
    fig.update_layout(
        **LAYOUT_BASE, title="TPSA vs MW — Oral Bioavailability Zone",
        xaxis_title="Molecular Weight (Da)", yaxis_title="TPSA (Å²)",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig_to_json(fig)
