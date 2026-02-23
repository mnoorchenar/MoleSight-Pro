from flask import Blueprint, render_template, request, jsonify, current_app
from ..data.compound_library import get_compound_library, get_summary_stats
from ..utils.molecular import compute_properties_from_smiles, assess_lipinski, assess_veber, assess_ghose, mol_to_svg, get_radar_data
from ..utils.charts import (
    property_distribution_chart, qed_distribution_chart,
    bioactivity_heatmap, radar_chart, tpsa_vs_mw_chart,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    stats = get_summary_stats()
    compounds = get_compound_library()

    chart_mw_logp   = property_distribution_chart(compounds)
    chart_qed       = qed_distribution_chart(compounds)
    chart_heatmap   = bioactivity_heatmap(compounds)
    chart_tpsa_mw   = tpsa_vs_mw_chart(compounds)

    return render_template("index.html",
        stats=stats,
        chart_mw_logp=chart_mw_logp,
        chart_qed=chart_qed,
        chart_heatmap=chart_heatmap,
        chart_tpsa_mw=chart_tpsa_mw,
        compounds=compounds,
    )


@main_bp.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None
    error  = None
    smiles_input = ""

    # Predefined example molecules
    examples = [
        ("Aspirin",      "CC(=O)Oc1ccccc1C(=O)O"),
        ("Ibuprofen",    "CC(C)Cc1ccc(cc1)C(C)C(=O)O"),
        ("Caffeine",     "Cn1cnc2c1c(=O)n(c(=O)n2C)C"),
        ("Paracetamol",  "CC(=O)Nc1ccc(O)cc1"),
        ("Omeprazole",   "COc1ccc2[nH]c(S(=O)Cc3ncc(C)c(OC)c3C)nc2c1"),
        ("Fluoxetine",   "CNCCC(Oc1ccc(cc1)C(F)(F)F)c1ccccc1"),
        ("Sildenafil",   "CCCC1=NN(C)C(=O)c2[nH]c(-c3cc(S(=O)(=O)N4CCN(CC4)C)ccc3OCC)c3c(CCC)ccc(=O)nc23"),
    ]

    if request.method == "POST":
        smiles_input = request.form.get("smiles", "").strip()
        if not smiles_input:
            error = "Please enter a SMILES string."
        else:
            props = compute_properties_from_smiles(smiles_input)
            if props is None:
                error = f"Invalid SMILES: '{smiles_input}'. Please check syntax."
            else:
                lipinski = assess_lipinski(props)
                veber    = assess_veber(props)
                ghose    = assess_ghose(props)
                radar    = get_radar_data(props)

                chart_radar = radar_chart(radar, name=smiles_input[:30])
                svg_img     = mol_to_svg(smiles_input)

                result = dict(
                    props=props, lipinski=lipinski,
                    veber=veber, ghose=ghose,
                    chart_radar=chart_radar, svg_img=svg_img,
                )

    return render_template("analyze.html",
        result=result, error=error,
        smiles_input=smiles_input,
        examples=examples,
    )


@main_bp.route("/api/properties", methods=["POST"])
def api_properties():
    data   = request.get_json(silent=True) or {}
    smiles = data.get("smiles", "")
    if not smiles:
        return jsonify({"error": "No SMILES provided"}), 400
    props = compute_properties_from_smiles(smiles)
    if props is None:
        return jsonify({"error": "Invalid SMILES"}), 422
    return jsonify(props)
