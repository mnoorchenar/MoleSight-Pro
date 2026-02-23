import numpy as np
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, current_app
from ..data.compound_library import get_compound_library, TARGETS
from ..utils.charts import screening_scatter, fig_to_json
import plotly.graph_objects as go

screening_bp = Blueprint("screening", __name__)


def _composite_score(c: dict, target_weight: dict) -> float:
    """
    Compute a normalised composite docking/scoring function.
    Mimics a pharmacophore + property-weighted scoring model.
    """
    qed      = c.get("qed", 0.5)
    logp     = c.get("logp", 2.5)
    tpsa     = c.get("tpsa", 70)
    mw       = c.get("mw", 300)
    ic50_nm  = c.get("ic50_nm", 500)

    pIC50 = -np.log10(max(ic50_nm, 0.001) * 1e-9)
    norm_pic50 = np.clip((pIC50 - 4) / 8, 0, 1)

    # Rule-of-five penalty
    ro5_pen = 0.0
    if mw > 500:      ro5_pen += 0.1
    if logp > 5:      ro5_pen += 0.1
    if tpsa > 140:    ro5_pen += 0.1

    score = (
        0.45 * norm_pic50
        + 0.25 * qed
        + 0.15 * max(0, (5 - abs(logp - 2.5)) / 5)
        + 0.10 * max(0, (140 - tpsa) / 140)
        + 0.05 * max(0, (500 - mw) / 500)
        - ro5_pen
    )
    # Add deterministic jitter based on compound name hash
    rng_seed = abs(hash(c.get("name", "X"))) % 1000
    rng = np.random.default_rng(rng_seed)
    score += rng.normal(0, 0.02)

    return round(float(np.clip(score, 0.01, 0.99)), 4)


@screening_bp.route("/")
def screening():
    compounds = get_compound_library()

    # Score all compounds
    scored = []
    for c in compounds:
        s = dict(c)
        s["score"] = _composite_score(c, {})
        scored.append(s)

    scored_sorted = sorted(scored, key=lambda x: x["score"], reverse=True)

    df = pd.DataFrame(scored_sorted)
    chart_scatter = screening_scatter(df)

    # Activity distribution bar
    target_counts = {}
    for c in compounds:
        t = c.get("target", "Unknown")
        target_counts[t] = target_counts.get(t, 0) + 1

    BG, GRID, ACCENT1, TEXT, FONT = "#0a0e1a","#1e2640","#00ff88","#c8d4f0","DM Mono, monospace"
    bar_fig = go.Figure(go.Bar(
        x=list(target_counts.keys()),
        y=list(target_counts.values()),
        marker=dict(
            color=list(target_counts.values()),
            colorscale=[[0,"#003366"],[1,ACCENT1]],
            line=dict(color="rgba(0,0,0,0)"),
        ),
    ))
    bar_fig.update_layout(
        paper_bgcolor="#0f1424", plot_bgcolor=BG,
        font=dict(family=FONT, color=TEXT, size=11),
        xaxis=dict(tickangle=-35, gridcolor=GRID),
        yaxis=dict(gridcolor=GRID),
        margin=dict(l=40,r=10,t=30,b=80),
        title="Compound Count by Biological Target",
    )
    chart_targets = fig_to_json(bar_fig)

    return render_template("screening.html",
        compounds=scored_sorted,
        targets=TARGETS,
        chart_scatter=chart_scatter,
        chart_targets=chart_targets,
    )


@screening_bp.route("/api/score", methods=["POST"])
def api_score():
    data   = request.get_json(silent=True) or {}
    target = data.get("target", "")
    compounds = get_compound_library()
    scored = []
    for c in compounds:
        s = dict(c)
        s["score"] = _composite_score(c, {"target": target})
        scored.append(s)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({"results": scored[:10], "target": target})
