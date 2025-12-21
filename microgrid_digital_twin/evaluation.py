"""
策略评估模块
============

用于评估能量管理策略的性能，包括成本、可再生能源利用率、
电池健康度等多维度指标。
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class EvaluationMetrics:
    """评估指标数据类"""
    total_cost: float = 0.0
    total_revenue: float = 0.0
    net_cost: float = 0.0
    
    renewable_energy_used: float = 0.0
    total_energy_consumed: float = 0.0
    renewable_ratio: float = 0.0
    
    grid_energy_imported: float = 0.0
    grid_energy_exported: float = 0.0
    grid_dependency: float = 0.0
    
    battery_cycles: float = 0.0
    average_soc: float = 0.0
    soc_violations: int = 0
    
    diesel_runtime_hours: float = 0.0
    diesel_fuel_consumed: float = 0.0
    
    co2_emissions: float = 0.0  # kg
    
    supply_reliability: float = 1.0
    power_quality_index: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            'cost_metrics': {
                'total_cost': round(self.total_cost, 2),
                'total_revenue': round(self.total_revenue, 2),
                'net_cost': round(self.net_cost, 2)
            },
            'energy_metrics': {
                'renewable_energy_used': round(self.renewable_energy_used, 2),
                'total_energy_consumed': round(self.total_energy_consumed, 2),
                'renewable_ratio': round(self.renewable_ratio * 100, 1)
            },
            'grid_metrics': {
                'energy_imported': round(self.grid_energy_imported, 2),
                'energy_exported': round(self.grid_energy_exported, 2),
                'grid_dependency': round(self.grid_dependency * 100, 1)
            },
            'battery_metrics': {
                'cycles': round(self.battery_cycles, 2),
                'average_soc': round(self.average_soc * 100, 1),
                'soc_violations': self.soc_violations
            },
            'environmental_metrics': {
                'diesel_runtime_hours': round(self.diesel_runtime_hours, 2),
                'diesel_fuel_consumed': round(self.diesel_fuel_consumed, 2),
                'co2_emissions': round(self.co2_emissions, 2)
            },
            'reliability_metrics': {
                'supply_reliability': round(self.supply_reliability * 100, 2),
                'power_quality_index': round(self.power_quality_index * 100, 2)
            }
        }


class StrategyEvaluator:
    """策略评估器"""
    
    def __init__(self):
        # CO2排放因子
        self.grid_co2_factor = 0.5  # kg CO2/kWh (电网)
        self.diesel_co2_factor = 2.7  # kg CO2/L (柴油)
        
        # 历史数据
        self.evaluation_history = []
        self.comparison_results = []
        
    def _infer_time_step_minutes(self, history: Dict) -> float:
        """尽量从历史时间戳推断时间步长（分钟）。"""
        try:
            ts = history.get('timestamp') or []
            if len(ts) >= 2:
                t0 = datetime.fromisoformat(ts[0])
                t1 = datetime.fromisoformat(ts[1])
                dt_min = (t1 - t0).total_seconds() / 60.0
                if dt_min > 0:
                    return float(dt_min)
        except Exception:
            pass
        # 兼容旧版本：默认按 1 分钟一步
        return 1.0

    def evaluate_episode(self, history: Dict) -> EvaluationMetrics:
        """
        评估单个回合的表现
        
        Args:
            history: 运行历史数据
            
        Returns:
            评估指标
        """
        metrics = EvaluationMetrics()
        
        if not history.get('solar_power'):
            return metrics

        dt_minutes = self._infer_time_step_minutes(history)
        dt_hours = dt_minutes / 60.0
        
        n_steps = len(history['solar_power'])
        
        # 能量计算 (kWh)
        # 每步能量 = 功率(kW) * dt_hours
        solar_energy = float(np.sum(history.get('solar_power', [])) * dt_hours)
        wind_energy = float(np.sum(history.get('wind_power', [])) * dt_hours)
        load_energy = float(np.sum(history.get('load_power', [])) * dt_hours)
        
        metrics.renewable_energy_used = solar_energy + wind_energy
        metrics.total_energy_consumed = load_energy
        
        if load_energy > 0:
            metrics.renewable_ratio = min(1.0, metrics.renewable_energy_used / load_energy)
        
        # 电网交互
        grid_power = np.array(history.get('grid_power', []))
        metrics.grid_energy_imported = float(np.sum(grid_power[grid_power > 0]) * dt_hours)
        metrics.grid_energy_exported = float(-np.sum(grid_power[grid_power < 0]) * dt_hours)
        
        if load_energy > 0:
            metrics.grid_dependency = metrics.grid_energy_imported / load_energy
        
        # 成本计算
        prices = history.get('electricity_price', [])
        if len(prices) == len(grid_power):
            for i, (power, price) in enumerate(zip(grid_power, prices)):
                if power > 0:
                    metrics.total_cost += float(power * price * dt_hours)
                else:
                    metrics.total_revenue += float(-power * price * 0.7 * dt_hours)  # 售电价格
        
        metrics.net_cost = metrics.total_cost - metrics.total_revenue
        
        # 电池统计
        soc_values = history.get('battery_soc', [])
        if soc_values:
            metrics.average_soc = np.mean(soc_values)
            metrics.soc_violations = sum(1 for soc in soc_values if soc < 0.1 or soc > 0.9)
            
            # 估算充放电循环
            soc_diff = np.abs(np.diff(soc_values))
            metrics.battery_cycles = np.sum(soc_diff) / 2  # 简化计算
        
        # 柴油机统计
        diesel_power = history.get('diesel_power', [])
        if diesel_power:
            diesel_hours = sum(1 for p in diesel_power if p > 0) * dt_hours
            metrics.diesel_runtime_hours = diesel_hours
            metrics.diesel_fuel_consumed = float(np.sum(diesel_power) * 0.3 * dt_hours)  # L
        
        # CO2排放
        metrics.co2_emissions = (
            metrics.grid_energy_imported * self.grid_co2_factor +
            metrics.diesel_fuel_consumed * self.diesel_co2_factor
        )
        
        # 可靠性评估
        if load_energy > 0:
            total_supply = (metrics.renewable_energy_used + 
                          metrics.grid_energy_imported +
                          float(np.sum([max(0, bp) for bp in history.get('battery_power', [])]) * dt_hours))
            metrics.supply_reliability = min(1.0, total_supply / load_energy)
        
        return metrics
    
    def compare_strategies(self, 
                           strategy_results: Dict[str, Dict]) -> Dict:
        """
        比较多个策略的表现
        
        Args:
            strategy_results: {策略名: 历史数据} 字典
            
        Returns:
            比较结果
        """
        comparison = {}
        
        for name, history in strategy_results.items():
            metrics = self.evaluate_episode(history)
            comparison[name] = metrics.to_dict()
        
        # 计算排名
        if len(comparison) > 1:
            rankings = {
                'cost_rank': self._rank_by('cost_metrics.net_cost', comparison, ascending=True),
                'renewable_rank': self._rank_by('energy_metrics.renewable_ratio', comparison, ascending=False),
                'reliability_rank': self._rank_by('reliability_metrics.supply_reliability', comparison, ascending=False)
            }
            comparison['rankings'] = rankings
        
        self.comparison_results.append({
            'timestamp': datetime.now().isoformat(),
            'comparison': comparison
        })
        
        return comparison
    
    def _rank_by(self, metric_path: str, comparison: Dict, ascending: bool = True) -> Dict:
        """根据指标排名"""
        values = {}
        for name, metrics in comparison.items():
            if name == 'rankings':
                continue
            try:
                keys = metric_path.split('.')
                value = metrics
                for key in keys:
                    value = value[key]
                values[name] = value
            except:
                values[name] = float('inf') if ascending else float('-inf')
        
        sorted_items = sorted(values.items(), key=lambda x: x[1], reverse=not ascending)
        return {name: rank + 1 for rank, (name, _) in enumerate(sorted_items)}
    
    def generate_report(self, metrics: EvaluationMetrics, 
                        period: str = "24小时") -> str:
        """
        生成评估报告
        
        Args:
            metrics: 评估指标
            period: 评估周期描述
            
        Returns:
            报告文本
        """
        report = []
        report.append(f"=" * 50)
        report.append(f"微网能量管理策略评估报告")
        report.append(f"评估周期: {period}")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"=" * 50)
        report.append("")
        
        # 成本分析
        report.append("【成本分析】")
        report.append(f"  总购电成本: ¥{metrics.total_cost:.2f}")
        report.append(f"  售电收入:   ¥{metrics.total_revenue:.2f}")
        report.append(f"  净成本:     ¥{metrics.net_cost:.2f}")
        report.append("")
        
        # 能源利用
        report.append("【能源利用】")
        report.append(f"  可再生能源发电: {metrics.renewable_energy_used:.2f} kWh")
        report.append(f"  总负荷消耗:     {metrics.total_energy_consumed:.2f} kWh")
        report.append(f"  可再生能源比例: {metrics.renewable_ratio * 100:.1f}%")
        report.append("")
        
        # 电网交互
        report.append("【电网交互】")
        report.append(f"  购入电量: {metrics.grid_energy_imported:.2f} kWh")
        report.append(f"  售出电量: {metrics.grid_energy_exported:.2f} kWh")
        report.append(f"  电网依赖度: {metrics.grid_dependency * 100:.1f}%")
        report.append("")
        
        # 储能系统
        report.append("【储能系统】")
        report.append(f"  充放电循环: {metrics.battery_cycles:.2f} 次")
        report.append(f"  平均SOC: {metrics.average_soc * 100:.1f}%")
        report.append(f"  SOC越限次数: {metrics.soc_violations} 次")
        report.append("")
        
        # 环境影响
        report.append("【环境影响】")
        report.append(f"  柴油机运行: {metrics.diesel_runtime_hours:.2f} 小时")
        report.append(f"  柴油消耗: {metrics.diesel_fuel_consumed:.2f} 升")
        report.append(f"  CO2排放: {metrics.co2_emissions:.2f} kg")
        report.append("")
        
        # 综合评价
        report.append("【综合评价】")
        score = self._calculate_score(metrics)
        report.append(f"  综合得分: {score:.1f}/100")
        report.append(f"  供电可靠性: {metrics.supply_reliability * 100:.1f}%")
        report.append(f"  评级: {self._get_rating(score)}")
        report.append("")
        
        # 改进建议
        report.append("【改进建议】")
        suggestions = self._generate_suggestions(metrics)
        for i, suggestion in enumerate(suggestions, 1):
            report.append(f"  {i}. {suggestion}")
        
        report.append("")
        report.append("=" * 50)
        
        return "\n".join(report)
    
    def _calculate_score(self, metrics: EvaluationMetrics) -> float:
        """计算综合得分"""
        score = 0.0
        
        # 成本效益 (30分)
        if metrics.total_energy_consumed > 0:
            cost_per_kwh = metrics.net_cost / metrics.total_energy_consumed
            cost_score = max(0, 30 - cost_per_kwh * 20)
            score += cost_score
        
        # 可再生能源利用 (25分)
        score += metrics.renewable_ratio * 25
        
        # 电网独立性 (15分)
        score += (1 - metrics.grid_dependency) * 15
        
        # 电池健康管理 (15分)
        if metrics.soc_violations == 0:
            score += 15
        else:
            score += max(0, 15 - metrics.soc_violations * 0.5)
        
        # 环境友好 (15分)
        if metrics.co2_emissions < 50:
            score += 15
        else:
            score += max(0, 15 - (metrics.co2_emissions - 50) * 0.1)
        
        return min(100, score)
    
    def _get_rating(self, score: float) -> str:
        """根据得分获取评级"""
        if score >= 90:
            return "优秀 ⭐⭐⭐⭐⭐"
        elif score >= 80:
            return "良好 ⭐⭐⭐⭐"
        elif score >= 70:
            return "中等 ⭐⭐⭐"
        elif score >= 60:
            return "及格 ⭐⭐"
        else:
            return "需改进 ⭐"
    
    def _generate_suggestions(self, metrics: EvaluationMetrics) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if metrics.renewable_ratio < 0.5:
            suggestions.append("增加可再生能源装机容量，提高清洁能源利用率")
        
        if metrics.grid_dependency > 0.3:
            suggestions.append("优化储能调度策略，减少对电网的依赖")
        
        if metrics.soc_violations > 10:
            suggestions.append("改进电池SOC管理，避免过充过放")
        
        if metrics.diesel_runtime_hours > 2:
            suggestions.append("减少柴油发电机使用，降低碳排放")
        
        if metrics.battery_cycles > 2:
            suggestions.append("优化电池充放电策略，延长电池寿命")
        
        if not suggestions:
            suggestions.append("当前策略表现良好，建议继续监控优化")
        
        return suggestions


class RealTimeMonitor:
    """实时监控器"""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.power_buffer = {
            'solar': [],
            'wind': [],
            'load': [],
            'battery': [],
            'grid': []
        }
        self.alerts = []
        
    def update(self, state: Dict):
        """更新监控数据"""
        self.power_buffer['solar'].append(state.get('solar_power', 0))
        self.power_buffer['wind'].append(state.get('wind_power', 0))
        self.power_buffer['load'].append(state.get('load_power', 0))
        self.power_buffer['battery'].append(state.get('battery_power', 0))
        self.power_buffer['grid'].append(state.get('grid_power', 0))
        
        # 保持窗口大小
        for key in self.power_buffer:
            if len(self.power_buffer[key]) > self.window_size:
                self.power_buffer[key] = self.power_buffer[key][-self.window_size:]
        
        # 检查告警
        self._check_alerts(state)
    
    def _check_alerts(self, state: Dict):
        """检查并生成告警"""
        current_time = datetime.now()
        
        # 电池SOC告警
        soc = state.get('battery_soc', 0.5)
        if soc < 0.15:
            self.alerts.append({
                'time': current_time,
                'level': 'warning',
                'message': f'电池电量过低: {soc*100:.1f}%'
            })
        elif soc > 0.9:
            self.alerts.append({
                'time': current_time,
                'level': 'info',
                'message': f'电池接近满充: {soc*100:.1f}%'
            })
        
        # 负荷过高告警
        load = state.get('load_power', 0)
        if load > 140:
            self.alerts.append({
                'time': current_time,
                'level': 'warning',
                'message': f'负荷较高: {load:.1f} kW'
            })
        
        # 清理旧告警
        cutoff = current_time - timedelta(minutes=30)
        self.alerts = [a for a in self.alerts if a['time'] > cutoff]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {}
        for key, values in self.power_buffer.items():
            if values:
                stats[key] = {
                    'current': values[-1],
                    'mean': np.mean(values),
                    'max': np.max(values),
                    'min': np.min(values),
                    'std': np.std(values)
                }
        return stats
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """获取最近的告警"""
        return self.alerts[-limit:]
