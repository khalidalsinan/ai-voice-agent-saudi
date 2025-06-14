import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceService:
    """Voice Processing Service for Saudi businesses."""
    
    def __init__(self, openai_api_key: Optional[str] = None, elevenlabs_api_key: Optional[str] = None):
        """Initialize the voice service with API keys."""
        self.openai_api_key = openai_api_key
        self.elevenlabs_api_key = elevenlabs_api_key
        self.conversation_contexts = {}
        
        # Initialize OpenAI client if key is provided
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            self.client = None
            logger.warning("No OpenAI API key provided, using mock responses")
    
    def get_current_time_info(self) -> Dict[str, Any]:
        """Get current time information (simplified without timezone)."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        # Day names in Arabic
        arabic_days = {
            'Monday': 'الاثنين', 'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء',
            'Thursday': 'الخميس', 'Friday': 'الجمعة', 'Saturday': 'السبت', 'Sunday': 'الأحد'
        }
        
        return {
            'current_date': now.strftime('%Y-%m-%d'),
            'current_time': now.strftime('%I:%M %p'),
            'current_day_english': now.strftime('%A'),
            'current_day_arabic': arabic_days.get(now.strftime('%A'), now.strftime('%A')),
            'yesterday_day_english': yesterday.strftime('%A'),
            'yesterday_day_arabic': arabic_days.get(yesterday.strftime('%A'), yesterday.strftime('%A')),
            'tomorrow_day_english': tomorrow.strftime('%A'),
            'tomorrow_day_arabic': arabic_days.get(tomorrow.strftime('%A'), tomorrow.strftime('%A')),
            'formatted_date': now.strftime('%A, %B %d, %Y'),
            'hour': now.hour,
            'is_business_hours': 8 <= now.hour <= 22
        }
    
    def create_intelligent_prompt(self, business_data: Dict[str, Any]) -> str:
        """Create an intelligent system prompt with business and time context."""
        time_info = self.get_current_time_info()
        business_name = business_data.get('name', 'Business')
        business_description = business_data.get('description', '')
        business_hours = business_data.get('hours', '')
        
        system_prompt = f"""You are an intelligent AI assistant for {business_name}, a business in Saudi Arabia.

CURRENT DATE & TIME:
- Today is {time_info['formatted_date']} ({time_info['current_day_arabic']})
- Current time: {time_info['current_time']}
- Yesterday was {time_info['yesterday_day_english']} ({time_info['yesterday_day_arabic']})
- Tomorrow will be {time_info['tomorrow_day_english']} ({time_info['tomorrow_day_arabic']})
- Business status: {'Open' if time_info['is_business_hours'] else 'Closed'} (typical hours)

BUSINESS INFORMATION:
Name: {business_name}
Description: {business_description}
Hours: {business_hours}

