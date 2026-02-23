"""
ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) predictor.
Multi-output regression trained on synthetic property distributions.
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputRegressor


INPUT_FEATURES = ["mw", "logp", "hbd", "hba", "tpsa", "rotbonds", "qed", "fsp3"]
ADMET_TARGETS  = [
    "Absorption",    # oral absorption probability (0-1)
    "Distribution",  # volume of distribution (normalised 0-1)
    "Metabolism",    # metabolic stability (0-1, higher = more stable)
    "Excretion",     # renal clearance score (0-1)
    "Toxicity",      # toxicity risk (0-1, higher = safer)
]

# ── Reference ranges for display ───────────────────────────────────────────────
ADMET_DESCRIPTIONS = {
    "Absorption":   "Predicted oral absorption via GI tract (Caco-2 / F%)",
    "Distribution": "Volume of distribution / tissue binding estimate",
    "Metabolism":   "Hepatic metabolic stability (CYP450 clearance)",
    "Excretion":    "Renal clearance and half-life estimate",
    "Toxicity":     "Safety score (hERG, AMES, hepatotoxicity composite)",
}

ADMET_THRESHOLDS = {
    "Absorption":   {"good": 0.6, "moderate": 0.35},
    "Distribution": {"good": 0.5, "moderate": 0.3},
    "Metabolism":   {"good": 0.65, "moderate": 0.4},
    "Excretion":    {"good": 0.55, "moderate": 0.3},
    "Toxicity":     {"good": 0.65, "moderate": 0.4},
}


class ADMETModel:
    """Predicts ADMET profile as 5 normalised scores (0 – 1, higher = better)."""

    def __init__(self):
        self.model = None
        self._train()

    def _simulate_admet(self, mw, logp, hbd, hba, tpsa, rot, qed, fsp3, rng):
        """
        Rule-based + stochastic simulation of ADMET scores.
        Encodes domain knowledge from medicinal chemistry:
          - Absorption: low MW, moderate LogP, low TPSA → better
          - Distribution: moderate LogP, fsp3 → better CNS penetration
          - Metabolism: high fsp3, low aromatic rings → more stable
          - Excretion:  low MW → better renal clearance
          - Toxicity:   low LogP, good QED → safer
        """
        # Absorption (Caco-2 / %F proxy)
        abs_base = (
            0.6 * _norm(mw, 150, 450, invert=True)
            + 0.2 * _norm(logp, -0.5, 4.5)
            + 0.2 * _norm(tpsa, 20, 100, invert=True)
        )
        absorption = np.clip(abs_base + rng.normal(0, 0.06, len(mw)), 0.05, 0.98)

        # Distribution (Vd proxy)
        dist_base = (
            0.4 * _norm(logp, 1, 4.5)
            + 0.4 * fsp3
            + 0.2 * _norm(hba, 0, 8, invert=True)
        )
        distribution = np.clip(dist_base + rng.normal(0, 0.07, len(mw)), 0.05, 0.95)

        # Metabolism (CYP stability)
        met_base = (
            0.5 * fsp3
            + 0.3 * _norm(logp, 0, 3.5, invert=True)
            + 0.2 * qed
        )
        metabolism = np.clip(met_base + rng.normal(0, 0.07, len(mw)), 0.05, 0.95)

        # Excretion (renal clearance)
        exc_base = (
            0.7 * _norm(mw, 100, 400, invert=True)
            + 0.2 * _norm(hbd, 0, 5)
            + 0.1 * _norm(rot, 0, 8, invert=True)
        )
        excretion = np.clip(exc_base + rng.normal(0, 0.07, len(mw)), 0.05, 0.95)

        # Toxicity safety score (composite: hERG, AMES, hepato)
        tox_base = (
            0.4 * _norm(logp, 0, 3.5, invert=True)
            + 0.3 * qed
            + 0.2 * _norm(hba, 0, 8, invert=True)
            + 0.1 * _norm(tpsa, 30, 120)
        )
        toxicity = np.clip(tox_base + rng.normal(0, 0.06, len(mw)), 0.05, 0.95)

        return np.column_stack([absorption, distribution, metabolism, excretion, toxicity])

    def _train(self):
        rng = np.random.default_rng(7)
        n = 2000

        mw   = rng.uniform(100, 700, n)
        logp = rng.uniform(-3, 8, n)
        hbd  = rng.integers(0, 12, n).astype(float)
        hba  = rng.integers(0, 16, n).astype(float)
        tpsa = rng.uniform(5, 250, n)
        rot  = rng.integers(0, 18, n).astype(float)
        qed  = rng.uniform(0.05, 0.95, n)
        fsp3 = rng.uniform(0.0, 1.0, n)

        X = np.column_stack([mw, logp, hbd, hba, tpsa, rot, qed, fsp3])
        y = self._simulate_admet(mw, logp, hbd, hba, tpsa, rot, qed, fsp3, rng)

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("reg", MultiOutputRegressor(
                GradientBoostingRegressor(
                    n_estimators=150, max_depth=4, learning_rate=0.1,
                    subsample=0.85, random_state=42,
                ),
                n_jobs=-1,
            )),
        ])
        pipeline.fit(X, y)
        self.model = pipeline

    def predict(self, props: dict) -> dict:
        """
        Predict ADMET scores for a single compound.
        Returns dict mapping ADMET_TARGETS → score (0–1).
        """
        feats = [[
            props.get("mw", 300),
            props.get("logp", 2.5),
            props.get("hbd", 2),
            props.get("hba", 4),
            props.get("tpsa", 70),
            props.get("rotbonds", 4),
            props.get("qed", 0.5),
            props.get("fsp3", 0.3),
        ]]
        preds = self.model.predict(feats)[0]
        scores = {}
        for name, val in zip(ADMET_TARGETS, preds):
            scores[name] = round(float(np.clip(val, 0.0, 1.0)), 3)

        overall = round(float(np.mean(list(scores.values()))), 3)
        return {"scores": scores, "overall": overall}

    def traffic_light(self, scores: dict) -> dict:
        """Return 'green' / 'amber' / 'red' for each ADMET category."""
        lights = {}
        for prop, val in scores.items():
            th = ADMET_THRESHOLDS.get(prop, {"good": 0.6, "moderate": 0.35})
            if val >= th["good"]:
                lights[prop] = "green"
            elif val >= th["moderate"]:
                lights[prop] = "amber"
            else:
                lights[prop] = "red"
        return lights


def _norm(arr, lo, hi, invert=False):
    """Clip-normalise array to [0,1]."""
    v = np.clip((arr - lo) / (hi - lo), 0.0, 1.0)
    return 1.0 - v if invert else v
