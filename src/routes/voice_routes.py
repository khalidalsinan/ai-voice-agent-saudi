from flask import Blueprint, request, jsonify
from src.models.voice_models import db, Business, Service, Customer, Appointment, CallLog
from src.services.voice_service import ConversationEngine, VoiceProcessor
import logging
from datetime import datetime, timedelta
import json

voice_bp = Blueprint('voice', __name__)
logger = logging.getLogger(__name__)

# Initialize services
conversation_engine = ConversationEngine()
voice_processor = VoiceProcessor()

@voice_bp.route('/voice/test', methods=['POST'])
def test_voice_processing():
    """Test voice processing without phone integration"""
    try:
        data = request.get_json()
        business_id = data.get('business_id')
        message = data.get('message', '')
        
        if not business_id or not message:
            return jsonify({"error": "business_id and message are required"}), 400
        
        # Get business configuration
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        business_config = {
            "name": business.name,
            "phone": business.phone,
            "ai_config": json.loads(business.ai_config) if business.ai_config else {}
        }
        
        # Process the message
        result = conversation_engine.process_message(
            business_id=str(business_id),
            message=message,
            business_config=business_config
        )
        
        return jsonify({
            "success": True,
            "business_name": business.name,
            "customer_message": message,
            "ai_response": result["response"],
            "intent": result["intent"],
            "requires_action": result["requires_action"]
        })
        
    except Exception as e:
        logger.error(f"Error in voice test: {str(e)}")
        return jsonify({"error": str(e)}), 500

