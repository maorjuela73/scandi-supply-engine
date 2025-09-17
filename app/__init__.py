from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
from .config import config_by_name

cache = Cache()

def create_app(config_name: str = "development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # inicializar extensiones
    cache.init_app(app)

    # registrar blueprint
    from .api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    CORS(app, resources={r"/api/*": {"origins": "https://scandi-supply-scan.lovable.app"}})

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app
