import pytest
import json
from app import create_app, db
from models import Calculation

@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_calculator_basic_operations(client):
    """Test basic arithmetic operations"""
    # Test addition
    response = client.post('/api/calculator/calculate', 
                          json={'expression': '2 + 3'},
                          headers={'X-Session-ID': 'test-session-1'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['result'] == '5'
    
    # Test subtraction
    response = client.post('/api/calculator/calculate', 
                          json={'expression': '10 - 4'},
                          headers={'X-Session-ID': 'test-session-1'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['result'] == '6'
    
    # Test multiplication
    response = client.post('/api/calculator/calculate', 
                          json={'expression': '3 * 4'},
                          headers={'X-Session-ID': 'test-session-1'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['result'] == '12'
    
    # Test division
    response = client.post('/api/calculator/calculate', 
                          json={'expression': '15 / 3'},
                          headers={'X-Session-ID': 'test-session-1'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['result'] == '5'

def test_calculator_division_by_zero(client):
    """Test division by zero error handling"""
    response = client.post('/api/calculator/calculate', 
                          json={'expression': '10 / 0'},
                          headers={'X-Session-ID': 'test-session-2'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'Division by zero' in data['message']

def test_calculator_invalid_expression(client):
    """Test invalid expression handling"""
    response = client.post('/api/calculator/calculate', 
                          json={'expression': '2 + + 3'},
                          headers={'X-Session-ID': 'test-session-3'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'Invalid expression' in data['error']

def test_calculator_history_storage(client):
    """Test that calculations are stored in history"""
    # Perform a calculation
    client.post('/api/calculator/calculate', 
               json={'expression': '5 * 6'},
               headers={'X-Session-ID': 'test-session-4'})
    
    # Get history
    response = client.get('/api/history/',
                         headers={'X-Session-ID': 'test-session-4'})
    assert response.status_code == 200
    history = response.get_json()
    assert len(history) == 1
    assert history[0]['expression'] == '5 * 6'
    assert history[0]['result'] == '30'

def test_calculator_history_session_isolation(client):
    """Test that history is isolated between sessions"""
    # Create calculation in session 1
    client.post('/api/calculator/calculate', 
               json={'expression': '2 + 2'},
               headers={'X-Session-ID': 'session-1'})
    
    # Create calculation in session 2
    client.post('/api/calculator/calculate', 
               json={'expression': '3 + 3'},
               headers={'X-Session-ID': 'session-2'})
    
    # Check history for session 1
    response1 = client.get('/api/history/',
                          headers={'X-Session-ID': 'session-1'})
    history1 = response1.get_json()
    assert len(history1) == 1
    assert history1[0]['expression'] == '2 + 2'
    
    # Check history for session 2
    response2 = client.get('/api/history/',
                          headers={'X-Session-ID': 'session-2'})
    history2 = response2.get_json()
    assert len(history2) == 1
    assert history2[0]['expression'] == '3 + 3'

def test_calculator_decimal_operations(client):
    """Test decimal number operations"""
    response = client.post('/api/calculator/calculate', 
                          json={'expression': '2.5 + 1.5'},
                          headers={'X-Session-ID': 'test-session-5'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['result'] == '4'
    
    # Test that whole numbers return as integers
    response = client.post('/api/calculator/calculate', 
                          json={'expression': '4.0 / 2.0'},
                          headers={'X-Session-ID': 'test-session-5'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['result'] == '2'

def test_calculator_expression_validation(client):
    """Test expression validation endpoint"""
    # Valid expression
    response = client.post('/api/calculator/validate',
                          json={'expression': '10 + 5'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['is_valid'] is True
    
    # Invalid expression
    response = client.post('/api/calculator/validate',
                          json={'expression': '10 + + 5'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['is_valid'] is False

def test_calculator_clear_history(client):
    """Test clearing calculation history"""
    # Add some calculations
    client.post('/api/calculator/calculate', 
               json={'expression': '1 + 1'},
               headers={'X-Session-ID': 'clear-test-session'})
    client.post('/api/calculator/calculate', 
               json={'expression': '2 + 2'},
               headers={'X-Session-ID': 'clear-test-session'})
    
    # Verify history exists
    response = client.get('/api/history/',
                         headers={'X-Session-ID': 'clear-test-session'})
    history = response.get_json()
    assert len(history) == 2
    
    # Clear history
    response = client.post('/api/calculator/clear',
                          headers={'X-Session-ID': 'clear-test-session'})
    assert response.status_code == 200
    
    # Verify history is cleared
    response = client.get('/api/history/',
                         headers={'X-Session-ID': 'clear-test-session'})
    history = response.get_json()
    assert len(history) == 0

def test_api_root_endpoint(client):
    """Test the API root endpoint"""
    response = client.get('/api')
    assert response.status_code == 200
    data = response.get_json()
    assert 'name' in data
    assert 'Calculator API' in data['name']
    assert 'endpoints' in data