INSTRUCTIONS:
- Respond in the same language the customer uses (Arabic or English)
- Be professional and helpful
- When asked about "today" - refer to {time_info['current_day_english']}
- For appointments, suggest available times
- Handle both Arabic and English naturally
- Provide specific information about services and pricing when available"""

        return system_prompt
    
    def detect_intent(self, message: str) -> Dict[str, Any]:
        """Detect customer intent from their message."""
        message_lower = message.lower()
        
        # Intent patterns
        if any(word in message_lower for word in ['book', 'appointment', 'schedule', 'موعد', 'حجز', 'احجز']):
            return {'intent': 'booking', 'confidence': 0.9}
        elif any(word in message_lower for word in ['price', 'cost', 'سعر', 'كم', 'تكلفة']):
            return {'intent': 'pricing', 'confidence': 0.8}
        elif any(word in message_lower for word in ['hours', 'open', 'closed', 'ساعات', 'مفتوح', 'مغلق']):
            return {'intent': 'hours', 'confidence': 0.8}
        elif any(word in message_lower for word in ['service', 'offer', 'خدمات', 'تقدمون']):
            return {'intent': 'services', 'confidence': 0.7}
        else:
            return {'intent': 'general', 'confidence': 0.5}
    
    def process_message(self, message: str, business_data: Dict[str, Any], conversation_id: str = "default") -> Dict[str, Any]:
        """Process customer message with AI response."""
        try:
            # Get conversation history
            conversation_history = self.conversation_contexts.get(conversation_id, [])
            
            # Detect intent
            intent_info = self.detect_intent(message)
            
            # Create intelligent prompt
            system_prompt = self.create_intelligent_prompt(business_data)
            
            # Add current message to history
            conversation_history.append({"role": "user", "content": message})
            
            if self.client:
                # Use real OpenAI API
                messages = [
                    {"role": "system", "content": system_prompt},
                    *conversation_history[-5:]  # Keep last 5 messages
                ]
                
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
                
            else:
                # Generate mock response
                ai_response = self.generate_mock_response(message, business_data, intent_info)
            
            # Add AI response to history
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Update conversation context
            self.conversation_contexts[conversation_id] = conversation_history
            
            return {
                'response': ai_response,
                'intent': intent_info['intent'],
                'confidence': intent_info['confidence'],
                'business_name': business_data.get('name', 'Business'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again.",
                'intent': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def generate_mock_response(self, message: str, business_data: Dict[str, Any], intent_info: Dict[str, Any]) -> str:
        """Generate intelligent mock responses for testing."""
        business_name = business_data.get('name', 'Business')
        time_info = self.get_current_time_info()
        intent = intent_info['intent']
        
        # Detect language
        is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
        
        if intent == 'booking':
            if is_arabic:
                return f"مرحباً بك في {business_name}! يمكنني مساعدتك في حجز موعد. اليوم هو {time_info['current_day_arabic']} ولدينا مواعيد متاحة. ما الوقت المناسب لك؟"
            else:
                return f"Hello! Welcome to {business_name}. I can help you book an appointment. Today is {time_info['current_day_english']} and we have availability. What time works best for you?"
        
        elif intent == 'hours':
            if is_arabic:
                return f"نحن في {business_name} مفتوحون اليوم ({time_info['current_day_arabic']}) والوقت الحالي {time_info['current_time']}. ساعات عملنا من الأحد إلى الخميس 8 صباحاً - 10 مساءً."
            else:
                return f"We at {business_name} are open today ({time_info['current_day_english']}) and it's currently {time_info['current_time']}. Our hours are Sunday to Thursday, 8 AM to 10 PM."
        
        elif intent == 'pricing':
            if is_arabic:
                return f"أسعارنا في {business_name} تنافسية جداً. الكشف العام 150 ريال، والتحاليل تبدأ من 80 ريال. هل تريد معرفة سعر خدمة معينة؟"
            else:
                return f"Our prices at {business_name} are very competitive. General consultation is 150 SAR, lab tests start from 80 SAR. Would you like to know about a specific service?"
        
        elif intent == 'services':
            if is_arabic:
                return f"نقدم في {business_name} خدمات شاملة: الكشف العام، التحاليل الطبية، والاستشارات المتخصصة. كيف يمكنني مساعدتك؟"
            else:
                return f"At {business_name}, we offer comprehensive services: general consultations, lab tests, and specialist consultations. How can I help you?"
        
        else:
            if is_arabic:
                return f"مرحباً بك في {business_name}! كيف يمكنني مساعدتك اليوم؟ يمكنني مساعدتك في حجز المواعيد أو الإجابة على استفساراتك."
            else:
                return f"Welcome to {business_name}! How can I help you today? I can assist with appointments, pricing, or answer any questions you may have."
    
    def clear_conversation_context(self, conversation_id: str = "default"):
        """Clear conversation history for a specific conversation."""
        if conversation_id in self.conversation_contexts:
            del self.conversation_contexts[conversation_id]
