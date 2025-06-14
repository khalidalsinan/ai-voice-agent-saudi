import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self, openai_api_key=None, elevenlabs_api_key=None):
        self.openai_api_key = openai_api_key
        self.elevenlabs_api_key = elevenlabs_api_key
        self.conversation_contexts = {}
        
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
    
    def process_message(self, message, business_data, conversation_id="default"):
        try:
            business_name = business_data.get('name', 'Business')
            
            if self.client:
                # Use real OpenAI API
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant for {business_name}. Respond in the same language the customer uses (Arabic or English). Be professional and helpful."},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                ai_response = response.choices[0].message.content
            else:
                # Generate mock response
                is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
                if is_arabic:
                    ai_response = f"مرحباً بك في {business_name}! كيف يمكنني مساعدتك اليوم؟"
                else:
                    ai_response = f"Hello! Welcome to {business_name}. How can I help you today?"
            
            return {
                'response': ai_response,
                'intent': 'general',
                'confidence': 0.8,
                'business_name': business_name
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again.",
                'intent': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
