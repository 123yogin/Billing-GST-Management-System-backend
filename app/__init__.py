from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register blueprints
    from app.billing.routes import bp as billing_bp
    app.register_blueprint(billing_bp, url_prefix='/api')
    
    from app.reports.routes import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    
    from app.deals.routes import bp as deals_bp
    app.register_blueprint(deals_bp, url_prefix='/api')
    
    from app.dealers.routes import bp as dealers_bp
    app.register_blueprint(dealers_bp, url_prefix='/api')
    
    return app

