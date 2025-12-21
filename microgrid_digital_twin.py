"""
微网数字孪生核心系统
包含发电、储能、负荷模型以及物理仿真
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json
from datetime import datetime, timedelta


@dataclass
class MicrogridState:
    """微网状态"""
    time_step: int
    solar_power: float  # kW
    wind_power: float  # kW
    battery_soc: float  # 0-1
    battery_power: float  # kW (正为充电，负为放电)
    grid_power: float  # kW (正为买电，负为卖电)
    load_demand: float  # kW
    electricity_price: float  # ¥/kWh
    total_cost: float  # ¥
    renewable_ratio: float  # 可再生能源占比
    
    def to_dict(self):
        return {
            'time_step': self.time_step,
            'solar_power': round(self.solar_power, 2),
            'wind_power': round(self.wind_power, 2),
            'battery_soc': round(self.battery_soc, 3),
            'battery_power': round(self.battery_power, 2),
            'grid_power': round(self.grid_power, 2),
            'load_demand': round(self.load_demand, 2),
            'electricity_price': round(self.electricity_price, 4),
            'total_cost': round(self.total_cost, 2),
            'renewable_ratio': round(self.renewable_ratio, 3)
        }


class MicrogridDigitalTwin:
    """微网数字孪生系统"""
    
    def __init__(self, config: Dict = None):
        # 默认配置
        self.config = config or {
            'solar_capacity': 100,  # kW
            'wind_capacity': 80,  # kW
            'battery_capacity': 200,  # kWh
            'battery_max_power': 50,  # kW
            'battery_efficiency': 0.95,
            'grid_max_power': 150,  # kW
            'initial_soc': 0.5,
            'time_step_hours': 0.25,  # 15分钟
        }
        
        # 状态变量
        self.current_time_step = 0
        self.battery_soc = self.config['initial_soc']
        self.total_cost = 0.0
        self.history: List[MicrogridState] = []
        
        # 生成基础数据
        self._generate_base_profiles()
        
    def _generate_base_profiles(self, days=7):
        """生成基础的太阳能、风能、负荷和电价曲线"""
        hours = days * 24
        time_steps = int(hours / self.config['time_step_hours'])
        
        # 太阳能功率曲线（模拟日出日落）
        self.solar_profile = []
        for t in range(time_steps):
            hour = (t * self.config['time_step_hours']) % 24
            if 6 <= hour <= 18:
                # 白天使用正弦曲线模拟
                solar_ratio = np.sin(np.pi * (hour - 6) / 12)
                noise = np.random.normal(0, 0.1)
                solar_power = max(0, self.config['solar_capacity'] * solar_ratio * (1 + noise))
            else:
                solar_power = 0
            self.solar_profile.append(solar_power)
        
        # 风能功率曲线（更随机，但有日夜周期）
        self.wind_profile = []
        base_wind = np.random.uniform(0.3, 0.7, time_steps)
        for t in range(time_steps):
            hour = (t * self.config['time_step_hours']) % 24
            # 夜间风力通常更强
            if 20 <= hour or hour <= 6:
                wind_factor = 1.3
            else:
                wind_factor = 0.9
            noise = np.random.normal(0, 0.15)
            wind_power = max(0, min(self.config['wind_capacity'], 
                                   self.config['wind_capacity'] * base_wind[t] * wind_factor * (1 + noise)))
            self.wind_profile.append(wind_power)
        
        # 负荷曲线（模拟典型日负荷）
        self.load_profile = []
        for t in range(time_steps):
            hour = (t * self.config['time_step_hours']) % 24
            if 8 <= hour <= 22:
                # 白天高负荷
                base_load = 70 + 30 * np.sin(np.pi * (hour - 8) / 14)
            else:
                # 夜间低负荷
                base_load = 30
            noise = np.random.normal(0, 5)
            load = max(20, base_load + noise)
            self.load_profile.append(load)
        
        # 电价曲线（峰谷电价）
        self.price_profile = []
        for t in range(time_steps):
            hour = (t * self.config['time_step_hours']) % 24
            if 8 <= hour <= 11 or 18 <= hour <= 21:
                # 峰时电价
                price = 1.2 + np.random.normal(0, 0.05)
            elif 23 <= hour or hour <= 6:
                # 谷时电价
                price = 0.4 + np.random.normal(0, 0.03)
            else:
                # 平时电价
                price = 0.8 + np.random.normal(0, 0.04)
            self.price_profile.append(max(0.3, price))
    
    def reset(self):
        """重置系统"""
        self.current_time_step = 0
        self.battery_soc = self.config['initial_soc']
        self.total_cost = 0.0
        self.history = []
        return self.get_observation()
    
    def get_observation(self) -> np.ndarray:
        """获取当前观测状态（用于强化学习）"""
        t = self.current_time_step % len(self.solar_profile)
        
        # 当前状态
        solar = self.solar_profile[t]
        wind = self.wind_profile[t]
        load = self.load_profile[t]
        price = self.price_profile[t]
        
        # 预测未来4个时间步（1小时）
        future_steps = 4
        solar_forecast = []
        wind_forecast = []
        load_forecast = []
        price_forecast = []
        
        for i in range(1, future_steps + 1):
            ft = (t + i) % len(self.solar_profile)
            solar_forecast.append(self.solar_profile[ft])
            wind_forecast.append(self.wind_profile[ft])
            load_forecast.append(self.load_profile[ft])
            price_forecast.append(self.price_profile[ft])
        
        obs = np.array([
            solar / self.config['solar_capacity'],
            wind / self.config['wind_capacity'],
            load / 100.0,
            price,
            self.battery_soc,
            np.mean(solar_forecast) / self.config['solar_capacity'],
            np.mean(wind_forecast) / self.config['wind_capacity'],
            np.mean(load_forecast) / 100.0,
            np.mean(price_forecast),
        ], dtype=np.float32)
        
        return obs
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        执行一步仿真
        action: [battery_power_ratio, grid_power_ratio]
                battery_power_ratio: -1到1，负为放电，正为充电
                grid_power_ratio: -1到1，负为卖电，正为买电
        """
        t = self.current_time_step % len(self.solar_profile)
        
        # 获取当前发电和负荷
        solar = self.solar_profile[t]
        wind = self.wind_profile[t]
        load = self.load_profile[t]
        price = self.price_profile[t]
        
        renewable_generation = solar + wind
        
        # 解析动作
        battery_power_ratio = np.clip(action[0], -1, 1)
        battery_power = battery_power_ratio * self.config['battery_max_power']
        
        # 电池功率约束（考虑SOC限制）
        if battery_power > 0:  # 充电
            max_charge = (1.0 - self.battery_soc) * self.config['battery_capacity'] / self.config['time_step_hours']
            battery_power = min(battery_power, max_charge)
        else:  # 放电
            max_discharge = self.battery_soc * self.config['battery_capacity'] / self.config['time_step_hours']
            battery_power = max(battery_power, -max_discharge)
        
        # 功率平衡
        net_power = renewable_generation - load - battery_power
        grid_power = -net_power  # 正为买电，负为卖电
        
        # 电网功率约束
        grid_power = np.clip(grid_power, -self.config['grid_max_power'], self.config['grid_max_power'])
        
        # 更新电池SOC
        battery_energy_change = battery_power * self.config['time_step_hours']
        if battery_power > 0:
            battery_energy_change *= self.config['battery_efficiency']
        else:
            battery_energy_change /= self.config['battery_efficiency']
        
        self.battery_soc += battery_energy_change / self.config['battery_capacity']
        self.battery_soc = np.clip(self.battery_soc, 0.0, 1.0)
        
        # 计算成本
        if grid_power > 0:
            # 买电
            cost = grid_power * self.config['time_step_hours'] * price
        else:
            # 卖电（收益为负成本）
            sell_price = price * 0.6  # 卖电价格通常低于买电价格
            cost = grid_power * self.config['time_step_hours'] * sell_price
        
        self.total_cost += cost
        
        # 计算可再生能源使用率
        renewable_used = min(renewable_generation, load + max(0, battery_power))
        renewable_ratio = renewable_used / load if load > 0 else 0
        
        # 保存状态
        state = MicrogridState(
            time_step=self.current_time_step,
            solar_power=solar,
            wind_power=wind,
            battery_soc=self.battery_soc,
            battery_power=battery_power,
            grid_power=grid_power,
            load_demand=load,
            electricity_price=price,
            total_cost=self.total_cost,
            renewable_ratio=renewable_ratio
        )
        self.history.append(state)
        
        # 计算奖励（强化学习）
        reward = -cost  # 最小化成本
        reward += renewable_ratio * 10  # 奖励使用可再生能源
        reward -= abs(grid_power) * 0.01  # 惩罚电网功率波动
        
        # 电池健康惩罚
        if self.battery_soc < 0.2 or self.battery_soc > 0.9:
            reward -= 5
        
        self.current_time_step += 1
        done = self.current_time_step >= len(self.solar_profile)
        
        next_obs = self.get_observation() if not done else np.zeros_like(self.get_observation())
        
        info = {
            'cost': cost,
            'renewable_ratio': renewable_ratio,
            'battery_soc': self.battery_soc
        }
        
        return next_obs, reward, done, info
    
    def get_current_state(self) -> MicrogridState:
        """获取当前状态"""
        if self.history:
            return self.history[-1]
        return None
    
    def get_statistics(self) -> Dict:
        """获取运行统计数据"""
        if not self.history:
            return {}
        
        states = self.history
        return {
            'total_cost': self.total_cost,
            'avg_renewable_ratio': np.mean([s.renewable_ratio for s in states]),
            'avg_battery_soc': np.mean([s.battery_soc for s in states]),
            'total_solar_energy': sum([s.solar_power for s in states]) * self.config['time_step_hours'],
            'total_wind_energy': sum([s.wind_power for s in states]) * self.config['time_step_hours'],
            'total_load_energy': sum([s.load_demand for s in states]) * self.config['time_step_hours'],
            'max_grid_import': max([s.grid_power for s in states if s.grid_power > 0], default=0),
            'max_grid_export': min([s.grid_power for s in states if s.grid_power < 0], default=0),
            'time_steps': len(states)
        }
    
    def query_state(self, query: str) -> str:
        """自然语言查询系统状态"""
        query = query.lower()
        
        if not self.history:
            return "系统尚未运行，没有可用数据。"
        
        current = self.get_current_state()
        stats = self.get_statistics()
        
        # 关键词匹配
        if '电池' in query or 'battery' in query or 'soc' in query:
            return f"当前电池SOC为{current.battery_soc*100:.1f}%，电池功率为{current.battery_power:.2f}kW（{'充电' if current.battery_power > 0 else '放电'}）。平均SOC为{stats['avg_battery_soc']*100:.1f}%。"
        
        elif '成本' in query or 'cost' in query or '费用' in query:
            return f"当前总成本为¥{stats['total_cost']:.2f}，当前电价为¥{current.electricity_price:.2f}/kWh。"
        
        elif '太阳能' in query or 'solar' in query or '光伏' in query:
            return f"当前太阳能发电{current.solar_power:.2f}kW，总发电量{stats['total_solar_energy']:.2f}kWh。"
        
        elif '风' in query or 'wind' in query:
            return f"当前风电发电{current.wind_power:.2f}kW，总发电量{stats['total_wind_energy']:.2f}kWh。"
        
        elif '负荷' in query or 'load' in query or '用电' in query:
            return f"当前负荷需求{current.load_demand:.2f}kW，总用电量{stats['total_load_energy']:.2f}kWh。"
        
        elif '电网' in query or 'grid' in query:
            return f"当前电网功率{current.grid_power:.2f}kW（{'买电' if current.grid_power > 0 else '卖电'}）。最大买电{stats['max_grid_import']:.2f}kW，最大卖电{abs(stats['max_grid_export']):.2f}kW。"
        
        elif '可再生' in query or 'renewable' in query or '绿色' in query:
            return f"当前可再生能源使用率{current.renewable_ratio*100:.1f}%，平均使用率{stats['avg_renewable_ratio']*100:.1f}%。"
        
        elif '概览' in query or '总结' in query or 'summary' in query or '状态' in query:
            renewable_gen = current.solar_power + current.wind_power
            return f"""微网系统运行概览（时间步{current.time_step}）:
            
发电情况：
- 太阳能: {current.solar_power:.2f} kW
- 风电: {current.wind_power:.2f} kW  
- 总可再生发电: {renewable_gen:.2f} kW

用电情况：
- 负荷需求: {current.load_demand:.2f} kW
- 电网功率: {current.grid_power:.2f} kW ({'买电' if current.grid_power > 0 else '卖电'})
- 电池功率: {current.battery_power:.2f} kW ({'充电' if current.battery_power > 0 else '放电'})

系统状态：
- 电池SOC: {current.battery_soc*100:.1f}%
- 可再生能源使用率: {current.renewable_ratio*100:.1f}%
- 当前电价: ¥{current.electricity_price:.2f}/kWh
- 累计成本: ¥{stats['total_cost']:.2f}
"""
        else:
            return f"未识别查询。当前时间步{current.time_step}，可查询：电池、成本、太阳能、风电、负荷、电网、可再生能源、概览。"


if __name__ == "__main__":
    # 测试数字孪生系统
    microgrid = MicrogridDigitalTwin()
    obs = microgrid.reset()
    
    print("初始观测:", obs)
    print("\n运行10个时间步...")
    
    for i in range(10):
        # 随机动作
        action = np.random.uniform(-0.5, 0.5, 2)
        obs, reward, done, info = microgrid.step(action)
        print(f"\nStep {i+1}:")
        print(f"  Reward: {reward:.2f}")
        print(f"  Cost: ¥{info['cost']:.2f}")
        print(f"  Renewable Ratio: {info['renewable_ratio']*100:.1f}%")
        print(f"  Battery SOC: {info['battery_soc']*100:.1f}%")
    
    print("\n\n===== 自然语言查询测试 =====")
    print(microgrid.query_state("当前系统概览"))
    print("\n" + "="*50 + "\n")
    print(microgrid.query_state("电池状态如何"))
