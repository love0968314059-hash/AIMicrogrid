"""
Prediction System for Microgrid Digital Twin
Predicts power generation, electricity prices, and load demand
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class PowerPredictor:
    """Predicts renewable power generation (PV and Wind)"""
    
    def __init__(self, pv_capacity=80.0, wind_capacity=60.0):
        self.pv_capacity = pv_capacity
        self.wind_capacity = wind_capacity
        self.pv_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.wind_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler_pv = StandardScaler()
        self.scaler_wind = StandardScaler()
        self._trained = False
        
    def generate_training_data(self, n_samples=1000):
        """Generate synthetic training data"""
        np.random.seed(42)
        hours = np.arange(n_samples) % 24
        days = np.arange(n_samples) // 24 % 365
        
        # Features: hour, day_of_year, weather_factor
        X = np.column_stack([
            hours,
            days,
            np.random.uniform(0.3, 1.0, n_samples),  # weather factor
            np.sin(2 * np.pi * hours / 24),  # time of day
            np.cos(2 * np.pi * hours / 24),
        ])
        
        # PV generation: follows solar pattern
        pv_factor = np.maximum(0, np.sin(np.pi * (hours - 6) / 12))
        pv_factor = np.clip(pv_factor, 0, 1)
        y_pv = self.pv_capacity * pv_factor * X[:, 2] + np.random.normal(0, 2, n_samples)
        y_pv = np.clip(y_pv, 0, self.pv_capacity)
        
        # Wind generation: more variable
        wind_factor = 0.5 + 0.5 * np.sin(2 * np.pi * days / 365)
        y_wind = self.wind_capacity * wind_factor * X[:, 2] + np.random.normal(0, 5, n_samples)
        y_wind = np.clip(y_wind, 0, self.wind_capacity)
        
        return X, y_pv, y_wind
    
    def train(self):
        """Train prediction models"""
        X, y_pv, y_wind = self.generate_training_data()
        X_scaled_pv = self.scaler_pv.fit_transform(X)
        X_scaled_wind = self.scaler_wind.fit_transform(X)
        
        self.pv_model.fit(X_scaled_pv, y_pv)
        self.wind_model.fit(X_scaled_wind, y_wind)
        self._trained = True
    
    def predict(self, hour, day_of_year=0, weather_factor=0.7, add_error=True, error_std=0.1):
        """Predict power generation for given conditions"""
        if not self._trained:
            self.train()
        
        X = np.array([[hour, day_of_year, weather_factor,
                      np.sin(2 * np.pi * hour / 24),
                      np.cos(2 * np.pi * hour / 24)]])
        
        X_scaled_pv = self.scaler_pv.transform(X)
        X_scaled_wind = self.scaler_wind.transform(X)
        
        pv_pred = self.pv_model.predict(X_scaled_pv)[0]
        wind_pred = self.wind_model.predict(X_scaled_wind)[0]
        
        if add_error:
            pv_pred *= (1 + np.random.normal(0, error_std))
            wind_pred *= (1 + np.random.normal(0, error_std))
        
        pv_pred = np.clip(pv_pred, 0, self.pv_capacity)
        wind_pred = np.clip(wind_pred, 0, self.wind_capacity)
        
        return pv_pred, wind_pred


class PricePredictor:
    """Predicts electricity prices"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self._trained = False
        self.base_price = 0.12  # $/kWh base price
        
    def generate_training_data(self, n_samples=1000):
        """Generate synthetic price data"""
        np.random.seed(42)
        hours = np.arange(n_samples) % 24
        days = np.arange(n_samples) // 24 % 7
        
        X = np.column_stack([
            hours,
            days,
            np.sin(2 * np.pi * hours / 24),
            np.cos(2 * np.pi * hours / 24),
            np.random.uniform(0.8, 1.2, n_samples),  # demand factor
        ])
        
        # Price follows demand pattern: higher during peak hours
        peak_hours = (hours >= 8) & (hours <= 20)
        price_multiplier = np.where(peak_hours, 1.3, 0.8)
        price_multiplier *= X[:, 4]  # demand factor
        
        y = self.base_price * price_multiplier + np.random.normal(0, 0.01, n_samples)
        y = np.clip(y, 0.05, 0.25)
        
        return X, y
    
    def train(self):
        """Train price prediction model"""
        X, y = self.generate_training_data()
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self._trained = True
    
    def predict(self, hour, day_of_week=0, demand_factor=1.0, add_error=True, error_std=0.1):
        """Predict electricity price"""
        if not self._trained:
            self.train()
        
        X = np.array([[hour, day_of_week,
                      np.sin(2 * np.pi * hour / 24),
                      np.cos(2 * np.pi * hour / 24),
                      demand_factor]])
        
        X_scaled = self.scaler.transform(X)
        price = self.model.predict(X_scaled)[0]
        
        if add_error:
            price *= (1 + np.random.normal(0, error_std))
        
        price = np.clip(price, 0.05, 0.25)
        return price


