import os
from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'drug-discovery-demo-2024')

    # Initialize and attach ML models lazily on first request
    from .models.drug_likeness import DrugLikenessModel
    from .models.admet import ADMETModel

    with app.app_context():
        app.drug_model = DrugLikenessModel()
        app.admet_model = ADMETModel()

    # Register blueprints
    from .routes.main import main_bp
    from .routes.screening import screening_bp
    from .routes.prediction import prediction_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(screening_bp, url_prefix='/screening')
    app.register_blueprint(prediction_bp, url_prefix='/predict')

    return app
