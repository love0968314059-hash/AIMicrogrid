"""
微网数字孪生系统主应用
集成所有功能模块，提供Gradio Web界面
"""

import numpy as np
import gradio as gr
import plotly.graph_objects as go
from typing import Tuple, Dict
import json
import time
import threading

from microgrid_digital_twin import MicrogridDigitalTwin, MicrogridState
from prediction_system import MicrogridPredictor
from rl_energy_management import RLEnergyManager, RuleBasedController
from visualization_3d import Microgrid3DVisualizer


class MicrogridSystem:
    """微网数字孪生系统主控制器"""
    
    def __init__(self):
        # 初始化各个子系统
        self.microgrid = MicrogridDigitalTwin()
        self.predictor = MicrogridPredictor()
        self.rl_manager = RLEnergyManager(state_dim=9, action_dim=2)
        self.rule_controller = RuleBasedController()
        self.visualizer = Microgrid3DVisualizer()
        
        # 系统状态
        self.is_running = False
        self.current_step = 0
        self.control_mode = 'RL'  # 'RL' or 'Rule' or 'Manual'
        self.auto_run = False
        
        # 训练状态
        self.is_training = False
        self.training_episodes = 0
        
        print("✓ 微网数字孪生系统初始化完成")
    
    def reset_system(self):
        """重置系统"""
        self.microgrid.reset()
        self.current_step = 0
        self.predictor = MicrogridPredictor()
        print("系统已重置")
        return self.get_current_info()
    
    def step_forward(self, control_mode='RL', battery_action=0.0, grid_action=0.0):
        """前进一步"""
        # 获取当前观测
        obs = self.microgrid.get_observation()
        
        # 更新预测器历史
        if self.microgrid.history:
            last_state = self.microgrid.history[-1]
            self.predictor.update_history(
                last_state.solar_power,
                last_state.wind_power,
                last_state.load_demand,
                last_state.electricity_price,
                last_state.time_step
            )
        
        # 根据控制模式选择动作
        if control_mode == 'RL':
            action = self.rl_manager.get_action(obs)
        elif control_mode == 'Rule':
            action = self.rule_controller.get_action(obs)
        else:  # Manual
            action = np.array([battery_action, grid_action])
        
        # 执行动作
        next_obs, reward, done, info = self.microgrid.step(action)
        self.current_step += 1
        
        return self.get_current_info()
    
    def run_simulation(self, steps=100, control_mode='RL'):
        """运行模拟"""
        results = []
        for _ in range(steps):
            info = self.step_forward(control_mode)
            results.append(info)
            if self.current_step >= len(self.microgrid.solar_profile):
                break
        return self.get_current_info()
    
    def train_rl_agent(self, episodes=5):
        """训练RL智能体"""
        self.is_training = True
        print(f"\n开始训练 {episodes} 个episodes...")
        
        results = self.rl_manager.train(self.microgrid, num_episodes=episodes)
        
        self.is_training = False
        self.training_episodes += episodes
        
        # 返回训练结果摘要
        summary = self.rl_manager.get_performance_summary()
        return summary
    
    def get_current_info(self) -> Dict:
        """获取当前系统信息"""
        if not self.microgrid.history:
            return {
                'status': '系统未运行',
                'step': 0,
                'stats': {}
            }
        
        current_state = self.microgrid.get_current_state()
        stats = self.microgrid.get_statistics()
        
        return {
            'status': '运行中',
            'step': self.current_step,
            'current_state': current_state.to_dict(),
            'stats': stats
        }
    
    def query_system(self, query: str) -> str:
        """自然语言查询"""
        return self.microgrid.query_state(query)
    
    def get_predictions(self, horizon=4):
        """获取预测"""
        if not self.predictor.solar_history:
            return "预测系统尚未初始化，请先运行系统。"
        
        predictions = self.predictor.predict_all(horizon=horizon, add_error=True)
        
        result = f"未来 {horizon} 个时间步（{horizon*15}分钟）预测:\n\n"
        
        result += "太阳能功率 (kW):\n"
        result += f"  预测: {[f'{x:.2f}' for x in predictions['solar'][0]]}\n"
        result += f"  实际: {[f'{x:.2f}' for x in predictions['solar'][1]]}\n\n"
        
        result += "风电功率 (kW):\n"
        result += f"  预测: {[f'{x:.2f}' for x in predictions['wind'][0]]}\n"
        result += f"  实际: {[f'{x:.2f}' for x in predictions['wind'][1]]}\n\n"
        
        result += "负荷需求 (kW):\n"
        result += f"  预测: {[f'{x:.2f}' for x in predictions['load'][0]]}\n"
        result += f"  实际: {[f'{x:.2f}' for x in predictions['load'][1]]}\n\n"
        
        result += "电价 (¥/kWh):\n"
        result += f"  预测: {[f'{x:.2f}' for x in predictions['price'][0]]}\n"
        result += f"  实际: {[f'{x:.2f}' for x in predictions['price'][1]]}\n\n"
        
        accuracy = self.predictor.get_prediction_accuracy()
        result += f"预测误差标准差: 太阳能{accuracy['solar_error_std']:.1%}, "
        result += f"风电{accuracy['wind_error_std']:.1%}, "
        result += f"负荷{accuracy['load_error_std']:.1%}, "
        result += f"电价{accuracy['price_error_std']:.1%}"
        
        return result
    
    def get_3d_visualization(self):
        """获取3D可视化"""
        if not self.microgrid.history:
            return go.Figure()
        
        current_state = self.microgrid.get_current_state()
        return self.visualizer.create_3d_scene(current_state)
    
    def get_dashboard(self):
        """获取仪表盘"""
        if not self.microgrid.history:
            return go.Figure()
        
        return self.visualizer.create_dashboard(self.microgrid.history)
    
    def get_sankey(self):
        """获取能量流桑基图"""
        if not self.microgrid.history:
            return go.Figure()
        
        current_state = self.microgrid.get_current_state()
        return self.visualizer.create_energy_flow_sankey(current_state)


