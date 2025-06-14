import os
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory storage
businesses = []
business_counter = 1

# Initialize OpenAI client
openai_client = None
if os.getenv('OPENAI_API_KEY'):
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI: {e}")

def get_current_day_info():
    """Get current day and time information for Saudi Arabia"""
    now = datetime.now()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    arabic_days = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
    
    current_day = days[now.weekday()]
    current_day_arabic = arabic_days[now.weekday()]
    current_time = now.strftime('%I:%M %p')
    
    return {
        'current_day': current_day,
        'current_day_arabic': current_day_arabic,
        'current_time': current_time,
        'current_date': now.strftime('%Y-%m-%d'),
        'formatted_date': now.strftime('%A, %B %d, %Y')
    }

def process_with_gpt(message, business_data):
    """Process message with real OpenAI GPT"""
    if not openai_client:
        return generate_fallback_response(message, business_data)
    
    try:
        day_info = get_current_day_info()
        business_name = business_data.get('name', 'Business')
        business_description = business_data.get('description', '')
        
        # Create intelligent system prompt
        system_prompt = f"""You are a professional AI assistant for {business_name}, a business in Saudi Arabia.

CURRENT DATE & TIME:
- Today is {day_info['formatted_date']} ({day_info['current_day']})
- Current time: {day_info['current_time']}

BUSINESS INFORMATION:
{business_description}

INSTRUCTIONS:
- Respond in the same language the customer uses (Arabic or English)
- Be professional, helpful, and concise
- When asked about "today" or current day, refer to {day_info['current_day']}
- Check business hours against the current day and time
- For appointment requests, suggest specific available times
- Provide accurate information based on the business description
- If business hours are mentioned in description, use them to answer availability questions
- Be natural and conversational, not robotic"""

        # Send to OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Detect intent
        intent = detect_intent(message)
        
        return {
            'response': ai_response,
            'intent': intent,
            'confidence': 0.9,
            'powered_by': 'OpenAI GPT-4'
        }
        
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return generate_fallback_response(message, business_data)

