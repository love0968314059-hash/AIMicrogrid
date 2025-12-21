"""
自然语言交互接口
================

支持用户通过自然语言与微网数字孪生系统交互，
查询系统状态、执行控制命令、获取分析报告等。
"""

import re
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime
import json


class CommandParser:
    """命令解析器"""
    
    def __init__(self):
        # 命令模式定义
        self.patterns = {
            'query_status': [
                r'(查看|显示|查询|获取|告诉我)(系统|微网|当前).*(状态|情况|信息)',
                r'(系统|微网).*(怎么样|如何|状态)',
                r'(current|show|get|display).*(status|state|info)',
            ],
            'query_power': [
                r'(查看|显示|查询|获取).*(功率|发电|出力|power)',
                r'(光伏|风电|太阳能|风力).*(功率|发电|多少)',
                r'(当前|现在).*(功率|发电)',
                r'(功率|发电).*(多少|情况|怎么样)',
                r'(solar|wind|power).*(output|generation|how much)',
            ],
            'query_battery': [
                r'(查看|显示|查询|获取).*(电池|储能|蓄电池|battery)',
                r'(电池|储能).*(电量|状态|soc|容量)',
                r'(battery|storage).*(status|soc|level|charge)',
            ],
            'query_load': [
                r'(查看|显示|查询|获取).*(负荷|负载|用电|load)',
                r'(当前|现在).*(负荷|用电|消耗)',
                r'(current|now).*(load|consumption|demand)',
            ],
            'query_price': [
                r'(查看|显示|查询|获取).*(电价|价格|price)',
                r'(当前|现在).*(电价|价格|多少钱)',
                r'(electricity|power).*(price|cost|rate)',
            ],
            'query_weather': [
                r'(查看|显示|查询|获取).*(天气|气象|weather)',
                r'(天气|气象).*(怎么样|如何)',
                r'(weather|climate|forecast)',
            ],
            'query_cost': [
                r'(查看|显示|查询|获取).*(成本|费用|花费|cost)',
                r'(今天|当前).*(成本|花了多少)',
                r'(total|current).*(cost|expense|spending)',
            ],
            'query_renewable': [
                r'(查看|显示|查询|获取).*(可再生|清洁|绿色).*(能源|比例)',
                r'(renewable|clean|green).*(energy|ratio|percentage)',
            ],
            'control_battery_charge': [
                r'(开始|启动|执行).*电池.*充电',
                r'(充电|charge).*电池',
                r'(start|begin).*(battery|charge)',
            ],
            'control_battery_discharge': [
                r'(开始|启动|执行).*电池.*放电',
                r'(放电|discharge).*电池',
                r'(start|begin).*(discharge)',
            ],
            'control_diesel_on': [
                r'(启动|打开|开启).*柴油.*发电',
                r'(start|turn on|enable).*(diesel|generator)',
            ],
            'control_diesel_off': [
                r'(关闭|停止|关掉).*柴油.*发电',
                r'(stop|turn off|disable).*(diesel|generator)',
            ],
            'generate_report': [
                r'(生成|创建|输出).*报告',
                r'(评估|分析).*策略',
                r'(generate|create|produce).*(report|analysis)',
            ],
            'predict_future': [
                r'(预测|预报|forecast).*未来',
                r'(未来|接下来).*(预测|怎么样)',
                r'(predict|forecast).*(future|next)',
            ],
            'help': [
                r'(帮助|help|指南|guide)',
                r'(怎么用|如何使用|怎么操作)',
                r'(what can you do|how to use)',
            ],
            'strategy_explain': [
                r'(解释|说明|分析).*(策略|决策|action)',
                r'(为什么|why).*(这样|决策|action)',
                r'(explain|describe).*(strategy|decision|action)',
            ],
        }
        
        # 编译正则表达式
        self.compiled_patterns = {}
        for intent, patterns in self.patterns.items():
            self.compiled_patterns[intent] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
    
    def parse(self, text: str) -> Tuple[str, Dict]:
        """
        解析用户输入
        
        Args:
            text: 用户输入文本
            
        Returns:
            (意图, 参数)
        """
        text = text.strip().lower()
        
        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    params = self._extract_params(text, intent)
                    return intent, params
        
        return 'unknown', {'original_text': text}
    
    def _extract_params(self, text: str, intent: str) -> Dict:
        """提取参数"""
        params = {}
        
        # 提取时间参数
        time_match = re.search(r'(\d+)\s*(分钟|小时|天|minute|hour|day)', text)
        if time_match:
            value = int(time_match.group(1))
            unit = time_match.group(2)
            if '分钟' in unit or 'minute' in unit:
                params['duration_minutes'] = value
            elif '小时' in unit or 'hour' in unit:
                params['duration_minutes'] = value * 60
            elif '天' in unit or 'day' in unit:
                params['duration_minutes'] = value * 1440
        
        # 提取数值参数
        value_match = re.search(r'(\d+\.?\d*)\s*(%|kw|kwh|元)', text, re.IGNORECASE)
        if value_match:
            params['value'] = float(value_match.group(1))
            params['unit'] = value_match.group(2).lower()
        
        return params


