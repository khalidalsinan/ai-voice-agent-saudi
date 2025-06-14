import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simple in-memory storage (no database!)
businesses = []
business_counter = 1

@app.route('/')
def home():
    return '''
    <h1>🤖 AI Voice Agent System</h1>
    <h2>✅ WORKING!</h2>
    <p><a href="/health">Health Check</a></p>
    <p><a href="/api/businesses">View Businesses</a></p>
    '''

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'AI Voice Agent is working!',
        'openai_configured': bool(os.getenv('OPENAI_API_KEY')),
        'elevenlabs_configured': bool(os.getenv('ELEVENLABS_API_KEY'))
    })

@app.route('/api/businesses', methods=['GET'])
def get_businesses():
    return jsonify({
        'success': True,
        'businesses': businesses
    })

@app.route('/api/businesses', methods=['POST'])
def create_business():
    global business_counter
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'success': False, 'error': 'Business name required'}), 400
    
    business = {
        'id': business_counter,
        'name': data['name'],
        'description': data.get('description', ''),
        'created': True
    }
    
    businesses.append(business)
    business_counter += 1
    
    return jsonify({
        'success': True,
        'message': 'Business created!',
        'business': business
    })

@app.route('/api/businesses/<int:business_id>/test-voice', methods=['POST'])
def test_voice():
    data = request.get_json()
    message = data.get('message', '')
    
    # Simple response
    is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
    
    if is_arabic:
        response = "مرحباً! كيف يمكنني مساعدتك؟"
    else:
        response = "Hello! How can I help you?"
    
    return jsonify({
        'success': True,
        'result': {
            'response': response,
            'intent': 'general'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
