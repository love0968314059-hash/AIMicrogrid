"""
Digital Twin System for Microgrid
Simulates microgrid operation and evaluates energy management strategies
"""
import numpy as np
import time
from datetime import datetime, timedelta
from predictors import PredictionSystem
from rl_energy_manager import RLEnergyManager, MicrogridEnv
from config import SYSTEM_CONFIG, PREDICTION_CONFIG, RL_CONFIG


class DigitalTwin:
    """Microgrid Digital Twin System"""
    
    def __init__(self, config=None):
        self.config = config or SYSTEM_CONFIG
        self.prediction_system = PredictionSystem(self.config)
        self.rl_manager = RLEnergyManager(self.config, self.prediction_system)
        
        # Current state
        self.current_time = datetime.now()
        self.battery_soc = self.config['initial_battery_soc']
        self.running = False
        
        # Statistics
        self.stats = {
            'total_cost': 0.0,
            'total_energy_imported': 0.0,
            'total_energy_exported': 0.0,
            'total_renewable_used': 0.0,
            'total_load_served': 0.0,
            'battery_cycles': 0,
            'time_steps': 0
        }
        
        # Real-time data
        self.realtime_data = {
            'timestamp': [],
            'pv_power': [],
            'wind_power': [],
            'load': [],
            'price': [],
            'battery_soc': [],
            'battery_power': [],
            'grid_power': [],
            'cost': [],
            'net_power': []
        }
    
    def initialize(self):
        """Initialize the digital twin"""
        print("Initializing Digital Twin...")
        print("Training RL agent...")
        self.rl_manager.train(episodes=50)  # Quick training for demo
        print("Digital Twin ready!")
    
    def step(self, action=None):
        """Execute one simulation step"""
        hour = self.current_time.hour
        day_of_year = self.current_time.timetuple().tm_yday
        day_of_week = self.current_time.weekday()
        
        # Get predictions
        pred = self.prediction_system.predict(
            hour, day_of_year, day_of_week,
            weather_factor=np.random.uniform(0.6, 1.0),
            demand_factor=np.random.uniform(0.9, 1.1)
        )
        
        # Get action from RL manager if not provided
        if action is None:
            state = np.array([
                self.battery_soc,
                pred['pv_power'],
                pred['wind_power'],
                pred['load'],
                pred['price'],
                hour / 24.0
            ], dtype=np.float32)
            action = self.rl_manager.get_action(state)
        else:
            action = np.clip(action, -self.config['battery_max_power'], self.config['battery_max_power'])
        
        # Simulate microgrid operation
        renewable_power = pred['pv_power'] + pred['wind_power']
        net_load = pred['load'] - renewable_power
        
        # Battery operation
        battery_power = action
        if battery_power > 0:  # Discharge
            actual_discharge = min(
                battery_power,
                self.battery_soc * self.config['battery_capacity'] / self.config['time_step'],
                self.config['battery_max_power']
            )
            energy_discharged = actual_discharge * self.config['time_step']
            self.battery_soc -= energy_discharged / self.config['battery_capacity']
        else:  # Charge
            actual_charge = max(
                battery_power,
                -(1 - self.battery_soc) * self.config['battery_capacity'] / self.config['time_step'],
                -self.config['battery_max_power']
            )
            energy_charged = -actual_charge * self.config['time_step'] * self.config['battery_efficiency']
            self.battery_soc += energy_charged / self.config['battery_capacity']
        
        self.battery_soc = np.clip(self.battery_soc, 0, 1)
        
        # Grid power
        grid_power = net_load - battery_power
        grid_power = np.clip(grid_power, self.config['grid_min_power'], self.config['grid_max_power'])
        
        # Calculate cost
        if grid_power > 0:  # Import
            cost = grid_power * pred['price'] * self.config['time_step']
            self.stats['total_energy_imported'] += grid_power * self.config['time_step']
        else:  # Export
            cost = grid_power * pred['price'] * 0.7 * self.config['time_step']
            self.stats['total_energy_exported'] += abs(grid_power) * self.config['time_step']
        
        self.stats['total_cost'] += cost
        self.stats['total_renewable_used'] += min(renewable_power, pred['load']) * self.config['time_step']
        self.stats['total_load_served'] += pred['load'] * self.config['time_step']
        self.stats['time_steps'] += 1
        
        # Store real-time data
        timestamp = self.current_time.isoformat()
        self.realtime_data['timestamp'].append(timestamp)
        self.realtime_data['pv_power'].append(pred['pv_power'])
        self.realtime_data['wind_power'].append(pred['wind_power'])
        self.realtime_data['load'].append(pred['load'])
        self.realtime_data['price'].append(pred['price'])
        self.realtime_data['battery_soc'].append(self.battery_soc)
        self.realtime_data['battery_power'].append(battery_power)
        self.realtime_data['grid_power'].append(grid_power)
        self.realtime_data['cost'].append(cost)
        self.realtime_data['net_power'].append(renewable_power - pred['load'])
        
        # Keep only recent history
        max_history = 1000
        for key in self.realtime_data:
            if len(self.realtime_data[key]) > max_history:
                self.realtime_data[key] = self.realtime_data[key][-max_history:]
        
        # Update time
        self.current_time += timedelta(hours=self.config['time_step'])
        
        return {
            'timestamp': timestamp,
            'pv_power': pred['pv_power'],
            'wind_power': pred['wind_power'],
            'load': pred['load'],
            'price': pred['price'],
            'battery_soc': self.battery_soc,
            'battery_power': battery_power,
            'grid_power': grid_power,
            'cost': cost,
            'renewable_power': renewable_power,
            'net_power': renewable_power - pred['load']
        }
    
    def evaluate_strategy(self, horizon=24, strategy='rl'):
        """Evaluate energy management strategy"""
        original_soc = self.battery_soc
        original_time = self.current_time
        
        results = []
        total_cost = 0.0
        
        for _ in range(horizon):
            if strategy == 'rl':
                result = self.step()
            elif strategy == 'greedy':
                # Greedy strategy: always minimize immediate cost
                pred = self.prediction_system.predict(
                    self.current_time.hour,
                    self.current_time.timetuple().tm_yday,
                    self.current_time.weekday()
                )
                net_load = pred['load'] - pred['pv_power'] - pred['wind_power']
                if net_load > 0 and self.battery_soc > 0.3:
                    action = min(net_load, 50)
                elif net_load < 0 and self.battery_soc < 0.8:
                    action = max(net_load, -50)
                else:
                    action = 0
                result = self.step(action)
            else:
                result = self.step(0)  # No battery action
            
            results.append(result)
            total_cost += result['cost']
        
        # Restore state
        self.battery_soc = original_soc
        self.current_time = original_time
        
        return {
            'strategy': strategy,
            'total_cost': total_cost,
            'average_cost_per_hour': total_cost / horizon,
            'final_soc': self.battery_soc,
            'results': results,
            'renewable_utilization': sum(r['renewable_power'] for r in results) / sum(r['load'] for r in results) if sum(r['load'] for r in results) > 0 else 0
        }
    
    def get_status(self):
        """Get current system status"""
        hour = self.current_time.hour
        day_of_year = self.current_time.timetuple().tm_yday
        day_of_week = self.current_time.weekday()
        
        pred = self.prediction_system.predict(hour, day_of_year, day_of_week)
        
        return {
            'current_time': self.current_time.isoformat(),
            'battery_soc': self.battery_soc,
            'battery_energy': self.battery_soc * self.config['battery_capacity'],
            'predictions': pred,
            'statistics': self.stats.copy(),
            'realtime_data': {
                k: v[-100:] if len(v) > 100 else v
                for k, v in self.realtime_data.items()
            }
        }
    
    def reset(self):
        """Reset the digital twin"""
        self.battery_soc = self.config['initial_battery_soc']
        self.current_time = datetime.now()
        self.stats = {
            'total_cost': 0.0,
            'total_energy_imported': 0.0,
            'total_energy_exported': 0.0,
            'total_renewable_used': 0.0,
            'total_load_served': 0.0,
            'battery_cycles': 0,
            'time_steps': 0
        }
        self.realtime_data = {k: [] for k in self.realtime_data.keys()}