class LoadPredictor:
    """Predicts load demand"""
    
    def __init__(self, base_load=50.0):
        self.base_load = base_load
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self._trained = False
    
    def generate_training_data(self, n_samples=1000):
        """Generate synthetic load data"""
        np.random.seed(42)
        hours = np.arange(n_samples) % 24
        days = np.arange(n_samples) // 24 % 7
        
        X = np.column_stack([
            hours,
            days,
            np.sin(2 * np.pi * hours / 24),
            np.cos(2 * np.pi * hours / 24),
            np.sin(2 * np.pi * days / 7),
            np.cos(2 * np.pi * days / 7),
        ])
        
        # Load follows daily and weekly patterns
        peak_hours = (hours >= 7) & (hours <= 22)
        weekday_factor = np.where(days < 5, 1.2, 0.8)
        
        load_multiplier = np.where(peak_hours, 1.5, 0.6) * weekday_factor
        y = self.base_load * load_multiplier + np.random.normal(0, 5, n_samples)
        y = np.clip(y, 10, 150)
        
        return X, y
    
    def train(self):
        """Train load prediction model"""
        X, y = self.generate_training_data()
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self._trained = True
    
    def predict(self, hour, day_of_week=0, add_error=True, error_std=0.1):
        """Predict load demand"""
        if not self._trained:
            self.train()
        
        X = np.array([[hour, day_of_week,
                      np.sin(2 * np.pi * hour / 24),
                      np.cos(2 * np.pi * hour / 24),
                      np.sin(2 * np.pi * day_of_week / 7),
                      np.cos(2 * np.pi * day_of_week / 7)]])
        
        X_scaled = self.scaler.transform(X)
        load = self.model.predict(X_scaled)[0]
        
        if add_error:
            load *= (1 + np.random.normal(0, error_std))
        
        load = np.clip(load, 10, 150)
        return load


class PredictionSystem:
    """Unified prediction system"""
    
    def __init__(self, config=None):
        if config is None:
            from config import SYSTEM_CONFIG, PREDICTION_CONFIG
            config = SYSTEM_CONFIG
            pred_config = PREDICTION_CONFIG
        else:
            pred_config = config.get('prediction', {})
        
        self.power_predictor = PowerPredictor(
            pv_capacity=config.get('pv_capacity', 80.0),
            wind_capacity=config.get('wind_capacity', 60.0)
        )
        self.price_predictor = PricePredictor()
        self.load_predictor = LoadPredictor()
        
        self.error_std = pred_config.get('prediction_error_std', 0.1)
        self.use_error = pred_config.get('use_prediction_error', True)
        
        # Initialize models
        self.power_predictor.train()
        self.price_predictor.train()
        self.load_predictor.train()
    
    def predict(self, hour, day_of_year=0, day_of_week=0, weather_factor=0.7, demand_factor=1.0):
        """Make predictions for all quantities"""
        pv, wind = self.power_predictor.predict(
            hour, day_of_year, weather_factor,
            add_error=self.use_error, error_std=self.error_std
        )
        price = self.price_predictor.predict(
            hour, day_of_week, demand_factor,
            add_error=self.use_error, error_std=self.error_std
        )
        load = self.load_predictor.predict(
            hour, day_of_week,
            add_error=self.use_error, error_std=self.error_std
        )
        
        return {
            'pv_power': pv,
            'wind_power': wind,
            'total_renewable': pv + wind,
            'price': price,
            'load': load,
            'hour': hour,
            'day_of_year': day_of_year,
            'day_of_week': day_of_week
        }
    
    def predict_horizon(self, start_hour=0, horizon=24, **kwargs):
        """Predict for multiple time steps"""
        predictions = []
        for i in range(horizon):
            hour = (start_hour + i) % 24
            day_of_year = kwargs.get('day_of_year', 0)
            day_of_week = (kwargs.get('day_of_week', 0) + i // 24) % 7
            pred = self.predict(hour, day_of_year, day_of_week, **kwargs)
            predictions.append(pred)
        return predictions
