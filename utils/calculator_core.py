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