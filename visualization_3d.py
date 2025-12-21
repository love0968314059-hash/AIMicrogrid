"""
3D可视化系统
创建美观的微网数字孪生3D可视化界面
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import List, Dict
from microgrid_digital_twin import MicrogridState


class Microgrid3DVisualizer:
    """微网3D可视化器"""
    
    def __init__(self):
        self.colors = {
            'solar': '#FFD700',  # 金色
            'wind': '#87CEEB',  # 天蓝色
            'battery': '#32CD32',  # 绿色
            'grid': '#FF6347',  # 番茄红
            'load': '#9370DB',  # 紫色
        }
        
    def create_3d_scene(self, state: MicrogridState) -> go.Figure:
        """创建3D场景"""
        fig = go.Figure()
        
        # 设置基础网格
        grid_size = 10
        x_grid = np.linspace(-5, 5, grid_size)
        y_grid = np.linspace(-5, 5, grid_size)
        X, Y = np.meshgrid(x_grid, y_grid)
        Z_base = np.zeros_like(X) - 0.5
        
        # 添加地面
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z_base,
            colorscale=[[0, '#2F4F4F'], [1, '#2F4F4F']],
            showscale=False,
            opacity=0.3,
            name='Ground'
        ))
        
        # 太阳能电池板（多个板块组成）
        solar_height = state.solar_power / 20  # 高度表示功率
        solar_positions = [(-3, -3), (-3, -2), (-2, -3), (-2, -2)]
        for i, (sx, sy) in enumerate(solar_positions):
            fig.add_trace(self._create_box(
                sx, sy, solar_height/2, 0.8, 0.8, solar_height,
                self.colors['solar'], f'Solar Panel {i+1}'
            ))
            # 添加能量流效果
            if state.solar_power > 0:
                fig.add_trace(self._create_energy_stream(
                    sx, sy, solar_height, self.colors['solar'], 'up'
                ))
        
        # 风力涡轮机（带旋转叶片）
        wind_positions = [(3, -3), (3, -2)]
        for i, (wx, wy) in enumerate(wind_positions):
            # 塔架
            tower_height = 4
            fig.add_trace(self._create_cylinder(
                wx, wy, tower_height/2, 0.15, tower_height,
                self.colors['wind'], f'Wind Tower {i+1}'
            ))
            # 叶片
            blade_size = state.wind_power / 40
            angle_offset = i * 120  # 不同风机不同角度
            for blade_angle in [0, 120, 240]:
                angle = blade_angle + angle_offset + state.time_step * 5
                fig.add_trace(self._create_wind_blade(
                    wx, wy, tower_height, blade_size, angle,
                    self.colors['wind']
                ))
            # 能量流
            if state.wind_power > 0:
                fig.add_trace(self._create_energy_stream(
                    wx, wy, tower_height, self.colors['wind'], 'spiral'
                ))
        
        # 储能电池（立方体，大小表示SOC）
        battery_x, battery_y = 0, -3
        battery_size = 1.5
        battery_height = state.battery_soc * 3  # SOC决定高度
        fig.add_trace(self._create_box(
            battery_x, battery_y, battery_height/2, 
            battery_size, battery_size, battery_height,
            self.colors['battery'], 'Battery Storage'
        ))
        # 电池充放电指示
        if abs(state.battery_power) > 0.1:
            direction = 'up' if state.battery_power > 0 else 'down'
            color = '#00FF00' if state.battery_power > 0 else '#FFA500'
            fig.add_trace(self._create_energy_stream(
                battery_x, battery_y, battery_height, color, direction
            ))
        
        # 负荷建筑（多个小建筑）
        load_positions = [(-3, 2), (-2, 2), (-1, 2), (0, 2)]
        load_per_building = state.load_demand / len(load_positions)
        for i, (lx, ly) in enumerate(load_positions):
            building_height = 2 + (load_per_building / 20)
            fig.add_trace(self._create_box(
                lx, ly, building_height/2, 0.7, 0.7, building_height,
                self.colors['load'], f'Load {i+1}'
            ))
            # 用电指示
            fig.add_trace(self._create_energy_stream(
                lx, ly, building_height, self.colors['load'], 'down'
            ))
        
        # 电网连接点（塔状结构）
        grid_x, grid_y = 3, 3
        grid_height = 5
        fig.add_trace(self._create_transmission_tower(
            grid_x, grid_y, grid_height, self.colors['grid'], 'Grid Connection'
        ))
        # 电网功率流
        if abs(state.grid_power) > 0.1:
            direction = 'down' if state.grid_power > 0 else 'up'  # 买电向下，卖电向上
            color = '#FF0000' if state.grid_power > 0 else '#00FF00'
            fig.add_trace(self._create_energy_stream(
                grid_x, grid_y, grid_height, color, direction
            ))
        
        # 添加连接线（能量流线路）
        # 太阳能到中心
        for sx, sy in solar_positions:
            fig.add_trace(self._create_connection_line(sx, sy, 0, 0, '#FFD700'))
        # 风电到中心
        for wx, wy in wind_positions:
            fig.add_trace(self._create_connection_line(wx, wy, 0, 0, '#87CEEB'))
        # 电池到中心
        fig.add_trace(self._create_connection_line(battery_x, battery_y, 0, 0, '#32CD32'))
        # 中心到负荷
        for lx, ly in load_positions:
            fig.add_trace(self._create_connection_line(0, 0, lx, ly, '#9370DB'))
        # 中心到电网
        fig.add_trace(self._create_connection_line(0, 0, grid_x, grid_y, '#FF6347'))
        
        # 添加中央能量管理中心
        fig.add_trace(self._create_sphere(0, 0, 1, 0.5, '#FFD700', 'Energy Management Center'))
        
        # 设置布局
        fig.update_layout(
            title={
                'text': f'微网数字孪生 3D 可视化 - 时间步: {state.time_step}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#FFFFFF'}
            },
            scene=dict(
                xaxis=dict(showgrid=False, showbackground=False, title=''),
                yaxis=dict(showgrid=False, showbackground=False, title=''),
                zaxis=dict(showgrid=False, showbackground=False, title=''),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2),
                    center=dict(x=0, y=0, z=0)
                ),
                aspectmode='cube'
            ),
            showlegend=True,
            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0.5)', font=dict(color='white')),
            paper_bgcolor='#1a1a1a',
            plot_bgcolor='#1a1a1a',
            height=700,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig
    
    def _create_box(self, cx, cy, cz, width, depth, height, color, name):
        """创建立方体"""
        x = [cx-width/2, cx+width/2, cx+width/2, cx-width/2, cx-width/2, cx+width/2, cx+width/2, cx-width/2]
        y = [cy-depth/2, cy-depth/2, cy+depth/2, cy+depth/2, cy-depth/2, cy-depth/2, cy+depth/2, cy+depth/2]
        z = [cz-height/2, cz-height/2, cz-height/2, cz-height/2, cz+height/2, cz+height/2, cz+height/2, cz+height/2]
        
        i = [0, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
        j = [1, 2, 3, 7, 5, 6, 5, 2, 0, 1, 6, 3]
        k = [2, 3, 7, 4, 6, 7, 1, 1, 5, 5, 7, 6]
        
        return go.Mesh3d(
            x=x, y=y, z=z, i=i, j=j, k=k,
            color=color, opacity=0.8, name=name,
            hovertemplate=f'<b>{name}</b><extra></extra>'
        )
    
    def _create_cylinder(self, cx, cy, cz, radius, height, color, name):
        """创建圆柱体"""
        theta = np.linspace(0, 2*np.pi, 20)
        z = np.linspace(cz-height/2, cz+height/2, 10)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x = cx + radius * np.cos(theta_grid)
        y = cy + radius * np.sin(theta_grid)
        
        return go.Surface(
            x=x, y=y, z=z_grid,
            colorscale=[[0, color], [1, color]],
            showscale=False, opacity=0.8, name=name,
            hovertemplate=f'<b>{name}</b><extra></extra>'
        )
    
    def _create_sphere(self, cx, cy, cz, radius, color, name):
        """创建球体"""
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        x = cx + radius * np.outer(np.cos(u), np.sin(v))
        y = cy + radius * np.outer(np.sin(u), np.sin(v))
        z = cz + radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        return go.Surface(
            x=x, y=y, z=z,
            colorscale=[[0, color], [1, color]],
            showscale=False, opacity=0.9, name=name,
            hovertemplate=f'<b>{name}</b><extra></extra>'
        )
    
    def _create_wind_blade(self, cx, cy, cz, size, angle, color):
        """创建风机叶片"""
        angle_rad = np.radians(angle)
        blade_length = size
        blade_width = size / 5
        
        # 叶片端点
        x = [cx, cx + blade_length * np.cos(angle_rad)]
        y = [cy, cy + blade_length * np.sin(angle_rad)]
        z = [cz, cz]
        
        return go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(color=color, width=8),
            showlegend=False,
            hoverinfo='skip'
        )
    
    def _create_transmission_tower(self, cx, cy, height, color, name):
        """创建输电塔"""
        # 简化的输电塔结构
        base_size = 0.5
        top_size = 0.2
        
        x = [cx-base_size, cx+base_size, cx+base_size, cx-base_size,
             cx-top_size, cx+top_size, cx+top_size, cx-top_size]
        y = [cy-base_size, cy-base_size, cy+base_size, cy+base_size,
             cy-top_size, cy-top_size, cy+top_size, cy+top_size]
        z = [0, 0, 0, 0, height, height, height, height]
        
        i = [0, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
        j = [1, 2, 3, 7, 5, 6, 5, 2, 0, 1, 6, 3]
        k = [2, 3, 7, 4, 6, 7, 1, 1, 5, 5, 7, 6]
        
        return go.Mesh3d(
            x=x, y=y, z=z, i=i, j=j, k=k,
            color=color, opacity=0.7, name=name,
            hovertemplate=f'<b>{name}</b><extra></extra>'
        )
    
    def _create_energy_stream(self, x, y, z, color, direction='up'):
        """创建能量流动效果"""
        if direction == 'up':
            z_stream = np.linspace(z, z+2, 10)
            x_stream = np.full_like(z_stream, x)
            y_stream = np.full_like(z_stream, y)
        elif direction == 'down':
            z_stream = np.linspace(z, 0, 10)
            x_stream = np.full_like(z_stream, x)
            y_stream = np.full_like(z_stream, y)
        elif direction == 'spiral':
            t = np.linspace(0, 2*np.pi, 10)
            radius = 0.3
            x_stream = x + radius * np.cos(t)
            y_stream = y + radius * np.sin(t)
            z_stream = np.linspace(z, z+2, 10)
        else:
            return go.Scatter3d()
        
        return go.Scatter3d(
            x=x_stream, y=y_stream, z=z_stream,
            mode='lines+markers',
            line=dict(color=color, width=4),
            marker=dict(size=3, color=color),
            showlegend=False,
            hoverinfo='skip'
        )
    
    def _create_connection_line(self, x1, y1, x2, y2, color):
        """创建连接线"""
        return go.Scatter3d(
            x=[x1, x2], y=[y1, y2], z=[0.5, 0.5],
            mode='lines',
            line=dict(color=color, width=2, dash='dash'),
            opacity=0.5,
            showlegend=False,
            hoverinfo='skip'
        )
    
    def create_dashboard(self, history: List[MicrogridState]) -> go.Figure:
        """创建仪表盘"""
        if not history:
            return go.Figure()
        
        # 创建子图
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('功率流动', '电池状态', '成本累积', '可再生能源占比', '电价变化', '负荷与发电'),
            specs=[
                [{'type': 'scatter'}, {'type': 'scatter'}],
                [{'type': 'scatter'}, {'type': 'scatter'}],
                [{'type': 'scatter'}, {'type': 'scatter'}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        time_steps = [s.time_step for s in history]
        
        # 1. 功率流动
        fig.add_trace(go.Scatter(x=time_steps, y=[s.solar_power for s in history],
                                 name='太阳能', line=dict(color='#FFD700')), row=1, col=1)
        fig.add_trace(go.Scatter(x=time_steps, y=[s.wind_power for s in history],
                                 name='风电', line=dict(color='#87CEEB')), row=1, col=1)
        fig.add_trace(go.Scatter(x=time_steps, y=[s.load_demand for s in history],
                                 name='负荷', line=dict(color='#9370DB')), row=1, col=1)
        
        # 2. 电池状态
        fig.add_trace(go.Scatter(x=time_steps, y=[s.battery_soc*100 for s in history],
                                 name='SOC (%)', line=dict(color='#32CD32'), fill='tozeroy'), row=1, col=2)
        
        # 3. 成本累积
        fig.add_trace(go.Scatter(x=time_steps, y=[s.total_cost for s in history],
                                 name='累计成本 (¥)', line=dict(color='#FF6347')), row=2, col=1)
        
        # 4. 可再生能源占比
        fig.add_trace(go.Scatter(x=time_steps, y=[s.renewable_ratio*100 for s in history],
                                 name='可再生能源 (%)', line=dict(color='#32CD32'), fill='tozeroy'), row=2, col=2)
        
        # 5. 电价变化
        fig.add_trace(go.Scatter(x=time_steps, y=[s.electricity_price for s in history],
                                 name='电价 (¥/kWh)', line=dict(color='#FFA500')), row=3, col=1)
        
        # 6. 电网功率
        fig.add_trace(go.Scatter(x=time_steps, y=[s.grid_power for s in history],
                                 name='电网功率 (kW)', line=dict(color='#FF6347')), row=3, col=2)
        
        # 更新布局
        fig.update_xaxes(title_text="时间步", row=3, col=1)
        fig.update_xaxes(title_text="时间步", row=3, col=2)
        fig.update_yaxes(title_text="功率 (kW)", row=1, col=1)
        fig.update_yaxes(title_text="SOC (%)", row=1, col=2)
        fig.update_yaxes(title_text="成本 (¥)", row=2, col=1)
        fig.update_yaxes(title_text="占比 (%)", row=2, col=2)
        fig.update_yaxes(title_text="电价 (¥/kWh)", row=3, col=1)
        fig.update_yaxes(title_text="功率 (kW)", row=3, col=2)
        
        fig.update_layout(
            height=900,
            showlegend=True,
            title_text="微网运行仪表盘",
            title_x=0.5,
            template='plotly_dark'
        )
        
        return fig
    
    def create_energy_flow_sankey(self, state: MicrogridState) -> go.Figure:
        """创建能量流桑基图"""
        # 节点定义
        labels = ['太阳能', '风电', '电池', '电网', '负荷', '能量中心']
        
        # 能量流
        sources = []
        targets = []
        values = []
        colors = []
        
        # 太阳能到中心
        if state.solar_power > 0.1:
            sources.append(0)
            targets.append(5)
            values.append(state.solar_power)
            colors.append('rgba(255, 215, 0, 0.4)')
        
        # 风电到中心
        if state.wind_power > 0.1:
            sources.append(1)
            targets.append(5)
            values.append(state.wind_power)
            colors.append('rgba(135, 206, 235, 0.4)')
        
        # 电池充放电
        if state.battery_power > 0.1:  # 充电
            sources.append(5)
            targets.append(2)
            values.append(state.battery_power)
            colors.append('rgba(50, 205, 50, 0.4)')
        elif state.battery_power < -0.1:  # 放电
            sources.append(2)
            targets.append(5)
            values.append(-state.battery_power)
            colors.append('rgba(50, 205, 50, 0.4)')
        
        # 电网
        if state.grid_power > 0.1:  # 买电
            sources.append(3)
            targets.append(5)
            values.append(state.grid_power)
            colors.append('rgba(255, 99, 71, 0.4)')
        elif state.grid_power < -0.1:  # 卖电
            sources.append(5)
            targets.append(3)
            values.append(-state.grid_power)
            colors.append('rgba(0, 255, 0, 0.4)')
        
        # 中心到负荷
        sources.append(5)
        targets.append(4)
        values.append(state.load_demand)
        colors.append('rgba(147, 112, 219, 0.4)')
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='black', width=0.5),
                label=labels,
                color=['#FFD700', '#87CEEB', '#32CD32', '#FF6347', '#9370DB', '#FFA500']
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=colors
            )
        )])
        
        fig.update_layout(
            title=f'能量流动桑基图 - 时间步 {state.time_step}',
            font=dict(size=12, color='white'),
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            height=500
        )
        
        return fig


if __name__ == "__main__":
    # 测试3D可视化
    from microgrid_digital_twin import MicrogridDigitalTwin
    
    print("===== 3D可视化测试 =====\n")
    
    # 创建微网系统
    microgrid = MicrogridDigitalTwin()
    microgrid.reset()
    
    # 运行几步
    for i in range(5):
        action = np.random.uniform(-0.5, 0.5, 2)
        microgrid.step(action)
    
    # 创建可视化
    visualizer = Microgrid3DVisualizer()
    current_state = microgrid.get_current_state()
    
    print(f"当前状态: 时间步{current_state.time_step}")
    print(f"  太阳能: {current_state.solar_power:.2f} kW")
    print(f"  风电: {current_state.wind_power:.2f} kW")
    print(f"  负荷: {current_state.load_demand:.2f} kW")
    print(f"  电池SOC: {current_state.battery_soc*100:.1f}%")
    
    # 生成3D场景
    fig = visualizer.create_3d_scene(current_state)
    print("\n3D场景已创建")
    
    # 生成仪表盘
    dashboard = visualizer.create_dashboard(microgrid.history)
    print("仪表盘已创建")
    
    # 生成桑基图
    sankey = visualizer.create_energy_flow_sankey(current_state)
    print("能量流桑基图已创建")
