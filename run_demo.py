#!/usr/bin/env python3
"""
微网数字孪生系统 - 简化演示脚本
运行一个短时间的模拟演示
"""

import sys

# 检查依赖
try:
    import numpy as np
except ImportError:
    print("❌ 错误: NumPy 未安装")
    print()
    print("请先安装依赖:")
    print("  pip3 install numpy")
    print("  或")
    print("  pip3 install -r requirements.txt")
    sys.exit(1)

from microgrid_digital_twin.core import MicrogridDigitalTwin
from microgrid_digital_twin.rl_agent import EnergyManagementAgent, AdaptiveEnergyManager
from microgrid_digital_twin.prediction import IntegratedForecaster

def run_short_demo():
    """运行一个短时间的演示（1小时）"""
    
    print("=" * 60)
    print("🔌 微网数字孪生系统 - 快速演示")
    print("=" * 60)
    print()
    
    # 初始化系统
    print("📊 初始化系统...")
    digital_twin = MicrogridDigitalTwin()
    manager = AdaptiveEnergyManager()
    forecaster = IntegratedForecaster(prediction_horizon=60)
    
    print("✅ 系统初始化完成")
    print(f"   - 光伏容量: {digital_twin.solar.capacity_kw} kW")
    print(f"   - 风电容量: {digital_twin.wind.capacity_kw} kW")
    print(f"   - 电池容量: {digital_twin.battery.capacity_kwh} kWh")
    print()
    
    # 运行1小时模拟（60分钟）
    print("⚡ 开始模拟（1小时，60分钟）...")
    print()
    
    total_minutes = 60
    report_interval = 10  # 每10分钟报告一次
    
    for minute in range(total_minutes):
        # 获取状态
        state = digital_twin.get_state()
        obs = digital_twin.get_observation()
        
        # 更新预测器
        forecaster.update(
            state['components']['solar']['current_power'],
            state['components']['wind']['current_power'],
            state['price']['buy_price'],
            state['components']['load']['current']
        )
        
        # 选择动作
        action = manager.select_action(obs, state, training=True)
        
        # 执行一步
        result = digital_twin.step(action)
        
        # 计算奖励并训练
        reward = manager.rl_agent.calculate_reward(state, action, result)
        next_obs = digital_twin.get_observation()
        manager.train(obs, action, reward, next_obs, False)
        
        # 定期报告
        if (minute + 1) % report_interval == 0:
            print(f"⏰ 第 {minute + 1} 分钟:")
            print(f"   ☀️  光伏: {result['solar_power']:.1f} kW")
            print(f"   💨 风电: {result['wind_power']:.1f} kW")
            print(f"   📈 负荷: {result['load_power']:.1f} kW")
            print(f"   🔋 电池SOC: {result['battery_soc']:.1%}")
            print(f"   ⚡ 电池功率: {result['battery_power']:.1f} kW")
            print(f"   🔌 电网: {result['grid_power']:.1f} kW")
            print(f"   💰 累计成本: ¥{result['total_cost']:.2f}")
            print(f"   🌿 可再生比例: {result['renewable_ratio']:.1%}")
            print()
    
    # 最终统计
    print("=" * 60)
    print("📊 模拟完成 - 最终统计")
    print("=" * 60)
    print()
    
    final_state = digital_twin.get_state()
    stats = final_state['statistics']
    
    print(f"💰 总成本: ¥{stats['total_cost']:.2f}")
    print(f"⚡ 总发电量: {stats['total_renewable_energy']:.2f} kWh")
    print(f"📈 总用电量: {stats['total_energy_consumed']:.2f} kWh")
    print(f"🌿 可再生能源比例: {stats['renewable_ratio']:.1%}")
    print()
    
    # RL智能体状态
    manager_status = manager.get_status()
    print("🤖 RL智能体状态:")
    print(f"   - 模式: {manager_status['mode']}")
    print(f"   - RL置信度: {manager_status['rl_confidence']:.2%}")
    print(f"   - 探索率: {manager_status['epsilon']:.3f}")
    print(f"   - 训练步数: {manager_status['training_steps']}")
    print(f"   - 经验池大小: {manager_status['buffer_size']}")
    print()
    
    # 预测示例
    print("🔮 预测示例（未来1小时）:")
    current_hour = digital_twin.current_time.hour
    current_minute = digital_twin.current_time.minute
    forecasts = forecaster.forecast_all(current_hour, current_minute)
    
    print(f"   ☀️  光伏预测: {forecasts['solar']['mean'].mean():.1f} kW")
    print(f"   💨 风电预测: {forecasts['wind']['mean'].mean():.1f} kW")
    print(f"   📈 负荷预测: {forecasts['load']['mean'].mean():.1f} kW")
    print(f"   💰 电价预测: ¥{forecasts['price']['mean'].mean():.2f}/kWh")
    print()
    
    print("✅ 演示完成！")
    print()
    print("💡 提示:")
    print("   - 运行完整30天模拟: python3 demo_enhanced.py")
    print("   - 打开3D可视化: 在浏览器中打开 microgrid_3d_visualization.html")
    print()

if __name__ == "__main__":
    try:
        run_short_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

