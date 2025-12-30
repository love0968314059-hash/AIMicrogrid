"""
微网数字孪生系统增强演示
============================

展示新增功能:
1. 3D组件交互式详细信息查看
2. 策略执行情况实时显示
3. RL策略与规则策略30天对比
4. 完整30天运行周期模拟
"""

from microgrid_digital_twin.core import MicrogridDigitalTwin
from microgrid_digital_twin.rl_agent import EnergyManagementAgent, RuleBasedAgent
from microgrid_digital_twin.visualization import Visualization3D
import numpy as np
import os
from datetime import datetime, timedelta


def run_30day_comparison():
    """运行30天策略对比模拟"""
    
    print("=" * 60)
    print("微网数字孪生系统 - 30天策略对比模拟")
    print("=" * 60)
    print()
    
    # 初始化系统
    digital_twin = MicrogridDigitalTwin()
    rl_agent = EnergyManagementAgent(state_dim=10, action_dim=2)
    rule_agent = RuleBasedAgent()
    
    print("📊 初始化完成...")
    print(f"⏰ 模拟周期: 30天 (43,200分钟)")
    print(f"⚡ 时间步长: 1分钟")
    print(f"🎯 目标: 对比RL策略与规则策略的性能")
    print()
    
    # 策略对比数据
    strategy_data = {
        'mode': '对比模式',
        'rl_confidence': 0.5,
        'epsilon': 1.0,
        'training_steps': 0,
        'buffer_size': 0,
        'recent_performance': 0,
        'rl_cost': 0,
        'rule_cost': 0,
        'rl_renewable': 0,
        'rule_renewable': 0,
        'comparison_history': {
            'days': [],
            'rl_costs': [],
            'rule_costs': [],
            'rl_renewable': [],
            'rule_renewable': []
        }
    }
    
    # 运行30天模拟
    total_minutes = 30 * 24 * 60  # 43,200分钟
    report_interval = 24 * 60  # 每天报告一次
    
    daily_rl_cost = 0
    daily_rule_cost = 0
    daily_rl_renewable = []
    daily_rule_renewable = []
    
    print("🚀 开始模拟...")
    print()
    
    for minute in range(total_minutes):
        # 获取当前状态
        state = digital_twin.get_state()
        obs = digital_twin.get_observation()
        
        # RL策略决策
        rl_action = rl_agent.select_action(obs, training=True)
        
        # 规则策略决策
        state_dict = {
            'battery_soc': digital_twin.battery.soc,
            'electricity_price': state['price']['buy_price'],
            'solar_power': state['components']['solar']['current_power'],
            'wind_power': state['components']['wind']['current_power'],
            'load_power': state['components']['load']['current']
        }
        rule_action = rule_agent.select_action(state_dict)
        
        # 执行RL策略
        digital_twin_rl = MicrogridDigitalTwin()
        digital_twin_rl.current_time = digital_twin.current_time
        digital_twin_rl.battery.soc = digital_twin.battery.soc
        rl_state = digital_twin_rl.step(rl_action)
        
        # 执行规则策略
        digital_twin_rule = MicrogridDigitalTwin()
        digital_twin_rule.current_time = digital_twin.current_time
        digital_twin_rule.battery.soc = digital_twin.battery.soc
        rule_state = digital_twin_rule.step(rule_action)
        
        # 累计成本和可再生能源比例
        daily_rl_cost += rl_state.get('cost', 0)
        daily_rule_cost += rule_state.get('cost', 0)
        daily_rl_renewable.append(rl_state.get('renewable_ratio', 0))
        daily_rule_renewable.append(rule_state.get('renewable_ratio', 0))
        
        # 训练RL智能体
        reward = rl_agent.calculate_reward(state_dict, rl_action, rl_state)
        next_obs = digital_twin_rl.get_observation()
        rl_agent.train_step(obs, rl_action, reward, next_obs, False)
        
        # 更新主系统状态
        digital_twin.step(rl_action)
        
        # 每天报告一次
        if (minute + 1) % report_interval == 0:
            day = (minute + 1) // report_interval
            
            avg_rl_renewable = np.mean(daily_rl_renewable)
            avg_rule_renewable = np.mean(daily_rule_renewable)
            
            # 记录数据
            strategy_data['comparison_history']['days'].append(day)
            strategy_data['comparison_history']['rl_costs'].append(daily_rl_cost)
            strategy_data['comparison_history']['rule_costs'].append(daily_rule_cost)
            strategy_data['comparison_history']['rl_renewable'].append(avg_rl_renewable)
            strategy_data['comparison_history']['rule_renewable'].append(avg_rule_renewable)
            
            # 打印报告
            savings = (daily_rule_cost - daily_rl_cost) / daily_rule_cost * 100 if daily_rule_cost > 0 else 0
            print(f"📅 第{day}天完成:")
            print(f"   💰 RL策略成本: ¥{daily_rl_cost:.2f}")
            print(f"   💰 规则策略成本: ¥{daily_rule_cost:.2f}")
            print(f"   💵 节省: ¥{daily_rule_cost - daily_rl_cost:.2f} ({savings:.1f}%)")
            print(f"   🌿 RL可再生比例: {avg_rl_renewable*100:.1f}%")
            print(f"   🌿 规则可再生比例: {avg_rule_renewable*100:.1f}%")
            print(f"   📈 训练步数: {rl_agent.training_steps}")
            print(f"   🎲 探索率: {rl_agent.epsilon:.3f}")
            print()
            
            # 重置每日累计
            daily_rl_cost = 0
            daily_rule_cost = 0
            daily_rl_renewable = []
            daily_rule_renewable = []
        
        # 更新策略数据
        strategy_data['training_steps'] = rl_agent.training_steps
        strategy_data['buffer_size'] = len(rl_agent.replay_buffer)
        strategy_data['epsilon'] = rl_agent.epsilon
        strategy_data['rl_confidence'] = min(0.95, 0.5 + minute / (total_minutes * 2))
    
    # 计算总体统计
    total_rl_cost = sum(strategy_data['comparison_history']['rl_costs'])
    total_rule_cost = sum(strategy_data['comparison_history']['rule_costs'])
    avg_rl_renewable = np.mean(strategy_data['comparison_history']['rl_renewable'])
    avg_rule_renewable = np.mean(strategy_data['comparison_history']['rule_renewable'])
    
    strategy_data['rl_cost'] = total_rl_cost
    strategy_data['rule_cost'] = total_rule_cost
    strategy_data['rl_renewable'] = avg_rl_renewable
    strategy_data['rule_renewable'] = avg_rule_renewable
    
    print("=" * 60)
    print("📊 30天模拟完成 - 总体结果")
    print("=" * 60)
    print()
    print(f"💰 RL策略总成本: ¥{total_rl_cost:.2f}")
    print(f"💰 规则策略总成本: ¥{total_rule_cost:.2f}")
    print(f"💵 总节省: ¥{total_rule_cost - total_rl_cost:.2f}")
    print(f"📉 节省比例: {(total_rule_cost - total_rl_cost) / total_rule_cost * 100:.1f}%")
    print()
    print(f"🌿 RL策略平均可再生能源利用率: {avg_rl_renewable*100:.1f}%")
    print(f"🌿 规则策略平均可再生能源利用率: {avg_rule_renewable*100:.1f}%")
    print(f"📈 可再生能源利用率提升: {(avg_rl_renewable - avg_rule_renewable)*100:.1f}%")
    print()
    print(f"🎓 RL智能体训练步数: {strategy_data['training_steps']}")
    print(f"💾 经验池大小: {strategy_data['buffer_size']}")
    print()
    
    # 生成3D可视化
    print("🎨 生成交互式3D可视化...")
    viz = Visualization3D(digital_twin)
    html_path = os.path.join(os.getcwd(), 'microgrid_3d_enhanced.html')
    html_path = viz.save_html(html_path, strategy_data=strategy_data)
    
    print(f"✅ 可视化已保存到: {html_path}")
    print()
    print("🎯 新功能说明:")
    print("   1. 点击3D场景中的组件查看详细信息")
    print("   2. 点击右侧📊按钮查看策略分析面板")
    print("   3. 策略面板包含执行情况和30天对比")
    print("   4. 系统自动运行30天模拟周期")
    print()
    
    return strategy_data


