import os
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simple in-memory storage
businesses = []
business_counter = 1

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Voice Agent System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        .tabs {
            display: flex;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 5px;
            margin-bottom: 30px;
        }
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            background: transparent;
            border: none;
            color: white;
            font-size: 16px;
        }
        .tab.active {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        .tab-content {
            display: none;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
        }
        .tab-content.active {
            display: block;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            font-size: 16px;
        }
        .btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .business-list {
            display: grid;
            gap: 20px;
        }
        .business-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #4CAF50;
        }
        .api-status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .api-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-ok { background: #4CAF50; }
        .status-error { background: #f44336; }
        #response-area {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            min-height: 100px;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Voice Agent System</h1>
            <p>Professional voice AI for Saudi businesses</p>
        </div>

        <div class="status-card">
            <h3>✅ System Status: ONLINE</h3>
            <p>Your AI Voice Agent is ready to handle customer calls in Arabic and English!</p>
            <div class="api-status">
                <div class="api-card">
                    <span class="status-indicator status-ok"></span>
                    <strong>System</strong><br>Running
                </div>
                <div class="api-card">
                    <span class="status-indicator {{ 'status-ok' if openai_configured else 'status-error' }}"></span>
                    <strong>OpenAI</strong><br>{{ 'Configured' if openai_configured else 'Not Configured' }}
                </div>
                <div class="api-card">
                    <span class="status-indicator {{ 'status-ok' if elevenlabs_configured else 'status-error' }}"></span>
                    <strong>ElevenLabs</strong><br>{{ 'Configured' if elevenlabs_configured else 'Not Configured' }}
                </div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">📊 Overview</button>
            <button class="tab" onclick="showTab('business')">🏢 Business</button>
            <button class="tab" onclick="showTab('test')">🎤 Test Voice</button>
        </div>

        <div id="overview" class="tab-content active">
            <h3>📈 Dashboard Overview</h3>
            <div class="business-list" id="business-overview">
                <p>Loading businesses...</p>
            </div>
        </div>

        <div id="business" class="tab-content">
            <h3>🏢 Business Management</h3>
            <div class="form-group">
                <label>Business Name</label>
                <input type="text" id="business-name" placeholder="Enter business name">
            </div>
            <div class="form-group">
                <label>Description (for AI training)</label>
                <textarea id="business-description" rows="4" placeholder="Describe your business, services, hours, pricing..."></textarea>
            </div>
            <button class="btn" onclick="createBusiness()">Create Business</button>
            
            <div style="margin-top: 30px;">
                <h4>📋 Your Businesses</h4>
                <div class="business-list" id="business-list">
                    <p>No businesses created yet.</p>
                </div>
            </div>
        </div>

        <div id="test" class="tab-content">
            <h3>🎤 Test Voice Processing</h3>
            <div class="form-group">
                <label>Select Business</label>
                <select id="test-business">
                    <option value="">Select a business...</option>
                </select>
            </div>
            <div class="form-group">
                <label>Test Message</label>
                <input type="text" id="test-message" placeholder="Type your message in Arabic or English">
            </div>
            <button class="btn" onclick="testVoice()">Test AI Response</button>
            <div id="response-area"></div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'overview' || tabName === 'business' || tabName === 'test') {
                loadBusinesses();
            }
        }

        function loadBusinesses() {
            fetch('/api/businesses')
                .then(response => response.json())
                .then(data => {
                    const businessList = document.getElementById('business-list');
                    const businessOverview = document.getElementById('business-overview');
                    const testSelect = document.getElementById('test-business');
                    
                    if (data.businesses && data.businesses.length > 0) {
                        // Update business list
                        businessList.innerHTML = data.businesses.map(b => `
                            <div class="business-card">
                                <h4>${b.name}</h4>
                                <p>${b.description || 'No description'}</p>
                                <small>ID: ${b.id}</small>
                            </div>
                        `).join('');
                        
                        // Update overview
                        businessOverview.innerHTML = `
                            <div class="business-card">
                                <h4>📊 Total Businesses: ${data.businesses.length}</h4>
                                <p>Your AI voice agents are ready to serve customers!</p>
                            </div>
                        `;
                        
                        // Update test select
                        testSelect.innerHTML = '<option value="">Select a business...</option>' +
                            data.businesses.map(b => `<option value="${b.id}">${b.name}</option>`).join('');
                    } else {
                        businessList.innerHTML = '<p>No businesses created yet.</p>';
                        businessOverview.innerHTML = '<p>Create your first business to get started!</p>';
                        testSelect.innerHTML = '<option value="">No businesses available</option>';
                    }
                });
        }

        function createBusiness() {
            const name = document.getElementById('business-name').value;
            const description = document.getElementById('business-description').value;
            
            if (!name) {
                alert('Please enter a business name');
                return;
            }
            
            fetch('/api/businesses', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Business created successfully!');
                    document.getElementById('business-name').value = '';
                    document.getElementById('business-description').value = '';
                    loadBusinesses();
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }

        function testVoice() {
            const businessId = document.getElementById('test-business').value;
            const message = document.getElementById('test-message').value;
            
            if (!businessId || !message) {
                alert('Please select a business and enter a message');
                return;
            }
            
            fetch(`/api/businesses/${businessId}/test-voice`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            })
            .then(response => response.json())
            .then(data => {
                const responseArea = document.getElementById('response-area');
                if (data.success) {
                    responseArea.textContent = `AI Response: ${data.result.response}\\n\\nIntent: ${data.result.intent}`;
                } else {
                    responseArea.textContent = `Error: ${data.error}`;
                }
            });
        }

        // Load businesses on page load
        loadBusinesses();
    </script>
</body>
</html>
    ''', 
    openai_configured=bool(os.getenv('OPENAI_API_KEY')),
    elevenlabs_configured=bool(os.getenv('ELEVENLABS_API_KEY'))
    )

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
def test_voice(business_id):
    data = request.get_json()
    message = data.get('message', '')
    
    # Find business
    business = next((b for b in businesses if b['id'] == business_id), None)
    if not business:
        return jsonify({'success': False, 'error': 'Business not found'}), 404
    
    # Enhanced response based on business description
    is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
    business_name = business['name']
    business_desc = business.get('description', '')
    
    if is_arabic:
        if 'موعد' in message or 'حجز' in message:
            response = f"مرحباً بك في {business_name}! يمكنني مساعدتك في حجز موعد. متى تفضل الحضور؟"
        elif 'سعر' in message or 'كم' in message:
            response = f"أسعارنا في {business_name} تنافسية جداً. {business_desc[:100]}... هل تريد معرفة سعر خدمة معينة؟"
        else:
            response = f"مرحباً بك في {business_name}! {business_desc[:100]}... كيف يمكنني مساعدتك؟"
    else:
        if 'appointment' in message.lower() or 'book' in message.lower():
            response = f"Hello! Welcome to {business_name}. I can help you book an appointment. When would you like to visit?"
        elif 'price' in message.lower() or 'cost' in message.lower():
            response = f"Our prices at {business_name} are very competitive. {business_desc[:100]}... What specific service are you interested in?"
        else:
            response = f"Hello! Welcome to {business_name}. {business_desc[:100]}... How can I help you today?"
    
    return jsonify({
        'success': True,
        'result': {
            'response': response,
            'intent': 'general',
            'business_name': business_name
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
