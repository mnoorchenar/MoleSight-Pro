"""
Drug-likeness binary classifier.
Trained on-the-fly using synthetic data generated from known drug property distributions.
"""

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score


FEATURE_NAMES = ["mw", "logp", "hbd", "hba", "tpsa", "rotbonds", "qed"]


class DrugLikenessModel:
    """Binary classifier: drug-like (1) vs non-drug-like (0)."""

    def __init__(self):
        self.model = None
        self.cv_accuracy = 0.0
        self.feature_names = FEATURE_NAMES
        self.importances = []
        self._train()

    def _generate_training_data(self, n: int = 1500) -> tuple:
        """
        Synthetic training set built from established drug-property distributions.
        Drug-like compounds follow Lipinski / Veber / Ghose rules.
        Decoys are generated outside those ranges.
        """
        rng = np.random.default_rng(42)
        X, y = [], []

        # ── Positive class: drug-like compounds ───────────────────────────
        n_pos = n // 2
        mw    = rng.uniform(150, 500, n_pos)
        logp  = rng.uniform(-1, 5, n_pos)
        hbd   = rng.integers(0, 6, n_pos).astype(float)
        hba   = rng.integers(0, 11, n_pos).astype(float)
        tpsa  = rng.uniform(20, 130, n_pos)
        rot   = rng.integers(0, 9, n_pos).astype(float)
        qed   = rng.uniform(0.4, 0.95, n_pos)

        for i in range(n_pos):
            X.append([mw[i], logp[i], hbd[i], hba[i], tpsa[i], rot[i], qed[i]])
            y.append(1)

        # ── Negative class: non-drug-like / decoys ─────────────────────────
        n_neg = n - n_pos
        mw    = rng.choice(
            [rng.uniform(500, 900, n_neg // 2), rng.uniform(50, 150, n_neg // 2)]
        ).flatten()[:n_neg]
        logp  = rng.choice(
            [rng.uniform(5, 12, n_neg // 2), rng.uniform(-5, -1.5, n_neg // 2)]
        ).flatten()[:n_neg]
        hbd   = rng.choice(
            [rng.integers(6, 15, n_neg // 2).astype(float),
             rng.integers(0, 3, n_neg // 2).astype(float)]
        ).flatten()[:n_neg]
        hba   = rng.choice(
            [rng.integers(11, 20, n_neg // 2).astype(float),
             rng.integers(0, 2, n_neg // 2).astype(float)]
        ).flatten()[:n_neg]
        tpsa  = rng.choice(
            [rng.uniform(140, 250, n_neg // 2), rng.uniform(5, 20, n_neg // 2)]
        ).flatten()[:n_neg]
        rot   = rng.integers(10, 20, n_neg).astype(float)
        qed   = rng.uniform(0.05, 0.38, n_neg)

        for i in range(n_neg):
            X.append([mw[i], logp[i], hbd[i], hba[i], tpsa[i], rot[i], qed[i]])
            y.append(0)

        return np.array(X, dtype=float), np.array(y)

    def _train(self):
        X, y = self._generate_training_data()

        # Add small Gaussian noise for regularisation
        rng = np.random.default_rng(0)
        X += rng.normal(0, 0.01, X.shape)

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", GradientBoostingClassifier(
                n_estimators=200, max_depth=4, learning_rate=0.08,
                subsample=0.85, min_samples_leaf=5, random_state=42,
            )),
        ])
        pipeline.fit(X, y)
        self.model = pipeline

        scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
        self.cv_accuracy = round(float(scores.mean()), 4)

        clf = pipeline.named_steps["clf"]
        self.importances = list(clf.feature_importances_.round(4))

    def predict(self, props: dict) -> dict:
        """
        Predict drug-likeness for a single compound.

        Parameters
        ----------
        props : dict containing keys mw, logp, hbd, hba, tpsa, rotbonds, qed

        Returns
        -------
        dict with probability, label, confidence_class
        """
        feats = [[
            props.get("mw", 300),
            props.get("logp", 2.5),
            props.get("hbd", 2),
            props.get("hba", 4),
            props.get("tpsa", 70),
            props.get("rotbonds", 4),
            props.get("qed", 0.5),
        ]]
        proba = float(self.model.predict_proba(feats)[0][1])
        label = "Drug-Like" if proba >= 0.5 else "Non Drug-Like"
        if proba >= 0.75:
            confidence = "High"
        elif proba >= 0.5:
            confidence = "Moderate"
        else:
            confidence = "Low"
        return {"probability": round(proba, 4), "label": label, "confidence": confidence}

    def predict_batch(self, compounds: list) -> list:
        """Predict a list of compound dicts. Returns list of result dicts."""
        results = []
        for c in compounds:
            r = self.predict(c)
            r["name"] = c.get("name", "?")
            results.append(r)
        return results
