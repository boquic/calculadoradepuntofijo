from flask import Flask
from .routes import bp as main_bp

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = "dev-key"  # cambia en prod si hace falta
    app.register_blueprint(main_bp)
    return app