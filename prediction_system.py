"""
微网预测系统
包含功率、电价、负荷预测，支持添加预测误差
"""

import numpy as np
import torch
import torch.nn as nn
from typing import List, Tuple, Dict
from collections import deque


class LSTMPredictor(nn.Module):
    """LSTM预测模型"""
    
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMPredictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        # x: (batch, seq_len, input_size)
        lstm_out, _ = self.lstm(x)
        # 取最后一个时间步的输出
        out = self.fc(lstm_out[:, -1, :])
        return out


class MicrogridPredictor:
    """微网预测系统"""
    
    def __init__(self, device='cpu'):
        self.device = device
        
        # 创建预测模型
        self.solar_predictor = LSTMPredictor(input_size=3, hidden_size=64, output_size=4).to(device)
        self.wind_predictor = LSTMPredictor(input_size=3, hidden_size=64, output_size=4).to(device)
        self.load_predictor = LSTMPredictor(input_size=3, hidden_size=64, output_size=4).to(device)
        self.price_predictor = LSTMPredictor(input_size=2, hidden_size=32, output_size=4).to(device)
        
        # 历史数据缓存
        self.solar_history = deque(maxlen=24)  # 保存24个时间步历史
        self.wind_history = deque(maxlen=24)
        self.load_history = deque(maxlen=24)
        self.price_history = deque(maxlen=24)
        
        # 预测误差配置
        self.solar_error_std = 0.15  # 太阳能预测误差标准差
        self.wind_error_std = 0.20   # 风电预测误差标准差
        self.load_error_std = 0.10   # 负荷预测误差标准差
        self.price_error_std = 0.08  # 电价预测误差标准差
        
        # 初始化模型（使用简单的启发式规则）
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化模型参数（简化版，使用启发式规则）"""
        # 实际应用中应该用历史数据训练
        # 这里为了快速演示，使用预设参数
        pass
    
    def update_history(self, solar: float, wind: float, load: float, price: float, time_step: int):
        """更新历史数据"""
        hour = (time_step * 0.25) % 24  # 假设每步15分钟
        
        self.solar_history.append([solar, hour, np.sin(2 * np.pi * hour / 24)])
        self.wind_history.append([wind, hour, np.cos(2 * np.pi * hour / 24)])
        self.load_history.append([load, hour, np.sin(2 * np.pi * hour / 24)])
        self.price_history.append([price, hour])
    
    def predict_solar(self, horizon=4, add_error=True) -> Tuple[List[float], List[float]]:
        """
        预测未来太阳能功率
        horizon: 预测时间步数
        add_error: 是否添加预测误差
        返回: (预测值列表, 真实值列表)
        """
        if len(self.solar_history) < 4:
            return [0.0] * horizon, [0.0] * horizon
        
        # 使用简单的启发式预测（基于历史模式）
        recent = list(self.solar_history)[-4:]
        recent_values = [x[0] for x in recent]
        recent_hours = [x[1] for x in recent]
        
        predictions = []
        true_values = []
        
        for i in range(horizon):
            future_hour = (recent_hours[-1] + 0.25 * (i + 1)) % 24
            
            # 简单的正弦模型
            if 6 <= future_hour <= 18:
                solar_ratio = np.sin(np.pi * (future_hour - 6) / 12)
                base_prediction = 100 * solar_ratio  # 假设100kW容量
            else:
                base_prediction = 0
            
            # 基于趋势调整
            if len(recent_values) >= 2:
                trend = recent_values[-1] - recent_values[-2]
                base_prediction += trend * 0.3
            
            true_value = base_prediction
            
            # 添加预测误差
            if add_error:
                error = np.random.normal(0, self.solar_error_std * abs(base_prediction))
                prediction = max(0, base_prediction + error)
            else:
                prediction = base_prediction
            
            predictions.append(max(0, prediction))
            true_values.append(max(0, true_value))
        
        return predictions, true_values
    
    def predict_wind(self, horizon=4, add_error=True) -> Tuple[List[float], List[float]]:
        """预测未来风电功率"""
        if len(self.wind_history) < 4:
            return [40.0] * horizon, [40.0] * horizon
        
        recent = list(self.wind_history)[-4:]
        recent_values = [x[0] for x in recent]
        recent_hours = [x[1] for x in recent]
        
        predictions = []
        true_values = []
        
        for i in range(horizon):
            future_hour = (recent_hours[-1] + 0.25 * (i + 1)) % 24
            
            # 风电基础预测（带日夜周期）
            if 20 <= future_hour or future_hour <= 6:
                base_value = 50  # 夜间风力强
            else:
                base_value = 35  # 白天风力弱
            
            # 基于最近值的自回归
            if len(recent_values) >= 2:
                ar_value = 0.7 * recent_values[-1] + 0.3 * np.mean(recent_values)
                base_prediction = 0.6 * base_value + 0.4 * ar_value
            else:
                base_prediction = base_value
            
            true_value = base_prediction
            
            # 添加预测误差
            if add_error:
                error = np.random.normal(0, self.wind_error_std * base_prediction)
                prediction = np.clip(base_prediction + error, 0, 80)
            else:
                prediction = np.clip(base_prediction, 0, 80)
            
            predictions.append(prediction)
            true_values.append(true_value)
        
        return predictions, true_values
    
    def predict_load(self, horizon=4, add_error=True) -> Tuple[List[float], List[float]]:
        """预测未来负荷需求"""
        if len(self.load_history) < 4:
            return [50.0] * horizon, [50.0] * horizon
        
        recent = list(self.load_history)[-4:]
        recent_values = [x[0] for x in recent]
        recent_hours = [x[1] for x in recent]
        
        predictions = []
        true_values = []
        
        for i in range(horizon):
            future_hour = (recent_hours[-1] + 0.25 * (i + 1)) % 24
            
            # 负荷基础预测（典型日负荷曲线）
            if 8 <= future_hour <= 22:
                base_load = 70 + 30 * np.sin(np.pi * (future_hour - 8) / 14)
            else:
                base_load = 30
            
            # 平滑过渡
            if len(recent_values) >= 2:
                smoothed = 0.7 * base_load + 0.3 * recent_values[-1]
            else:
                smoothed = base_load
            
            true_value = smoothed
            
            # 添加预测误差
            if add_error:
                error = np.random.normal(0, self.load_error_std * smoothed)
                prediction = max(20, smoothed + error)
            else:
                prediction = max(20, smoothed)
            
            predictions.append(prediction)
            true_values.append(true_value)
        
        return predictions, true_values
    
    def predict_price(self, horizon=4, add_error=True) -> Tuple[List[float], List[float]]:
        """预测未来电价"""
        if len(self.price_history) < 4:
            return [0.8] * horizon, [0.8] * horizon
        
        recent = list(self.price_history)[-4:]
        recent_values = [x[0] for x in recent]
        recent_hours = [x[1] for x in recent]
        
        predictions = []
        true_values = []
        
        for i in range(horizon):
            future_hour = (recent_hours[-1] + 0.25 * (i + 1)) % 24
            
            # 峰谷电价
            if 8 <= future_hour <= 11 or 18 <= future_hour <= 21:
                base_price = 1.2  # 峰时
            elif 23 <= future_hour or future_hour <= 6:
                base_price = 0.4  # 谷时
            else:
                base_price = 0.8  # 平时
            
            true_value = base_price
            
            # 添加预测误差
            if add_error:
                error = np.random.normal(0, self.price_error_std * base_price)
                prediction = max(0.3, base_price + error)
            else:
                prediction = max(0.3, base_price)
            
            predictions.append(prediction)
            true_values.append(true_value)
        
        return predictions, true_values
    
    def predict_all(self, horizon=4, add_error=True) -> Dict[str, Tuple[List[float], List[float]]]:
        """预测所有变量"""
        return {
            'solar': self.predict_solar(horizon, add_error),
            'wind': self.predict_wind(horizon, add_error),
            'load': self.predict_load(horizon, add_error),
            'price': self.predict_price(horizon, add_error)
        }
    
    def get_prediction_accuracy(self) -> Dict[str, float]:
        """获取预测精度统计"""
        return {
            'solar_error_std': self.solar_error_std,
            'wind_error_std': self.wind_error_std,
            'load_error_std': self.load_error_std,
            'price_error_std': self.price_error_std,
            'solar_mape': self.solar_error_std * 100,  # 简化的MAPE估计
            'wind_mape': self.wind_error_std * 100,
            'load_mape': self.load_error_std * 100,
            'price_mape': self.price_error_std * 100,
        }
    
    def set_error_levels(self, solar_err=None, wind_err=None, load_err=None, price_err=None):
        """设置预测误差水平"""
        if solar_err is not None:
            self.solar_error_std = solar_err
        if wind_err is not None:
            self.wind_error_std = wind_err
        if load_err is not None:
            self.load_error_std = load_err
        if price_err is not None:
            self.price_error_std = price_err


if __name__ == "__main__":
    # 测试预测系统
    predictor = MicrogridPredictor()
    
    # 模拟更新历史数据
    for t in range(24):
        hour = t
        solar = 100 * max(0, np.sin(np.pi * (hour - 6) / 12)) if 6 <= hour <= 18 else 0
        wind = 50 + np.random.normal(0, 10)
        load = 70 if 8 <= hour <= 22 else 30
        price = 1.2 if (8 <= hour <= 11 or 18 <= hour <= 21) else 0.8
        
        predictor.update_history(solar, wind, load, price, t)
    
    # 进行预测
    print("===== 预测测试 =====\n")
    
    predictions = predictor.predict_all(horizon=4, add_error=True)
    
    print("太阳能功率预测 (kW):")
    print(f"  预测值: {[f'{x:.2f}' for x in predictions['solar'][0]]}")
    print(f"  真实值: {[f'{x:.2f}' for x in predictions['solar'][1]]}")
    
    print("\n风电功率预测 (kW):")
    print(f"  预测值: {[f'{x:.2f}' for x in predictions['wind'][0]]}")
    print(f"  真实值: {[f'{x:.2f}' for x in predictions['wind'][1]]}")
    
    print("\n负荷需求预测 (kW):")
    print(f"  预测值: {[f'{x:.2f}' for x in predictions['load'][0]]}")
    print(f"  真实值: {[f'{x:.2f}' for x in predictions['load'][1]]}")
    
    print("\n电价预测 (¥/kWh):")
    print(f"  预测值: {[f'{x:.2f}' for x in predictions['price'][0]]}")
    print(f"  真实值: {[f'{x:.2f}' for x in predictions['price'][1]]}")
    
    print("\n预测精度统计:")
    accuracy = predictor.get_prediction_accuracy()
    for key, value in accuracy.items():
        print(f"  {key}: {value:.2f}")
