from flask import Blueprint, request, jsonify
from utils.calculator_core import Calculator
from utils.validators import validate_expression
from models import db
from models.calculation import Calculation
import uuid

calculator_bp = Blueprint('calculator', __name__)

@calculator_bp.route('/calculate', methods=['POST'])
def calculate():
    """Perform calculation"""
    try:
        data = request.get_json()
        expression = data.get('expression', '').strip()
        session_id = request.headers.get('X-Session-ID') or str(uuid.uuid4())
        
        # Validate expression
        if not validate_expression(expression):
            return jsonify({
                'error': 'Invalid expression',
                'message': 'Expression contains invalid characters or syntax'
            }), 400
        
        # Perform calculation
        calculator = Calculator()
        result = calculator.evaluate(expression)
        
        # Store in database
        calculation = Calculation(
            expression=expression,
            result=str(result),
            session_id=session_id
        )
        db.session.add(calculation)
        db.session.commit()
        
        return jsonify({
            'expression': expression,
            'result': result,
            'session_id': session_id
        })
        
    except ZeroDivisionError:
        return jsonify({
            'error': 'Division by zero',
            'message': 'Cannot divide by zero'
        }), 400
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid calculation',
            'message': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Calculation failed',
            'message': 'An unexpected error occurred'
        }), 500

@calculator_bp.route('/validate', methods=['POST'])
def validate_expression_route():
    """Validate expression without calculating"""
    data = request.get_json()
    expression = data.get('expression', '').strip()
    
    is_valid = validate_expression(expression)
    return jsonify({
        'expression': expression,
        'is_valid': is_valid
    })

@calculator_bp.route('/clear', methods=['POST'])
def clear_history():
    """Clear calculation history for session"""
    session_id = request.headers.get('X-Session-ID')
    if session_id:
        Calculation.query.filter_by(session_id=session_id).delete()
        db.session.commit()
    
    return jsonify({'message': 'History cleared successfully'})