def detect_intent(message):
    """Detect customer intent"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['book', 'appointment', 'schedule', 'موعد', 'حجز', 'احجز']):
        return 'booking'
    elif any(word in message_lower for word in ['price', 'cost', 'سعر', 'كم', 'تكلفة']):
        return 'pricing'
    elif any(word in message_lower for word in ['hours', 'open', 'closed', 'today', 'ساعات', 'مفتوح', 'مغلق', 'اليوم']):
        return 'hours'
    elif any(word in message_lower for word in ['service', 'offer', 'خدمات', 'تقدمون']):
        return 'services'
    else:
        return 'general'

def generate_fallback_response(message, business_data):
    """Fallback response when OpenAI is not available"""
    day_info = get_current_day_info()
    business_name = business_data.get('name', 'Business')
    business_desc = business_data.get('description', '')
    
    is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
    intent = detect_intent(message)
    
    if intent == 'hours':
        if is_arabic:
            response = f"اليوم هو {day_info['current_day_arabic']} والوقت الحالي {day_info['current_time']}. بناءً على معلومات {business_name}: {business_desc}"
        else:
            response = f"Today is {day_info['current_day']} and it's currently {day_info['current_time']}. Based on {business_name}'s schedule: {business_desc}"
    elif intent == 'booking':
        if is_arabic:
            response = f"يمكنني مساعدتك في حجز موعد في {business_name}. اليوم هو {day_info['current_day_arabic']}. {business_desc}"
        else:
            response = f"I can help you book an appointment at {business_name}. Today is {day_info['current_day']}. {business_desc}"
    else:
        if is_arabic:
            response = f"مرحباً بك في {business_name}! كيف يمكنني مساعدتك؟"
        else:
            response = f"Hello! Welcome to {business_name}. How can I help you?"
    
    return {
        'response': response,
        'intent': intent,
        'confidence': 0.6,
        'powered_by': 'Fallback System'
    }

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
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 20px;
            margin-top: 15px;
            min-height: 120px;
            white-space: pre-wrap;
            font-family: monospace;
            border-left: 4px solid #4CAF50;
        }
        .ai-badge {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Voice Agent System</h1>
            <p>Powered by OpenAI GPT-4 <span class="ai-badge">SMART AI</span></p>
        </div>

        <div class="status-card">
            <h3>✅ System Status: ONLINE</h3>
            <p>Your AI Voice Agent is ready with intelligent responses!</p>
            <div class="api-status">
                <div class="api-card">
                    <span class="status-indicator status-ok"></span>
                    <strong>System</strong><br>Running
                </div>
                <div class="api-card">
                    <span class="status-indicator {{ 'status-ok' if openai_configured else 'status-error' }}"></span>
                    <strong>OpenAI GPT-4</strong><br>{{ 'Connected' if openai_configured else 'Not Configured' }}
                </div>
                <div class="api-card">
                    <span class="status-indicator {{ 'status-ok' if elevenlabs_configured else 'status-error' }}"></span>
                    <strong>ElevenLabs</strong><br>{{ 'Connected' if elevenlabs_configured else 'Not Configured' }}
                </div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('business')">🏢 Business</button>
            <button class="tab" onclick="showTab('test')">🧠 Test AI</button>
        </div>

        <div id="business" class="tab-content active">
            <h3>🏢 Business Management</h3>
            <div class="form-group">
                <label>Business Name</label>
                <input type="text" id="business-name" placeholder="Enter business name">
            </div>
            <div class="form-group">
                <label>Business Description (AI Training Data)</label>
                <textarea id="business-description" rows="6" placeholder="Example: Alsinan Family Medical Clinic - Open Monday & Thursday 4PM-11PM. Services: General consultation (150 SAR), Lab tests (80 SAR), Specialist consultations (200 SAR). Located in Riyadh. Accepts insurance."></textarea>
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
            <h3>🧠 Test AI Intelligence</h3>
            <div class="form-group">
                <label>Select Business</label>
                <select id="test-business">
                    <option value="">Select a business...</option>
                </select>
            </div>
            <div class="form-group">
                <label>Test Message (Arabic or English)</label>
                <input type="text" id="test-message" placeholder="Try: 'Are you open today?' or 'هل أنتم مفتوحين اليوم؟'">
            </div>
            <button class="btn" onclick="testVoice()">🧠 Test AI Response</button>
            <div id="response-area">AI responses will appear here...</div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'business' || tabName === 'test') {
                loadBusinesses();
            }
        }

        function loadBusinesses() {
            fetch('/api/businesses')
                .then(response => response.json())
                .then(data => {
                    const businessList = document.getElementById('business-list');
                    const testSelect = document.getElementById('test-business');
                    
                    if (data.businesses && data.businesses.length > 0) {
                        businessList.innerHTML = data.businesses.map(b => `
                            <div class="business-card">
                                <h4>${b.name}</h4>
                                <p><strong>AI Training Data:</strong> ${b.description || 'No description'}</p>
                                <small>Business ID: ${b.id}</small>
                            </div>
                        `).join('');
                        
                        testSelect.innerHTML = '<option value="">Select a business...</option>' +
                            data.businesses.map(b => `<option value="${b.id}">${b.name}</option>`).join('');
                    } else {
                        businessList.innerHTML = '<p>No businesses created yet.</p>';
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
            
            const responseArea = document.getElementById('response-area');
            responseArea.textContent = '🧠 AI is thinking...';
            
            fetch(`/api/businesses/${businessId}/test-voice`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    responseArea.innerHTML = `
<strong>🤖 AI Response:</strong>
${data.result.response}

<strong>📊 Analysis:</strong>
Intent: ${data.result.intent}
Confidence: ${(data.result.confidence * 100).toFixed(0)}%
Powered by: ${data.result.powered_by}
                    `;
                } else {
                    responseArea.textContent = `❌ Error: ${data.error}`;
                }
            });
        }

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
        'message': 'AI Voice Agent with GPT-4 is working!',
        'openai_configured': bool(os.getenv('OPENAI_API_KEY')),
        'elevenlabs_configured': bool(os.getenv('ELEVENLABS_API_KEY')),
        'ai_engine': 'OpenAI GPT-4' if openai_client else 'Fallback System'
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
    
    # Process with real GPT
    result = process_with_gpt(message, business)
    
    return jsonify({
        'success': True,
        'result': result
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