def show_component_details():
    """展示可交互组件列表"""
    print("=" * 60)
    print("🖱️ 可交互3D组件")
    print("=" * 60)
    print()
    print("点击以下组件查看详细信息:")
    print()
    print("1. ☀️ 光伏阵列")
    print("   - 实时发电功率和利用率")
    print("   - 环境条件（辐照度、温度、云量）")
    print("   - 技术参数（转换效率、面板面积）")
    print()
    print("2. 🔋 储能系统")
    print("   - 电池SOC和剩余容量")
    print("   - 充放电参数和效率")
    print("   - 安全运行范围")
    print()
    print("3. 🏭 负荷中心")
    print("   - 当前负荷和负荷率")
    print("   - 用电统计和成本")
    print("   - 负荷类型分析")
    print()
    print("4. 🎛️ 控制中心")
    print("   - 系统运行模式和策略")
    print("   - 通讯状态监控")
    print("   - 数据采集配置")
    print()


def show_strategy_panel_guide():
    """展示策略面板使用指南"""
    print("=" * 60)
    print("📊 策略分析面板使用指南")
    print("=" * 60)
    print()
    print("📍 位置: 点击界面右侧的📊按钮打开")
    print()
    print("🔖 标签1: 执行情况")
    print("   - 当前策略状态（模式、置信度、探索率）")
    print("   - 实时决策建议（电池、柴油机操作）")
    print("   - 训练统计（步数、经验池、表现）")
    print()
    print("🔖 标签2: 策略对比")
    print("   - 30天成本对比曲线图")
    print("   - RL策略 vs 规则策略成本统计")
    print("   - 可再生能源利用率对比")
    print("   - 节省比例计算")
    print()


if __name__ == "__main__":
    print()
    print("🔌 微网数字孪生系统 - 增强版演示")
    print("=" * 60)
    print()
    
    # 显示新功能介绍
    show_component_details()
    print()
    show_strategy_panel_guide()
    print()
    
    # 询问是否运行完整模拟
    print("⚠️  注意: 完整30天模拟需要较长时间（约10-30分钟）")
    print()
    run_choice = input("是否运行完整30天模拟? (y/n): ").strip().lower()
    
    if run_choice == 'y':
        print()
        strategy_data = run_30day_comparison()
        print("✅ 演示完成！")
        print()
        print(f"📂 打开 {os.path.join(os.getcwd(), 'microgrid_3d_enhanced.html')} 查看完整可视化界面")
    else:
        print()
        print("💡 您可以直接打开 /workspace/microgrid_3d_visualization.html")
        print("   体验交互式3D可视化和策略分析功能！")
        print()
        print("🎮 功能体验:")
        print("   1. 点击组件查看详细信息")
        print("   2. 打开策略面板查看分析数据")
        print("   3. 开始模拟观察30天运行效果")
    
    print()
