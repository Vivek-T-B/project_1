# Calculator App Architecture Specification

## Overview
A comprehensive Flask-based calculator application with modern web interface, supporting basic arithmetic operations, calculation history, keyboard input, and responsive design.

## Project Structure
```
project_1/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                      # Project documentation
├── tests/                         # Test suite
│   ├── test_api.py               # API endpoint tests
│   ├── test_calculator.py        # Calculator logic tests
│   └── test_ui.py                # Frontend component tests
├── static/                        # Static assets
│   ├── css/
│   │   ├── calculator.css        # Main calculator styles
│   │   └── responsive.css        # Mobile/tablet responsive styles
│   ├── js/
│   │   ├── calculator.js         # Calculator logic and UI interaction
│   │   ├── keyboard-handler.js   # Keyboard input handling
│   │   └── history-manager.js    # History panel management
│   └── fonts/                    # Web fonts
├── templates/                     # HTML templates
│   ├── base.html                 # Base template
│   ├── calculator.html           # Main calculator interface
│   └── history.html              # History view component
├── models/                       # Database models
│   ├── __init__.py
│   ├── calculation.py            # Calculation model
│   └── user_session.py           # User session model
├── routes/                       # Flask route handlers
│   ├── __init__.py
│   ├── calculator_routes.py      # Calculator operation routes
│   └── history_routes.py         # History management routes
├── utils/                        # Utility functions
│   ├── __init__.py
│   ├── calculator_core.py        # Core calculation logic
│   ├── validators.py             # Input validation functions
│   └── error_handlers.py         # Error handling utilities
└── config.py                     # Application configuration
```

## Backend Architecture

### Flask Application Structure

#### Main Application (app.py)
```python
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Calculation
from routes.calculator_routes import calculator_bp
from routes.history_routes import history_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(calculator_bp, url_prefix='/api/calculator')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500
```

#### Database Models

**models/calculation.py**
```python
from datetime import datetime
from models import db

class Calculation(db.Model):
    __tablename__ = 'calculations'
    
    id = db.Column(db.Integer, primary_key=True)
    expression = db.Column(db.String(500), nullable=False)
    result = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100), nullable=False)
    error_message = db.Column(db.String(200), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'expression': self.expression,
            'result': self.result,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'error_message': self.error_message
        }
```

**models/user_session.py**
```python
from datetime import datetime, timedelta
import uuid

class UserSession:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.is_active = True
    
    def update_activity(self):
        self.last_activity = datetime.utcnow()
    
    def is_expired(self, timeout_minutes=30):
        return datetime.utcnow() - self.last_activity > timedelta(minutes=timeout_minutes)
```

#### API Routes

**routes/calculator_routes.py**
```python
from flask import Blueprint, request, jsonify
from utils.calculator_core import Calculator
from utils.validators import validate_expression
from models import Calculation, db
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
```

**routes/history_routes.py**
```python
from flask import Blueprint, request, jsonify
from models import Calculation, db

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
```

#### Core Calculation Logic

**utils/calculator_core.py**
```python
import re
import operator
from typing import Union

class Calculator:
    def __init__(self):
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }
    
    def evaluate(self, expression: str) -> Union[float, int]:
        """Evaluate mathematical expression"""
        # Remove whitespace
        expression = expression.replace(' ', '')
        
        # Basic validation
        if not expression:
            raise ValueError("Empty expression")
        
        # Handle simple expressions (number operator number)
        pattern = r'^(\d*\.?\d+)\s*([+\-*/])\s*(\d*\.?\d+)$'
        match = re.match(pattern, expression)
        
        if match:
            left_operand = float(match.group(1))
            operator_symbol = match.group(2)
            right_operand = float(match.group(3))
            
            if operator_symbol not in self.operators:
                raise ValueError(f"Unsupported operator: {operator_symbol}")
            
            if operator_symbol == '/' and right_operand == 0:
                raise ZeroDivisionError("Division by zero")
            
            result = self.operators[operator_symbol](left_operand, right_operand)
            
            # Return int if result is whole number
            return int(result) if result.is_integer() else round(result, 10)
        
        # For more complex expressions, use safe evaluation
        return self._safe_eval(expression)
    
    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate expression using restricted evaluation"""
        # Only allow numbers, basic operators, and parentheses
        if not re.match(r'^[\d+\-*/.()\s]+$', expression):
            raise ValueError("Expression contains invalid characters")
        
        # Replace operator symbols with lambda functions
        # This is a simplified approach - in production, use a proper expression parser
        try:
            # Use eval with restricted locals (still not recommended for production)
            allowed_globals = {"__builtins__": {}}
            return eval(expression, allowed_globals, {})
        except:
            raise ValueError("Invalid expression format")
```

