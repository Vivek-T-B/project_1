from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

from models import db
from models.calculation import Calculation
from routes.calculator_routes import calculator_bp
from routes.history_routes import history_bp

def create_app():
    app = Flask(__name__)
    
    # Default configuration
    project_dir = os.path.dirname(os.path.abspath(__file__))
    default_db = 'sqlite:///' + os.path.join(project_dir, 'calculator.db')
    app.config.from_mapping(
        SECRET_KEY='calculator-secret-key-2024',
        SQLALCHEMY_DATABASE_URI=default_db,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Initialize extensions
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(calculator_bp, url_prefix='/api/calculator')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    
    # Main route - serve calculator page
    @app.route('/')
    def index():
        return render_template('calculator.html')
    
    # API root route
    @app.route('/api')
    def api_root():
        return jsonify({
            'name': 'Calculator API',
            'version': '1.0.0',
            'endpoints': {
                'calculate': '/api/calculator/calculate',
                'validate': '/api/calculator/validate',
                'clear_history': '/api/calculator/clear',
                'history': '/api/history',
                'delete_calculation': '/api/history/<id>'
            }
        })

    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

if __name__ == '__main__':
    app = create_app()
    # Use port 5000 by default
    app.run(host='0.0.0.0', port=5000, debug=True)
