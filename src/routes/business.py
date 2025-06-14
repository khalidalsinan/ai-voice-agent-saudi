from flask import Blueprint, request, jsonify
from src.models.user import db, User
import os

business_bp = Blueprint('business', __name__)

@business_bp.route('/businesses', methods=['GET'])
def get_businesses():
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'businesses': [{
                'id': u.id,
                'name': u.username,
                'email': u.email
            } for u in users]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses', methods=['POST'])
def create_business():
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'success': False, 'error': 'Business name is required'}), 400
        
        user = User(
            username=data['name'],
            email=data.get('email', f"{data['name'].lower().replace(' ', '')}@test.com")
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Business created successfully',
            'business': {
                'id': user.id,
                'name': user.username,
                'email': user.email
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/test-voice', methods=['POST'])
def test_voice_processing(business_id):
    try:
        user = User.query.get_or_404(business_id)
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Simple mock response
        message = data['message']
        is_arabic = any(char in message for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')
        
        if is_arabic:
            response = f"مرحباً بك في {user.username}! كيف يمكنني مساعدتك؟"
        else:
            response = f"Hello! Welcome to {user.username}. How can I help you?"
        
        return jsonify({
            'success': True,
            'result': {
                'response': response,
                'intent': 'general',
                'business_name': user.username
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

