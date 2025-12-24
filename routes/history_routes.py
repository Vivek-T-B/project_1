from flask import Blueprint, request, jsonify
from models import db
from models.calculation import Calculation

history_bp = Blueprint('history', __name__)

@history_bp.route('/', methods=['GET'])
def get_history():
    """Get calculation history for session"""
    session_id = request.headers.get('X-Session-ID')
    limit = request.args.get('limit', 50, type=int)
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    calculations = Calculation.query.filter_by(session_id=session_id)\
                                  .order_by(Calculation.timestamp.desc())\
                                  .limit(limit)\
                                  .all()
    
    return jsonify([calc.to_dict() for calc in calculations])

@history_bp.route('/<int:calc_id>', methods=['DELETE'])
def delete_calculation(calc_id):
    """Delete specific calculation from history"""
    calculation = Calculation.query.get(calc_id)
    if calculation:
        db.session.delete(calculation)
        db.session.commit()
        return jsonify({'message': 'Calculation deleted successfully'})
    
    return jsonify({'error': 'Calculation not found'}), 404