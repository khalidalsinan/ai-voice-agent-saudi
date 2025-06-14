import os
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

businesses = []
business_counter = 1

# Initialize AI clients
ai_client = None
ai_status = "Not Configured"
ai_provider = "None"

def initialize_ai():
    global ai_client, ai_status, ai_provider
    
    # Try Anthropic Claude first
    if os.getenv('ANTHROPIC_API_KEY'):
        try:
            import anthropic
            ai_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            ai_status = "Connected ✅"
            ai_provider = "Anthropic Claude"
            logger.info("Anthropic Claude connected successfully")
            return
        except Exception as e:
            logger.error(f"Anthropic failed: {str(e)}")
    
    # Try OpenAI
    if os.getenv('OPENAI_API_KEY'):
        try:
            from openai import OpenAI
            ai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            test_response = ai_client.chat.completions.create(
                model="gpt-4o-mini",  # Use a lighter, modern model
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            ai_status = "Connected ✅"
            ai_provider = "OpenAI GPT-4o-mini"
            logger.info("OpenAI GPT-4o-mini connected successfully")
            return
        except Exception as e:
            logger.error(f"OpenAI failed: {str(e)}")
    
    # Try Google Gemini
    if os.getenv('GOOGLE_API_KEY'):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            ai_client = genai.GenerativeModel('gemini-1.5-flash')  # Updated model
            ai_status = "Connected ✅"
            ai_provider = "Google Gemini"
            logger.info("Google Gemini connected successfully")
            return
        except Exception as e:
            logger.error(f"Google Gemini failed: {str(e)}")
    
    # Try Groq
    if os.getenv('GROQ_API_KEY'):
        try:
            from groq import Groq
            ai_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            test_response = ai_client.chat.completions.create(
                model="llama3-70b-8192",  # Use a more powerful model
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            ai_status = "Connected ✅"
            ai_provider = "Groq Llama"
            logger.info("Groq Llama connected successfully")
            return
        except Exception as e:
            logger.error(f"Groq failed: {str(e)}")
    
    ai_status = "No API Keys Found"
    ai_provider = "Fallback System"
    logger.error("No valid API keys found for any AI provider")

# Initialize AI on startup
initialize_ai()

def get_current_day_info(is_tomorrow=False):
    now = datetime.now()
    if is_tomorrow:
        now += timedelta(days=1)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    arabic_days = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
    
    return {
        'current_day': days[now.weekday()],
        'current_day_arabic': arabic_days[now.weekday()],
        'current_time': now.strftime('%I:%M %p'),
        'formatted_date': now.strftime('%A, %B %d, %Y'),
        'is_tomorrow': is_tomorrow
    }

def detect_intent(message):
    message_lower = message.lower()
    if any(word in message_lower for word in ['tomorrow', 'غداً']):
        if any(word in message_lower for word in ['hours', 'open', 'closed', 'ساعات', 'مفتوح', 'مغلق']):
            return 'hours_tomorrow'
    if any(word in message_lower for word in ['book', 'appointment', 'schedule', 'موعد', 'حجز']):
        return 'booking'
    elif any(word in message_lower for word in ['price', 'cost', 'سعر', 'كم']):
        return 'pricing'
    elif any(word in message_lower for word in ['hours', 'open', 'closed', 'today', 'ساعات', 'مفتوح', 'مغلق', 'اليوم']):
        return 'hours'
    elif any(word in message_lower for word in ['service', 'offer', 'خدمات']):
        return 'services'
    else:
        return 'general'

def process_with_ai(message, business_data):
    if not ai_client:
        logger.warning("No AI client available, falling back to smart fallback")
        return generate_smart_fallback(message, business_data)
    
    try:
        is_tomorrow = detect_intent(message) == 'hours_tomorrow'
        day_info = get_current_day_info(is_tomorrow=is_tomorrow)
        business_name = business_data.get('name', 'Business')
        business_description = business_data.get('description', '')
        
        # Check if off-topic
        business_keywords = ['appointment', 'book', 'price', 'cost', 'service', 'open', 'closed', 'hours', 'available', 'tomorrow', 'موعد', 'حجز', 'سعر', 'خدمة', 'مفتوح', 'مغلق', 'ساعات', 'غداً']
        is_business_related = any(keyword in message.lower() for keyword in business_keywords)
        
        if not is_business_related:
            is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
            if is_arabic:
                response = f"أنا مساعد ذكي لـ {business_name}. أستطيع مساعدتك في المواعيد والخدمات الطبية فقط. كيف يمكنني مساعدتك؟"
            else:
                response = f"I'm an AI assistant for {business_name}. I can help with appointments, services, and medical inquiries. How can I assist you today?"
            
            return {
                'response': response,
                'intent': 'off_topic',
                'confidence': 0.9,
                'powered_by': ai_provider
            }
        
        system_prompt = f"""You are a professional AI assistant for {business_name}, a business that provides services based on the following description: {business_description}

CURRENT INFO:
- Today is {day_info['current_day']}, {day_info['formatted_date']} at {day_info['current_time']}
- Tomorrow is {get_current_day_info(is_tomorrow=True)['current_day']}, {get_current_day_info(is_tomorrow=True)['formatted_date']}

RESPONSE RULES:
1. Be concise and professional (max 2 sentences)
2. For hours questions: Check if the query is about today or tomorrow, then give a direct yes/no answer about being open, followed by specific hours if available in the description
3. For appointments: Suggest specific available times based on the business description
4. For pricing: Provide specific prices if mentioned in the description
5. Respond in the same language as the customer (Arabic or English)
6. Do not repeat the entire business description in the response
7. Be helpful, direct, and context-aware
8. If the query mentions 'tomorrow' or 'غداً', provide information for {get_current_day_info(is_tomorrow=True)['current_day']}
9. If the business description lacks specific details, respond based on general knowledge but stay professional

Examples:
- "Are you open today?" → "No, we're closed today. We're open Monday and Tuesday from 4pm-11pm."
- "Is the business closed tomorrow?" → "Yes, we're closed tomorrow (Sunday). We're open Monday and Tuesday from 4pm-11pm."
- "هل أنتم مفتوحين غداً؟" → "نعم، نحن مفتوحون غداً (الأحد). نعمل من 4 مساءً إلى 11 مساءً."
- "What services do you offer?" → "We offer general consultations and lab tests. Please check our website for more details."
"""

        # Call different AI providers
        if ai_provider == "Anthropic Claude":
            response = ai_client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Updated to a more recent model
                max_tokens=150,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": f"{system_prompt}\n\nCustomer message: {message}"}
                ]
            )
            ai_response = response.content[0].text.strip()
            
        elif ai_provider == "OpenAI GPT-4o-mini":
            response = ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=150,
                temperature=0.3
            )
            ai_response = response.choices[0].message.content.strip()
            
        elif ai_provider == "Google Gemini":
            prompt = f"{system_prompt}\n\nCustomer message: {message}"
            response = ai_client.generate_content(prompt)
            ai_response = response.text.strip()
            
        elif ai_provider == "Groq Llama":
            response = ai_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=150,
                temperature=0.3
            )
            ai_response = response.choices[0].message.content.strip()
        
        intent = detect_intent(message)
        
        return {
            'response': ai_response,
            'intent': intent,
            'confidence': 0.95,
            'powered_by': ai_provider
        }
        
    except Exception as e:
        logger.error(f"AI API error: {str(e)}")
        return generate_smart_fallback(message, business_data)

