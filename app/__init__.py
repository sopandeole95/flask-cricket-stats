from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# define db at module scope
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object("app.config.Config")
    db.init_app(app)

    # create tables
    with app.app_context():
        from . import models   # safe: models only imports db and base classes
        db.create_all()

    # now that db & models exist, import and register routes
    from .routes import stats_bp   # <-- move this inside the function
    app.register_blueprint(stats_bp)

    return app