#### Input Validation

**utils/validators.py**
```python
import re

def validate_expression(expression: str) -> bool:
    """Validate calculator expression"""
    if not expression or not isinstance(expression, str):
        return False
    
    # Remove whitespace
    expression = expression.strip()
    
    # Check for valid characters (numbers, operators, decimal points, parentheses)
    if not re.match(r'^[\d+\-*/.()\s]+$', expression):
        return False
    
    # Basic syntax validation
    if _has_invalid_syntax(expression):
        return False
    
    return True

def _has_invalid_syntax(expression: str) -> bool:
    """Check for basic syntax errors"""
    # Remove spaces
    expression = expression.replace(' ', '')
    
    # Check for consecutive operators (except negative numbers)
    operator_pattern = r'[+\*/]{2,}|--+(?!\d)|-{2,}(?=\d)'
    if re.search(operator_pattern, expression):
        return True
    
    # Check for operators at start/end (except negative at start)
    if expression[0] in '+*/' or expression[-1] in '+*/-':
        return True
    
    # Check for multiple decimal points in numbers
    decimal_pattern = r'\d*\.\d*\.\d*'
    if re.search(decimal_pattern, expression):
        return True
    
    # Check for unmatched parentheses
    if expression.count('(') != expression.count(')'):
        return True
    
    return False

def sanitize_expression(expression: str) -> str:
    """Sanitize expression for safe processing"""
    # Remove potentially dangerous characters
    expression = re.sub(r'[^0-9+\-*/.()\s]', '', expression)
    return expression.strip()
```

## Frontend Architecture

### HTML Structure

**templates/base.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Calculator App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/calculator.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/responsive.css') }}">
    {% block head %}{% endblock %}
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    {% block scripts %}{% endblock %}
</body>
</html>
```

**templates/calculator.html**
```html
{% extends "base.html" %}

{% block title %}Calculator{% endblock %}

{% block content %}
<div class="calculator-app">
    <header class="app-header">
        <h1>Calculator</h1>
        <div class="session-info">
            <span id="session-status" class="session-status">Connected</span>
        </div>
    </header>
    
    <div class="calculator-container">
        <!-- Main Calculator Display -->
        <div class="calculator">
            <div class="display">
                <div class="previous-operand" id="previous-operand"></div>
                <div class="current-operand" id="current-operand">0</div>
            </div>
            
            <div class="buttons-grid">
                <button class="btn btn-clear" data-action="clear">C</button>
                <button class="btn btn-clear" data-action="clear-entry">CE</button>
                <button class="btn btn-operator" data-action="backspace">⌫</button>
                <button class="btn btn-operator" data-operator="/">÷</button>
                
                <button class="btn" data-number="7">7</button>
                <button class="btn" data-number="8">8</button>
                <button class="btn" data-number="9">9</button>
                <button class="btn btn-operator" data-operator="*">×</button>
                
                <button class="btn" data-number="4">4</button>
                <button class="btn" data-number="5">5</button>
                <button class="btn" data-number="6">6</button>
                <button class="btn btn-operator" data-operator="-">-</button>
                
                <button class="btn" data-number="1">1</button>
                <button class="btn" data-number="2">2</button>
                <button class="btn" data-number="3">3</button>
                <button class="btn btn-operator" data-operator="+">+</button>
                
                <button class="btn btn-zero" data-number="0">0</button>
                <button class="btn" data-action="decimal">.</button>
                <button class="btn btn-equals" data-action="calculate">=</button>
            </div>
        </div>
        
        <!-- History Panel -->
        <div class="history-panel">
            <div class="history-header">
                <h3>History</h3>
                <button class="btn btn-small" data-action="clear-history">Clear</button>
            </div>
            <div class="history-list" id="history-list">
                <!-- History items will be populated here -->
            </div>
        </div>
    </div>
    
    <!-- Error Display -->
    <div class="error-display" id="error-display" style="display: none;">
        <span id="error-message"></span>
        <button class="btn btn-small" data-action="dismiss-error">×</button>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/keyboard-handler.js') }}"></script>
