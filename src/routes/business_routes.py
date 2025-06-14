from flask import Blueprint, request, jsonify, render_template_string
from src.models.voice_models import Business, Service, Customer, Appointment, CallLog
from src.services.voice_service import VoiceService
from src.models.user import db
import os
import json
from datetime import datetime

business_bp = Blueprint('business', __name__)

# Initialize voice service
voice_service = VoiceService(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    elevenlabs_api_key=os.getenv('ELEVENLABS_API_KEY')
)

@business_bp.route('/businesses', methods=['GET'])
def get_businesses():
    """Get all businesses."""
    try:
        businesses = Business.query.all()
        return jsonify({
            'success': True,
            'businesses': [{
                'id': b.id,
                'name': b.name,
                'description': getattr(b, 'description', ''),
                'created_at': getattr(b, 'created_at', None)
            } for b in businesses]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses', methods=['POST'])
def create_business():
    """Create a new business."""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'success': False, 'error': 'Business name is required'}), 400
        
        # Create business with only the fields that exist
        business = Business(name=data['name'])
        
        # Try to set description if the field exists
        if hasattr(Business, 'description') and 'description' in data:
            business.description = data['description']
        
        db.session.add(business)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Business created successfully',
            'business': {
                'id': business.id,
                'name': business.name
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/test-voice', methods=['POST'])
def test_voice_processing(business_id):
    """Test voice processing for a specific business."""
    try:
        business = Business.query.get_or_404(business_id)
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Prepare business data for voice service
        business_data = {
            'id': business.id,
            'name': business.name,
            'description': getattr(business, 'description', ''),
        }
        
        # Process the message
        result = voice_service.process_message(
            message=data['message'],
            business_data=business_data,
            conversation_id=f"test_{business_id}"
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
