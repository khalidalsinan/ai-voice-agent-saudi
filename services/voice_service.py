import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from elevenlabs import ElevenLabs
import asyncio

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """Simplified voice processing for Heroku deployment"""
    
    def __init__(self):
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        self.client = None
        
        if self.elevenlabs_key and self.elevenlabs_key != "demo_key_placeholder":
            try:
                self.client = ElevenLabs(api_key=self.elevenlabs_key)
                logger.info("ElevenLabs client initialized successfully")
            except Exception as e:
                logger.warning(f"ElevenLabs initialization failed: {str(e)}")
                self.client = None
        else:
            logger.warning("ElevenLabs API key not configured - using mock responses")
    
    def synthesize_speech(self, text: str, voice_id: str = "pNInz6obpgDQGcFmaJgB") -> Optional[bytes]:
        """Convert text to speech using ElevenLabs"""
        try:
            if not self.client:
                logger.warning("ElevenLabs not configured - returning None for speech synthesis")
                return None
            
            # Generate speech
            audio = self.client.generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2"
            )
            
            return b''.join(audio)
            
        except Exception as e:
            logger.error(f"Speech synthesis error: {str(e)}")
            return None
    
    def get_available_voices(self) -> list:
        """Get available voices from ElevenLabs"""
        try:
            if not self.client:
                return [
                    {"voice_id": "demo_voice_1", "name": "Demo Arabic Voice"},
                    {"voice_id": "demo_voice_2", "name": "Demo English Voice"}
                ]
            
            voices = self.client.voices.get_all()
            return [{"voice_id": voice.voice_id, "name": voice.name} for voice in voices.voices]
            
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return []

