from flask import Blueprint, request, jsonify
from src.models.voice_models import Business
from src.services.voice_service import VoiceService
from src.models.user import db
import os
from datetime import datetime

business_bp = Blueprint('business', __name__)

voice_service = VoiceService(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    elevenlabs_api_key=os.getenv('ELEVENLABS_API_KEY')
)

@business_bp.route('/businesses', methods=['GET'])
def get_businesses():
    try:
        businesses = Business.query.all()
        return jsonify({
            'success': True,
            'businesses': [{
                'id': b.id,
                'name': b.name,
                'phone': b.phone,
                'email': b.email,
                'description': b.description,
                'hours': b.hours,
                'created_at': b.created_at.isoformat() if b.created_at else None
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
        
        business = Business(
            name=data['name'],
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            description=data.get('description', ''),
            hours=data.get('hours', ''),
            created_at=datetime.utcnow()
        )
        
        db.session.add(business)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Business created successfully',
            'business': {
                'id': business.id,
                'name': business.name,
                'phone': business.phone,
                'email': business.email,
                'description': business.description,
                'hours': business.hours
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>', methods=['PUT'])
def update_business(business_id):
    try:
        business = Business.query.get_or_404(business_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        if 'name' in data:
            business.name = data['name']
        if 'phone' in data:
            business.phone = data['phone']
        if 'email' in data:
            business.email = data['email']
        if 'description' in data:
            business.description = data['description']
        if 'hours' in data:
            business.hours = data['hours']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Business updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/test-voice', methods=['POST'])
def test_voice_processing(business_id):
    try:
        business = Business.query.get_or_404(business_id)
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        business_data = {
            'id': business.id,
            'name': business.name,
            'description': business.description,
            'hours': business.hours,
            'phone': business.phone,
            'email': business.email
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