# 创建全局系统实例
system = MicrogridSystem()


def create_gradio_interface():
    """创建Gradio界面"""
    
    with gr.Blocks(title="微网数字孪生系统", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🌐 微网数字孪生系统
        ## 集成预测、强化学习能量管理和3D可视化的智能微网系统
        
        本系统包含：
        - 🔋 微网数字孪生核心仿真（太阳能、风电、储能、负荷）
        - 📊 功率/电价/负荷预测系统（支持预测误差模拟）
        - 🤖 基于强化学习的自适应能量管理策略（PPO算法）
        - 📈 实时3D可视化和数据仪表盘
        - 💬 自然语言系统查询接口
        """)
        
        with gr.Tabs():
            # Tab 1: 系统控制
            with gr.Tab("🎮 系统控制"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 控制面板")
                        
                        control_mode = gr.Radio(
                            choices=['RL', 'Rule', 'Manual'],
                            value='RL',
                            label="控制模式",
                            info="RL: 强化学习策略 | Rule: 基于规则 | Manual: 手动控制"
                        )
                        
                        with gr.Group(visible=False) as manual_controls:
                            battery_slider = gr.Slider(-1, 1, value=0, step=0.1, 
                                                      label="电池动作 (-1:放电, +1:充电)")
                            grid_slider = gr.Slider(-1, 1, value=0, step=0.1,
                                                   label="电网动作")
                        
                        def update_manual_visibility(mode):
                            return gr.update(visible=(mode == 'Manual'))
                        
                        control_mode.change(
                            update_manual_visibility,
                            inputs=[control_mode],
                            outputs=[manual_controls]
                        )
                        
                        with gr.Row():
                            reset_btn = gr.Button("🔄 重置系统", variant="secondary")
                            step_btn = gr.Button("▶️ 单步运行", variant="primary")
                        
                        run_steps = gr.Slider(1, 200, value=50, step=1, 
                                            label="运行步数")
                        run_btn = gr.Button("🚀 连续运行", variant="primary", size="lg")
                        
                        gr.Markdown("---")
                        gr.Markdown("### 训练控制")
                        train_episodes = gr.Slider(1, 20, value=5, step=1,
                                                  label="训练episodes数")
                        train_btn = gr.Button("🎓 训练RL智能体", variant="secondary")
                        training_output = gr.Textbox(label="训练结果", lines=5)
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 系统状态")
                        status_display = gr.JSON(label="当前状态")
                        
                        gr.Markdown("### 系统统计")
                        stats_display = gr.Textbox(label="运行统计", lines=10)
            
            # Tab 2: 3D可视化
            with gr.Tab("🌍 3D可视化"):
                gr.Markdown("""
                ### 微网3D实时可视化
                - 🌞 黄色: 太阳能电池板
                - 💨 蓝色: 风力涡轮机
                - 🔋 绿色: 储能电池
                - 🏢 紫色: 负荷建筑
                - 🔌 红色: 电网连接点
                """)
                
                with gr.Row():
                    refresh_3d_btn = gr.Button("🔄 刷新3D视图", variant="primary")
                
                plot_3d = gr.Plot(label="3D场景")
                
                with gr.Row():
                    sankey_plot = gr.Plot(label="能量流动桑基图")
            
            # Tab 3: 数据仪表盘
            with gr.Tab("📊 数据仪表盘"):
                gr.Markdown("### 系统运行数据分析")
                
                refresh_dashboard_btn = gr.Button("🔄 刷新仪表盘", variant="primary")
                dashboard_plot = gr.Plot(label="运行仪表盘")
            
            # Tab 4: 预测系统
            with gr.Tab("🔮 预测系统"):
                gr.Markdown("""
                ### 功率/电价/负荷预测系统
                基于历史数据预测未来趋势，支持预测误差模拟
                """)
                
                with gr.Row():
                    pred_horizon = gr.Slider(1, 12, value=4, step=1,
                                            label="预测时间范围（时间步，每步15分钟）")
                    predict_btn = gr.Button("🔮 进行预测", variant="primary")
                
                prediction_output = gr.Textbox(label="预测结果", lines=20)
                
                gr.Markdown("### 预测误差设置")
                with gr.Row():
                    solar_err = gr.Slider(0, 0.5, value=0.15, step=0.01, label="太阳能预测误差")
                    wind_err = gr.Slider(0, 0.5, value=0.20, step=0.01, label="风电预测误差")
                with gr.Row():
                    load_err = gr.Slider(0, 0.5, value=0.10, step=0.01, label="负荷预测误差")
                    price_err = gr.Slider(0, 0.5, value=0.08, step=0.01, label="电价预测误差")
                
                update_err_btn = gr.Button("更新误差设置", variant="secondary")
                
                def update_errors(s_err, w_err, l_err, p_err):
                    system.predictor.set_error_levels(s_err, w_err, l_err, p_err)
                    return "预测误差设置已更新"
                
                update_err_btn.click(
                    update_errors,
                    inputs=[solar_err, wind_err, load_err, price_err],
                    outputs=[prediction_output]
                )
            
            # Tab 5: 自然语言查询
            with gr.Tab("💬 智能查询"):
                gr.Markdown("""
                ### 自然语言系统查询
                你可以用中文询问系统状态，例如：
                - "当前系统概览"
                - "电池状态如何"
                - "现在的太阳能发电是多少"
                - "总成本是多少"
                - "可再生能源使用率"
                """)
                
                with gr.Row():
                    query_input = gr.Textbox(
                        label="输入查询",
                        placeholder="例如：当前系统概览",
                        lines=2
                    )
                
                query_btn = gr.Button("🔍 查询", variant="primary")
                query_output = gr.Textbox(label="查询结果", lines=15)
                
                # 快速查询按钮
                gr.Markdown("### 快速查询")
                with gr.Row():
                    quick_q1 = gr.Button("系统概览")
                    quick_q2 = gr.Button("电池状态")
                    quick_q3 = gr.Button("成本信息")
                    quick_q4 = gr.Button("可再生能源")
        
        # 事件处理函数
        def reset_system_handler():
            info = system.reset_system()
            stats_text = format_stats(info)
            return info['current_state'], stats_text
        
        def step_forward_handler(mode, bat, grid):
            info = system.step_forward(mode, bat, grid)
            stats_text = format_stats(info)
            return info['current_state'], stats_text
        
        def run_simulation_handler(steps, mode):
            info = system.run_simulation(int(steps), mode)
            stats_text = format_stats(info)
            return info['current_state'], stats_text
        
        def train_handler(episodes):
            summary = system.train_rl_agent(int(episodes))
            result = f"训练完成！\n\n"
            result += f"总episodes: {summary['total_episodes']}\n"
            result += f"平均奖励: {summary['avg_reward']:.2f}\n"
            result += f"平均成本: ¥{summary['avg_cost']:.2f}\n"
            result += f"平均可再生能源占比: {summary['avg_renewable_ratio']*100:.1f}%\n"
            result += f"最佳奖励: {summary['best_reward']:.2f}\n"
            result += f"最低成本: ¥{summary['best_cost']:.2f}\n"
            return result
        
        def format_stats(info):
            if info['status'] == '系统未运行':
                return "系统未运行"
            
            stats = info['stats']
            text = f"运行统计 (步数: {stats['time_steps']})\n"
            text += f"━━━━━━━━━━━━━━━━━━━━\n"
            text += f"总成本: ¥{stats['total_cost']:.2f}\n"
            text += f"平均可再生能源占比: {stats['avg_renewable_ratio']*100:.1f}%\n"
            text += f"平均电池SOC: {stats['avg_battery_soc']*100:.1f}%\n"
            text += f"━━━━━━━━━━━━━━━━━━━━\n"
            text += f"太阳能总发电: {stats['total_solar_energy']:.2f} kWh\n"
            text += f"风电总发电: {stats['total_wind_energy']:.2f} kWh\n"
            text += f"总负荷: {stats['total_load_energy']:.2f} kWh\n"
            text += f"━━━━━━━━━━━━━━━━━━━━\n"
            text += f"最大电网买电: {stats['max_grid_import']:.2f} kW\n"
            text += f"最大电网卖电: {abs(stats['max_grid_export']):.2f} kW\n"
            return text
        
        def get_3d_viz():
            return system.get_3d_visualization()
        
        def get_dashboard_viz():
            return system.get_dashboard()
        
        def get_sankey_viz():
            return system.get_sankey()
        
        def predict_handler(horizon):
            return system.get_predictions(int(horizon))
        
        def query_handler(query):
            return system.query_system(query)
        
        # 绑定事件
        reset_btn.click(
            reset_system_handler,
            outputs=[status_display, stats_display]
        )
        
        step_btn.click(
            step_forward_handler,
            inputs=[control_mode, battery_slider, grid_slider],
            outputs=[status_display, stats_display]
        )
        
        run_btn.click(
            run_simulation_handler,
            inputs=[run_steps, control_mode],
            outputs=[status_display, stats_display]
        )
        
        train_btn.click(
            train_handler,
            inputs=[train_episodes],
            outputs=[training_output]
        )
        
        refresh_3d_btn.click(get_3d_viz, outputs=[plot_3d])
        refresh_3d_btn.click(get_sankey_viz, outputs=[sankey_plot])
        
        refresh_dashboard_btn.click(get_dashboard_viz, outputs=[dashboard_plot])
        
        predict_btn.click(
            predict_handler,
            inputs=[pred_horizon],
            outputs=[prediction_output]
        )
        
        query_btn.click(
            query_handler,
            inputs=[query_input],
            outputs=[query_output]
        )
        
        # 快速查询
        quick_q1.click(lambda: system.query_system("系统概览"), outputs=[query_output])
        quick_q2.click(lambda: system.query_system("电池状态"), outputs=[query_output])
        quick_q3.click(lambda: system.query_system("成本信息"), outputs=[query_output])
        quick_q4.click(lambda: system.query_system("可再生能源"), outputs=[query_output])
    
    return app


if __name__ == "__main__":
    print("=" * 50)
    print("🌐 微网数字孪生系统启动中...")
    print("=" * 50)
    
    # 创建并启动Gradio应用
    app = create_gradio_interface()
    
    print("\n✅ 系统初始化完成！")
    print("\n系统功能:")
    print("  ✓ 微网数字孪生核心仿真")
    print("  ✓ 功率/电价/负荷预测")
    print("  ✓ 强化学习能量管理")
    print("  ✓ 3D实时可视化")
    print("  ✓ 自然语言查询")
    print("\n正在启动Web界面...")
    
    # 启动应用
    app.launch(
        share=True,  # 创建公共链接，方便Colab使用
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
