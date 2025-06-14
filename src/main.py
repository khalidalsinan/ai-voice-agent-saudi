import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__)))

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.business import business_bp

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///voice_agent.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app, origins="*")
    db.init_app(app)
    
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(business_bp, url_prefix='/api')
    
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "AI Voice Agent System"
        })
    
    @app.route('/')
    def index():
        return render_template_string('''
        <h1>🤖 AI Voice Agent System</h1>
        <p>✅ System is ONLINE and working!</p>
        <a href="/health">Health Check</a>
        ''')
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
