from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.services.voice_service import VoiceService
import os

business_bp = Blueprint('business', __name__)

voice_service = VoiceService(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    elevenlabs_api_key=os.getenv('ELEVENLABS_API_KEY')
)

# Simple business storage using User model for now
@business_bp.route('/businesses', methods=['GET'])
def get_businesses():
    try:
        # Use User model as temporary business storage
        businesses = User.query.all()
        return jsonify({
            'success': True,
            'businesses': [{
                'id': b.id,
                'name': b.username,  # Use username as business name
                'email': b.email
            } for b in businesses]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses', methods=['POST'])
def create_business():
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'success': False, 'error': 'Business name is required'}), 400
        
        # Create business using User model
        business = User(
            username=data['name'],
            email=data.get('email', f"{data['name'].lower().replace(' ', '')}@business.com")
        )
        
        db.session.add(business)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Business created successfully',
            'business': {
                'id': business.id,
                'name': business.username,
                'email': business.email
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/test-voice', methods=['POST'])
def test_voice_processing(business_id):
    try:
        business = User.query.get_or_404(business_id)
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        business_data = {
            'id': business.id,
            'name': business.username,
            'description': f"Welcome to {business.username}! We provide excellent services."
        }
        
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
