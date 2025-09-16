from flask import Flask
from flask_caching import Cache
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

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app
