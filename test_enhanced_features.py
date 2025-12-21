"""
测试增强功能
"""

from microgrid_digital_twin.core import MicrogridDigitalTwin
from microgrid_digital_twin.visualization import Visualization3D
from datetime import timedelta

def test_30day_simulation():
    """测试30天模拟周期"""
    print("测试1: 30天模拟周期")
    print("-" * 40)
    
    dt = MicrogridDigitalTwin()
    
    # 检查初始设置
    assert dt.simulation_duration == timedelta(days=30), "模拟周期应为30天"
    print("✅ 模拟周期设置正确: 30天")
    
    # 检查经过时间计算
    elapsed = dt.get_elapsed_days()
    assert elapsed == 0, "初始经过天数应为0"
    print(f"✅ 初始经过天数: {elapsed}天")
    
    # 模拟几步
    for _ in range(1440):  # 模拟1天
        dt.step()
    
    elapsed = dt.get_elapsed_days()
    print(f"✅ 模拟1天后经过天数: {elapsed:.2f}天")
    
    # 检查是否完成
    is_complete = dt.is_simulation_complete()
    print(f"✅ 30天模拟是否完成: {is_complete} (预期: False)")
    
    print()


def test_visualization_with_strategy():
    """测试可视化模块支持策略数据"""
    print("测试2: 可视化模块策略数据支持")
    print("-" * 40)
    
    dt = MicrogridDigitalTwin()
    viz = Visualization3D(dt)
    
    # 准备测试策略数据
    strategy_data = {
        'mode': '测试模式',
        'rl_confidence': 0.75,
        'epsilon': 0.15,
        'training_steps': 1000,
        'buffer_size': 500,
        'recent_performance': 0.82,
        'rl_cost': 150.5,
        'rule_cost': 180.2,
        'rl_renewable': 0.85,
        'rule_renewable': 0.78,
        'comparison_history': {
            'days': [1, 2, 3],
            'rl_costs': [50.0, 55.0, 45.5],
            'rule_costs': [60.0, 62.0, 58.2],
            'rl_renewable': [0.84, 0.86, 0.85],
            'rule_renewable': [0.77, 0.79, 0.78]
        }
    }
    
    # 生成HTML
    html = viz.generate(strategy_data)
    
    # 检查是否包含策略数据
    assert 'strategy-panel' in html, "HTML应包含策略面板"
    assert 'comparison-chart' in html, "HTML应包含对比图表"
    assert 'component-modal' in html, "HTML应包含组件详情模态窗口"
    
    print("✅ HTML包含策略面板")
    print("✅ HTML包含对比图表")
    print("✅ HTML包含组件详情模态窗口")
    
    # 保存测试文件
    test_path = '/workspace/test_visualization.html'
    viz.save_html(test_path)
    print(f"✅ 测试可视化已保存: {test_path}")
    
    print()


def test_component_interaction():
    """测试组件交互功能"""
    print("测试3: 组件交互功能")
    print("-" * 40)
    
    dt = MicrogridDigitalTwin()
    viz = Visualization3D(dt)
    html = viz.generate()
    
    # 检查交互功能
    interactive_elements = [
        'clickableObjects',
        'onCanvasClick',
        'showComponentDetail',
        'getSolarDetail',
        'getBatteryDetail',
        'getLoadDetail',
        'getControlDetail'
    ]
    
    for element in interactive_elements:
        assert element in html, f"HTML应包含{element}函数"
        print(f"✅ 包含{element}功能")
    
    print()


def test_strategy_panel_functions():
    """测试策略面板功能"""
    print("测试4: 策略面板功能")
    print("-" * 40)
    
    dt = MicrogridDigitalTwin()
    viz = Visualization3D(dt)
    html = viz.generate()
    
    # 检查策略相关功能
    strategy_elements = [
        'updateStrategyDisplay',
        'drawComparisonChart',
        'toggle-strategy',
        'strategy-tab',
        'execution-content',
        'comparison-content'
    ]
    
    for element in strategy_elements:
        assert element in html, f"HTML应包含{element}"
        print(f"✅ 包含{element}元素/功能")
    
    print()


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("微网数字孪生系统 - 增强功能测试")
    print("=" * 50)
    print()
    
    try:
        test_30day_simulation()
        test_visualization_with_strategy()
        test_component_interaction()
        test_strategy_panel_functions()
        
        print("=" * 50)
        print("🎉 所有测试通过！")
        print("=" * 50)
        print()
        print("✅ 30天模拟周期功能正常")
        print("✅ 可视化策略数据支持正常")
        print("✅ 组件交互功能正常")
        print("✅ 策略面板功能正常")
        print()
        print("📂 可以打开以下文件查看效果:")
        print("   - /workspace/microgrid_3d_visualization.html (主界面)")
        print("   - /workspace/test_visualization.html (测试界面)")
        print()
        
        return True
        
    except AssertionError as e:
        print()
        print("❌ 测试失败:")
        print(f"   {str(e)}")
        return False
    except Exception as e:
        print()
        print("❌ 测试出错:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
