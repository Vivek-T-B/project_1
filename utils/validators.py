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