class NLPInterface:
    """自然语言接口"""
    
    def __init__(self, digital_twin=None, agent=None, evaluator=None, forecaster=None):
        """
        初始化NLP接口
        
        Args:
            digital_twin: 数字孪生系统实例
            agent: 能量管理智能体
            evaluator: 策略评估器
            forecaster: 预测系统
        """
        self.digital_twin = digital_twin
        self.agent = agent
        self.evaluator = evaluator
        self.forecaster = forecaster
        
        self.parser = CommandParser()
        self.conversation_history = []
        
        # 注册处理函数
        self.handlers = {
            'query_status': self._handle_query_status,
            'query_power': self._handle_query_power,
            'query_battery': self._handle_query_battery,
            'query_load': self._handle_query_load,
            'query_price': self._handle_query_price,
            'query_weather': self._handle_query_weather,
            'query_cost': self._handle_query_cost,
            'query_renewable': self._handle_query_renewable,
            'control_battery_charge': self._handle_battery_charge,
            'control_battery_discharge': self._handle_battery_discharge,
            'control_diesel_on': self._handle_diesel_on,
            'control_diesel_off': self._handle_diesel_off,
            'generate_report': self._handle_generate_report,
            'predict_future': self._handle_predict_future,
            'help': self._handle_help,
            'strategy_explain': self._handle_strategy_explain,
            'unknown': self._handle_unknown,
        }
    
    def process(self, user_input: str) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            系统响应
        """
        # 记录对话
        self.conversation_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # 解析意图
        intent, params = self.parser.parse(user_input)
        
        # 处理请求
        handler = self.handlers.get(intent, self._handle_unknown)
        response = handler(params)
        
        # 记录响应
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat(),
            'intent': intent
        })
        
        return response
    
    def _handle_query_status(self, params: Dict) -> str:
        """处理系统状态查询"""
        if not self.digital_twin:
            return "系统未初始化，无法获取状态信息。"
        
        state = self.digital_twin.get_state()
        components = state['components']
        weather = state['weather']
        stats = state['statistics']
        price = state['price']
        
        # 计算功率平衡
        solar_power = components['solar']['current_power']
        wind_power = components['wind']['current_power']
        load_power = components['load']['current']
        renewable_total = solar_power + wind_power
        power_balance = renewable_total - load_power
        
        response = []
        response.append("📊 【微网系统当前状态】")
        response.append(f"⏰ 时间: {state['timestamp']}")
        response.append("")
        
        # 发电设备
        response.append("🔋 发电设备:")
        response.append(f"  ☀️ 光伏: {solar_power:.1f} kW (额定 {components['solar']['capacity']:.0f} kW)")
        response.append(f"  💨 风电: {wind_power:.1f} kW (额定 {components['wind']['capacity']:.0f} kW)")
        response.append(f"  🌿 可再生总出力: {renewable_total:.1f} kW")
        response.append("")
        
        # 储能系统
        battery_soc = components['battery']['soc']
        soc_status = self._get_soc_status_icon(battery_soc)
        response.append("🔌 储能系统:")
        response.append(f"  电池SOC: {battery_soc*100:.1f}% {soc_status}")
        response.append(f"  可用容量: {battery_soc * components['battery']['capacity']:.1f} kWh")
        response.append(f"  健康度: {components['battery']['health']*100:.1f}%")
        response.append("")
        
        # 负荷与电网
        response.append("📈 负荷与电网:")
        response.append(f"  当前负荷: {load_power:.1f} kW")
        response.append(f"  负载率: {load_power/components['load']['peak']*100:.1f}%")
        response.append(f"  电网状态: {'✅ 已连接' if components['grid']['connected'] else '⚠️ 离网'}")
        response.append("")
        
        # 功率流分析
        response.append("⚡ 功率流分析:")
        if power_balance > 0:
            response.append(f"  状态: 🟢 功率盈余 +{power_balance:.1f} kW")
            response.append(f"  建议: 可向电池充电或向电网售电")
        elif power_balance < -10:
            response.append(f"  状态: 🔴 功率缺口 {power_balance:.1f} kW")
            response.append(f"  建议: 需要电池放电或从电网购电")
        else:
            response.append(f"  状态: 🟡 基本平衡 {power_balance:+.1f} kW")
        response.append(f"  自给率: {min(100, renewable_total/max(load_power, 1)*100):.1f}%")
        response.append("")
        
        # 电价信息
        period_names = {'peak': '🔴 高峰', 'normal': '🟡 平段', 'valley': '🟢 低谷'}
        response.append("💰 运行统计:")
        response.append(f"  当前电价: ¥{price['buy_price']:.2f}/kWh ({period_names.get(price['period'], price['period'])})")
        response.append(f"  累计成本: ¥{stats['total_cost']:.2f}")
        response.append(f"  可再生比例: {stats['renewable_ratio']*100:.1f}%")
        response.append(f"  清洁发电: {stats['total_renewable_energy']:.1f} kWh")
        
        return "\n".join(response)
    
    def _get_soc_status_icon(self, soc: float) -> str:
        """获取SOC状态图标"""
        if soc >= 0.8:
            return "⚡ 充足"
        elif soc >= 0.5:
            return "✅ 正常"
        elif soc >= 0.3:
            return "⚠️ 偏低"
        elif soc >= 0.15:
            return "🔶 警告"
        else:
            return "🔴 危险"
    
    def _handle_query_power(self, params: Dict) -> str:
        """处理功率查询"""
        if not self.digital_twin:
            return "系统未初始化。"
        
        state = self.digital_twin.get_state()
        components = state['components']
        weather = state['weather']
        
        solar_power = components['solar']['current_power']
        wind_power = components['wind']['current_power']
        solar_capacity = components['solar']['capacity']
        wind_capacity = components['wind']['capacity']
        load_power = components['load']['current']
        
        total_renewable = solar_power + wind_power
        total_capacity = solar_capacity + wind_capacity
        
        response = []
        response.append("⚡ 【发电功率详情】")
        response.append("")
        
        # 光伏详情
        solar_ratio = solar_power / solar_capacity * 100 if solar_capacity > 0 else 0
        response.append("☀️ 光伏发电系统:")
        response.append(f"   当前出力: {solar_power:.1f} kW")
        response.append(f"   额定容量: {solar_capacity:.1f} kW")
        response.append(f"   利用率: {solar_ratio:.1f}%")
        response.append(f"   {self._get_power_bar(solar_ratio)}")
        response.append(f"   太阳辐照: {weather['irradiance']:.0f} W/m²")
        response.append("")
        
        # 风电详情
        wind_ratio = wind_power / wind_capacity * 100 if wind_capacity > 0 else 0
        response.append("💨 风力发电系统:")
        response.append(f"   当前出力: {wind_power:.1f} kW")
        response.append(f"   额定容量: {wind_capacity:.1f} kW")
        response.append(f"   利用率: {wind_ratio:.1f}%")
        response.append(f"   {self._get_power_bar(wind_ratio)}")
        response.append(f"   当前风速: {weather['wind_speed']:.1f} m/s")
        response.append("")
        
        # 汇总
        response.append("🌿 可再生能源汇总:")
        response.append(f"   总出力: {total_renewable:.1f} kW / {total_capacity:.1f} kW")
        response.append(f"   负荷覆盖率: {total_renewable/max(load_power, 1)*100:.1f}%")
        
        # 功率流向
        power_balance = total_renewable - load_power
        response.append("")
        response.append("⚡ 功率流向:")
        if power_balance > 0:
            response.append(f"   🟢 盈余 {power_balance:.1f} kW → 可充电/售电")
        else:
            response.append(f"   🔴 缺口 {abs(power_balance):.1f} kW → 需放电/购电")
        
        return "\n".join(response)
    
    def _get_power_bar(self, percentage: float) -> str:
        """生成功率条显示"""
        filled = int(percentage / 10)
        empty = 10 - filled
        return f"   [{'█' * filled}{'░' * empty}] {percentage:.0f}%"
    
    def _handle_query_battery(self, params: Dict) -> str:
        """处理电池状态查询"""
        if not self.digital_twin:
            return "系统未初始化。"
        
        state = self.digital_twin.get_state()
        battery = state['components']['battery']
        price = state['price']
        
        soc = battery['soc']
        capacity = battery['capacity']
        current_energy = soc * capacity
        
        response = []
        response.append("🔋 【储能系统详细状态】")
        response.append("")
        
        # 基本信息
        response.append("📊 电池参数:")
        response.append(f"   总容量: {capacity:.1f} kWh")
        response.append(f"   当前电量: {current_energy:.1f} kWh")
        response.append(f"   SOC: {soc*100:.1f}%")
        response.append(f"   {self._get_soc_bar(soc)}")
        response.append("")
        
        # 健康状态
        health = battery['health']
        response.append("💚 健康状态:")
        response.append(f"   健康度: {health*100:.1f}%")
        response.append(f"   有效容量: {capacity * health:.1f} kWh")
        health_status = "优秀" if health > 0.9 else ("良好" if health > 0.8 else ("一般" if health > 0.7 else "需关注"))
        response.append(f"   状态评估: {health_status}")
        response.append("")
        
        # 可用能量分析
        usable_energy = max(0, (soc - 0.1) * capacity)  # 保留10%最低SOC
        chargeable_energy = max(0, (0.9 - soc) * capacity)  # 最高充到90%
        
        response.append("⚡ 能量可用性:")
        response.append(f"   可放电能量: {usable_energy:.1f} kWh")
        response.append(f"   可充电空间: {chargeable_energy:.1f} kWh")
        response.append("")
        
        # 运行建议
        response.append("💡 运行建议:")
        if soc > 0.8:
            response.append("   ⚡ 电量充足，可考虑在高峰时段放电")
            if price['period'] == 'peak':
                response.append("   💰 当前为高峰电价，建议放电售电")
        elif soc > 0.5:
            response.append("   ✅ 电量正常，可灵活调度")
        elif soc > 0.3:
            response.append("   ⚠️ 电量偏低，建议在低谷时段充电")
            if price['period'] == 'valley':
                response.append("   💰 当前为低谷电价，建议充电")
        else:
            response.append("   🔴 电量不足，应优先充电")
            response.append("   避免深度放电以保护电池寿命")
        
        # SOC状态指示
        response.append("")
        status_icon = self._get_soc_status_icon(soc)
        response.append(f"📍 当前状态: {status_icon}")
        
        return "\n".join(response)
    
    def _get_soc_bar(self, soc: float) -> str:
        """生成SOC条形图"""
        filled = int(soc * 20)
        empty = 20 - filled
        # 使用颜色区间
        if soc > 0.6:
            bar_char = '🟩'
        elif soc > 0.3:
            bar_char = '🟨'
        else:
            bar_char = '🟥'
        return f"   [{bar_char * (filled // 2)}{'⬜' * (empty // 2)}]"
    
    def _handle_query_load(self, params: Dict) -> str:
        """处理负荷查询"""
        if not self.digital_twin:
            return "系统未初始化。"
        
        state = self.digital_twin.get_state()
        load = state['components']['load']
        
        response = []
        response.append("📊 【负荷信息】")
        response.append(f"当前负荷: {load['current']:.1f} kW")
        response.append(f"基础负荷: {load['base']:.1f} kW")
        response.append(f"峰值负荷: {load['peak']:.1f} kW")
        response.append(f"负载率: {load['current']/load['peak']*100:.1f}%")
        
        return "\n".join(response)
    
    def _handle_query_price(self, params: Dict) -> str:
        """处理电价查询"""
        if not self.digital_twin:
            return "系统未初始化。"
        
        state = self.digital_twin.get_state()
        price = state['price']
        
        period_names = {'peak': '高峰', 'normal': '平段', 'valley': '低谷'}
        
        response = []
        response.append("💰 【电价信息】")
        response.append(f"当前电价: ¥{price['buy_price']:.2f}/kWh")
        response.append(f"售电价格: ¥{price['sell_price']:.2f}/kWh")
        response.append(f"时段类型: {period_names.get(price['period'], price['period'])}")
        response.append("")
        response.append("分时电价标准:")
        response.append("  高峰(9-12,17-21): ¥1.20/kWh")
        response.append("  平段(7-9,12-17,21-23): ¥0.80/kWh")
        response.append("  低谷(23-7): ¥0.40/kWh")
        
        return "\n".join(response)
    
    def _handle_query_weather(self, params: Dict) -> str:
        """处理天气查询"""
        if not self.digital_twin:
            return "系统未初始化。"
        
        state = self.digital_twin.get_state()
        weather = state['weather']
        
        response = []
        response.append("🌤️ 【天气信息】")
        response.append(f"太阳辐照度: {weather['irradiance']:.0f} W/m²")
        response.append(f"环境温度: {weather['temperature']:.1f} °C")
        response.append(f"风速: {weather['wind_speed']:.1f} m/s")
        response.append(f"云量: {weather['cloud_cover']*100:.0f}%")
        response.append(f"湿度: {weather['humidity']:.0f}%")
        
        return "\n".join(response)
    
    def _handle_query_cost(self, params: Dict) -> str:
        """处理成本查询"""
        if not self.digital_twin:
            return "系统未初始化。"
        
        state = self.digital_twin.get_state()
        stats = state['statistics']
        
        response = []
        response.append("💵 【成本统计】")
        response.append(f"累计总成本: ¥{stats['total_cost']:.2f}")
        response.append(f"总能耗: {stats['total_energy_consumed']:.2f} kWh")
        
        if stats['total_energy_consumed'] > 0:
            avg_cost = stats['total_cost'] / stats['total_energy_consumed']
            response.append(f"平均电价: ¥{avg_cost:.3f}/kWh")
        
        return "\n".join(response)
    
    def _handle_query_renewable(self, params: Dict) -> str:
        """处理可再生能源查询"""
        if not self.digital_twin:
            return "系统未初始化。"
        
        state = self.digital_twin.get_state()
        stats = state['statistics']
        
        response = []
        response.append("🌿 【可再生能源利用】")
        response.append(f"可再生能源发电: {stats['total_renewable_energy']:.2f} kWh")
        response.append(f"总能源消耗: {stats['total_energy_consumed']:.2f} kWh")
        response.append(f"可再生能源比例: {stats['renewable_ratio']*100:.1f}%")
        
        if stats['renewable_ratio'] > 0.8:
            response.append("🌟 优秀！清洁能源利用率很高")
        elif stats['renewable_ratio'] > 0.5:
            response.append("✅ 良好，继续努力提高清洁能源比例")
        else:
            response.append("⚠️ 建议优化调度，提高可再生能源利用率")
        
        return "\n".join(response)
    
    def _handle_battery_charge(self, params: Dict) -> str:
        """处理电池充电命令"""
        if not self.digital_twin:
            return "系统未初始化，无法执行充电命令。"
        
        power = params.get('value', 50)
        return f"⚡ 已发送充电指令\n充电功率: {power:.1f}% 额定功率\n请在下一个时间步查看执行效果。"
    
    def _handle_battery_discharge(self, params: Dict) -> str:
        """处理电池放电命令"""
        if not self.digital_twin:
            return "系统未初始化，无法执行放电命令。"
        
        power = params.get('value', 50)
        return f"🔋 已发送放电指令\n放电功率: {power:.1f}% 额定功率\n请在下一个时间步查看执行效果。"
    
    def _handle_diesel_on(self, params: Dict) -> str:
        """处理柴油机启动命令"""
        return "🏭 已发送柴油发电机启动指令\n预计启动时间: 5分钟\n注意: 请确认可再生能源确实不足。"
    
    def _handle_diesel_off(self, params: Dict) -> str:
        """处理柴油机关闭命令"""
        return "🛑 已发送柴油发电机停机指令\n发电机正在安全停机..."
    
    def _handle_generate_report(self, params: Dict) -> str:
        """处理报告生成请求"""
        if not self.digital_twin or not self.evaluator:
            return "系统组件未完全初始化，无法生成报告。"
        
        metrics = self.evaluator.evaluate_episode(self.digital_twin.history)
        report = self.evaluator.generate_report(metrics)
        return report
    
    def _handle_predict_future(self, params: Dict) -> str:
        """处理未来预测请求"""
        if not self.forecaster:
            return "预测系统未初始化。"
        
        duration = params.get('duration_minutes', 60)
        hour = datetime.now().hour
        minute = datetime.now().minute
        
        forecasts = self.forecaster.forecast_all(hour, minute)
        
        response = []
        response.append(f"🔮 【未来{duration}分钟预测】")
        response.append("")
        response.append("☀️ 光伏发电预测:")
        response.append(f"   平均: {np.mean(forecasts['solar']['mean']):.1f} kW")
        response.append(f"   范围: {np.min(forecasts['solar']['lower_95']):.1f} - {np.max(forecasts['solar']['upper_95']):.1f} kW")
        response.append("")
        response.append("💨 风力发电预测:")
        response.append(f"   平均: {np.mean(forecasts['wind']['mean']):.1f} kW")
        response.append("")
        response.append("📊 负荷预测:")
        response.append(f"   平均: {np.mean(forecasts['load']['mean']):.1f} kW")
        response.append("")
        response.append("💰 电价预测:")
        response.append(f"   平均: ¥{np.mean(forecasts['price']['mean']):.2f}/kWh")
        
        return "\n".join(response)
    
    def _handle_strategy_explain(self, params: Dict) -> str:
        """处理策略解释请求"""
        if not self.agent or not self.digital_twin:
            return "能量管理系统未初始化。"
        
        state = self.digital_twin.get_state()
        
        # 检查是否有详细分析方法
        if hasattr(self.agent, 'format_strategy_display'):
            return self.agent.format_strategy_display(state)
        elif hasattr(self.agent, 'get_detailed_strategy_analysis'):
            analysis = self.agent.get_detailed_strategy_analysis(state)
            return self._format_strategy_analysis(analysis)
        else:
            # 回退到基础解释
            explanation = self.agent.get_policy_explanation(state)
            
            response = []
            response.append("🧠 【能量管理策略分析】")
            response.append("")
            response.append(explanation)
            response.append("")
            response.append("策略制定考虑因素:")
            response.append("  1. 当前可再生能源出力")
            response.append("  2. 负荷需求水平")
            response.append("  3. 电池荷电状态")
            response.append("  4. 实时电价")
            response.append("  5. 天气预报信息")
            
            return "\n".join(response)
    
    def _format_strategy_analysis(self, analysis: Dict) -> str:
        """格式化策略分析结果"""
        lines = []
        lines.append("=" * 50)
        lines.append("  🧠 智能能量管理策略详细分析")
        lines.append("=" * 50)
        lines.append("")
        
        # 当前状况
        cond = analysis.get('current_conditions', {})
        lines.append("📊 【当前系统状况】")
        lines.append(f"   可再生发电: {cond.get('renewable_total', 0):.1f} kW")
        lines.append(f"   负荷需求: {cond.get('load_power', 0):.1f} kW")
        lines.append(f"   功率平衡: {cond.get('power_balance', 0):+.1f} kW")
        lines.append(f"   电池SOC: {cond.get('battery_soc', 50):.1f}%")
        lines.append(f"   电价: ¥{cond.get('electricity_price', 0.8):.2f}/kWh")
        lines.append("")
        
        # 决策结果
        dec = analysis.get('decision', {})
        lines.append("🎯 【策略决策】")
        lines.append(f"   电池操作: {dec.get('battery_action_type', '待机')}")
        lines.append(f"   柴油发电: {'启动' if dec.get('diesel_on', False) else '关闭'}")
        lines.append("")
        
        # 决策因素
        factors = analysis.get('factors', {})
        if factors:
            lines.append("🔍 【关键决策因素】")
            for name, factor in factors.items():
                lines.append(f"   • {factor.get('description', name)}")
        lines.append("")
        
        # 预期结果
        out = analysis.get('expected_outcomes', {})
        lines.append("📈 【预期效果】")
        lines.append(f"   预计成本: ¥{out.get('net_cost', 0):.2f}/h")
        lines.append(f"   电网依赖: {out.get('grid_dependency', '中')}")
        lines.append("")
        
        # 置信度
        conf = analysis.get('confidence', {})
        lines.append(f"🎲 置信度: {conf.get('level', 50):.0f}% - {conf.get('description', '中等')}")
        
        return "\n".join(lines)
    
    def _handle_help(self, params: Dict) -> str:
        """处理帮助请求"""
        response = []
        response.append("📖 【微网数字孪生系统使用指南】")
        response.append("")
        response.append("您可以通过自然语言与系统交互，支持以下功能:")
        response.append("")
        response.append("📊 状态查询:")
        response.append('  - "查看系统状态"')
        response.append('  - "当前功率多少"')
        response.append('  - "电池电量"')
        response.append('  - "今天的负荷情况"')
        response.append('  - "现在电价多少"')
        response.append('  - "天气怎么样"')
        response.append("")
        response.append("🔧 控制命令:")
        response.append('  - "开始充电"')
        response.append('  - "电池放电"')
        response.append('  - "启动柴油发电机"')
        response.append('  - "关闭发电机"')
        response.append("")
        response.append("📈 分析功能:")
        response.append('  - "生成评估报告"')
        response.append('  - "预测未来1小时"')
        response.append('  - "解释当前策略"')
        response.append('  - "可再生能源利用率"')
        response.append("")
        response.append("💡 提示: 您可以用自然的方式提问，系统会理解您的意图。")
        
        return "\n".join(response)
    
    def _handle_unknown(self, params: Dict) -> str:
        """处理未知请求"""
        return (
            "🤔 抱歉，我没有完全理解您的意思。\n\n"
            "您可以尝试:\n"
            '  - "查看系统状态" - 获取微网运行状态\n'
            '  - "电池电量" - 查看储能状态\n'
            '  - "生成报告" - 获取性能评估\n'
            '  - "帮助" - 查看完整功能列表\n\n'
            "请重新描述您的需求，我会尽力帮助您。"
        )
    
    def get_conversation_summary(self) -> str:
        """获取对话摘要"""
        if not self.conversation_history:
            return "暂无对话记录"
        
        summary = []
        summary.append(f"共 {len(self.conversation_history)} 条消息")
        
        # 统计意图
        intents = [msg.get('intent', 'user') for msg in self.conversation_history 
                   if msg['role'] == 'assistant']
        if intents:
            from collections import Counter
            intent_counts = Counter(intents)
            summary.append("常用功能:")
            for intent, count in intent_counts.most_common(3):
                summary.append(f"  - {intent}: {count}次")
        
        return "\n".join(summary)


# 便于导入
import numpy as np
