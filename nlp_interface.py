"""
Natural Language Interface for Microgrid Digital Twin System
Allows users to query and control the system using natural language
"""
import re
from datetime import datetime, timedelta


class NLPInterface:
    """Natural Language Processing Interface"""
    
    def __init__(self, digital_twin):
        self.dt = digital_twin
        
        # Intent patterns
        self.patterns = {
            'status': [
                r'状态|情况|怎么样|如何|运行',
                r'status|how|what|current',
            ],
            'battery': [
                r'电池|储能|soc|电量',
                r'battery|storage|soc|charge',
            ],
            'power': [
                r'功率|发电|负荷|负载',
                r'power|generation|load|demand',
            ],
            'price': [
                r'价格|电价|成本',
                r'price|cost|electricity',
            ],
            'prediction': [
                r'预测|forecast|future|next',
            ],
            'evaluate': [
                r'评估|评价|性能|效果',
                r'evaluate|performance|assess',
            ],
            'control': [
                r'控制|执行|运行|开始|停止',
                r'control|execute|run|start|stop',
            ],
            'statistics': [
                r'统计|数据|历史|累计',
                r'statistics|data|history|cumulative',
            ],
        }
    
    def parse_query(self, query):
        """Parse natural language query"""
        query_lower = query.lower()
        
        # Determine intent
        intent = None
        for intent_name, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    intent = intent_name
                    break
            if intent:
                break
        
        if not intent:
            intent = 'general'
        
        # Extract parameters
        params = {}
        
        # Time references
        if re.search(r'(\d+)\s*(小时|小时前|小时后|hours?|h)', query_lower):
            match = re.search(r'(\d+)\s*(小时|小时前|小时后|hours?|h)', query_lower)
            hours = int(match.group(1))
            if '前' in match.group(2) or 'ago' in query_lower:
                params['hours_offset'] = -hours
            else:
                params['hours_offset'] = hours
        
        # Strategy type
        if re.search(r'rl|强化学习|reinforcement', query_lower):
            params['strategy'] = 'rl'
        elif re.search(r'greedy|贪婪|贪心', query_lower):
            params['strategy'] = 'greedy'
        
        return intent, params
    
    def process_query(self, query):
        """Process query and return response"""
        intent, params = self.parse_query(query)
        
        try:
            if intent == 'status':
                return self.get_status()
            elif intent == 'battery':
                return self.get_battery_info()
            elif intent == 'power':
                return self.get_power_info()
            elif intent == 'price':
                return self.get_price_info()
            elif intent == 'prediction':
                return self.get_prediction(params)
            elif intent == 'evaluate':
                return self.evaluate_strategy(params)
            elif intent == 'statistics':
                return self.get_statistics()
            else:
                return self.get_general_info()
        except Exception as e:
            return f"处理查询时出错: {str(e)}"
    
    def get_status(self):
        """Get system status"""
        status = self.dt.get_status()
        battery_pct = status['battery_soc'] * 100
        pred = status['predictions']
        
        response = f"""系统当前状态：
- 时间: {status['current_time']}
- 电池SOC: {battery_pct:.1f}% ({status['battery_energy']:.1f} kWh)
- 光伏发电: {pred['pv_power']:.1f} kW
- 风电发电: {pred['wind_power']:.1f} kW
- 总可再生能源: {pred['total_renewable']:.1f} kW
- 负荷需求: {pred['load']:.1f} kW
- 电价: ${pred['price']:.3f}/kWh
- 净功率: {pred['total_renewable'] - pred['load']:.1f} kW
"""
        return response
    
    def get_battery_info(self):
        """Get battery information"""
        status = self.dt.get_status()
        battery_pct = status['battery_soc'] * 100
        
        response = f"""电池状态：
- SOC: {battery_pct:.1f}%
- 可用能量: {status['battery_energy']:.1f} kWh
- 总容量: {self.dt.config['battery_capacity']} kWh
- 最大功率: {self.dt.config['battery_max_power']} kW
- 效率: {self.dt.config['battery_efficiency'] * 100:.1f}%
"""
        return response
    
    def get_power_info(self):
        """Get power generation and load information"""
        status = self.dt.get_status()
        pred = status['predictions']
        
        response = f"""功率信息：
- 光伏发电: {pred['pv_power']:.1f} kW
- 风电发电: {pred['wind_power']:.1f} kW
- 总可再生能源: {pred['total_renewable']:.1f} kW
- 负荷需求: {pred['load']:.1f} kW
- 净功率: {pred['total_renewable'] - pred['load']:.1f} kW
"""
        return response
    
    def get_price_info(self):
        """Get price information"""
        status = self.dt.get_status()
        pred = status['predictions']
        stats = status['statistics']
        
        avg_cost = stats['total_cost'] / stats['time_steps'] if stats['time_steps'] > 0 else 0
        
        response = f"""电价信息：
- 当前电价: ${pred['price']:.3f}/kWh
- 累计成本: ${stats['total_cost']:.2f}
- 平均每小时成本: ${avg_cost:.2f}
- 累计购电: {stats['total_energy_imported']:.1f} kWh
- 累计售电: {stats['total_energy_exported']:.1f} kWh
"""
        return response
    
    def get_prediction(self, params):
        """Get predictions"""
        horizon = params.get('hours_offset', 24)
        if horizon < 0:
            return "无法查询过去时间的预测"
        
        predictions = self.dt.prediction_system.predict_horizon(
            start_hour=self.dt.current_time.hour,
            horizon=min(horizon, 24)
        )
        
        response = f"未来{len(predictions)}小时预测：\n"
        for i, pred in enumerate(predictions[:12]):  # Show first 12 hours
            response += f"  {i+1}小时后: PV={pred['pv_power']:.1f}kW, "
            response += f"Wind={pred['wind_power']:.1f}kW, "
            response += f"Load={pred['load']:.1f}kW, "
            response += f"Price=${pred['price']:.3f}/kWh\n"
        
        return response
    
    def evaluate_strategy(self, params):
        """Evaluate energy management strategy"""
        strategy = params.get('strategy', 'rl')
        horizon = 24
        
        result = self.dt.evaluate_strategy(horizon=horizon, strategy=strategy)
        
        response = f"""策略评估结果 ({strategy.upper()}策略，{horizon}小时)：
- 总成本: ${result['total_cost']:.2f}
- 平均每小时成本: ${result['average_cost_per_hour']:.2f}
- 最终SOC: {result['final_soc']*100:.1f}%
- 可再生能源利用率: {result['renewable_utilization']*100:.1f}%
"""
        return response
    
    def get_statistics(self):
        """Get system statistics"""
        status = self.dt.get_status()
        stats = status['statistics']
        
        response = f"""系统统计信息：
- 累计成本: ${stats['total_cost']:.2f}
- 累计购电: {stats['total_energy_imported']:.1f} kWh
- 累计售电: {stats['total_energy_exported']:.1f} kWh
- 可再生能源使用: {stats['total_renewable_used']:.1f} kWh
- 负荷服务: {stats['total_load_served']:.1f} kWh
- 运行时间步: {stats['time_steps']} 小时
"""
        return response
    
    def get_general_info(self):
        """Get general information"""
        return """微网数字孪生系统
可用查询：
- 查询系统状态："系统状态如何？"
- 查询电池："电池电量多少？"
- 查询功率："当前发电和负荷情况？"
- 查询价格："电价是多少？"
- 查询预测："未来24小时预测"
- 评估策略："评估RL策略性能"
- 查询统计："系统统计数据"
"""
