from flask import Blueprint, render_template, request, jsonify, current_app
from ..data.compound_library import get_compound_library
from ..utils.molecular import compute_properties_from_smiles, assess_lipinski, get_radar_data
from ..utils.charts import (
    admet_gauge_chart, feature_importance_chart,
    probability_gauge, radar_chart,
)
from ..models.drug_likeness import FEATURE_NAMES
from ..models.admet import ADMET_DESCRIPTIONS, ADMET_THRESHOLDS

prediction_bp = Blueprint("prediction", __name__)

EXAMPLES = [
    ("Aspirin",      "CC(=O)Oc1ccccc1C(=O)O"),
    ("Ibuprofen",    "CC(C)Cc1ccc(cc1)C(C)C(=O)O"),
    ("Sildenafil",   "CCCC1=NN(C)C(=O)c2[nH]c(-c3cc(S(=O)(=O)N4CCN(CC4)C)ccc3OCC)c3c(CCC)ccc(=O)nc23"),
    ("Paracetamol",  "CC(=O)Nc1ccc(O)cc1"),
    ("Fluoxetine",   "CNCCC(Oc1ccc(cc1)C(F)(F)F)c1ccccc1"),
    ("Atorvastatin", "CC(C)c1c(C(=O)Nc2ccccc2F)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CC[C@@H](O)C[C@@H](O)CC(=O)O"),
]


@prediction_bp.route("/drug-likeness", methods=["GET", "POST"])
def drug_likeness():
    result = None
    error  = None
    smiles_input = ""

    if request.method == "POST":
        smiles_input = request.form.get("smiles", "").strip()
        if not smiles_input:
            error = "Please enter a SMILES string."
        else:
            props = compute_properties_from_smiles(smiles_input)
            if props is None:
                error = f"Invalid SMILES: '{smiles_input}'"
            else:
                model = current_app.drug_model
                pred  = model.predict(props)
                lipinski = assess_lipinski(props)
                radar  = get_radar_data(props)

                chart_gauge = probability_gauge(pred["probability"], pred["label"])
                chart_fi    = feature_importance_chart(
                    FEATURE_NAMES, model.importances
                )
                chart_radar = radar_chart(radar)

                result = dict(
                    props=props, pred=pred,
                    lipinski=lipinski,
                    chart_gauge=chart_gauge,
                    chart_fi=chart_fi,
                    chart_radar=chart_radar,
                    cv_accuracy=model.cv_accuracy,
                )

    return render_template("prediction.html",
        result=result, error=error,
        smiles_input=smiles_input,
        examples=EXAMPLES,
    )


@prediction_bp.route("/admet", methods=["GET", "POST"])
def admet():
    result = None
    error  = None
    smiles_input = ""

    if request.method == "POST":
        smiles_input = request.form.get("smiles", "").strip()
        if not smiles_input:
            error = "Please enter a SMILES string."
        else:
            props = compute_properties_from_smiles(smiles_input)
            if props is None:
                error = f"Invalid SMILES: '{smiles_input}'"
            else:
                admet_model = current_app.admet_model
                admet_res   = admet_model.predict(props)
                lights      = admet_model.traffic_light(admet_res["scores"])

                chart_gauges = admet_gauge_chart(admet_res["scores"])

                result = dict(
                    props=props,
                    admet=admet_res,
                    lights=lights,
                    descriptions=ADMET_DESCRIPTIONS,
                    chart_gauges=chart_gauges,
                )

    return render_template("admet.html",
        result=result, error=error,
        smiles_input=smiles_input,
        examples=EXAMPLES,
    )


@prediction_bp.route("/api/drug-likeness", methods=["POST"])
def api_drug_likeness():
    data   = request.get_json(silent=True) or {}
    smiles = data.get("smiles", "")
    if not smiles:
        return jsonify({"error": "No SMILES provided"}), 400
    props = compute_properties_from_smiles(smiles)
    if props is None:
        return jsonify({"error": "Invalid SMILES"}), 422
    pred = current_app.drug_model.predict(props)
    return jsonify({"smiles": smiles, "properties": props, "prediction": pred})


@prediction_bp.route("/api/admet", methods=["POST"])
def api_admet():
    data   = request.get_json(silent=True) or {}
    smiles = data.get("smiles", "")
    if not smiles:
        return jsonify({"error": "No SMILES provided"}), 400
    props = compute_properties_from_smiles(smiles)
    if props is None:
        return jsonify({"error": "Invalid SMILES"}), 422
    admet_res = current_app.admet_model.predict(props)
    return jsonify({"smiles": smiles, "properties": props, "admet": admet_res})