class ConversationEngine:
    """Simplified conversation engine for Heroku deployment"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.openai_key and self.openai_key != "demo_key_placeholder":
            try:
                self.client = OpenAI(api_key=self.openai_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {str(e)}")
                self.client = None
        else:
            logger.warning("OpenAI API key not configured - using mock responses")
        
        self.conversation_contexts = {}
    
    def process_message(self, business_id: str, message: str, business_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process customer message and generate response"""
        try:
            # Get or create conversation context
            if business_id not in self.conversation_contexts:
                self.conversation_contexts[business_id] = {
                    "messages": [],
                    "business_config": business_config,
                    "intent_history": []
                }
            
            context = self.conversation_contexts[business_id]
            
            # Add customer message to context
            context["messages"].append({
                "role": "user",
                "content": message
            })
            
            # Generate response
            if not self.client:
                # Use mock response for testing
                ai_response = self._generate_mock_response(message, business_config)
            else:
                # Use OpenAI for real conversation
                ai_response = self._generate_ai_response(context, business_config)
            
            # Add AI response to context
            context["messages"].append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Analyze intent
            intent = self._analyze_intent(message, ai_response)
            context["intent_history"].append(intent)
            
            return {
                "response": ai_response,
                "intent": intent,
                "requires_action": intent.get("action_required", False)
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please hold while I connect you to a human agent.",
                "intent": {"type": "error", "action_required": True},
                "requires_action": True
            }
    
    def _generate_ai_response(self, context: Dict[str, Any], business_config: Dict[str, Any]) -> str:
        """Generate AI response using OpenAI"""
        try:
            business_name = business_config.get("name", "Business")
            
            system_prompt = f"""You are a helpful AI assistant for {business_name}, a business in Saudi Arabia. 
            You can communicate in both Arabic and English. Your role is to:
            
            1. Answer questions about services, pricing, and business hours
            2. Help customers book appointments
            3. Provide helpful information about the business
            4. Be polite, professional, and culturally appropriate
            
            Business Information:
            - Name: {business_name}
            - Services: General consultation, treatments, and specialized care
            - Hours: Sunday-Thursday 9AM-5PM, Friday 2PM-6PM, Saturday 9AM-1PM
            - Pricing: Consultation 150 SAR, Basic treatment 200 SAR, Specialized care 300 SAR
            
            Always be helpful and try to assist the customer with their needs."""
            
            messages = [
                {"role": "system", "content": system_prompt}
            ] + context["messages"]
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._generate_mock_response(context["messages"][-1]["content"], business_config)
    
    def _generate_mock_response(self, message: str, business_config: Dict[str, Any]) -> str:
        """Generate mock response for testing without OpenAI"""
        business_name = business_config.get("name", "Business")
        message_lower = message.lower()
        
        # Arabic greeting detection
        if any(word in message_lower for word in ["مرحبا", "السلام", "أهلا", "صباح", "مساء"]):
            return f"مرحباً بك في {business_name}! كيف يمكنني مساعدتك اليوم؟"
        
        # English greeting
        elif any(word in message_lower for word in ["hello", "hi", "good morning", "good afternoon", "good evening"]):
            return f"Hello! Welcome to {business_name}. How can I help you today?"
        
        # Service inquiry
        elif any(word in message_lower for word in ["service", "services", "خدمة", "خدمات", "what do you offer"]):
            return f"We offer several services at {business_name}:\n- General consultation (150 SAR)\n- Basic treatment (200 SAR)\n- Specialized care (300 SAR)\n\nWould you like to know more about any specific service or book an appointment?"
        
        # Pricing inquiry
        elif any(word in message_lower for word in ["price", "cost", "how much", "سعر", "كم", "تكلفة", "pricing"]):
            return "Our current pricing is:\n- Consultation: 150 SAR\n- Basic treatment: 200 SAR\n- Specialized care: 300 SAR\n\nWould you like to book an appointment?"
        
        # Booking inquiry
        elif any(word in message_lower for word in ["book", "appointment", "schedule", "حجز", "موعد", "reserve"]):
            return "I'd be happy to help you book an appointment! What service would you like to schedule, and what date and time work best for you? We're available:\n- Sunday-Thursday: 9 AM to 5 PM\n- Friday: 2 PM to 6 PM\n- Saturday: 9 AM to 1 PM"
        
        # Hours inquiry
        elif any(word in message_lower for word in ["hours", "open", "close", "time", "ساعات", "مفتوح", "وقت", "when"]):
            return f"Our business hours are:\n- Sunday to Thursday: 9 AM to 5 PM\n- Friday: 2 PM to 6 PM\n- Saturday: 9 AM to 1 PM\n\nWhen would you like to visit {business_name}?"
        
        # Location inquiry
        elif any(word in message_lower for word in ["where", "location", "address", "أين", "موقع", "عنوان"]):
            return f"We're located in Riyadh, Saudi Arabia. For the exact address and directions, please call us or visit our website. Would you like to book an appointment?"
        
        # Default response
        else:
            return f"Thank you for contacting {business_name}. I'm here to help with:\n- Information about our services and pricing\n- Booking appointments\n- Business hours and location\n- Any other questions you may have\n\nHow can I assist you today?"
    
    def _analyze_intent(self, customer_message: str, ai_response: str) -> Dict[str, Any]:
        """Analyze customer intent from the conversation"""
        message_lower = customer_message.lower()
        
        # Booking intent
        if any(word in message_lower for word in ["book", "appointment", "schedule", "حجز", "موعد", "reserve"]):
            return {
                "type": "booking",
                "confidence": 0.9,
                "action_required": True,
                "extracted_info": {
                    "service_requested": "general",
                    "urgency": "normal"
                }
            }
        
        # Pricing intent
        elif any(word in message_lower for word in ["price", "cost", "how much", "سعر", "كم", "تكلفة"]):
            return {
                "type": "pricing_inquiry",
                "confidence": 0.8,
                "action_required": False,
                "extracted_info": {
                    "service_interest": "general"
                }
            }
        
        # Hours intent
        elif any(word in message_lower for word in ["hours", "open", "close", "time", "ساعات", "مفتوح", "وقت"]):
            return {
                "type": "hours_inquiry",
                "confidence": 0.8,
                "action_required": False
            }
        
        # Service inquiry
        elif any(word in message_lower for word in ["service", "services", "خدمة", "خدمات", "what do you offer"]):
            return {
                "type": "service_inquiry",
                "confidence": 0.7,
                "action_required": False
            }
        
        # Greeting
        elif any(word in message_lower for word in ["hello", "hi", "مرحبا", "السلام", "أهلا"]):
            return {
                "type": "greeting",
                "confidence": 0.9,
                "action_required": False
            }
        
        # Default
        else:
            return {
                "type": "general_inquiry",
                "confidence": 0.5,
                "action_required": False
            }
    
    def get_conversation_summary(self, business_id: str) -> Dict[str, Any]:
        """Get conversation summary"""
        if business_id not in self.conversation_contexts:
            return {"summary": "No conversation found", "outcome": "unknown"}
        
        context = self.conversation_contexts[business_id]
        intents = context.get("intent_history", [])
        
        # Determine primary intent and outcome
        if any(intent["type"] == "booking" for intent in intents):
            outcome = "appointment_requested"
        elif any(intent["type"] == "pricing_inquiry" for intent in intents):
            outcome = "pricing_provided"
        elif any(intent["type"] == "service_inquiry" for intent in intents):
            outcome = "service_info_provided"
        else:
            outcome = "general_inquiry"
        
        return {
            "summary": f"Customer conversation with {len(context['messages'])} messages",
            "outcome": outcome,
            "intents_detected": [intent["type"] for intent in intents],
            "total_messages": len(context["messages"])
        }