<script src="{{ url_for('static', filename='js/history-manager.js') }}"></script>
<script src="{{ url_for('static', filename='js/calculator.js') }}"></script>
{% endblock %}
```

### CSS Styling

**static/css/calculator.css**
```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #34495e;
    --accent-color: #3498db;
    --success-color: #27ae60;
    --error-color: #e74c3c;
    --warning-color: #f39c12;
    --background-color: #ecf0f1;
    --button-color: #bdc3c7;
    --button-hover-color: #95a5a6;
    --text-color: #2c3e50;
    --border-radius: 8px;
    --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-color);
}

.container {
    max-width: 1200px;
    width: 100%;
    padding: 20px;
}

.calculator-app {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    overflow: hidden;
}

.app-header {
    background: var(--primary-color);
    color: white;
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.app-header h1 {
    font-size: 1.5rem;
    font-weight: 600;
}

.session-status {
    background: var(--success-color);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
}

.calculator-container {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 20px;
    padding: 20px;
}

/* Calculator Display */
.display {
    background: var(--secondary-color);
    color: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: var(--border-radius);
    text-align: right;
    min-height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.previous-operand {
    font-size: 1rem;
    opacity: 0.7;
    margin-bottom: 5px;
}

.current-operand {
    font-size: 2rem;
    font-weight: 600;
    word-wrap: break-word;
    word-break: break-all;
}

/* Calculator Buttons */
.buttons-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

.btn {
    background: var(--button-color);
    border: none;
    border-radius: var(--border-radius);
    padding: 20px;
    font-size: 1.2rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    user-select: none;
}

.btn:hover {
    background: var(--button-hover-color);
    transform: translateY(-2px);
}

.btn:active {
    transform: translateY(0);
}

.btn-clear {
    background: var(--warning-color);
    color: white;
}

.btn-operator {
    background: var(--accent-color);
    color: white;
}

.btn-equals {
    background: var(--success-color);
    color: white;
}

.btn-zero {
    grid-column: span 2;
}

.btn-small {
    padding: 8px 12px;
    font-size: 0.9rem;
}

/* History Panel */
.history-panel {
    background: var(--background-color);
    border-radius: var(--border-radius);
    padding: 20px;
}

.history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--button-color);
}

.history-header h3 {
    color: var(--primary-color);
}

.history-list {
    max-height: 400px;
    overflow-y: auto;
}

.history-item {
    background: white;
    padding: 10px;
    margin-bottom: 8px;
    border-radius: 4px;
    border-left: 4px solid var(--accent-color);
    cursor: pointer;
    transition: all 0.2s ease;
}

.history-item:hover {
    background: #f8f9fa;
    transform: translateX(4px);
}

.history-expression {
    font-size: 0.9rem;
    color: var(--secondary-color);
    margin-bottom: 4px;
}

.history-result {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--primary-color);
}

.history-time {
    font-size: 0.7rem;
    color: #7f8c8d;
    text-align: right;
    margin-top: 4px;
}

