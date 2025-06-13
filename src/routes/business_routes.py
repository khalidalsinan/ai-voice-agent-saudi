from flask import Blueprint, request, jsonify
from src.models.voice_models import db, Business, Service, Customer, Appointment
import logging
from datetime import datetime, timedelta
import json

business_bp = Blueprint('business', __name__)
logger = logging.getLogger(__name__)

@business_bp.route('/businesses', methods=['GET'])
def get_businesses():
    """Get all businesses"""
    try:
        businesses = Business.query.all()
        return jsonify({
            "success": True,
            "businesses": [business.to_dict() for business in businesses],
            "count": len(businesses)
        })
    except Exception as e:
        logger.error(f"Error getting businesses: {str(e)}")
        return jsonify({"error": str(e)}), 500

@business_bp.route('/businesses', methods=['POST'])
def create_business():
    """Create a new business"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Business name is required"}), 400
        
        # Create business
        business = Business(
            name=data['name'],
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            description=data.get('description', ''),
            business_hours=json.dumps(data.get('business_hours', {
                "sunday": {"open": "09:00", "close": "17:00"},
                "monday": {"open": "09:00", "close": "17:00"},
                "tuesday": {"open": "09:00", "close": "17:00"},
                "wednesday": {"open": "09:00", "close": "17:00"},
                "thursday": {"open": "09:00", "close": "17:00"},
                "friday": {"open": "14:00", "close": "18:00"},
                "saturday": {"open": "09:00", "close": "13:00"}
            })),
            ai_config=json.dumps(data.get('ai_config', {
                "language_preference": "both",
                "voice_id": "pNInz6obpgDQGcFmaJgB",
                "greeting_message": "Welcome! How can I help you today?"
            }))
        )
        
        db.session.add(business)
        db.session.commit()
        
        # Create default services
        default_services = [
            {"name": "General Consultation", "price": 150, "duration_minutes": 30},
            {"name": "Basic Treatment", "price": 200, "duration_minutes": 45},
            {"name": "Specialized Care", "price": 300, "duration_minutes": 60}
        ]
        
        for service_data in default_services:
            service = Service(
                business_id=business.id,
                name=service_data["name"],
                price=service_data["price"],
                duration_minutes=service_data["duration_minutes"],
                description=f"{service_data['name']} service"
            )
            db.session.add(service)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "business": business.to_dict(),
            "message": "Business created successfully with default services"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating business: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@business_bp.route('/businesses/<int:business_id>', methods=['GET'])
def get_business(business_id):
    """Get a specific business"""
    try:
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        return jsonify({
            "success": True,
            "business": business.to_dict()
        })
    except Exception as e:
        logger.error(f"Error getting business: {str(e)}")
        return jsonify({"error": str(e)}), 500

@business_bp.route('/businesses/<int:business_id>', methods=['PUT'])
def update_business(business_id):
    """Update a business"""
    try:
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            business.name = data['name']
        if 'phone' in data:
            business.phone = data['phone']
        if 'email' in data:
            business.email = data['email']
        if 'description' in data:
            business.description = data['description']
        if 'business_hours' in data:
            business.business_hours = json.dumps(data['business_hours'])
        if 'ai_config' in data:
            business.ai_config = json.dumps(data['ai_config'])
        
        business.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "business": business.to_dict(),
            "message": "Business updated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error updating business: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/services', methods=['GET'])
def get_business_services(business_id):
    """Get services for a business"""
    try:
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        services = Service.query.filter_by(business_id=business_id, is_active=True).all()
        
        return jsonify({
            "success": True,
            "business_id": business_id,
            "services": [service.to_dict() for service in services],
            "count": len(services)
        })
    except Exception as e:
        logger.error(f"Error getting business services: {str(e)}")
        return jsonify({"error": str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/services', methods=['POST'])
def create_service(business_id):
    """Create a new service for a business"""
    try:
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({"error": "Service name is required"}), 400
        
        service = Service(
            business_id=business_id,
            name=data['name'],
            description=data.get('description', ''),
            price=float(data.get('price', 0)),
            duration_minutes=int(data.get('duration_minutes', 30))
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "service": service.to_dict(),
            "message": "Service created successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating service: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/appointments', methods=['GET'])
def get_business_appointments(business_id):
    """Get appointments for a business"""
    try:
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        
        # Build query
        query = Appointment.query.filter_by(business_id=business_id)
        
        if start_date:
            query = query.filter(Appointment.appointment_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Appointment.appointment_date <= datetime.fromisoformat(end_date))
        if status:
            query = query.filter(Appointment.status == status)
        
        appointments = query.order_by(Appointment.appointment_date.desc()).all()
        
        return jsonify({
            "success": True,
            "business_id": business_id,
            "appointments": [appointment.to_dict() for appointment in appointments],
            "count": len(appointments)
        })
    except Exception as e:
        logger.error(f"Error getting business appointments: {str(e)}")
        return jsonify({"error": str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/appointments', methods=['POST'])
def create_appointment(business_id):
    """Create a new appointment"""
    try:
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('customer_phone'):
            return jsonify({"error": "Customer phone is required"}), 400
        if not data.get('appointment_date'):
            return jsonify({"error": "Appointment date is required"}), 400
        
        # Find or create customer
        customer = Customer.query.filter_by(phone=data['customer_phone']).first()
        if not customer:
            customer = Customer(
                name=data.get('customer_name', ''),
                phone=data['customer_phone'],
                email=data.get('customer_email', ''),
                preferred_language=data.get('preferred_language', 'ar')
            )
            db.session.add(customer)
            db.session.flush()  # Get customer ID
        
        # Create appointment
        appointment = Appointment(
            business_id=business_id,
            customer_id=customer.id,
            service_id=data.get('service_id'),
            appointment_date=datetime.fromisoformat(data['appointment_date']),
            duration_minutes=int(data.get('duration_minutes', 30)),
            notes=data.get('notes', ''),
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "appointment": appointment.to_dict(),
            "message": "Appointment created successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@business_bp.route('/businesses/<int:business_id>/analytics', methods=['GET'])
def get_business_analytics(business_id):
    """Get analytics for a business"""
    try:
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # Get appointments count
        total_appointments = Appointment.query.filter_by(business_id=business_id).count()
        recent_appointments = Appointment.query.filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= start_date
        ).count()
        
        # Get call logs count
        from src.models.voice_models import CallLog
        total_calls = CallLog.query.filter_by(business_id=business_id).count()
        recent_calls = CallLog.query.filter(
            CallLog.business_id == business_id,
            CallLog.started_at >= start_date
        ).count()
        
        # Get services count
        active_services = Service.query.filter_by(business_id=business_id, is_active=True).count()
        
        return jsonify({
            "success": True,
            "business_id": business_id,
            "analytics": {
                "total_appointments": total_appointments,
                "recent_appointments": recent_appointments,
                "total_calls": total_calls,
                "recent_calls": recent_calls,
                "active_services": active_services,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
        })
    except Exception as e:
        logger.error(f"Error getting business analytics: {str(e)}")
        return jsonify({"error": str(e)}), 500