@voice_bp.route('/voice/synthesize', methods=['POST'])
def synthesize_speech():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        voice_id = data.get('voice_id', 'pNInz6obpgDQGcFmaJgB')
        
        if not text:
            return jsonify({"error": "text is required"}), 400
        
        # Generate speech
        audio_data = voice_processor.synthesize_speech(text, voice_id)
        
        if audio_data:
            # In a real implementation, you'd return the audio file
            # For now, we'll just confirm the synthesis worked
            return jsonify({
                "success": True,
                "message": "Speech synthesized successfully",
                "text": text,
                "voice_id": voice_id,
                "audio_length": len(audio_data)
            })
        else:
            return jsonify({
                "success": False,
                "message": "Speech synthesis not available (API key not configured)",
                "text": text
            })
        
    except Exception as e:
        logger.error(f"Error in speech synthesis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@voice_bp.route('/voice/voices', methods=['GET'])
def get_available_voices():
    """Get available voices for speech synthesis"""
    try:
        voices = voice_processor.get_available_voices()
        return jsonify({
            "success": True,
            "voices": voices,
            "count": len(voices)
        })
        
    except Exception as e:
        logger.error(f"Error getting voices: {str(e)}")
        return jsonify({"error": str(e)}), 500

@voice_bp.route('/voice/conversation/<business_id>/summary', methods=['GET'])
def get_conversation_summary(business_id):
    """Get conversation summary for a business"""
    try:
        summary = conversation_engine.get_conversation_summary(business_id)
        return jsonify({
            "success": True,
            "business_id": business_id,
            "summary": summary
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation summary: {str(e)}")
        return jsonify({"error": str(e)}), 500

@voice_bp.route('/voice/conversation/<business_id>/clear', methods=['POST'])
def clear_conversation(business_id):
    """Clear conversation context for a business"""
    try:
        if business_id in conversation_engine.conversation_contexts:
            del conversation_engine.conversation_contexts[business_id]
        
        return jsonify({
            "success": True,
            "message": f"Conversation cleared for business {business_id}"
        })
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Twilio webhook endpoints (simplified for Heroku)
@voice_bp.route('/webhook/twilio/voice', methods=['POST'])
def twilio_voice_webhook():
    """Handle incoming Twilio voice calls"""
    try:
        # Get call information from Twilio
        from_number = request.form.get('From', '')
        to_number = request.form.get('To', '')
        call_sid = request.form.get('CallSid', '')
        
        logger.info(f"Incoming call: {from_number} -> {to_number} (SID: {call_sid})")
        
        # Find business by phone number
        business = Business.query.filter_by(phone=to_number).first()
        if not business:
            # Return TwiML for unknown number
            return '''<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="alice" language="en">Sorry, this number is not configured for AI assistance.</Say>
                <Hangup/>
            </Response>''', 200, {'Content-Type': 'text/xml'}
        
        # Create or find customer
        customer = Customer.query.filter_by(phone=from_number).first()
        if not customer:
            customer = Customer(
                phone=from_number,
                preferred_language='ar'  # Default to Arabic for Saudi numbers
            )
            db.session.add(customer)
            db.session.commit()
        
        # Create call log
        call_log = CallLog(
            business_id=business.id,
            customer_id=customer.id,
            call_sid=call_sid,
            from_number=from_number,
            to_number=to_number,
            direction='inbound',
            status='in-progress'
        )
        db.session.add(call_log)
        db.session.commit()
        
        # Return TwiML response
        business_name = business.name
        return f'''<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="alice" language="ar">مرحباً بك في {business_name}. مساعدي الذكي سيساعدك الآن.</Say>
            <Say voice="alice" language="en">Welcome to {business_name}. Our AI assistant will help you now.</Say>
            <Gather input="speech" action="/api/voice/webhook/twilio/process/{call_log.id}" method="POST" speechTimeout="3" language="ar-SA,en-US">
                <Say voice="alice" language="ar">كيف يمكنني مساعدتك اليوم؟</Say>
                <Say voice="alice" language="en">How can I help you today?</Say>
            </Gather>
        </Response>''', 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error in Twilio voice webhook: {str(e)}")
        return '''<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="alice" language="en">Sorry, we're experiencing technical difficulties.</Say>
            <Hangup/>
        </Response>''', 200, {'Content-Type': 'text/xml'}

@voice_bp.route('/webhook/twilio/process/<int:call_log_id>', methods=['POST'])
def process_twilio_speech(call_log_id):
    """Process speech input from Twilio"""
    try:
        # Get speech result from Twilio
        speech_result = request.form.get('SpeechResult', '')
        confidence = request.form.get('Confidence', '0')
        
        logger.info(f"Speech received for call {call_log_id}: {speech_result} (confidence: {confidence})")
        
        # Get call log and business
        call_log = CallLog.query.get(call_log_id)
        if not call_log:
            return '''<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="alice" language="en">Sorry, call not found.</Say>
                <Hangup/>
            </Response>''', 200, {'Content-Type': 'text/xml'}
        
        business = Business.query.get(call_log.business_id)
        if not business:
            return '''<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="alice" language="en">Sorry, business not found.</Say>
                <Hangup/>
            </Response>''', 200, {'Content-Type': 'text/xml'}
        
        # Process the speech with AI
        business_config = {
            "name": business.name,
            "phone": business.phone,
            "ai_config": json.loads(business.ai_config) if business.ai_config else {}
        }
        
        result = conversation_engine.process_message(
            business_id=str(business.id),
            message=speech_result,
            business_config=business_config
        )
        
        # Update call log
        call_log.transcript = (call_log.transcript or '') + f"\nCustomer: {speech_result}\nAI: {result['response']}"
        call_log.intent_detected = result['intent']['type']
        db.session.commit()
        
        # Generate TwiML response
        ai_response = result['response']
        
        # Determine if we need to continue the conversation
        if result['requires_action'] and result['intent']['type'] == 'booking':
            # For booking, gather more information
            return f'''<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="alice" language="ar">{ai_response}</Say>
                <Gather input="speech" action="/api/voice/webhook/twilio/process/{call_log_id}" method="POST" speechTimeout="5" language="ar-SA,en-US">
                    <Say voice="alice" language="ar">يرجى تحديد التاريخ والوقت المفضل لديك.</Say>
                </Gather>
            </Response>''', 200, {'Content-Type': 'text/xml'}
        else:
            # End the call with the response
            return f'''<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="alice" language="ar">{ai_response}</Say>
                <Say voice="alice" language="ar">شكراً لاتصالك بنا. نتطلع لخدمتك قريباً.</Say>
                <Say voice="alice" language="en">Thank you for calling. We look forward to serving you soon.</Say>
                <Hangup/>
            </Response>''', 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error processing Twilio speech: {str(e)}")
        return '''<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="alice" language="en">Sorry, we're experiencing technical difficulties.</Say>
            <Hangup/>
        </Response>''', 200, {'Content-Type': 'text/xml'}

@voice_bp.route('/webhook/twilio/status', methods=['POST'])
def twilio_status_webhook():
    """Handle Twilio call status updates"""
    try:
        call_sid = request.form.get('CallSid', '')
        call_status = request.form.get('CallStatus', '')
        call_duration = request.form.get('CallDuration', '0')
        
        logger.info(f"Call status update: {call_sid} -> {call_status} (duration: {call_duration})")
        
        # Update call log
        call_log = CallLog.query.filter_by(call_sid=call_sid).first()
        if call_log:
            call_log.status = call_status
            call_log.duration = int(call_duration) if call_duration.isdigit() else 0
            if call_status in ['completed', 'failed', 'busy', 'no-answer']:
                call_log.ended_at = datetime.utcnow()
                call_log.outcome = 'completed' if call_status == 'completed' else 'failed'
            db.session.commit()
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        logger.error(f"Error in Twilio status webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

