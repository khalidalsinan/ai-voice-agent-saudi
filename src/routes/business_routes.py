from flask import Blueprint, request, jsonify, render_template_string
from src.models.voice_models import Business, Service, Customer, Appointment, CallLog, Conversation
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
    """Create a new business."""
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
                'hours': business.hours,
                'created_at': business.created_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>', methods=['GET'])
def get_business(business_id):
    """Get a specific business by ID."""
    try:
        business = Business.query.get_or_404(business_id)
        
        # Get services for this business
        services = Service.query.filter_by(business_id=business_id).all()
        
        return jsonify({
            'success': True,
            'business': {
                'id': business.id,
                'name': business.name,
                'phone': business.phone,
                'email': business.email,
                'description': business.description,
                'hours': business.hours,
                'created_at': business.created_at.isoformat() if business.created_at else None,
                'services': [{
                    'id': s.id,
                    'name': s.name,
                    'description': s.description,
                    'price': float(s.price) if s.price else 0,
                    'duration': s.duration
                } for s in services]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>', methods=['PUT'])
def update_business(business_id):
    """Update a business."""
    try:
        business = Business.query.get_or_404(business_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Update business fields
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
        
        business.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Business updated successfully',
            'business': {
                'id': business.id,
                'name': business.name,
                'phone': business.phone,
                'email': business.email,
                'description': business.description,
                'hours': business.hours,
                'created_at': business.created_at.isoformat() if business.created_at else None,
                'updated_at': business.updated_at.isoformat() if business.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>', methods=['DELETE'])
def delete_business(business_id):
    """Delete a business."""
    try:
        business = Business.query.get_or_404(business_id)
        
        # Delete related services first
        Service.query.filter_by(business_id=business_id).delete()
        
        # Delete the business
        db.session.delete(business)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Business deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/services', methods=['GET'])
def get_business_services(business_id):
    """Get all services for a business."""
    try:
        business = Business.query.get_or_404(business_id)
        services = Service.query.filter_by(business_id=business_id).all()
        
        return jsonify({
            'success': True,
            'business_name': business.name,
            'services': [{
                'id': s.id,
                'name': s.name,
                'description': s.description,
                'price': float(s.price) if s.price else 0,
                'duration': s.duration,
                'created_at': s.created_at.isoformat() if s.created_at else None
            } for s in services]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/services', methods=['POST'])
def create_service(business_id):
    """Create a new service for a business."""
    try:
        business = Business.query.get_or_404(business_id)
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'success': False, 'error': 'Service name is required'}), 400
        
        service = Service(
            business_id=business_id,
            name=data['name'],
            description=data.get('description', ''),
            price=float(data.get('price', 0)) if data.get('price') else 0,
            duration=int(data.get('duration', 30)) if data.get('duration') else 30,
            created_at=datetime.utcnow()
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Service created successfully',
            'service': {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'price': float(service.price),
                'duration': service.duration,
                'created_at': service.created_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/services/<int:service_id>', methods=['PUT'])
def update_service(business_id, service_id):
    """Update a service."""
    try:
        service = Service.query.filter_by(id=service_id, business_id=business_id).first_or_404()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Update service fields
        if 'name' in data:
            service.name = data['name']
        if 'description' in data:
            service.description = data['description']
        if 'price' in data:
            service.price = float(data['price']) if data['price'] else 0
        if 'duration' in data:
            service.duration = int(data['duration']) if data['duration'] else 30
        
        service.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Service updated successfully',
            'service': {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'price': float(service.price),
                'duration': service.duration,
                'updated_at': service.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/services/<int:service_id>', methods=['DELETE'])
def delete_service(business_id, service_id):
    """Delete a service."""
    try:
        service = Service.query.filter_by(id=service_id, business_id=business_id).first_or_404()
        
        db.session.delete(service)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Service deleted successfully'
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
            'description': business.description,
            'hours': business.hours,
            'phone': business.phone,
            'email': business.email
        }
        
        # Get services for context
        services = Service.query.filter_by(business_id=business_id).all()
        if services:
            services_text = ", ".join([f"{s.name} ({s.price} SAR)" for s in services])
            business_data['services'] = services_text
        
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

@business_bp.route('/businesses/<int:business_id>/analytics', methods=['GET'])
def get_business_analytics(business_id):
    """Get analytics for a specific business."""
    try:
        business = Business.query.get_or_404(business_id)
        
        # Get call logs
        call_logs = CallLog.query.filter_by(business_id=business_id).all()
        
        # Get appointments
        appointments = Appointment.query.filter_by(business_id=business_id).all()
        
        # Calculate basic analytics
        total_calls = len(call_logs)
        total_appointments = len(appointments)
        
        # Get recent activity
        recent_calls = CallLog.query.filter_by(business_id=business_id)\
                                  .order_by(CallLog.created_at.desc())\
                                  .limit(10).all()
        
        return jsonify({
            'success': True,
            'analytics': {
                'business_name': business.name,
                'total_calls': total_calls,
                'total_appointments': total_appointments,
                'conversion_rate': (total_appointments / total_calls * 100) if total_calls > 0 else 0,
                'recent_calls': [{
                    'id': call.id,
                    'customer_phone': call.customer_phone,
                    'duration': call.duration,
                    'status': call.status,
                    'created_at': call.created_at.isoformat() if call.created_at else None
                } for call in recent_calls]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

