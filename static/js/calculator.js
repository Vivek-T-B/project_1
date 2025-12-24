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
    
    handleKeyPress(event) {
        const key = event.key;
        
        // Number keys
        if (this.isNumberKey(key)) {
            this.inputNumber(key);
        }
        
        // Operator keys
        else if (this.isOperatorKey(key)) {
            this.inputOperation(this.mapOperatorKey(key));
        }
        
        // Special keys
        else if (key === 'Enter' || key === '=') {
            this.calculate();
        }
        
        else if (key === 'Backspace') {
            this.backspace();
        }
        
        else if (key === 'Delete' || key === 'c' || key === 'C') {
            this.clear();
        }
        
        else if (key === '.') {
            this.inputDecimal();
        }
        
        else if (key === 'Escape') {
            this.clearEntry();
        }
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

// Initialize calculator when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.calculator = new Calculator();
});