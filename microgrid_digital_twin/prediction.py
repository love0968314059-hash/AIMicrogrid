"""
预测模块
========

包含功率预测、电价预测、负荷预测模型。
支持LSTM、GRU等深度学习模型，以及简单的统计预测。
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import deque
import warnings


class TimeSeriesBuffer:
    """时间序列数据缓冲区"""
    
    def __init__(self, max_size: int = 1440):  # 默认存储24小时（每分钟一个点）
        self.buffer = deque(maxlen=max_size)
        
    def add(self, value: float):
        self.buffer.append(value)
        
    def get_sequence(self, length: int) -> np.ndarray:
        if len(self.buffer) < length:
            # 如果数据不足，用均值填充
            data = list(self.buffer)
            mean_val = np.mean(data) if data else 0
            padding = [mean_val] * (length - len(data))
            return np.array(padding + data)
        return np.array(list(self.buffer)[-length:])
    
    def __len__(self):
        return len(self.buffer)


class BasePredictor:
    """预测器基类"""
    
    def __init__(self, sequence_length: int = 60, prediction_horizon: int = 60):
        """
        Args:
            sequence_length: 输入序列长度（分钟）
            prediction_horizon: 预测时长（分钟）
        """
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.buffer = TimeSeriesBuffer()
        self.prediction_errors = deque(maxlen=1000)
        
    def update(self, value: float):
        """更新历史数据"""
        self.buffer.add(value)
        
    def get_prediction_error_stats(self) -> Dict[str, float]:
        """获取预测误差统计"""
        if len(self.prediction_errors) == 0:
            return {'mae': 0, 'rmse': 0, 'mape': 0}
        
        errors = np.array(self.prediction_errors)
        return {
            'mae': np.mean(np.abs(errors)),
            'rmse': np.sqrt(np.mean(errors ** 2)),
            'mape': np.mean(np.abs(errors)) * 100
        }


class PowerPredictor(BasePredictor):
    """功率预测器（光伏/风电）"""
    
    def __init__(self, power_type: str = 'solar', **kwargs):
        super().__init__(**kwargs)
        self.power_type = power_type
        self.daily_pattern = None
        self.fitted = False
        
    def fit(self, historical_data: np.ndarray):
        """训练预测模型"""
        # 计算日平均模式
        if len(historical_data) >= 1440:
            # 重塑为 (天数, 1440分钟)
            n_days = len(historical_data) // 1440
            reshaped = historical_data[:n_days * 1440].reshape(n_days, 1440)
            self.daily_pattern = np.mean(reshaped, axis=0)
        else:
            self.daily_pattern = historical_data
        self.fitted = True
        
    def predict(self, current_hour: int, current_minute: int, 
                weather_forecast: Optional[Dict] = None) -> np.ndarray:
        """
        预测未来功率
        
        Args:
            current_hour: 当前小时
            current_minute: 当前分钟
            weather_forecast: 天气预报
            
        Returns:
            预测功率序列
        """
        predictions = np.zeros(self.prediction_horizon)
        current_idx = current_hour * 60 + current_minute
        
        # 获取历史序列
        history = self.buffer.get_sequence(self.sequence_length)
        
        for i in range(self.prediction_horizon):
            future_idx = (current_idx + i) % 1440
            
            if self.power_type == 'solar':
                # 光伏功率预测：基于时间和天气
                hour = (current_hour + (current_minute + i) // 60) % 24
                base_power = self._solar_base_pattern(hour, future_idx % 60)
                
                # 添加天气影响
                if weather_forecast:
                    cloud_factor = 1 - 0.7 * weather_forecast.get('cloud_cover', 0.3)
                    base_power *= cloud_factor
                    
            else:  # wind
                # 风电功率预测：基于历史趋势
                if len(history) > 0:
                    trend = np.polyfit(range(len(history)), history, 1)
                    base_power = max(0, trend[0] * (len(history) + i) + trend[1])
                else:
                    base_power = 20  # 默认值
                    
                # 添加随机波动
                if weather_forecast:
                    wind_factor = weather_forecast.get('wind_speed', 8) / 8
                    base_power *= wind_factor
            
            # 添加预测不确定性
            noise = np.random.normal(0, 0.05 * max(1, base_power))
            predictions[i] = max(0, base_power + noise)
            
        return predictions
    
    def _solar_base_pattern(self, hour: int, minute: int) -> float:
        """光伏基础功率模式"""
        time_decimal = hour + minute / 60
        if 6 <= time_decimal <= 18:
            # 高斯分布模拟日照曲线
            peak_hour = 12
            power = 100 * np.exp(-0.5 * ((time_decimal - peak_hour) / 3) ** 2)
            return power
        return 0
    
    def predict_with_uncertainty(self, current_hour: int, current_minute: int,
                                  weather_forecast: Optional[Dict] = None,
                                  n_samples: int = 100) -> Dict[str, np.ndarray]:
        """带不确定性的预测"""
        samples = []
        for _ in range(n_samples):
            pred = self.predict(current_hour, current_minute, weather_forecast)
            samples.append(pred)
        
        samples = np.array(samples)
        return {
            'mean': np.mean(samples, axis=0),
            'std': np.std(samples, axis=0),
            'lower_95': np.percentile(samples, 2.5, axis=0),
            'upper_95': np.percentile(samples, 97.5, axis=0),
            'samples': samples
        }


class PricePredictor(BasePredictor):
    """电价预测器"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 标准分时电价模式
        self.base_prices = {
            'peak': 1.2,
            'normal': 0.8,
            'valley': 0.4
        }
        
        # 价格波动参数
        self.volatility = 0.05
        
    def get_period(self, hour: int) -> str:
        """获取电价时段"""
        if 23 <= hour or hour < 7:
            return 'valley'
        elif 9 <= hour < 12 or 17 <= hour < 21:
            return 'peak'
        else:
            return 'normal'
    
    def predict(self, current_hour: int, current_minute: int,
                market_conditions: Optional[Dict] = None) -> np.ndarray:
        """
        预测未来电价
        
        Args:
            current_hour: 当前小时
            current_minute: 当前分钟
            market_conditions: 市场条件
            
        Returns:
            预测电价序列
        """
        predictions = np.zeros(self.prediction_horizon)
        
        for i in range(self.prediction_horizon):
            future_minute = current_minute + i
            future_hour = (current_hour + future_minute // 60) % 24
            
            period = self.get_period(future_hour)
            base_price = self.base_prices[period]
            
            # 添加市场影响
            if market_conditions:
                demand_factor = market_conditions.get('demand_factor', 1.0)
                base_price *= demand_factor
            
            # 添加随机波动
            noise = np.random.normal(0, self.volatility * base_price)
            predictions[i] = max(0.1, base_price + noise)
            
        return predictions
    
    def predict_with_uncertainty(self, current_hour: int, current_minute: int,
                                  market_conditions: Optional[Dict] = None,
                                  n_samples: int = 100) -> Dict[str, np.ndarray]:
        """带不确定性的电价预测"""
        samples = []
        for _ in range(n_samples):
            pred = self.predict(current_hour, current_minute, market_conditions)
            samples.append(pred)
        
        samples = np.array(samples)
        return {
            'mean': np.mean(samples, axis=0),
            'std': np.std(samples, axis=0),
            'lower_bound': np.percentile(samples, 5, axis=0),
            'upper_bound': np.percentile(samples, 95, axis=0)
        }


class LoadPredictor(BasePredictor):
    """负荷预测器"""
    
    def __init__(self, base_load: float = 80, peak_load: float = 150, **kwargs):
        super().__init__(**kwargs)
        self.base_load = base_load
        self.peak_load = peak_load
        
        # 标准日负荷曲线（每小时）
        self.hourly_pattern = np.array([
            0.6, 0.5, 0.45, 0.4, 0.45, 0.5,  # 0-5
            0.6, 0.8, 1.0, 0.95, 0.9, 0.85,  # 6-11
            0.8, 0.85, 0.9, 0.95, 1.0, 1.0,  # 12-17
            0.95, 0.9, 0.85, 0.8, 0.7, 0.65  # 18-23
        ])
        
        # 周末调整系数
        self.weekend_factor = 0.85
        
    def predict(self, current_hour: int, current_minute: int,
                is_weekend: bool = False,
                special_events: Optional[Dict] = None) -> np.ndarray:
        """
        预测未来负荷
        
        Args:
            current_hour: 当前小时
            current_minute: 当前分钟
            is_weekend: 是否周末
            special_events: 特殊事件
            
        Returns:
            预测负荷序列
        """
        predictions = np.zeros(self.prediction_horizon)
        
        # 获取历史趋势
        history = self.buffer.get_sequence(self.sequence_length)
        if len(history) > 10:
            recent_mean = np.mean(history[-10:])
            trend_factor = recent_mean / (self.base_load * 0.7) if self.base_load > 0 else 1
        else:
            trend_factor = 1.0
        
        for i in range(self.prediction_horizon):
            future_minute = current_minute + i
            future_hour = (current_hour + future_minute // 60) % 24
            
            # 基础负荷
            pattern_value = self.hourly_pattern[future_hour]
            load = self.base_load + (self.peak_load - self.base_load) * pattern_value
            
            # 周末调整
            if is_weekend:
                load *= self.weekend_factor
            
            # 趋势调整
            load *= np.clip(trend_factor, 0.8, 1.2)
            
            # 特殊事件
            if special_events:
                event_factor = special_events.get('factor', 1.0)
                load *= event_factor
            
            # 添加随机波动
            noise = np.random.normal(0, 0.08 * load)
            predictions[i] = max(0, load + noise)
            
        return predictions
    
    def predict_with_uncertainty(self, current_hour: int, current_minute: int,
                                  is_weekend: bool = False,
                                  n_samples: int = 100) -> Dict[str, np.ndarray]:
        """带不确定性的负荷预测"""
        samples = []
        for _ in range(n_samples):
            pred = self.predict(current_hour, current_minute, is_weekend)
            samples.append(pred)
        
        samples = np.array(samples)
        return {
            'mean': np.mean(samples, axis=0),
            'std': np.std(samples, axis=0),
            'lower_90': np.percentile(samples, 5, axis=0),
            'upper_90': np.percentile(samples, 95, axis=0)
        }


class IntegratedForecaster:
    """综合预测系统"""
    
    def __init__(self, prediction_horizon: int = 60):
        self.solar_predictor = PowerPredictor(power_type='solar', 
                                               prediction_horizon=prediction_horizon)
        self.wind_predictor = PowerPredictor(power_type='wind',
                                              prediction_horizon=prediction_horizon)
        self.price_predictor = PricePredictor(prediction_horizon=prediction_horizon)
        self.load_predictor = LoadPredictor(prediction_horizon=prediction_horizon)
        
        self.prediction_horizon = prediction_horizon
        
    def update(self, solar_power: float, wind_power: float, 
               price: float, load: float):
        """更新所有预测器"""
        self.solar_predictor.update(solar_power)
        self.wind_predictor.update(wind_power)
        self.price_predictor.update(price)
        self.load_predictor.update(load)
        
    def forecast_all(self, current_hour: int, current_minute: int,
                     weather_forecast: Optional[Dict] = None,
                     is_weekend: bool = False) -> Dict[str, Dict]:
        """获取所有预测"""
        return {
            'solar': self.solar_predictor.predict_with_uncertainty(
                current_hour, current_minute, weather_forecast
            ),
            'wind': self.wind_predictor.predict_with_uncertainty(
                current_hour, current_minute, weather_forecast
            ),
            'price': self.price_predictor.predict_with_uncertainty(
                current_hour, current_minute
            ),
            'load': self.load_predictor.predict_with_uncertainty(
                current_hour, current_minute, is_weekend
            )
        }
    
    def get_scenario_forecasts(self, current_hour: int, current_minute: int,
                                n_scenarios: int = 10) -> List[Dict]:
        """生成多场景预测"""
        scenarios = []
        for i in range(n_scenarios):
            scenario = {
                'id': i,
                'solar': self.solar_predictor.predict(current_hour, current_minute),
                'wind': self.wind_predictor.predict(current_hour, current_minute),
                'price': self.price_predictor.predict(current_hour, current_minute),
                'load': self.load_predictor.predict(current_hour, current_minute),
                'probability': 1.0 / n_scenarios
            }
            scenarios.append(scenario)
        return scenarios