def generate_smart_fallback(message, business_data):
    is_tomorrow = detect_intent(message) == 'hours_tomorrow'
    day_info = get_current_day_info(is_tomorrow=is_tomorrow)
    business_name = business_data.get('name', 'Business')
    business_desc = business_data.get('description', '').lower()
    
    is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
    intent = detect_intent(message)
    
    if intent in ['hours', 'hours_tomorrow']:
        target_day = day_info['current_day'].lower()
        target_day_short = target_day[:3]
        is_open = any(day in business_desc for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] if day in target_day_short)
        
        if is_arabic:
            day_label = day_info['current_day_arabic'] + (' (غداً)' if is_tomorrow else '')
            if is_open:
                response = f"نعم، نحن مفتوحون {day_label}. تحقق من ساعات العمل المحددة في وصف الشركة."
            else:
                response = f"لا، نحن مغلقون {day_label}. تحقق من جدول العمل في وصف الشركة."
        else:
            day_label = day_info['current_day'] + (' (tomorrow)' if is_tomorrow else '')
            if is_open:
                response = f"Yes, we're open {day_label}. Please check our scheduled hours in the business description."
            else:
                response = f"No, we're closed {day_label}. Check our operating schedule in the business description."
    else:
        if is_arabic:
            response = f"مرحباً بك في {business_name}! كيف يمكنني مساعدتك؟"
        else:
            response = f"Hello! Welcome to {business_name}. How can I help you?"
    
    return {
        'response': response,
        'intent': intent,
        'confidence': 0.7,
        'powered_by': 'Smart Fallback'
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
        .api-status {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Voice Agent System</h1>
        
        <div class="status">
            <h3>✅ System Status: ONLINE</h3>
            <p>Your AI Voice Agent is ready to handle customer calls!</p>
        </div>
        
        <div class="api-status">
            <strong>🧠 AI Engine:</strong> {{ ai_provider }} - {{ ai_status }}<br>
            <strong>🎤 ElevenLabs:</strong> {{ 'Configured' if elevenlabs_configured else 'Not Configured' }}
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="/dashboard" class="btn">🚀 Open Dashboard</a>
            <a href="/health" class="btn">🔍 Health Check</a>
        </div>
        
        <div class="feature">
            <strong>🎤 Smart Voice Processing</strong><br>
            Powered by {{ ai_provider }} for intelligent responses
        </div>
        <div class="feature">
            <strong>📅 Date-Aware Responses</strong><br>
            Knows current day, tomorrow, and business hours
        </div>
        <div class="feature">
            <strong>💼 Professional Handling</strong><br>
            Concise, helpful responses in Arabic and English
        </div>
    </div>
</body>
</html>
    ''', 
    ai_provider=ai_provider,
    ai_status=ai_status,
    elevenlabs_configured=bool(os.getenv('ELEVENLABS_API_KEY'))
    )

@app.route('/dashboard')
def dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Voice Agent Dashboard</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1000px; 
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
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
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
        .business-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #4CAF50;
        }
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI Voice Agent Dashboard</h1>
        
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
                <textarea id="business-description" rows="6" placeholder="Example: Alsinan Family Medical Clinic - Open Monday & Tuesday 4PM-11PM, closed Sunday. Services: General consultation (150 SAR), Lab tests (80 SAR). Located in Qatif. Accepts insurance."></textarea>
            </div>
            <button class="btn" onclick="createBusiness()">Create Business</button>
            
            <div style="margin-top: 30px;">
                <h4>📋 Your Businesses</h4>
                <div id="business-list">
                    <p>Loading businesses...</p>
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
                <input type="text" id="test-message" placeholder="Try: 'Are you open tomorrow?' or 'هل أنتم مفتوحين غداً؟'">
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
            
            loadBusinesses();
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
    ''')

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'ai_provider': ai_provider,
        'ai_status': ai_status,
        'elevenlabs_configured': bool(os.getenv('ELEVENLABS_API_KEY'))
    })

@app.route('/api/businesses', methods=['GET'])
def get_businesses():
    return jsonify({'success': True, 'businesses': businesses})

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
    
    return jsonify({'success': True, 'message': 'Business created!', 'business': business})

@app.route('/api/businesses/<int:business_id>/test-voice', methods=['POST'])
def test_voice(business_id):
    data = request.get_json()
    message = data.get('message', '')
    
    business = next((b for b in businesses if b['id'] == business_id), None)
    if not business:
        return jsonify({'success': False, 'error': 'Business not found'}), 404
    
    result = process_with_ai(message, business)
    return jsonify({'success': True, 'result': result})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
