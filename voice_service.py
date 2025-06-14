import os
import json
import logging
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceService:
    """
    Advanced Voice Processing Service with intelligent date/time awareness
    and business-specific conversation handling for Saudi businesses.
    """
    
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
    
    def get_saudi_time_info(self) -> Dict[str, Any]:
        """
        Get comprehensive time and date information for Saudi Arabia.
        Returns detailed time context for intelligent conversation.
        """
        saudi_tz = pytz.timezone('Asia/Riyadh')
        now = datetime.now(saudi_tz)
        
        # Calculate relative dates
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        # Day names in Arabic and English
        arabic_days = {
            'Monday': 'الاثنين',
            'Tuesday': 'الثلاثاء', 
            'Wednesday': 'الأربعاء',
            'Thursday': 'الخميس',
            'Friday': 'الجمعة',
            'Saturday': 'السبت',
            'Sunday': 'الأحد'
        }
        
        # Month names in Arabic
        arabic_months = {
            'January': 'يناير', 'February': 'فبراير', 'March': 'مارس',
            'April': 'أبريل', 'May': 'مايو', 'June': 'يونيو',
            'July': 'يوليو', 'August': 'أغسطس', 'September': 'سبتمبر',
            'October': 'أكتوبر', 'November': 'نوفمبر', 'December': 'ديسمبر'
        }
        
        return {
            'current_datetime': now,
            'current_date': now.strftime('%Y-%m-%d'),
            'current_time': now.strftime('%I:%M %p'),
            'current_time_24h': now.strftime('%H:%M'),
            'current_day_english': now.strftime('%A'),
            'current_day_arabic': arabic_days.get(now.strftime('%A'), now.strftime('%A')),
            'current_month_english': now.strftime('%B'),
            'current_month_arabic': arabic_months.get(now.strftime('%B'), now.strftime('%B')),
            'yesterday_date': yesterday.strftime('%Y-%m-%d'),
            'yesterday_day_english': yesterday.strftime('%A'),
            'yesterday_day_arabic': arabic_days.get(yesterday.strftime('%A'), yesterday.strftime('%A')),
            'tomorrow_date': tomorrow.strftime('%Y-%m-%d'),
            'tomorrow_day_english': tomorrow.strftime('%A'),
            'tomorrow_day_arabic': arabic_days.get(tomorrow.strftime('%A'), tomorrow.strftime('%A')),
            'formatted_date_english': now.strftime('%A, %B %d, %Y'),
            'formatted_date_arabic': f"{arabic_days.get(now.strftime('%A'), now.strftime('%A'))}، {now.day} {arabic_months.get(now.strftime('%B'), now.strftime('%B'))} {now.year}",
            'is_weekend': now.weekday() >= 4,  # Friday=4, Saturday=5
            'hour': now.hour,
            'is_morning': 6 <= now.hour < 12,
            'is_afternoon': 12 <= now.hour < 17,
            'is_evening': 17 <= now.hour < 21,
            'is_night': now.hour >= 21 or now.hour < 6
        }
    
    def parse_business_hours(self, hours_text: str) -> Dict[str, Any]:
        """
        Parse business hours text and return structured information.
        Supports both Arabic and English hour formats.
        """
        if not hours_text:
            return {'parsed': False, 'always_open': False}
        
        # Common patterns for business hours
        hours_lower = hours_text.lower()
        
        # Check if always open
        if any(phrase in hours_lower for phrase in ['24/7', '24 hours', 'always open', 'مفتوح دائماً']):
            return {'parsed': True, 'always_open': True}
        
        # Parse day-specific hours (basic implementation)
        # This can be enhanced based on your specific needs
        return {
            'parsed': True,
            'always_open': False,
            'original_text': hours_text,
            'needs_manual_check': True
        }
    
    def check_if_open_now(self, business_hours: str, time_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if business is currently open based on hours and current time.
        """
        hours_info = self.parse_business_hours(business_hours)
        
        if hours_info.get('always_open'):
            return {
                'is_open': True,
                'status': 'open',
                'message': 'We are open 24/7!'
            }
        
        # For now, return a general response
        # This can be enhanced with more sophisticated hour parsing
        current_hour = time_info['hour']
        is_business_hours = 8 <= current_hour <= 22  # Assume 8 AM to 10 PM
        
        return {
            'is_open': is_business_hours,
            'status': 'open' if is_business_hours else 'closed',
            'message': 'We are currently open' if is_business_hours else 'We are currently closed',
            'hours_text': business_hours
        }
    
    def create_intelligent_prompt(self, business_data: Dict[str, Any], conversation_history: list = None) -> str:
        """
        Create an intelligent system prompt with comprehensive business and time context.
        """
        time_info = self.get_saudi_time_info()
        business_name = business_data.get('name', 'Business')
        business_description = business_data.get('description', '')
        business_hours = business_data.get('hours', '')
        
        # Check current status
        status_info = self.check_if_open_now(business_hours, time_info)
        
        # Build comprehensive context
        system_prompt = f"""You are an intelligent AI assistant for {business_name}, a business in Saudi Arabia.

CURRENT DATE & TIME CONTEXT:
- Today is {time_info['formatted_date_english']} ({time_info['formatted_date_arabic']})
- Current time: {time_info['current_time']} ({time_info['current_time_24h']})
- Yesterday was {time_info['yesterday_day_english']} ({time_info['yesterday_day_arabic']})
- Tomorrow will be {time_info['tomorrow_day_english']} ({time_info['tomorrow_day_arabic']})
- Current status: {status_info['message']}

BUSINESS INFORMATION:
Name: {business_name}
Description: {business_description}
Hours: {business_hours}

INTELLIGENT CAPABILITIES:
- You understand relative time references (today, tomorrow, yesterday, this week, next week)
- You can determine if the business is currently open or closed
- You can book appointments for future dates
- You respond in the same language the customer uses (Arabic or English)
- You understand Saudi cultural context and business practices

CONVERSATION GUIDELINES:
1. Be professional, helpful, and culturally appropriate for Saudi customers
2. When asked about "today" - refer to {time_info['current_day_english']} ({time_info['current_day_arabic']})
3. When asked about hours "today" - check current day against business hours
4. For appointment booking, suggest available times based on business hours
5. Use appropriate greetings based on time of day (morning/afternoon/evening)
6. Handle both Arabic and English naturally
7. If asked about dates, be specific about which day you mean

EXAMPLE RESPONSES:
- "Are you open today?" → Check {time_info['current_day_english']} hours and current time
- "Can I book for tomorrow?" → Refer to {time_info['tomorrow_day_english']} availability
- "What about yesterday?" → Refer to {time_info['yesterday_day_english']} (past date)

Always be helpful and provide specific, accurate information based on the current date and time context."""

        return system_prompt
    
    def detect_intent(self, message: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect customer intent from their message with enhanced accuracy.
        """
        message_lower = message.lower()
        
        # Enhanced intent patterns
        booking_patterns = [
            'book', 'appointment', 'schedule', 'reserve', 'موعد', 'حجز', 'احجز', 'أريد موعد'
        ]
        
        pricing_patterns = [
            'price', 'cost', 'how much', 'سعر', 'كم', 'تكلفة', 'أسعار'
        ]
        
        hours_patterns = [
            'hours', 'open', 'closed', 'time', 'when', 'ساعات', 'مفتوح', 'مغلق', 'متى'
        ]
        
        services_patterns = [
            'service', 'what do you', 'offer', 'provide', 'خدمات', 'تقدمون', 'ماذا'
        ]
        
        # Check for time-related queries
        time_patterns = [
            'today', 'tomorrow', 'yesterday', 'اليوم', 'غداً', 'أمس', 'بكرة'
        ]
        
        # Determine intent with confidence scoring
        intents = []
        
        if any(pattern in message_lower for pattern in booking_patterns):
            intents.append(('booking', 0.9))
        
        if any(pattern in message_lower for pattern in pricing_patterns):
            intents.append(('pricing', 0.8))
        
        if any(pattern in message_lower for pattern in hours_patterns):
            intents.append(('hours', 0.8))
        
        if any(pattern in message_lower for pattern in services_patterns):
            intents.append(('services', 0.7))
        
        if any(pattern in message_lower for pattern in time_patterns):
            intents.append(('time_query', 0.9))
        
        # Return highest confidence intent
        if intents:
            primary_intent = max(intents, key=lambda x: x[1])
            return {
                'intent': primary_intent[0],
                'confidence': primary_intent[1],
                'all_intents': intents
            }
        
        return {
            'intent': 'general',
            'confidence': 0.5,
            'all_intents': []
        }
    
    def process_message(self, message: str, business_data: Dict[str, Any], conversation_id: str = "default") -> Dict[str, Any]:
        """
        Process customer message with intelligent AI response.
        """
        try:
            # Get conversation history
            conversation_history = self.conversation_contexts.get(conversation_id, [])
            
            # Detect intent
            intent_info = self.detect_intent(message, business_data)
            
            # Create intelligent prompt
            system_prompt = self.create_intelligent_prompt(business_data, conversation_history)
            
            # Add current message to history
            conversation_history.append({"role": "user", "content": message})
            
            if self.client:
                # Use real OpenAI API
                messages = [
                    {"role": "system", "content": system_prompt},
                    *conversation_history[-5:]  # Keep last 5 messages for context
                ]
                
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
                
            else:
                # Generate intelligent mock response
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
                'response': f"I apologize, but I'm experiencing technical difficulties. Please try again or contact us directly.",
                'intent': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def generate_mock_response(self, message: str, business_data: Dict[str, Any], intent_info: Dict[str, Any]) -> str:
        """
        Generate intelligent mock responses for testing without OpenAI API.
        """
        business_name = business_data.get('name', 'Business')
        time_info = self.get_saudi_time_info()
        intent = intent_info['intent']
        
        # Detect language
        is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
        
        if intent == 'booking':
            if is_arabic:
                return f"مرحباً بك في {business_name}! يمكنني مساعدتك في حجز موعد. نحن مفتوحون اليوم ({time_info['current_day_arabic']}) ولدينا مواعيد متاحة. ما الوقت المناسب لك؟"
            else:
                return f"Hello! Welcome to {business_name}. I can help you book an appointment. We're open today ({time_info['current_day_english']}) and have availability. What time works best for you?"
        
        elif intent == 'hours':
            if is_arabic:
                return f"نحن في {business_name} مفتوحون اليوم ({time_info['current_day_arabic']}) والوقت الحالي {time_info['current_time']}. ساعات عملنا هي من الأحد إلى الخميس من 8 صباحاً إلى 10 مساءً."
            else:
                return f"We at {business_name} are open today ({time_info['current_day_english']}) and it's currently {time_info['current_time']}. Our hours are Sunday to Thursday, 8 AM to 10 PM."
        
        elif intent == 'pricing':
            if is_arabic:
                return f"أسعارنا في {business_name} تنافسية جداً. الكشف العام 150 ريال، والتحاليل تبدأ من 80 ريال. هل تريد معرفة سعر خدمة معينة؟"
            else:
                return f"Our prices at {business_name} are very competitive. General consultation is 150 SAR, lab tests start from 80 SAR. Would you like to know about a specific service?"
        
        elif intent == 'services':
            if is_arabic:
                return f"نقدم في {business_name} خدمات طبية شاملة: الكشف العام، التحاليل الطبية، الأشعة، والاستشارات المتخصصة. كيف يمكنني مساعدتك؟"
            else:
                return f"At {business_name}, we offer comprehensive medical services: general consultations, lab tests, X-rays, and specialist consultations. How can I help you?"
        
        elif intent == 'time_query':
            if 'today' in message.lower() or 'اليوم' in message:
                if is_arabic:
                    return f"اليوم هو {time_info['formatted_date_arabic']} والوقت الحالي {time_info['current_time']}. نحن مفتوحون ومستعدون لخدمتك!"
                else:
                    return f"Today is {time_info['formatted_date_english']} and it's currently {time_info['current_time']}. We're open and ready to serve you!"
            
            elif 'tomorrow' in message.lower() or 'غداً' in message or 'بكرة' in message:
                if is_arabic:
                    return f"غداً هو {time_info['tomorrow_day_arabic']} ({time_info['tomorrow_date']}). يمكنك حجز موعد لغد إذا أردت!"
                else:
                    return f"Tomorrow is {time_info['tomorrow_day_english']} ({time_info['tomorrow_date']}). You can book an appointment for tomorrow if you'd like!"
        
        else:
            if is_arabic:
                return f"مرحباً بك في {business_name}! كيف يمكنني مساعدتك اليوم؟ يمكنني مساعدتك في حجز المواعيد، معرفة الأسعار، أو الإجابة على أي استفسارات."
            else:
                return f"Welcome to {business_name}! How can I help you today? I can assist with appointments, pricing information, or answer any questions you may have."
    
    def synthesize_speech(self, text: str, language: str = "auto") -> bytes:
        """
        Convert text to speech using ElevenLabs API.
        """
        if not self.elevenlabs_api_key:
            logger.warning("ElevenLabs API key not provided")
            return b""
        
        try:
            # This would integrate with ElevenLabs API
            # Implementation depends on ElevenLabs SDK
            logger.info(f"Synthesizing speech for text: {text[:50]}...")
            return b"mock_audio_data"
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return b""
    
    def clear_conversation_context(self, conversation_id: str = "default"):
        """Clear conversation history for a specific conversation."""
        if conversation_id in self.conversation_contexts:
            del self.conversation_contexts[conversation_id]

