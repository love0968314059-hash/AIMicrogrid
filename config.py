"""
Configuration file for Microgrid Digital Twin System
"""
import os

# System Configuration
SYSTEM_CONFIG = {
    'battery_capacity': 100.0,  # kWh
    'battery_max_power': 50.0,  # kW
    'battery_efficiency': 0.95,
    'initial_battery_soc': 0.5,  # 50%
    
    'pv_capacity': 80.0,  # kW
    'wind_capacity': 60.0,  # kW
    
    'grid_max_power': 100.0,  # kW
    'grid_min_power': -100.0,  # kW (negative means export)
    
    'time_step': 1,  # hours
    'prediction_horizon': 24,  # hours
}

# Prediction Configuration
PREDICTION_CONFIG = {
    'prediction_error_mean': 0.0,
    'prediction_error_std': 0.1,  # 10% standard deviation
    'use_prediction_error': True,
}

# RL Configuration
RL_CONFIG = {
    'learning_rate': 3e-4,
    'gamma': 0.99,
    'tau': 0.005,
    'buffer_size': 100000,
    'batch_size': 64,
    'training_steps': 10000,
}

# Visualization Configuration
VIZ_CONFIG = {
    'update_interval': 1.0,  # seconds
    'history_length': 100,
}
