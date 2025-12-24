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