/**
 * Main Application Logic
 * Handles API communication and UI updates
 */

const API_BASE = window.location.origin;

class MicrogridApp {
    constructor() {
        this.visualization = null;
        this.updateInterval = null;
        this.running = false;
        this.init();
    }
    
    init() {
        // Initialize 3D visualization
        const container = document.getElementById('canvas-container');
        this.visualization = new MicrogridVisualization(container);
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initial status update
        this.updateStatus();
        
        // Start periodic updates
        this.startUpdates();
    }
    
    setupEventListeners() {
        // Control buttons
        document.getElementById('start-btn').addEventListener('click', () => this.startSimulation());
        document.getElementById('stop-btn').addEventListener('click', () => this.stopSimulation());
        document.getElementById('reset-btn').addEventListener('click', () => this.resetSimulation());
        
        // NLP input
        const nlpInput = document.getElementById('nlp-input');
        nlpInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.processNLPQuery(nlpInput.value);
                nlpInput.value = '';
            }
        });
    }
    
    async updateStatus() {
        try {
            const response = await fetch(`${API_BASE}/api/status`);
            const data = await response.json();
            
            // Update UI
            this.updateUI(data);
            
            // Update 3D visualization
            if (this.visualization) {
                const currentData = {
                    battery_soc: data.battery_soc,
                    pv_power: data.predictions.pv_power,
                    wind_power: data.predictions.wind_power,
                    load: data.predictions.load,
                    price: data.predictions.price,
                    grid_power: data.realtime_data.grid_power?.[data.realtime_data.grid_power.length - 1] || 0
                };
                this.visualization.update(currentData);
            }
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }
    
    updateUI(data) {
        // Update battery SOC
        const batterySOC = (data.battery_soc * 100).toFixed(1);
        document.getElementById('battery-soc').textContent = `${batterySOC}%`;
        
        // Update power values
        document.getElementById('pv-power').textContent = data.predictions.pv_power.toFixed(1);
        document.getElementById('wind-power').textContent = data.predictions.wind_power.toFixed(1);
        document.getElementById('load').textContent = data.predictions.load.toFixed(1);
        
        // Update price
        document.getElementById('price').textContent = `$${data.predictions.price.toFixed(3)}`;
        
        // Update total cost
        const totalCost = data.statistics.total_cost || 0;
        document.getElementById('total-cost').textContent = `$${totalCost.toFixed(2)}`;
    }
    
    async startSimulation() {
        try {
            const response = await fetch(`${API_BASE}/api/control`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'start' })
            });
            const result = await response.json();
            if (result.status === 'started') {
                this.running = true;
                console.log('Simulation started');
            }
        } catch (error) {
            console.error('Error starting simulation:', error);
        }
    }
    
    async stopSimulation() {
        try {
            const response = await fetch(`${API_BASE}/api/control`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'stop' })
            });
            const result = await response.json();
            if (result.status === 'stopped') {
                this.running = false;
                console.log('Simulation stopped');
            }
        } catch (error) {
            console.error('Error stopping simulation:', error);
        }
    }
    
    async resetSimulation() {
        try {
            const response = await fetch(`${API_BASE}/api/control`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'reset' })
            });
            const result = await response.json();
            if (result.status === 'reset') {
                this.running = false;
                await this.updateStatus();
                console.log('Simulation reset');
            }
        } catch (error) {
            console.error('Error resetting simulation:', error);
        }
    }
    
    async processNLPQuery(query) {
        const responseDiv = document.getElementById('nlp-response');
        responseDiv.innerHTML = '<div class="loading"></div> 处理中...';
        
        try {
            const response = await fetch(`${API_BASE}/api/nlp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            const result = await response.json();
            responseDiv.textContent = result.response || '无响应';
        } catch (error) {
            responseDiv.textContent = `错误: ${error.message}`;
        }
    }
    
    startUpdates() {
        // Update every second
        this.updateInterval = setInterval(() => {
            this.updateStatus();
        }, 1000);
    }
    
    stopUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MicrogridApp();
});
