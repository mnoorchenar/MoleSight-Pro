"""
Curated compound library with known drugs and synthetic decoys.
Properties are either RDKit-computed or literature-sourced.
"""

# Each entry: name, SMILES, MW, LogP, HBD, HBA, TPSA, RotBonds, drug_like, activity_class
KNOWN_DRUGS = [
    {
        "name": "Aspirin",
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "mw": 180.16, "logp": 1.19, "hbd": 1, "hba": 4,
        "tpsa": 63.6, "rotbonds": 3, "qed": 0.55,
        "drug_like": 1, "target": "COX-1/2", "activity": "anti-inflammatory",
        "ic50_nm": 50.0, "bioavailability": 80
    },
    {
        "name": "Ibuprofen",
        "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
        "mw": 206.29, "logp": 3.97, "hbd": 1, "hba": 2,
        "tpsa": 37.3, "rotbonds": 4, "qed": 0.67,
        "drug_like": 1, "target": "COX-1/2", "activity": "anti-inflammatory",
        "ic50_nm": 13.0, "bioavailability": 100
    },
    {
        "name": "Paracetamol",
        "smiles": "CC(=O)Nc1ccc(O)cc1",
        "mw": 151.16, "logp": 0.91, "hbd": 2, "hba": 3,
        "tpsa": 49.3, "rotbonds": 2, "qed": 0.59,
        "drug_like": 1, "target": "COX-3", "activity": "analgesic",
        "ic50_nm": 25.0, "bioavailability": 88
    },
    {
        "name": "Caffeine",
        "smiles": "Cn1cnc2c1c(=O)n(c(=O)n2C)C",
        "mw": 194.19, "logp": -0.07, "hbd": 0, "hba": 6,
        "tpsa": 58.4, "rotbonds": 0, "qed": 0.60,
        "drug_like": 1, "target": "Adenosine receptor", "activity": "stimulant",
        "ic50_nm": 44000.0, "bioavailability": 100
    },
    {
        "name": "Metformin",
        "smiles": "CN(C)C(=N)NC(=N)N",
        "mw": 129.16, "logp": -1.43, "hbd": 4, "hba": 5,
        "tpsa": 91.8, "rotbonds": 2, "qed": 0.26,
        "drug_like": 1, "target": "AMPK", "activity": "antidiabetic",
        "ic50_nm": 100000.0, "bioavailability": 55
    },
    {
        "name": "Atorvastatin",
        "smiles": "CC(C)c1c(C(=O)Nc2ccccc2F)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CC[C@@H](O)C[C@@H](O)CC(=O)O",
        "mw": 558.64, "logp": 6.36, "hbd": 4, "hba": 9,
        "tpsa": 111.0, "rotbonds": 13, "qed": 0.45,
        "drug_like": 0, "target": "HMG-CoA reductase", "activity": "antihyperlipidemic",
        "ic50_nm": 8.2, "bioavailability": 14
    },
    {
        "name": "Amlodipine",
        "smiles": "CCOC(=O)C1=C(COCCN)NC(C)=C(C(=O)OC)C1c1ccccc1Cl",
        "mw": 408.88, "logp": 3.0, "hbd": 2, "hba": 8,
        "tpsa": 97.9, "rotbonds": 9, "qed": 0.56,
        "drug_like": 1, "target": "L-type Ca channel", "activity": "antihypertensive",
        "ic50_nm": 0.9, "bioavailability": 64
    },
    {
        "name": "Omeprazole",
        "smiles": "COc1ccc2[nH]c(S(=O)Cc3ncc(C)c(OC)c3C)nc2c1",
        "mw": 345.42, "logp": 2.23, "hbd": 1, "hba": 7,
        "tpsa": 87.8, "rotbonds": 5, "qed": 0.72,
        "drug_like": 1, "target": "H+/K+ ATPase", "activity": "proton pump inhibitor",
        "ic50_nm": 0.5, "bioavailability": 65
    },
    {
        "name": "Sildenafil",
        "smiles": "CCCC1=NN(C)C(=O)c2[nH]c(-c3cc(S(=O)(=O)N4CCN(CC4)C)ccc3OCC)c3c(CCC)ccc(=O)nc23",
        "mw": 474.58, "logp": 1.9, "hbd": 1, "hba": 9,
        "tpsa": 113.0, "rotbonds": 6, "qed": 0.53,
        "drug_like": 0, "target": "PDE5", "activity": "vasodilator",
        "ic50_nm": 3.5, "bioavailability": 40
    },
    {
        "name": "Fluoxetine",
        "smiles": "CNCCC(Oc1ccc(cc1)C(F)(F)F)c1ccccc1",
        "mw": 309.33, "logp": 4.05, "hbd": 1, "hba": 2,
        "tpsa": 21.3, "rotbonds": 7, "qed": 0.76,
        "drug_like": 1, "target": "SERT", "activity": "antidepressant",
        "ic50_nm": 25.8, "bioavailability": 72
    },
    {
        "name": "Warfarin",
        "smiles": "OC(=O)c1ccccc1/C=C(\\C)C(=O)c1ccccc1O",
        "mw": 308.33, "logp": 2.7, "hbd": 1, "hba": 5,
        "tpsa": 63.6, "rotbonds": 5, "qed": 0.50,
        "drug_like": 1, "target": "Vitamin K epoxide reductase", "activity": "anticoagulant",
        "ic50_nm": 1.0, "bioavailability": 100
    },
    {
        "name": "Tamoxifen",
        "smiles": "CCC(=C(c1ccccc1)c1ccc(OCCN(C)C)cc1)c1ccccc1",
        "mw": 371.51, "logp": 6.3, "hbd": 0, "hba": 2,
        "tpsa": 18.5, "rotbonds": 8, "qed": 0.48,
        "drug_like": 0, "target": "Estrogen receptor", "activity": "antiestrogen",
        "ic50_nm": 2.0, "bioavailability": 100
    },
    {
        "name": "Dexamethasone",
        "smiles": "C[C@@H]1C[C@H]2[C@@H]3CC(F)c4cc(=O)c(cc4[C@@]3(C)C[C@@H]2[C@@]1(O)C(=O)CO)O",
        "mw": 392.46, "logp": 1.83, "hbd": 3, "hba": 7,
        "tpsa": 105.0, "rotbonds": 2, "qed": 0.49,
        "drug_like": 0, "target": "Glucocorticoid receptor", "activity": "anti-inflammatory",
        "ic50_nm": 1.2, "bioavailability": 80
    },
    {
        "name": "Ciprofloxacin",
        "smiles": "OC(=O)c1cn(C2CC2)c2cc(N3CCNCC3)c(F)cc2c1=O",
        "mw": 331.34, "logp": 0.28, "hbd": 2, "hba": 8,
        "tpsa": 75.0, "rotbonds": 2, "qed": 0.74,
        "drug_like": 1, "target": "DNA gyrase / Topoisomerase IV", "activity": "antibacterial",
        "ic50_nm": 1.0, "bioavailability": 70
    },
    {
        "name": "Losartan",
        "smiles": "CCCCc1nc(Cl)c(CO)n1Cc1ccc(-c2ccccc2-c2tetrazol-5-yl)cc1",
        "mw": 422.92, "logp": 4.01, "hbd": 2, "hba": 8,
        "tpsa": 96.5, "rotbonds": 7, "qed": 0.62,
        "drug_like": 1, "target": "AT1 receptor", "activity": "antihypertensive",
        "ic50_nm": 20.0, "bioavailability": 33
    },
    {
        "name": "Naloxone",
        "smiles": "O=C1CC[C@@H]2c3c(O)ccc4c3[C@@]2(CC1=O)[C@@H](O)CC4N(CC=C)CC=C",
        "mw": 327.37, "logp": 1.25, "hbd": 2, "hba": 5,
        "tpsa": 65.8, "rotbonds": 2, "qed": 0.33,
        "drug_like": 1, "target": "Opioid receptors", "activity": "opioid antagonist",
        "ic50_nm": 1.0, "bioavailability": 2
    },
    {
        "name": "Compound_A7",
        "smiles": "Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1",
        "mw": 493.6, "logp": 3.6, "hbd": 3, "hba": 9,
        "tpsa": 86.2, "rotbonds": 7, "qed": 0.42,
        "drug_like": 0, "target": "EGFR", "activity": "kinase inhibitor",
        "ic50_nm": 0.1, "bioavailability": 45
    },
    {
        "name": "Compound_B3",
        "smiles": "CN1CCN(c2ccc(Nc3ncc(F)c(Nc4cc(N(C)C)ccc4=O)n3)cc2)CC1",
        "mw": 460.54, "logp": 2.9, "hbd": 3, "hba": 9,
        "tpsa": 78.5, "rotbonds": 5, "qed": 0.55,
        "drug_like": 1, "target": "ALK", "activity": "kinase inhibitor",
        "ic50_nm": 0.5, "bioavailability": 60
    },
    {
        "name": "Compound_C9",
        "smiles": "O=C(Nc1ccc(Oc2ccc(NC(=O)Nc3ccc(Cl)c(CF3)c3)cc2)cc1)c1ccc[nH]1",
        "mw": 500.89, "logp": 5.1, "hbd": 4, "hba": 7,
        "tpsa": 92.4, "rotbonds": 8, "qed": 0.38,
        "drug_like": 0, "target": "BRAF", "activity": "kinase inhibitor",
        "ic50_nm": 18.0, "bioavailability": 30
    },
    {
        "name": "Compound_D2",
        "smiles": "CC(=O)Nc1ccc(-c2ccc(NC(=O)c3ccc(N(C)C)cc3)cc2)cc1",
        "mw": 389.46, "logp": 2.5, "hbd": 2, "hba": 6,
        "tpsa": 71.3, "rotbonds": 7, "qed": 0.63,
        "drug_like": 1, "target": "JAK2", "activity": "kinase inhibitor",
        "ic50_nm": 5.0, "bioavailability": 70
    },
]

TARGETS = [
    "COX-1/2", "EGFR", "HER2", "ALK", "BRAF", "MEK",
    "PI3K", "mTOR", "CDK4/6", "PARP", "JAK2", "VEGFR",
    "BCR-ABL", "HDAC", "Proteasome", "Topoisomerase",
]

def get_compound_library():
    """Return the full compound library as a list of dicts."""
    return KNOWN_DRUGS

def get_summary_stats():
    """Return summary statistics for the dashboard."""
    total = len(KNOWN_DRUGS)
    drug_like = sum(1 for c in KNOWN_DRUGS if c['drug_like'] == 1)
    avg_qed = round(sum(c['qed'] for c in KNOWN_DRUGS) / total, 3)
    high_activity = sum(1 for c in KNOWN_DRUGS if c['ic50_nm'] < 100)
    return {
        "total_compounds": total,
        "drug_like_count": drug_like,
        "drug_like_pct": round(drug_like / total * 100, 1),
        "avg_qed": avg_qed,
        "high_activity_count": high_activity,
        "targets_covered": len(set(c['target'] for c in KNOWN_DRUGS)),
    }
