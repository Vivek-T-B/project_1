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

// Initialize keyboard handler when calculator is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for calculator to be initialized
    const initKeyboardHandler = () => {
        if (window.calculator) {
            window.keyboardHandler = new KeyboardHandler(window.calculator);
        } else {
            setTimeout(initKeyboardHandler, 100);
        }
    };
    initKeyboardHandler();
});