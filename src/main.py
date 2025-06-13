import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from src.models.voice_models import db
from src.routes.user import user_bp
from src.routes.voice_routes import voice_bp
from src.routes.business_routes import business_bp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration for Heroku
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Heroku PostgreSQL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Local SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voice_agent.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Enable CORS for all routes
    CORS(app, origins="*")
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(voice_bp, url_prefix='/api')
    app.register_blueprint(business_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "AI Voice Agent System",
            "version": "1.0.0",
            "environment": os.getenv('FLASK_ENV', 'development')
        })
    
    # Root endpoint with system information
    @app.route('/')
    def index():
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Voice Agent System</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }
                .container {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }
                h1 { 
                    color: #fff; 
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 2.5em;
                }
                .status {
                    background: rgba(76, 175, 80, 0.2);
                    border: 1px solid rgba(76, 175, 80, 0.5);
                    border-radius: 10px;
                    padding: 15px;
                    margin: 20px 0;
                    text-align: center;
                }
                .btn {
                    background: linear-gradient(45deg, #4CAF50, #45a049);
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                    margin: 10px 5px;
                    transition: transform 0.2s;
                }
                .btn:hover {
                    transform: translateY(-2px);
                }
                .feature {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 AI Voice Agent System</h1>
                
                <div class="status">
                    <h3>✅ System Status: ONLINE</h3>
                    <p>Your AI Voice Agent is ready to handle customer calls in Arabic and English!</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="/dashboard" class="btn">🚀 Open Dashboard</a>
                    <a href="/health" class="btn">🔍 Health Check</a>
                </div>
                
                <div class="feature">
                    <strong>🎤 Bilingual Voice Processing</strong><br>
                    Handles customer calls in Arabic and English with natural conversation flow
                </div>
                <div class="feature">
                    <strong>📅 Smart Appointment Booking</strong><br>
                    Automatically schedules appointments and manages availability
                </div>
                <div class="feature">
                    <strong>💼 Business Management</strong><br>
                    Complete business configuration and service management
                </div>
                <div class="feature">
                    <strong>📊 Analytics & Reporting</strong><br>
                    Detailed insights into customer interactions and business performance
                </div>
                
                <div style="text-align: center; margin-top: 40px; opacity: 0.8;">
                    <p>Built with ❤️ for Saudi businesses | Powered by OpenAI, ElevenLabs & Twilio</p>
                </div>
            </div>
        </body>
        </html>
        ''')
    
    # Dashboard route
    @app.route('/dashboard')
    def dashboard():
        with open(os.path.join(app.root_path, 'static', 'dashboard.html'), 'r') as f:
            return f.read()
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')

