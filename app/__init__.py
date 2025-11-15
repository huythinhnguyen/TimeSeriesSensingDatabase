from flask import Flask, g
from config import Config
from app.models import Database

def create_app(config=None):
    """Application factory"""
    app = Flask(__name__)
    
    if config:
        app.config.update(config)
    else:
        app.config.from_object(Config)
    
    # Register blueprints
    from app.routes import api
    app.register_blueprint(api)
    
    # Get database connection per request
    @app.before_request
    def before_request():
        if 'db' not in g:
            g.db = Database(app.config['DATABASE_URL'])
            g.db.connect()
    
    # Cleanup after request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db = g.pop('db', None)
        if db:
            db.close()
    
    return app
