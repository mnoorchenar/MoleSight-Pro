"""
Molecular utility functions for property calculation.
Uses RDKit when available; falls back to pre-computed values otherwise.
"""

import math

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors, QED, Draw
    from rdkit.Chem.Draw import rdMolDraw2D
    import base64
    import io
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


LIPINSKI_RULES = {
    "MW ≤ 500": lambda p: p["mw"] <= 500,
    "LogP ≤ 5": lambda p: p["logp"] <= 5,
    "HBD ≤ 5": lambda p: p["hbd"] <= 5,
    "HBA ≤ 10": lambda p: p["hba"] <= 10,
}

VEBER_RULES = {
    "TPSA ≤ 140 Å²": lambda p: p["tpsa"] <= 140,
    "RotBonds ≤ 10": lambda p: p["rotbonds"] <= 10,
}

GHOSE_RULES = {
    "MW 160–480": lambda p: 160 <= p["mw"] <= 480,
    "LogP −0.4 to 5.6": lambda p: -0.4 <= p["logp"] <= 5.6,
    "HeavyAtoms 20–70": lambda p: 20 <= p.get("heavy_atoms", 25) <= 70,
    "Molar Refractivity 40–130": lambda p: 40 <= p.get("mr", 80) <= 130,
}


def compute_properties_from_smiles(smiles: str) -> dict | None:
    """
    Compute molecular properties from a SMILES string.
    Returns a dict of properties or None if SMILES is invalid.
    """
    if not RDKIT_AVAILABLE:
        return _fallback_properties(smiles)

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = rdMolDescriptors.CalcNumHBD(mol)
    hba = rdMolDescriptors.CalcNumHBA(mol)
    tpsa = rdMolDescriptors.CalcTPSA(mol)
    rotbonds = rdMolDescriptors.CalcNumRotatableBonds(mol)
    heavy_atoms = mol.GetNumHeavyAtoms()
    rings = rdMolDescriptors.CalcNumRings(mol)
    aromatic_rings = rdMolDescriptors.CalcNumAromaticRings(mol)
    mr = Descriptors.MolMR(mol)
    qed_val = QED.qed(mol)
    fsp3 = rdMolDescriptors.CalcFractionCSP3(mol)
    stereo_centers = len(rdMolDescriptors.FindPotentialStereo(mol))
    formula = rdMolDescriptors.CalcMolFormula(mol)

    return {
        "mw": round(mw, 2),
        "logp": round(logp, 2),
        "hbd": hbd,
        "hba": hba,
        "tpsa": round(tpsa, 1),
        "rotbonds": rotbonds,
        "heavy_atoms": heavy_atoms,
        "rings": rings,
        "aromatic_rings": aromatic_rings,
        "mr": round(mr, 2),
        "qed": round(qed_val, 3),
        "fsp3": round(fsp3, 3),
        "stereo_centers": stereo_centers,
        "formula": formula,
        "smiles": smiles,
    }


def _fallback_properties(smiles: str) -> dict:
    """Rough heuristic estimates when RDKit is unavailable."""
    n_atoms = len([c for c in smiles if c.isalpha() and c.upper() in "CNOPS"])
    mw = n_atoms * 12.0 + 18.0
    logp = (smiles.count("C") - smiles.count("O") - smiles.count("N")) * 0.5
    hbd = smiles.count("O") + smiles.count("N")
    hba = smiles.count("O") + smiles.count("N") + smiles.count("n")
    tpsa = hba * 12.0
    rotbonds = smiles.count("-") + smiles.count("CC") // 2
    heavy_atoms = n_atoms
    return {
        "mw": round(mw, 2), "logp": round(logp, 2),
        "hbd": min(hbd, 10), "hba": min(hba, 15),
        "tpsa": round(tpsa, 1), "rotbonds": min(rotbonds, 12),
        "heavy_atoms": heavy_atoms, "rings": 0,
        "aromatic_rings": 0, "mr": round(mw / 4, 2),
        "qed": 0.5, "fsp3": 0.3, "stereo_centers": 0,
        "formula": "C?H?N?O?", "smiles": smiles,
    }


def assess_lipinski(props: dict) -> dict:
    """Assess Lipinski's Rule of Five compliance."""
    results = {}
    violations = 0
    for rule, fn in LIPINSKI_RULES.items():
        passed = fn(props)
        results[rule] = passed
        if not passed:
            violations += 1
    return {
        "rules": results,
        "violations": violations,
        "passed": violations <= 1,  # Ro5 allows max 1 violation
        "label": "Drug-Like" if violations <= 1 else "Not Drug-Like",
    }


def assess_veber(props: dict) -> dict:
    results = {}
    violations = 0
    for rule, fn in VEBER_RULES.items():
        passed = fn(props)
        results[rule] = passed
        if not passed:
            violations += 1
    return {"rules": results, "violations": violations, "passed": violations == 0}


def assess_ghose(props: dict) -> dict:
    results = {}
    violations = 0
    for rule, fn in GHOSE_RULES.items():
        passed = fn(props)
        results[rule] = passed
        if not passed:
            violations += 1
    return {"rules": results, "violations": violations, "passed": violations <= 1}


def mol_to_svg(smiles: str, width: int = 400, height: int = 300) -> str | None:
    """Render molecule as an SVG string."""
    if not RDKIT_AVAILABLE:
        return None
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    try:
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        drawer.drawOptions().addStereoAnnotation = True
        drawer.drawOptions().backgroundColour = (0.05, 0.06, 0.1, 1)
        drawer.drawOptions().atomLabelFontSize = 0.6
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        # Adjust stroke color for dark background
        svg = svg.replace("fill:#000000", "fill:#e0e6f0")
        svg = svg.replace("stroke:#000000", "stroke:#e0e6f0")
        return svg
    except Exception:
        return None


def compute_similarity(smiles1: str, smiles2: str) -> float:
    """Compute Tanimoto similarity between two SMILES using Morgan fingerprints."""
    if not RDKIT_AVAILABLE:
        return 0.5
    from rdkit.Chem import AllChem
    from rdkit import DataStructs
    mol1 = Chem.MolFromSmiles(smiles1)
    mol2 = Chem.MolFromSmiles(smiles2)
    if mol1 is None or mol2 is None:
        return 0.0
    fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, 2048)
    fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, 2048)
    return round(DataStructs.TanimotoSimilarity(fp1, fp2), 4)


def get_radar_data(props: dict) -> dict:
    """Normalize properties for radar/spider chart (0–1 scale)."""
    def clamp(v, lo, hi):
        return max(0.0, min(1.0, (v - lo) / (hi - lo)))

    return {
        "MW":        round(1 - clamp(props["mw"], 0, 700), 3),        # inverted: smaller=better
        "LogP":      round(1 - clamp(abs(props["logp"]), 0, 7), 3),   # closer to 2 is ideal
        "HBD":       round(1 - clamp(props["hbd"], 0, 10), 3),
        "HBA":       round(1 - clamp(props["hba"], 0, 15), 3),
        "TPSA":      round(1 - clamp(props["tpsa"], 0, 200), 3),
        "RotBonds":  round(1 - clamp(props["rotbonds"], 0, 15), 3),
        "QED":       props.get("qed", 0.5),
    }