/* Error Display */
.error-display {
    background: var(--error-color);
    color: white;
    padding: 15px;
    margin: 20px;
    border-radius: var(--border-radius);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.error-display button {
    background: transparent;
    border: 1px solid white;
    color: white;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .calculator-container {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .history-panel {
        order: -1;
    }
    
    .btn {
        padding: 15px;
        font-size: 1rem;
    }
}
```

**static/css/responsive.css**
```css
/* Tablet styles */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .calculator-app {
        max-width: 500px;
        margin: 0 auto;
    }
    
    .app-header {
        padding: 15px;
    }
    
    .app-header h1 {
        font-size: 1.3rem;
    }
    
    .calculator-container {
        padding: 15px;
    }
    
    .buttons-grid {
        gap: 8px;
    }
    
    .btn {
        padding: 12px;
        font-size: 1rem;
    }
    
    .display {
        padding: 15px;
        min-height: 60px;
    }
    
    .current-operand {
        font-size: 1.5rem;
    }
}

/* Mobile styles */
@media (max-width: 480px) {
    .calculator-container {
        padding: 10px;
        gap: 10px;
    }
    
    .buttons-grid {
        gap: 6px;
    }
    
    .btn {
        padding: 10px;
        font-size: 0.9rem;
    }
    
    .display {
        padding: 10px;
        min-height: 50px;
    }
    
    .current-operand {
        font-size: 1.2rem;
    }
    
    .previous-operand {
        font-size: 0.8rem;
    }
    
    .history-panel {
        padding: 10px;
    }
    
    .history-item {
        padding: 8px;
    }
    
    .history-expression {
        font-size: 0.8rem;
    }
    
    .history-result {
        font-size: 1rem;
    }
}

/* Small mobile styles */
@media (max-width: 360px) {
    .btn {
        padding: 8px;
        font-size: 0.8rem;
    }
    
    .current-operand {
        font-size: 1rem;
    }
    
    .buttons-grid {
        gap: 4px;
    }
}
```

### JavaScript Architecture

**static/js/calculator.js**
```javascript
class Calculator {
    constructor() {
        this.currentOperand = '0';
        this.previousOperand = '';
        this.operation = undefined;
        this.shouldResetScreen = false;
        this.sessionId = this.getOrCreateSessionId();
        this.history = new HistoryManager();
        
        this.initializeElements();
        this.bindEvents();
        this.loadHistory();
    }
    
    initializeElements() {
        this.currentOperandElement = document.getElementById('current-operand');
        this.previousOperandElement = document.getElementById('previous-operand');
        this.errorDisplay = document.getElementById('error-display');
        this.errorMessage = document.getElementById('error-message');
    }
    
    bindEvents() {
        // Button clicks
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', (e) => this.handleButtonClick(e));
        });
        
        // Keyboard events
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }
    
    handleButtonClick(event) {
        const target = event.target;
        const action = target.dataset.action;
        const number = target.dataset.number;
        const operator = target.dataset.operator;
        
        if (action) {
            this.handleAction(action);
        } else if (number !== undefined) {
            this.inputNumber(number);
        } else if (operator) {
            this.inputOperation(operator);
        }
    }
    
    handleAction(action) {
        switch (action) {
            case 'clear':
                this.clear();
                break;
            case 'clear-entry':
                this.clearEntry();
                break;
            case 'backspace':
                this.backspace();
                break;
            case 'decimal':
                this.inputDecimal();
                break;
            case 'calculate':
                this.calculate();
                break;
            case 'clear-history':
                this.clearHistory();
                break;
            case 'dismiss-error':
                this.dismissError();
                break;
        }
    }
    
    inputNumber(number) {
        if (this.shouldResetScreen) {
            this.currentOperand = '';
            this.shouldResetScreen = false;
        }
        
        if (this.currentOperand === '0' && number !== '0') {
            this.currentOperand = number;
        } else if (this.currentOperand !== '0' || number !== '0') {
            this.currentOperand += number;
        }
        
        this.updateDisplay();
    }
    
    inputOperation(operator) {
        if (this.currentOperand === '') return;
        
        if (this.previousOperand !== '' && this.operation) {
            this.calculate();
        }
        
        this.operation = operator;
        this.previousOperand = this.currentOperand;
        this.currentOperand = '';
        this.updateDisplay();
    }
    
    inputDecimal() {
        if (this.shouldResetScreen) {
            this.currentOperand = '0';
            this.shouldResetScreen = false;
        }
        
        if (this.currentOperand.indexOf('.') === -1) {
            this.currentOperand += '.';
            this.updateDisplay();
        }
    }
    
    async calculate() {
        let expression;
        
        if (this.previousOperand !== '' && this.currentOperand !== '' && this.operation) {
            expression = `${this.previousOperand} ${this.operation} ${this.currentOperand}`;
            
            try {
                const result = await this.performCalculation(expression);
                
                // Store in history
                await this.history.addCalculation(expression, result);
                
                // Update display
                this.currentOperand = result;
                this.operation = undefined;
                this.previousOperand = '';
                this.shouldResetScreen = true;
                this.updateDisplay();
                this.loadHistory(); // Refresh history
                
            } catch (error) {
                this.showError(error.message);
            }
        }
    }
    
    async performCalculation(expression) {
        try {
            const response = await fetch('/api/calculator/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.sessionId
                },
                body: JSON.stringify({ expression })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Calculation failed');
            }
            
            return data.result;
            
        } catch (error) {
            throw new Error('Network error: ' + error.message);
        }
    }
    
    clear() {
        this.currentOperand = '0';
        this.previousOperand = '';
        this.operation = undefined;
        this.updateDisplay();
    }
    
    clearEntry() {
        this.currentOperand = '0';
        this.updateDisplay();
    }
    
    backspace() {
        if (this.currentOperand.length > 1) {
            this.currentOperand = this.currentOperand.slice(0, -1);
        } else {
            this.currentOperand = '0';
        }
        this.updateDisplay();
    }
    
    updateDisplay() {
        this.currentOperandElement.textContent = this.currentOperand;
        
        if (this.operation != null) {
            this.previousOperandElement.textContent = 
                `${this.previousOperand} ${this.operation}`;
        } else {
            this.previousOperandElement.textContent = '';
        }
    }
    
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorDisplay.style.display = 'flex';
        
        setTimeout(() => {
            this.dismissError();
        }, 5000);
    }
    
    dismissError() {
        this.errorDisplay.style.display = 'none';
    }
    
    getOrCreateSessionId() {
        let sessionId = localStorage.getItem('calculator-session-id');
        if (!sessionId) {
            sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('calculator-session-id', sessionId);
        }
        return sessionId;
    }
    
    async loadHistory() {
        try {
            const historyData = await this.history.getHistory();
            this.displayHistory(historyData);
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }
    
    displayHistory(historyData) {
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';
        
        historyData.forEach(calc => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <div class="history-expression">${calc.expression}</div>
                <div class="history-result">${calc.result}</div>
                <div class="history-time">${new Date(calc.timestamp).toLocaleTimeString()}</div>
            `;
            
            historyItem.addEventListener('click', () => {
                this.loadCalculation(calc);
            });
            
            historyList.appendChild(historyItem);
        });
    }
    
    loadCalculation(calc) {
        this.currentOperand = calc.result;
        this.updateDisplay();
    }
    
    async clearHistory() {
        try {
            await this.history.clearHistory();
            this.loadHistory();
        } catch (error) {
            this.showError('Failed to clear history');
        }
    }
}

// Initialize calculator when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.calculator = new Calculator();
});
```

**static/js/keyboard-handler.js**
```javascript
class KeyboardHandler {
    constructor(calculator) {
        this.calculator = calculator;
        this.bindEvents();
    }
    
    bindEvents() {
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
    }
    
    handleKeyDown(event) {
        // Prevent default for calculator keys
        if (this.isCalculatorKey(event)) {
            event.preventDefault();
        }
        
        const key = event.key;
        
        // Number keys
        if (this.isNumberKey(key)) {
            this.calculator.inputNumber(key);
        }
        
        // Operator keys
        else if (this.isOperatorKey(key)) {
            this.calculator.inputOperation(this.mapOperatorKey(key));
        }
        
        // Special keys
        else if (key === 'Enter' || key === '=') {
            this.calculator.calculate();
        }
        
        else if (key === 'Backspace') {
            this.calculator.backspace();
        }
        
        else if (key === 'Delete' || key === 'c' || key === 'C') {
            this.calculator.clear();
        }
        
        else if (key === '.') {
            this.calculator.inputDecimal();
        }
        
        else if (key === 'Escape') {
            this.calculator.clearEntry();
        }
    }
    
    isCalculatorKey(event) {
        const key = event.key;
        return this.isNumberKey(key) || 
               this.isOperatorKey(key) || 
               ['Enter', '=', 'Backspace', 'Delete', 'c', 'C', '.', 'Escape'].includes(key);
    }
    
    isNumberKey(key) {
        return /[0-9]/.test(key);
    }
    
    isOperatorKey(key) {
        return ['+', '-', '*', '/'].includes(key);
    }
    
    mapOperatorKey(key) {
        const operatorMap = {
            '*': '×',
            '/': '÷'
        };
        return operatorMap[key] || key;
    }
}
```

**static/js/history-manager.js**
```javascript
class HistoryManager {
    constructor() {
        this.baseUrl = '/api/history';
    }
    
    async getHistory(limit = 50) {
        const response = await fetch(`${this.baseUrl}/?limit=${limit}`, {
            headers: {
                'X-Session-ID': this.getSessionId()
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch history');
        }
        
        return await response.json();
    }
    
    async addCalculation(expression, result) {
        // This is handled by the calculate endpoint, so we don't need to add separately
        return true;
    }
    
    async clearHistory() {
        const response = await fetch(`${this.baseUrl}/clear`, {
            method: 'POST',
            headers: {
                'X-Session-ID': this.getSessionId()
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to clear history');
        }
        
        return await response.json();
    }
    
    async deleteCalculation(calcId) {
        const response = await fetch(`${this.baseUrl}/${calcId}`, {
            method: 'DELETE',
            headers: {
                'X-Session-ID': this.getSessionId()
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete calculation');
        }
        
        return await response.json();
    }
    
    getSessionId() {
        return localStorage.getItem('calculator-session-id');
    }
}
```

## Error Handling Strategy

### Backend Error Handling
1. **Validation Errors**: Invalid expressions, malformed requests
2. **Calculation Errors**: Division by zero, overflow, invalid operations
3. **Database Errors**: Connection issues, query failures
4. **Network Errors**: Timeout, server unavailable

### Frontend Error Handling
1. **User Input Validation**: Real-time expression validation
2. **Network Error Handling**: Connection loss, API failures
3. **Display Errors**: Visual feedback for all error states
4. **Recovery Mechanisms**: Graceful degradation and retry logic

### Error Response Format
```json
{
    "error": "Error type",
    "message": "Human-readable error message",
    "details": "Additional error details (optional)",
    "timestamp": "2025-12-24T17:35:29.261Z"
}
```

## Testing Strategy

### Unit Tests
- **Calculator Logic**: Mathematical operations, edge cases
- **Validation Functions**: Input sanitization, expression validation
- **Error Handling**: Error conditions and recovery

### Integration Tests
- **API Endpoints**: CRUD operations, request/response handling
- **Database Operations**: Model creation, queries, transactions
- **Session Management**: Session creation, persistence, cleanup

### Frontend Tests
- **Component Tests**: UI interaction, state management
- **Keyboard Handler**: Key mapping, event handling
- **History Manager**: Data persistence, display updates

### Test Structure
```
tests/
├── unit/
│   ├── test_calculator_core.py
│   ├── test_validators.py
│   └── test_models.py
├── integration/
│   ├── test_calculator_routes.py
│   ├── test_history_routes.py
│   └── test_database.py
├── frontend/
│   ├── test_calculator_ui.py
│   └── test_keyboard_handler.py
└── conftest.py  # Pytest configuration
```

## Security Considerations

### Input Validation
- Whitelist allowed characters in expressions
- Sanitize all user inputs
- Prevent injection attacks
- Limit expression complexity

### Session Management
- Secure session token generation
- Session timeout and cleanup
- Cross-session data isolation

### API Security
- Rate limiting for calculation requests
- Request size limits
- Error message sanitization

## Performance Optimizations

### Frontend
- Debounced input validation
- Efficient DOM updates
- Lazy loading of history
- Responsive design for all devices

### Backend
- Connection pooling for database
- Caching for frequent calculations
- Optimized database queries
- Session cleanup

## Deployment Considerations

### Environment Configuration
- Development vs production settings
- Database migration strategy
- Static file serving optimization
- SSL/TLS configuration

### Monitoring and Logging
- Application performance monitoring
- Error tracking and alerting
- User activity analytics
- Database performance metrics

This architecture provides a solid foundation for a modern, scalable calculator application with comprehensive features, robust error handling, and excellent user experience across all devices.