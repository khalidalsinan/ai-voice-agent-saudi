import os
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

businesses = []
business_counter = 1

# Initialize OpenAI client with better error handling
openai_client = None
openai_status = "Not Configured"

try:
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        from openai import OpenAI
        openai_client = OpenAI(api_key=api_key)
        # Test the connection
        test_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        openai_status = "Connected ✅"
        logger.info("OpenAI GPT-4 connected successfully")
    else:
        openai_status = "No API Key"
        logger.warning("No OpenAI API key found")
except Exception as e:
    openai_status = f"Error: {str(e)[:50]}"
    logger.error(f"OpenAI initialization failed: {e}")

def get_current_day_info():
    now = datetime.now()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    arabic_days = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
    
    return {
        'current_day': days[now.weekday()],
        'current_day_arabic': arabic_days[now.weekday()],
        'current_time': now.strftime('%I:%M %p'),
        'formatted_date': now.strftime('%A, %B %d, %Y')
    }

def process_with_gpt(message, business_data):
    if not openai_client:
        return generate_smart_fallback(message, business_data)
    
    try:
        day_info = get_current_day_info()
        business_name = business_data.get('name', 'Business')
        business_description = business_data.get('description', '')
        
        # Detect if message is off-topic
        business_keywords = ['appointment', 'book', 'price', 'cost', 'service', 'open', 'closed', 'hours', 'available', 'موعد', 'حجز', 'سعر', 'خدمة', 'مفتوح', 'مغلق', 'ساعات']
        is_business_related = any(keyword in message.lower() for keyword in business_keywords)
        
        if not is_business_related:
            # Handle off-topic requests
            is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
            if is_arabic:
                return {
                    'response': f"أنا مساعد ذكي لـ {business_name}. أستطيع مساعدتك في المواعيد والخدمات الطبية فقط. كيف يمكنني مساعدتك؟",
                    'intent': 'off_topic',
                    'confidence': 0.9,
                    'powered_by': 'OpenAI GPT-4'
                }
            else:
                return {
                    'response': f"I'm an AI assistant for {business_name}. I can help you with appointments, services, and medical inquiries. How can I assist you today?",
                    'intent': 'off_topic',
                    'confidence': 0.9,
                    'powered_by': 'OpenAI GPT-4'
                }
        
        system_prompt = f"""You are a professional AI assistant for {business_name}.

CURRENT INFO:
- Today is {day_info['current_day']} at {day_info['current_time']}

BUSINESS INFO:
{business_description}

RESPONSE RULES:
1. Be concise and professional (max 2 sentences)
2. For hours questions: Give direct yes/no answer about being open today, then state actual hours
3. For appointments: Suggest specific available times
4. For pricing: Give specific prices if mentioned in description
5. Respond in the same language as the customer
6. Don't repeat the entire business description
7. Be helpful and direct

Examples:
- "Are you open today?" → "No, we're closed today. We're open Monday and Tuesday from 4pm-11pm."
- "هل أنتم مفتوحين اليوم؟" → "لا، نحن مغلقون اليوم. نعمل يوم الاثنين والثلاثاء من 4 مساءً إلى 11 مساءً."
"""

        response = openai_client.chat.completions.create(
            model="gpt-4",
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
            'powered_by': 'OpenAI GPT-4'
        }
        
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return generate_smart_fallback(message, business_data)

def detect_intent(message):
    message_lower = message.lower()
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

def generate_smart_fallback(message, business_data):
    day_info = get_current_day_info()
    business_name = business_data.get('name', 'Business')
    business_desc = business_data.get('description', '').lower()
    
    is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
    intent = detect_intent(message)
    
    if intent == 'hours':
        current_day = day_info['current_day'].lower()
        
        # Smart parsing of business hours
        is_open_today = False
        if 'mon' in business_desc and 'monday' in current_day:
            is_open_today = True
        elif 'tue' in business_desc and 'tuesday' in current_day:
            is_open_today = True
        elif 'wed' in business_desc and 'wednesday' in current_day:
            is_open_today = True
        elif 'thu' in business_desc and 'thursday' in current_day:
            is_open_today = True
        elif 'fri' in business_desc and 'friday' in current_day:
            is_open_today = True
        elif 'sat' in business_desc and 'saturday' in current_day:
            is_open_today = True
        elif 'sun' in business_desc and 'sunday' in current_day:
            is_open_today = True
        
        if is_arabic:
            if is_open_today:
                response = f"نعم، نحن مفتوحون اليوم. ساعات العمل حسب الجدول المحدد."
            else:
                response = f"لا، نحن مغلقون اليوم ({day_info['current_day_arabic']}). تحقق من ساعات العمل المحددة."
        else:
            if is_open_today:
                response = f"Yes, we're open today. Please check our scheduled hours."
            else:
                response = f"No, we're closed today ({day_info['current_day']}). Please check our operating schedule."
    
    elif intent == 'general':
        # Check if it's off-topic
        business_keywords = ['appointment', 'book', 'price', 'service', 'open', 'موعد', 'حجز', 'سعر', 'خدمة']
        is_business_related = any(keyword in message.lower() for keyword in business_keywords)
        
        if not is_business_related:
            if is_arabic:
                response = f"أنا مساعد ذكي لـ {business_name}. أستطيع مساعدتك في المواعيد والخدمات فقط."
            else:
                response = f"I'm an AI assistant for {business_name}. I can help with appointments and services."
        else:
            if is_arabic:
                response = f"مرحباً بك في {business_name}! كيف يمكنني مساعدتك؟"
            else:
                response = f"Hello! Welcome to {business_name}. How can I help you?"
    
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
            <strong>🧠 OpenAI GPT-4:</strong> {{ openai_status }}<br>
            <strong>🎤 ElevenLabs:</strong> {{ 'Configured' if elevenlabs_configured else 'Not Configured' }}
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="/dashboard" class="btn">🚀 Open Dashboard</a>
            <a href="/health" class="btn">🔍 Health Check</a>
        </div>
        
        <div class="feature">
            <strong>🎤 Smart Voice Processing</strong><br>
            Powered by OpenAI GPT-4 for intelligent responses
        </div>
        <div class="feature">
            <strong>📅 Date-Aware Responses</strong><br>
            Knows current day and business hours
        </div>
        <div class="feature">
            <strong>💼 Professional Handling</strong><br>
            Concise, helpful responses in Arabic and English
        </div>
    </div>
</body>
</html>
    ''', 
    openai_status=openai_status,
    elevenlabs_configured=bool(os.getenv('ELEVENLABS_API_KEY'))
    )

@app.route('/dashboard')
def dashboard():
    return "Dashboard coming soon..."

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'openai_status': openai_status,
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
    
    result = process_with_gpt(message, business)
    return jsonify({'success': True, 'result': result})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
