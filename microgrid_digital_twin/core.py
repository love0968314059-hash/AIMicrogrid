"""
微网数字孪生核心模拟系统
=======================

包含微网各个组件的数学模型和实时模拟功能。
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json


@dataclass
class SolarPanel:
    """光伏发电系统"""
    capacity_kw: float = 100.0  # 装机容量 (kW)
    efficiency: float = 0.18   # 转换效率
    panel_area: float = 500.0  # 面板面积 (m²)
    temperature_coeff: float = -0.004  # 温度系数
    
    def generate_power(self, irradiance: float, temperature: float) -> float:
        """
        计算光伏发电功率
        
        Args:
            irradiance: 太阳辐照度 (W/m²)
            temperature: 环境温度 (°C)
        
        Returns:
            发电功率 (kW)
        """
        # 温度修正
        temp_factor = 1 + self.temperature_coeff * (temperature - 25)
        temp_factor = max(0.7, min(1.1, temp_factor))
        
        # 计算功率
        power = (irradiance / 1000) * self.panel_area * self.efficiency * temp_factor
        return min(power, self.capacity_kw)


@dataclass
class WindTurbine:
    """风力发电系统"""
    capacity_kw: float = 50.0   # 额定功率 (kW)
    cut_in_speed: float = 3.0   # 切入风速 (m/s)
    rated_speed: float = 12.0   # 额定风速 (m/s)
    cut_out_speed: float = 25.0 # 切出风速 (m/s)
    rotor_diameter: float = 20.0  # 转子直径 (m)
    
    def generate_power(self, wind_speed: float) -> float:
        """
        计算风力发电功率
        
        Args:
            wind_speed: 风速 (m/s)
        
        Returns:
            发电功率 (kW)
        """
        if wind_speed < self.cut_in_speed or wind_speed > self.cut_out_speed:
            return 0.0
        elif wind_speed < self.rated_speed:
            # 立方关系
            power = self.capacity_kw * ((wind_speed - self.cut_in_speed) / 
                                        (self.rated_speed - self.cut_in_speed)) ** 3
            return power
        else:
            return self.capacity_kw


@dataclass
class BatteryStorage:
    """电池储能系统"""
    capacity_kwh: float = 200.0  # 容量 (kWh)
    max_charge_rate: float = 50.0  # 最大充电功率 (kW)
    max_discharge_rate: float = 50.0  # 最大放电功率 (kW)
    charge_efficiency: float = 0.95  # 充电效率
    discharge_efficiency: float = 0.95  # 放电效率
    soc: float = 0.5  # 当前荷电状态 (0-1)
    soc_min: float = 0.1  # 最小SOC
    soc_max: float = 0.9  # 最大SOC
    cycle_count: int = 0  # 充放电循环次数
    health: float = 1.0  # 电池健康度
    
    def charge(self, power: float, duration_hours: float = 1/60) -> Tuple[float, float]:
        """
        充电操作
        
        Args:
            power: 充电功率 (kW)
            duration_hours: 持续时间 (小时)
        
        Returns:
            (实际充电功率, 充入能量)
        """
        # 限制充电功率
        actual_power = min(power, self.max_charge_rate)
        
        # 计算可充入能量
        available_capacity = (self.soc_max - self.soc) * self.capacity_kwh
        energy_to_add = actual_power * duration_hours * self.charge_efficiency
        actual_energy = min(energy_to_add, available_capacity)
        
        # 更新SOC
        self.soc += actual_energy / self.capacity_kwh
        self.soc = min(self.soc, self.soc_max)
        
        return actual_power, actual_energy
    
    def discharge(self, power: float, duration_hours: float = 1/60) -> Tuple[float, float]:
        """
        放电操作
        
        Args:
            power: 放电功率 (kW)
            duration_hours: 持续时间 (小时)
        
        Returns:
            (实际放电功率, 放出能量)
        """
        # 限制放电功率
        actual_power = min(power, self.max_discharge_rate)
        
        # 计算可放出能量
        available_energy = (self.soc - self.soc_min) * self.capacity_kwh
        energy_to_release = actual_power * duration_hours / self.discharge_efficiency
        actual_energy = min(energy_to_release, available_energy)
        
        # 更新SOC
        self.soc -= actual_energy / self.capacity_kwh
        self.soc = max(self.soc, self.soc_min)
        
        return actual_power, actual_energy * self.discharge_efficiency


@dataclass
class DieselGenerator:
    """柴油发电机"""
    capacity_kw: float = 100.0  # 额定功率 (kW)
    min_load_ratio: float = 0.3  # 最低负载率
    fuel_consumption_rate: float = 0.3  # 燃油消耗率 (L/kWh)
    startup_time: float = 5.0  # 启动时间 (分钟)
    is_running: bool = False
    run_hours: float = 0.0
    
    def generate_power(self, required_power: float) -> Tuple[float, float]:
        """
        发电并计算燃油消耗
        
        Args:
            required_power: 需求功率 (kW)
        
        Returns:
            (实际发电功率, 燃油消耗 L)
        """
        if not self.is_running:
            return 0.0, 0.0
        
        min_power = self.capacity_kw * self.min_load_ratio
        actual_power = max(min_power, min(required_power, self.capacity_kw))
        fuel = actual_power * self.fuel_consumption_rate / 60  # 每分钟消耗
        
        return actual_power, fuel


@dataclass
class Load:
    """负荷模型"""
    base_load: float = 80.0  # 基础负荷 (kW)
    peak_load: float = 150.0  # 峰值负荷 (kW)
    load_profile: List[float] = field(default_factory=lambda: [
        0.6, 0.5, 0.45, 0.4, 0.45, 0.5,  # 0-5点
        0.6, 0.8, 1.0, 0.95, 0.9, 0.85,  # 6-11点
        0.8, 0.85, 0.9, 0.95, 1.0, 1.0,  # 12-17点
        0.95, 0.9, 0.85, 0.8, 0.7, 0.65  # 18-23点
    ])
    
    def get_load(self, hour: int, noise_factor: float = 0.1) -> float:
        """
        获取当前时刻负荷
        
        Args:
            hour: 小时 (0-23)
            noise_factor: 噪声系数
        
        Returns:
            负荷功率 (kW)
        """
        profile_value = self.load_profile[hour % 24]
        base = self.base_load + (self.peak_load - self.base_load) * profile_value
        noise = np.random.normal(0, noise_factor * base)
        return max(0, base + noise)


@dataclass
class GridConnection:
    """电网连接"""
    max_import: float = 100.0  # 最大购电功率 (kW)
    max_export: float = 50.0   # 最大售电功率 (kW)
    is_connected: bool = True
    
    def exchange_power(self, power: float) -> float:
        """
        与电网交换功率
        
        Args:
            power: 正值为购电，负值为售电 (kW)
        
        Returns:
            实际交换功率 (kW)
        """
        if not self.is_connected:
            return 0.0
        
        if power > 0:
            return min(power, self.max_import)
        else:
            return max(power, -self.max_export)


class WeatherSimulator:
    """天气模拟器"""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.base_temp = 20.0
        self.cloud_cover = 0.3
        
    def get_conditions(self, timestamp: datetime) -> Dict[str, float]:
        """获取天气条件"""
        hour = timestamp.hour
        day_of_year = timestamp.timetuple().tm_yday
        
        # 太阳辐照度 (考虑日变化和季节)
        solar_angle = np.sin(np.pi * (hour - 6) / 12) if 6 <= hour <= 18 else 0
        solar_angle = max(0, solar_angle)
        seasonal_factor = 0.7 + 0.3 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        base_irradiance = 1000 * solar_angle * seasonal_factor
        
        # 云层影响
        self.cloud_cover = np.clip(
            self.cloud_cover + self.rng.normal(0, 0.05), 0, 1
        )
        irradiance = base_irradiance * (1 - 0.7 * self.cloud_cover)
        irradiance += self.rng.normal(0, 20)
        irradiance = max(0, irradiance)
        
        # 温度
        daily_temp_var = 8 * np.sin(np.pi * (hour - 6) / 12)
        seasonal_temp = 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        temperature = self.base_temp + daily_temp_var + seasonal_temp
        temperature += self.rng.normal(0, 2)
        
        # 风速
        base_wind = 5 + 3 * np.sin(2 * np.pi * hour / 24)
        wind_speed = base_wind + self.rng.exponential(2)
        wind_speed = np.clip(wind_speed, 0, 30)
        
        return {
            'irradiance': irradiance,
            'temperature': temperature,
            'wind_speed': wind_speed,
            'cloud_cover': self.cloud_cover,
            'humidity': 50 + 30 * self.cloud_cover + self.rng.normal(0, 5)
        }


class ElectricityPriceSimulator:
    """电价模拟器"""
    
    def __init__(self):
        # 分时电价 (元/kWh)
        self.price_profile = {
            'peak': 1.2,      # 高峰 (9-12, 17-21)
            'normal': 0.8,   # 平段
            'valley': 0.4,   # 低谷 (23-7)
        }
        
    def get_price(self, hour: int) -> Dict[str, float]:
        """获取电价"""
        if 23 <= hour or hour < 7:
            period = 'valley'
        elif 9 <= hour < 12 or 17 <= hour < 21:
            period = 'peak'
        else:
            period = 'normal'
        
        buy_price = self.price_profile[period]
        sell_price = buy_price * 0.7  # 上网电价为购电价的70%
        
        return {
            'buy_price': buy_price,
            'sell_price': sell_price,
            'period': period
        }


class MicrogridDigitalTwin:
    """微网数字孪生主类"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化微网数字孪生系统
        
        Args:
            config: 配置字典
        """
        config = config or {}
        
        # 初始化组件
        self.solar = SolarPanel(**config.get('solar', {}))
        self.wind = WindTurbine(**config.get('wind', {}))
        self.battery = BatteryStorage(**config.get('battery', {}))
        self.diesel = DieselGenerator(**config.get('diesel', {}))
        self.load = Load(**config.get('load', {}))
        self.grid = GridConnection(**config.get('grid', {}))
        
        # 模拟器
        self.weather = WeatherSimulator()
        self.price_sim = ElectricityPriceSimulator()
        
        # 时间
        self.current_time = datetime.now()
        self.time_step = timedelta(minutes=1)
        
        # 历史数据
        self.history = {
            'timestamp': [],
            'solar_power': [],
            'wind_power': [],
            'load_power': [],
            'battery_soc': [],
            'battery_power': [],
            'grid_power': [],
            'diesel_power': [],
            'electricity_price': [],
            'weather': [],
            'total_cost': [],
            'renewable_ratio': []
        }
        
        # 累计统计
        self.total_cost = 0.0
        self.total_renewable_energy = 0.0
        self.total_energy_consumed = 0.0
        
    def step(self, action: Optional[Dict] = None) -> Dict:
        """
        执行一个时间步的模拟
        
        Args:
            action: 控制动作字典，包含:
                - battery_action: 电池动作 (-1到1，负为放电，正为充电)
                - diesel_on: 柴油机开关
                
        Returns:
            状态字典
        """
        action = action or {}
        
        # 获取天气和电价
        weather = self.weather.get_conditions(self.current_time)
        price = self.price_sim.get_price(self.current_time.hour)
        
        # 可再生能源发电
        solar_power = self.solar.generate_power(
            weather['irradiance'], 
            weather['temperature']
        )
        wind_power = self.wind.generate_power(weather['wind_speed'])
        renewable_power = solar_power + wind_power
        
        # 负荷
        load_power = self.load.get_load(self.current_time.hour)
        
        # 电池控制
        battery_action = action.get('battery_action', 0)
        battery_power = 0.0
        if battery_action > 0:  # 充电
            power_to_charge = abs(battery_action) * self.battery.max_charge_rate
            _, energy = self.battery.charge(power_to_charge, 1/60)
            battery_power = -power_to_charge  # 负值表示消耗功率
        elif battery_action < 0:  # 放电
            power_to_discharge = abs(battery_action) * self.battery.max_discharge_rate
            _, energy = self.battery.discharge(power_to_discharge, 1/60)
            battery_power = power_to_discharge  # 正值表示提供功率
        
        # 柴油机控制
        diesel_on = action.get('diesel_on', False)
        self.diesel.is_running = diesel_on
        diesel_power, fuel = self.diesel.generate_power(
            max(0, load_power - renewable_power - battery_power)
        )
        
        # 功率平衡
        net_power = renewable_power + battery_power + diesel_power - load_power
        grid_power = self.grid.exchange_power(-net_power)  # 正值为购电
        
        # 计算成本
        if grid_power > 0:
            cost = grid_power * price['buy_price'] / 60  # 每分钟成本
        else:
            cost = grid_power * price['sell_price'] / 60  # 售电收入（负成本）
        
        # 添加柴油成本
        diesel_cost = fuel * 8.0  # 假设柴油8元/升
        cost += diesel_cost
        
        self.total_cost += cost
        
        # 更新统计
        self.total_renewable_energy += (solar_power + wind_power) / 60
        self.total_energy_consumed += load_power / 60
        
        # 计算可再生能源比例
        if self.total_energy_consumed > 0:
            renewable_ratio = self.total_renewable_energy / self.total_energy_consumed
        else:
            renewable_ratio = 0
        
        # 记录历史
        state = {
            'timestamp': self.current_time.isoformat(),
            'solar_power': solar_power,
            'wind_power': wind_power,
            'load_power': load_power,
            'battery_soc': self.battery.soc,
            'battery_power': battery_power,
            'grid_power': grid_power,
            'diesel_power': diesel_power,
            'electricity_price': price['buy_price'],
            'price_period': price['period'],
            'weather': weather,
            'cost': cost,
            'total_cost': self.total_cost,
            'renewable_ratio': renewable_ratio,
            'power_balance': {
                'generation': renewable_power + diesel_power,
                'consumption': load_power,
                'storage': -battery_power,
                'grid': grid_power
            }
        }
        
        # 保存历史
        for key in self.history:
            if key in state:
                self.history[key].append(state[key])
            elif key == 'renewable_ratio':
                self.history[key].append(renewable_ratio)
        
        # 时间推进
        self.current_time += self.time_step
        
        return state
    
    def get_state(self) -> Dict:
        """获取当前系统状态"""
        weather = self.weather.get_conditions(self.current_time)
        price = self.price_sim.get_price(self.current_time.hour)
        
        return {
            'timestamp': self.current_time.isoformat(),
            'components': {
                'solar': {
                    'capacity': self.solar.capacity_kw,
                    'current_power': self.solar.generate_power(
                        weather['irradiance'], weather['temperature']
                    )
                },
                'wind': {
                    'capacity': self.wind.capacity_kw,
                    'current_power': self.wind.generate_power(weather['wind_speed'])
                },
                'battery': {
                    'capacity': self.battery.capacity_kwh,
                    'soc': self.battery.soc,
                    'health': self.battery.health
                },
                'diesel': {
                    'capacity': self.diesel.capacity_kw,
                    'is_running': self.diesel.is_running,
                    'run_hours': self.diesel.run_hours
                },
                'load': {
                    'current': self.load.get_load(self.current_time.hour, 0),
                    'base': self.load.base_load,
                    'peak': self.load.peak_load
                },
                'grid': {
                    'connected': self.grid.is_connected,
                    'max_import': self.grid.max_import,
                    'max_export': self.grid.max_export
                }
            },
            'weather': weather,
            'price': price,
            'statistics': {
                'total_cost': self.total_cost,
                'total_renewable_energy': self.total_renewable_energy,
                'total_energy_consumed': self.total_energy_consumed,
                'renewable_ratio': self.total_renewable_energy / max(1, self.total_energy_consumed)
            }
        }
    
    def reset(self):
        """重置系统状态"""
        self.battery.soc = 0.5
        self.diesel.is_running = False
        self.diesel.run_hours = 0
        self.total_cost = 0.0
        self.total_renewable_energy = 0.0
        self.total_energy_consumed = 0.0
        self.current_time = datetime.now()
        self.history = {key: [] for key in self.history}
        
    def get_observation(self) -> np.ndarray:
        """获取强化学习观测向量"""
        state = self.get_state()
        weather = state['weather']
        
        obs = np.array([
            self.current_time.hour / 24,  # 归一化时间
            state['components']['solar']['current_power'] / self.solar.capacity_kw,
            state['components']['wind']['current_power'] / self.wind.capacity_kw,
            state['components']['load']['current'] / self.load.peak_load,
            self.battery.soc,
            state['price']['buy_price'] / 1.5,  # 归一化电价
            weather['irradiance'] / 1000,
            weather['wind_speed'] / 30,
            weather['temperature'] / 40,
            1.0 if self.grid.is_connected else 0.0
        ], dtype=np.float32)
        
        return obs
    
    def to_json(self) -> str:
        """导出系统状态为JSON"""
        return json.dumps(self.get_state(), indent=2, default=str)
