"""
微电网数字孪生系统 - Microgrid Digital Twin System
===================================================
一个可在Google Colab中运行的交互式微电网可视化系统
包含: 光伏发电、储能系统、负荷管理、能量流动可视化

作者: AI Assistant
版本: 1.0.0
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import time
from datetime import datetime, timedelta
import random

# ============================================================================
# 颜色主题配置
# ============================================================================
COLORS = {
    'solar': '#FFD700',      # 金黄色 - 太阳能
    'battery': '#00CED1',    # 青色 - 储能
    'load': '#FF6347',       # 番茄红 - 负荷
    'grid': '#9370DB',       # 紫色 - 电网
    'flow_positive': '#00FF00',  # 绿色 - 正向能量流
    'flow_negative': '#FF4500',  # 橙红色 - 反向能量流
    'background': '#1a1a2e',     # 深蓝黑背景
    'panel': '#16213e',          # 面板背景
    'text': '#eee'               # 文字颜色
}


# ============================================================================
# 3D 模型生成函数
# ============================================================================

def create_solar_panel_3d(x_offset=0, y_offset=0, z_offset=0, scale=1.0, tilt_angle=30):
    """
    创建3D太阳能电池板模型
    
    参数:
        x_offset, y_offset, z_offset: 位置偏移
        scale: 缩放比例
        tilt_angle: 倾斜角度(度)
    """
    # 电池板尺寸
    width = 2.0 * scale
    height = 1.0 * scale
    thickness = 0.05 * scale
    
    # 倾斜角度转弧度
    tilt_rad = np.radians(tilt_angle)
    
    # 创建电池板顶点
    panel_vertices = []
    
    # 底边
    x = np.array([0, width, width, 0, 0, width, width, 0]) + x_offset
    y = np.array([0, 0, 0, 0, height * np.cos(tilt_rad), height * np.cos(tilt_rad), 
                  height * np.cos(tilt_rad), height * np.cos(tilt_rad)]) + y_offset
    z = np.array([0, 0, thickness, thickness, 
                  height * np.sin(tilt_rad), height * np.sin(tilt_rad),
                  height * np.sin(tilt_rad) + thickness, height * np.sin(tilt_rad) + thickness]) + z_offset
    
    # 创建网格
    i = [0, 0, 0, 0, 4, 4, 0, 1, 1, 2, 2, 3]
    j = [1, 2, 4, 5, 5, 6, 3, 2, 5, 3, 6, 7]
    k = [2, 3, 5, 6, 6, 7, 4, 5, 6, 6, 7, 4]
    
    return go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=COLORS['solar'],
        opacity=0.9,
        name='太阳能板',
        hoverinfo='name',
        flatshading=True
    )


def create_solar_panel_array(rows=2, cols=3, spacing=2.5):
    """创建太阳能电池板阵列"""
    panels = []
    for i in range(rows):
        for j in range(cols):
            panel = create_solar_panel_3d(
                x_offset=j * spacing,
                y_offset=i * spacing * 0.8,
                z_offset=1.5,  # 支架高度
                scale=1.0,
                tilt_angle=35
            )
            panels.append(panel)
    
    # 添加支架
    for i in range(rows):
        for j in range(cols):
            # 支架柱子
            support = create_support_pole(
                x=j * spacing + 1,
                y=i * spacing * 0.8 + 0.4,
                height=1.5
            )
            panels.append(support)
    
    return panels


def create_support_pole(x, y, height, radius=0.05):
    """创建支撑杆"""
    theta = np.linspace(0, 2*np.pi, 10)
    z = np.linspace(0, height, 2)
    theta, z = np.meshgrid(theta, z)
    
    x_cyl = radius * np.cos(theta) + x
    y_cyl = radius * np.sin(theta) + y
    
    return go.Surface(
        x=x_cyl, y=y_cyl, z=z,
        colorscale=[[0, '#666666'], [1, '#888888']],
        showscale=False,
        hoverinfo='skip'
    )


def create_battery_storage_3d(x_offset=0, y_offset=0, z_offset=0, soc=0.75):
    """
    创建3D储能电池模型
    
    参数:
        x_offset, y_offset, z_offset: 位置偏移
        soc: 电池荷电状态 (0-1)
    """
    # 电池柜尺寸
    width = 1.5
    depth = 0.8
    height = 2.0
    
    # 外壳顶点
    x = np.array([0, width, width, 0, 0, width, width, 0]) + x_offset
    y = np.array([0, 0, depth, depth, 0, 0, depth, depth]) + y_offset
    z = np.array([0, 0, 0, 0, height, height, height, height]) + z_offset
    
    i = [0, 0, 0, 0, 4, 4, 0, 1, 1, 2, 2, 3]
    j = [1, 2, 4, 5, 5, 6, 3, 2, 5, 3, 6, 7]
    k = [2, 3, 5, 6, 6, 7, 4, 5, 6, 6, 7, 4]
    
    # 根据SOC选择颜色
    if soc > 0.6:
        color = '#00CED1'  # 青色 - 高电量
    elif soc > 0.3:
        color = '#FFA500'  # 橙色 - 中电量
    else:
        color = '#FF4500'  # 红色 - 低电量
    
    battery_case = go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=0.85,
        name=f'储能电池 (SOC: {soc*100:.0f}%)',
        hoverinfo='name',
        flatshading=True
    )
    
    # 电量指示条
    indicator_height = height * soc * 0.8
    indicator_z = np.array([0.1, 0.1, 0.1, 0.1, 
                            indicator_height, indicator_height, indicator_height, indicator_height]) + z_offset
    indicator_x = np.array([0.1, 0.3, 0.3, 0.1, 0.1, 0.3, 0.3, 0.1]) + x_offset
    indicator_y = np.array([depth+0.01, depth+0.01, depth+0.01, depth+0.01,
                            depth+0.01, depth+0.01, depth+0.01, depth+0.01]) + y_offset
    
    indicator = go.Mesh3d(
        x=indicator_x, y=indicator_y, z=indicator_z,
        i=[0, 4], j=[1, 5], k=[2, 6],
        color='#00FF00' if soc > 0.5 else '#FFFF00',
        opacity=1.0,
        hoverinfo='skip'
    )
    
    return [battery_case, indicator]


def create_battery_bank(count=4, soc_list=None):
    """创建储能电池组"""
    if soc_list is None:
        soc_list = [0.8, 0.65, 0.75, 0.9][:count]
    
    batteries = []
    spacing = 1.8
    
    for i in range(count):
        soc = soc_list[i] if i < len(soc_list) else 0.5
        battery_parts = create_battery_storage_3d(
            x_offset=10 + i * spacing,
            y_offset=0,
            z_offset=0,
            soc=soc
        )
        batteries.extend(battery_parts)
    
    return batteries


def create_load_building_3d(x_offset=0, y_offset=0, z_offset=0, 
                            building_type='residential', load_level=0.5):
    """
    创建3D负荷建筑模型
    
    参数:
        building_type: 'residential', 'commercial', 'industrial'
        load_level: 负荷水平 (0-1)
    """
    # 根据建筑类型设置尺寸
    if building_type == 'residential':
        width, depth, height = 2.0, 1.5, 2.5
        color = '#4169E1'  # 皇家蓝
    elif building_type == 'commercial':
        width, depth, height = 3.0, 2.0, 4.0
        color = '#32CD32'  # 酸橙绿
    else:  # industrial
        width, depth, height = 4.0, 3.0, 3.0
        color = '#708090'  # 灰石色
    
    # 建筑主体
    x = np.array([0, width, width, 0, 0, width, width, 0]) + x_offset
    y = np.array([0, 0, depth, depth, 0, 0, depth, depth]) + y_offset
    z = np.array([0, 0, 0, 0, height, height, height, height]) + z_offset
    
    i = [0, 0, 0, 0, 4, 4, 0, 1, 1, 2, 2, 3]
    j = [1, 2, 4, 5, 5, 6, 3, 2, 5, 3, 6, 7]
    k = [2, 3, 5, 6, 6, 7, 4, 5, 6, 6, 7, 4]
    
    # 根据负荷水平调整颜色亮度
    building = go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=0.8 + load_level * 0.2,
        name=f'{building_type.capitalize()} (负荷: {load_level*100:.0f}%)',
        hoverinfo='name',
        flatshading=True
    )
    
    # 添加窗户效果（亮灯）
    windows = []
    window_color = '#FFFF00' if load_level > 0.3 else '#333333'
    
    # 简化的窗户指示
    for floor in range(int(height)):
        for w in range(int(width)):
            window = go.Scatter3d(
                x=[x_offset + 0.5 + w],
                y=[y_offset + depth + 0.01],
                z=[z_offset + 0.5 + floor],
                mode='markers',
                marker=dict(
                    size=5,
                    color=window_color if random.random() < load_level else '#222222',
                    opacity=0.9
                ),
                hoverinfo='skip',
                showlegend=False
            )
            windows.append(window)
    
    return [building] + windows


def create_load_district():
    """创建负荷区域（多个建筑）"""
    buildings = []
    
    # 住宅区
    for i in range(3):
        load = 0.3 + random.random() * 0.5
        building = create_load_building_3d(
            x_offset=20 + i * 3,
            y_offset=0,
            z_offset=0,
            building_type='residential',
            load_level=load
        )
        buildings.extend(building)
    
    # 商业建筑
    building = create_load_building_3d(
        x_offset=20,
        y_offset=4,
        z_offset=0,
        building_type='commercial',
        load_level=0.7
    )
    buildings.extend(building)
    
    # 工业建筑
    building = create_load_building_3d(
        x_offset=25,
        y_offset=4,
        z_offset=0,
        building_type='industrial',
        load_level=0.85
    )
    buildings.extend(building)
    
    return buildings


def create_power_grid_tower(x_offset=0, y_offset=0):
    """创建电网塔架"""
    # 简化的输电塔
    tower_height = 5.0
    
    # 塔身（四个支柱）
    towers = []
    base_size = 0.8
    
    # 主干
    x = [x_offset, x_offset, x_offset + 0.2, x_offset + 0.2,
         x_offset + 0.3, x_offset + 0.3, x_offset - 0.1, x_offset - 0.1]
    y = [y_offset, y_offset + 0.2, y_offset + 0.2, y_offset,
         y_offset + 0.1, y_offset + 0.1, y_offset + 0.1, y_offset + 0.1]
    z = [0, 0, 0, 0, tower_height, tower_height, tower_height, tower_height]
    
    i = [0, 0, 4, 4]
    j = [1, 2, 5, 6]
    k = [2, 3, 6, 7]
    
    tower = go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color='#A0A0A0',
        opacity=0.9,
        name='电网接入点',
        hoverinfo='name'
    )
    
    # 电线
    wire = go.Scatter3d(
        x=[x_offset, x_offset + 5],
        y=[y_offset + 0.1, y_offset + 0.1],
        z=[tower_height - 0.5, tower_height - 1],
        mode='lines',
        line=dict(color='#FFD700', width=3),
        name='输电线',
        hoverinfo='name'
    )
    
    return [tower, wire]


def create_energy_flow_lines(solar_power, battery_power, grid_power, load_power):
    """
    创建能量流动线条
    
    参数:
        solar_power: 光伏出力 (kW)
        battery_power: 储能功率 (正=放电, 负=充电)
        grid_power: 电网功率 (正=购电, 负=售电)
        load_power: 负荷功率 (kW)
    """
    flows = []
    
    # 光伏到中心节点
    if solar_power > 0:
        flow1 = go.Scatter3d(
            x=[4, 8, 12],
            y=[2, 2, 2],
            z=[2, 2, 2],
            mode='lines+markers',
            line=dict(color=COLORS['solar'], width=max(2, solar_power/10)),
            marker=dict(size=[0, 8, 0], color=COLORS['solar']),
            name=f'光伏出力: {solar_power:.1f} kW',
            hoverinfo='name'
        )
        flows.append(flow1)
    
    # 储能流动
    if battery_power != 0:
        if battery_power > 0:  # 放电
            x_flow = [12, 12, 12]
            color = '#00FF00'
            name = f'电池放电: {battery_power:.1f} kW'
        else:  # 充电
            x_flow = [12, 12, 12]
            color = '#FF6600'
            name = f'电池充电: {-battery_power:.1f} kW'
        
        flow2 = go.Scatter3d(
            x=x_flow,
            y=[0.5, 1.5, 2],
            z=[1, 1.5, 2],
            mode='lines+markers',
            line=dict(color=color, width=max(2, abs(battery_power)/10)),
            marker=dict(size=[0, 6, 0], color=color),
            name=name,
            hoverinfo='name'
        )
        flows.append(flow2)
    
    # 电网流动
    if grid_power != 0:
        if grid_power > 0:  # 从电网购电
            color = '#9370DB'
            name = f'购电: {grid_power:.1f} kW'
        else:  # 向电网售电
            color = '#00CED1'
            name = f'售电: {-grid_power:.1f} kW'
        
        flow3 = go.Scatter3d(
            x=[-3, 4, 12],
            y=[5, 3.5, 2],
            z=[4, 3, 2],
            mode='lines+markers',
            line=dict(color=color, width=max(2, abs(grid_power)/10)),
            marker=dict(size=[0, 6, 0], color=color),
            name=name,
            hoverinfo='name'
        )
        flows.append(flow3)
    
    # 到负荷
    if load_power > 0:
        flow4 = go.Scatter3d(
            x=[12, 16, 22],
            y=[2, 2, 2],
            z=[2, 2, 1.5],
            mode='lines+markers',
            line=dict(color=COLORS['load'], width=max(2, load_power/10)),
            marker=dict(size=[0, 8, 0], color=COLORS['load']),
            name=f'负荷消耗: {load_power:.1f} kW',
            hoverinfo='name'
        )
        flows.append(flow4)
    
    return flows


def create_ground_plane():
    """创建地面平面"""
    x = np.linspace(-5, 35, 10)
    y = np.linspace(-5, 15, 10)
    x, y = np.meshgrid(x, y)
    z = np.zeros_like(x)
    
    ground = go.Surface(
        x=x, y=y, z=z,
        colorscale=[[0, '#2d5016'], [1, '#3d6b1e']],
        showscale=False,
        hoverinfo='skip',
        opacity=0.7
    )
    return ground


# ============================================================================
# 数据模拟类
# ============================================================================

class MicrogridSimulator:
    """微电网数据模拟器"""
    
    def __init__(self, pv_capacity=100, battery_capacity=200, max_load=150):
        """
        初始化模拟器
        
        参数:
            pv_capacity: 光伏装机容量 (kW)
            battery_capacity: 储能容量 (kWh)
            max_load: 最大负荷 (kW)
        """
        self.pv_capacity = pv_capacity
        self.battery_capacity = battery_capacity
        self.max_load = max_load
        self.battery_soc = 0.5  # 初始SOC 50%
        self.time = datetime.now().replace(hour=6, minute=0, second=0)
        
        # 历史数据
        self.history = {
            'time': [],
            'pv_power': [],
            'battery_power': [],
            'load_power': [],
            'grid_power': [],
            'soc': []
        }
    
    def get_solar_irradiance(self, hour):
        """获取太阳辐照度（基于时间）"""
        if hour < 6 or hour > 19:
            return 0
        # 使用正弦函数模拟日照曲线
        irradiance = np.sin((hour - 6) / 13 * np.pi)
        # 添加随机波动（模拟云层）
        irradiance *= (0.8 + random.random() * 0.4)
        return max(0, irradiance)
    
    def get_load_profile(self, hour):
        """获取负荷曲线（基于时间）"""
        # 典型日负荷曲线
        base_load = 0.3  # 基础负荷
        
        if 0 <= hour < 6:
            load = base_load + 0.1
        elif 6 <= hour < 9:
            load = base_load + 0.3 + (hour - 6) * 0.1
        elif 9 <= hour < 12:
            load = 0.7
        elif 12 <= hour < 14:
            load = 0.85  # 午高峰
        elif 14 <= hour < 18:
            load = 0.65
        elif 18 <= hour < 21:
            load = 0.9  # 晚高峰
        else:
            load = 0.4
        
        # 添加随机波动
        load *= (0.9 + random.random() * 0.2)
        return min(1.0, load)
    
    def simulate_step(self):
        """模拟一个时间步"""
        hour = self.time.hour + self.time.minute / 60
        
        # 计算光伏出力
        irradiance = self.get_solar_irradiance(hour)
        pv_power = self.pv_capacity * irradiance
        
        # 计算负荷
        load_factor = self.get_load_profile(hour)
        load_power = self.max_load * load_factor
        
        # 能量平衡计算
        power_balance = pv_power - load_power
        
        # 储能控制策略
        battery_power = 0
        
        if power_balance > 0:
            # 有盈余，优先给电池充电
            if self.battery_soc < 0.95:
                charge_power = min(power_balance, self.battery_capacity * 0.2)  # 最大0.2C充电
                charge_energy = charge_power / 60  # 转换为kWh（假设1分钟步长）
                self.battery_soc = min(0.95, self.battery_soc + charge_energy / self.battery_capacity)
                battery_power = -charge_power  # 负值表示充电
                power_balance -= charge_power
        else:
            # 有缺口，优先从电池放电
            if self.battery_soc > 0.1:
                discharge_power = min(-power_balance, self.battery_capacity * 0.3)  # 最大0.3C放电
                discharge_energy = discharge_power / 60
                self.battery_soc = max(0.1, self.battery_soc - discharge_energy / self.battery_capacity)
                battery_power = discharge_power  # 正值表示放电
                power_balance += discharge_power
        
        # 剩余的由电网平衡
        grid_power = -power_balance  # 正值表示从电网购电
        
        # 记录历史数据
        self.history['time'].append(self.time)
        self.history['pv_power'].append(pv_power)
        self.history['battery_power'].append(battery_power)
        self.history['load_power'].append(load_power)
        self.history['grid_power'].append(grid_power)
        self.history['soc'].append(self.battery_soc)
        
        # 保持历史数据长度
        max_history = 1440  # 24小时 * 60分钟
        for key in self.history:
            if len(self.history[key]) > max_history:
                self.history[key] = self.history[key][-max_history:]
        
        # 时间步进
        self.time += timedelta(minutes=1)
        
        return {
            'pv_power': pv_power,
            'battery_power': battery_power,
            'load_power': load_power,
            'grid_power': grid_power,
            'soc': self.battery_soc,
            'time': self.time
        }
    
    def get_battery_soc_list(self, count=4):
        """获取电池组SOC列表"""
        base_soc = self.battery_soc
        return [base_soc + random.uniform(-0.1, 0.1) for _ in range(count)]


# ============================================================================
# 可视化界面类
# ============================================================================

class MicrogridDigitalTwin:
    """微电网数字孪生系统主类"""
    
    def __init__(self):
        """初始化数字孪生系统"""
        self.simulator = MicrogridSimulator(
            pv_capacity=100,
            battery_capacity=200,
            max_load=150
        )
        self.is_running = False
        self.current_state = None
        
        # 创建UI组件
        self._create_widgets()
    
    def _create_widgets(self):
        """创建交互式控件"""
        # 控制面板标题
        self.title_html = widgets.HTML(
            value="""
            <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                        padding: 20px; border-radius: 10px; margin-bottom: 10px;'>
                <h1 style='color: #00CED1; margin: 0; text-align: center;'>
                    ⚡ 微电网数字孪生系统 ⚡
                </h1>
                <p style='color: #aaa; text-align: center; margin: 10px 0 0 0;'>
                    Microgrid Digital Twin System - Interactive 3D Visualization
                </p>
            </div>
            """
        )
        
        # 光伏容量滑块
        self.pv_slider = widgets.FloatSlider(
            value=100,
            min=10,
            max=500,
            step=10,
            description='光伏容量(kW):',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='400px')
        )
        
        # 储能容量滑块
        self.battery_slider = widgets.FloatSlider(
            value=200,
            min=50,
            max=1000,
            step=50,
            description='储能容量(kWh):',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='400px')
        )
        
        # 最大负荷滑块
        self.load_slider = widgets.FloatSlider(
            value=150,
            min=50,
            max=500,
            step=10,
            description='最大负荷(kW):',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='400px')
        )
        
        # 时间滑块
        self.time_slider = widgets.IntSlider(
            value=12,
            min=0,
            max=23,
            step=1,
            description='模拟时间:',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='400px')
        )
        
        # 更新按钮
        self.update_button = widgets.Button(
            description='🔄 更新视图',
            button_style='primary',
            layout=widgets.Layout(width='150px')
        )
        self.update_button.on_click(self._on_update_click)
        
        # 自动运行按钮
        self.run_button = widgets.Button(
            description='▶️ 开始模拟',
            button_style='success',
            layout=widgets.Layout(width='150px')
        )
        self.run_button.on_click(self._on_run_click)
        
        # 视图选择
        self.view_dropdown = widgets.Dropdown(
            options=[
                ('3D系统视图', '3d'),
                ('能量流动图', 'flow'),
                ('实时数据图', 'realtime'),
                ('综合仪表盘', 'dashboard')
            ],
            value='dashboard',
            description='视图模式:',
            style={'description_width': '80px'},
            layout=widgets.Layout(width='200px')
        )
        
        # 状态显示
        self.status_html = widgets.HTML(value='')
        
        # 输出区域
        self.output = widgets.Output()
        
        # 布局
        controls_row1 = widgets.HBox([self.pv_slider, self.battery_slider])
        controls_row2 = widgets.HBox([self.load_slider, self.time_slider])
        buttons_row = widgets.HBox([
            self.view_dropdown, 
            self.update_button, 
            self.run_button
        ], layout=widgets.Layout(justify_content='center', margin='10px 0'))
        
        self.control_panel = widgets.VBox([
            self.title_html,
            controls_row1,
            controls_row2,
            buttons_row,
            self.status_html,
            self.output
        ])
    
    def _on_update_click(self, button):
        """更新按钮点击处理"""
        self._update_simulator()
        self._update_display()
    
    def _on_run_click(self, button):
        """运行按钮点击处理"""
        if self.is_running:
            self.is_running = False
            self.run_button.description = '▶️ 开始模拟'
            self.run_button.button_style = 'success'
        else:
            self.is_running = True
            self.run_button.description = '⏹️ 停止模拟'
            self.run_button.button_style = 'danger'
            self._run_simulation()
    
    def _update_simulator(self):
        """更新模拟器参数"""
        self.simulator.pv_capacity = self.pv_slider.value
        self.simulator.battery_capacity = self.battery_slider.value
        self.simulator.max_load = self.load_slider.value
        
        # 设置时间
        hour = self.time_slider.value
        self.simulator.time = self.simulator.time.replace(hour=hour, minute=0)
        
        # 运行一步模拟
        self.current_state = self.simulator.simulate_step()
    
    def _run_simulation(self):
        """运行连续模拟"""
        import asyncio
        
        while self.is_running:
            self._update_simulator()
            self._update_display()
            self.time_slider.value = (self.time_slider.value + 1) % 24
            time.sleep(0.5)
    
    def _update_display(self):
        """更新显示"""
        with self.output:
            clear_output(wait=True)
            
            view_mode = self.view_dropdown.value
            
            if view_mode == '3d':
                fig = self._create_3d_view()
            elif view_mode == 'flow':
                fig = self._create_flow_view()
            elif view_mode == 'realtime':
                fig = self._create_realtime_view()
            else:
                fig = self._create_dashboard_view()
            
            fig.show()
            
            # 更新状态显示
            if self.current_state:
                self._update_status()
    
    def _update_status(self):
        """更新状态显示"""
        state = self.current_state
        
        # 确定电网状态
        if state['grid_power'] > 0:
            grid_status = f"<span style='color: #FF6347;'>购电 {state['grid_power']:.1f} kW</span>"
        elif state['grid_power'] < 0:
            grid_status = f"<span style='color: #00FF00;'>售电 {-state['grid_power']:.1f} kW</span>"
        else:
            grid_status = "<span style='color: #00CED1;'>平衡</span>"
        
        # 确定电池状态
        if state['battery_power'] > 0:
            battery_status = f"<span style='color: #00FF00;'>放电 {state['battery_power']:.1f} kW</span>"
        elif state['battery_power'] < 0:
            battery_status = f"<span style='color: #FFA500;'>充电 {-state['battery_power']:.1f} kW</span>"
        else:
            battery_status = "<span style='color: #00CED1;'>待机</span>"
        
        status_html = f"""
        <div style='background: #16213e; padding: 15px; border-radius: 8px; 
                    display: flex; justify-content: space-around; flex-wrap: wrap;'>
            <div style='text-align: center; padding: 10px;'>
                <div style='color: #FFD700; font-size: 24px;'>☀️ {state['pv_power']:.1f} kW</div>
                <div style='color: #aaa;'>光伏出力</div>
            </div>
            <div style='text-align: center; padding: 10px;'>
                <div style='color: #00CED1; font-size: 24px;'>🔋 {state['soc']*100:.1f}%</div>
                <div style='color: #aaa;'>{battery_status}</div>
            </div>
            <div style='text-align: center; padding: 10px;'>
                <div style='color: #FF6347; font-size: 24px;'>🏠 {state['load_power']:.1f} kW</div>
                <div style='color: #aaa;'>负荷消耗</div>
            </div>
            <div style='text-align: center; padding: 10px;'>
                <div style='color: #9370DB; font-size: 24px;'>⚡ {grid_status}</div>
                <div style='color: #aaa;'>电网交互</div>
            </div>
            <div style='text-align: center; padding: 10px;'>
                <div style='color: #fff; font-size: 24px;'>🕐 {state['time'].strftime('%H:%M')}</div>
                <div style='color: #aaa;'>当前时间</div>
            </div>
        </div>
        """
        self.status_html.value = status_html
    
    def _create_3d_view(self):
        """创建3D系统视图"""
        state = self.current_state or self.simulator.simulate_step()
        
        fig = go.Figure()
        
        # 添加地面
        fig.add_trace(create_ground_plane())
        
        # 添加光伏阵列
        solar_panels = create_solar_panel_array(rows=2, cols=3)
        for panel in solar_panels:
            fig.add_trace(panel)
        
        # 添加储能系统
        soc_list = self.simulator.get_battery_soc_list(4)
        batteries = create_battery_bank(count=4, soc_list=soc_list)
        for battery in batteries:
            fig.add_trace(battery)
        
        # 添加负荷区域
        buildings = create_load_district()
        for building in buildings:
            fig.add_trace(building)
        
        # 添加电网接入点
        grid_tower = create_power_grid_tower(x_offset=-2, y_offset=5)
        for element in grid_tower:
            fig.add_trace(element)
        
        # 添加能量流动线
        flow_lines = create_energy_flow_lines(
            solar_power=state['pv_power'],
            battery_power=state['battery_power'],
            grid_power=state['grid_power'],
            load_power=state['load_power']
        )
        for flow in flow_lines:
            fig.add_trace(flow)
        
        # 添加标签
        labels = [
            go.Scatter3d(x=[3], y=[4], z=[4], mode='text',
                        text=['☀️ 光伏发电区'], textfont=dict(size=14, color='#FFD700'),
                        hoverinfo='skip', showlegend=False),
            go.Scatter3d(x=[13], y=[-1], z=[3], mode='text',
                        text=['🔋 储能系统'], textfont=dict(size=14, color='#00CED1'),
                        hoverinfo='skip', showlegend=False),
            go.Scatter3d(x=[25], y=[-1], z=[5], mode='text',
                        text=['🏠 负荷区域'], textfont=dict(size=14, color='#FF6347'),
                        hoverinfo='skip', showlegend=False),
            go.Scatter3d(x=[-2], y=[6], z=[6], mode='text',
                        text=['⚡ 电网'], textfont=dict(size=14, color='#9370DB'),
                        hoverinfo='skip', showlegend=False),
        ]
        for label in labels:
            fig.add_trace(label)
        
        # 设置布局
        fig.update_layout(
            title=dict(
                text='微电网数字孪生 - 3D系统视图',
                font=dict(size=20, color='#00CED1')
            ),
            scene=dict(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
                zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
                bgcolor='#0a0a1a',
                camera=dict(
                    eye=dict(x=1.5, y=-1.5, z=0.8),
                    up=dict(x=0, y=0, z=1)
                ),
                aspectmode='data'
            ),
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#1a1a2e',
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            showlegend=True,
            legend=dict(
                font=dict(color='#eee'),
                bgcolor='rgba(22, 33, 62, 0.8)',
                bordercolor='#00CED1',
                borderwidth=1
            )
        )
        
        return fig
    
    def _create_flow_view(self):
        """创建能量流动桑基图"""
        state = self.current_state or self.simulator.simulate_step()
        
        # 节点
        labels = ['光伏', '储能', '电网', '负荷']
        
        # 计算流动值
        flows_source = []
        flows_target = []
        flows_value = []
        flows_color = []
        
        # 光伏出力
        if state['pv_power'] > 0:
            # 光伏到负荷
            pv_to_load = min(state['pv_power'], state['load_power'])
            if pv_to_load > 0:
                flows_source.append(0)
                flows_target.append(3)
                flows_value.append(pv_to_load)
                flows_color.append('rgba(255, 215, 0, 0.6)')
            
            # 光伏到储能（充电）
            if state['battery_power'] < 0:
                flows_source.append(0)
                flows_target.append(1)
                flows_value.append(-state['battery_power'])
                flows_color.append('rgba(255, 215, 0, 0.6)')
            
            # 光伏到电网（售电）
            if state['grid_power'] < 0:
                flows_source.append(0)
                flows_target.append(2)
                flows_value.append(-state['grid_power'])
                flows_color.append('rgba(255, 215, 0, 0.6)')
        
        # 储能放电
        if state['battery_power'] > 0:
            flows_source.append(1)
            flows_target.append(3)
            flows_value.append(state['battery_power'])
            flows_color.append('rgba(0, 206, 209, 0.6)')
        
        # 电网购电
        if state['grid_power'] > 0:
            flows_source.append(2)
            flows_target.append(3)
            flows_value.append(state['grid_power'])
            flows_color.append('rgba(147, 112, 219, 0.6)')
        
        # 确保有数据显示
        if not flows_value:
            flows_source = [0]
            flows_target = [3]
            flows_value = [0.1]
            flows_color = ['rgba(100, 100, 100, 0.3)']
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='#1a1a2e', width=0.5),
                label=labels,
                color=['#FFD700', '#00CED1', '#9370DB', '#FF6347']
            ),
            link=dict(
                source=flows_source,
                target=flows_target,
                value=flows_value,
                color=flows_color
            )
        )])
        
        fig.update_layout(
            title=dict(
                text='微电网能量流动图',
                font=dict(size=20, color='#00CED1')
            ),
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#1a1a2e',
            font=dict(color='#eee', size=14),
            height=500
        )
        
        return fig
    
    def _create_realtime_view(self):
        """创建实时数据图表"""
        history = self.simulator.history
        
        if len(history['time']) < 2:
            # 生成一些模拟数据
            for _ in range(60):
                self.simulator.simulate_step()
            history = self.simulator.history
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('功率曲线', '电池SOC', '能量平衡', '累计能量'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        times = list(range(len(history['time'])))
        time_labels = [t.strftime('%H:%M') for t in history['time']]
        
        # 功率曲线
        fig.add_trace(go.Scatter(
            x=times, y=history['pv_power'],
            name='光伏', line=dict(color='#FFD700', width=2)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=times, y=history['load_power'],
            name='负荷', line=dict(color='#FF6347', width=2)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=times, y=[abs(p) for p in history['battery_power']],
            name='储能', line=dict(color='#00CED1', width=2)
        ), row=1, col=1)
        
        # SOC曲线
        fig.add_trace(go.Scatter(
            x=times, y=[s*100 for s in history['soc']],
            name='SOC', line=dict(color='#00FF00', width=2),
            fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.2)'
        ), row=1, col=2)
        
        # 能量平衡柱状图（最近10个点）
        recent = min(10, len(times))
        categories = ['光伏', '储能', '电网', '负荷']
        if recent > 0:
            values = [
                sum(history['pv_power'][-recent:]) / recent,
                sum(history['battery_power'][-recent:]) / recent,
                sum(history['grid_power'][-recent:]) / recent,
                -sum(history['load_power'][-recent:]) / recent
            ]
            colors = ['#FFD700', '#00CED1', '#9370DB', '#FF6347']
            
            fig.add_trace(go.Bar(
                x=categories, y=values,
                marker_color=colors,
                name='平均功率'
            ), row=2, col=1)
        
        # 累计能量
        pv_cumsum = np.cumsum(history['pv_power']) / 60  # 转换为kWh
        load_cumsum = np.cumsum(history['load_power']) / 60
        
        fig.add_trace(go.Scatter(
            x=times, y=pv_cumsum,
            name='累计发电', line=dict(color='#FFD700', width=2)
        ), row=2, col=2)
        
        fig.add_trace(go.Scatter(
            x=times, y=load_cumsum,
            name='累计用电', line=dict(color='#FF6347', width=2)
        ), row=2, col=2)
        
        fig.update_layout(
            title=dict(
                text='微电网实时数据监控',
                font=dict(size=20, color='#00CED1')
            ),
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#16213e',
            font=dict(color='#eee'),
            height=600,
            showlegend=True,
            legend=dict(
                bgcolor='rgba(22, 33, 62, 0.8)',
                bordercolor='#00CED1',
                borderwidth=1
            )
        )
        
        # 更新所有子图的样式
        fig.update_xaxes(gridcolor='#333', zerolinecolor='#444')
        fig.update_yaxes(gridcolor='#333', zerolinecolor='#444')
        
        return fig
    
    def _create_dashboard_view(self):
        """创建综合仪表盘视图"""
        state = self.current_state or self.simulator.simulate_step()
        history = self.simulator.history
        
        # 确保有足够的历史数据
        if len(history['time']) < 10:
            for _ in range(60):
                self.simulator.simulate_step()
            history = self.simulator.history
            state = self.current_state
        
        fig = make_subplots(
            rows=2, cols=3,
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                [{"type": "scatter3d", "colspan": 2}, None, {"type": "pie"}]
            ],
            subplot_titles=('', '', '', '3D系统概览', '', '能量构成'),
            row_heights=[0.3, 0.7],
            vertical_spacing=0.1,
            horizontal_spacing=0.05
        )
        
        # 光伏仪表盘
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=state['pv_power'],
            title={'text': "☀️ 光伏出力 (kW)", 'font': {'color': '#FFD700', 'size': 14}},
            delta={'reference': self.simulator.pv_capacity * 0.5, 'relative': True},
            gauge={
                'axis': {'range': [0, self.simulator.pv_capacity], 'tickcolor': '#eee'},
                'bar': {'color': '#FFD700'},
                'bgcolor': '#16213e',
                'borderwidth': 2,
                'bordercolor': '#FFD700',
                'steps': [
                    {'range': [0, self.simulator.pv_capacity*0.3], 'color': '#2d2d2d'},
                    {'range': [self.simulator.pv_capacity*0.3, self.simulator.pv_capacity*0.7], 'color': '#3d3d3d'},
                    {'range': [self.simulator.pv_capacity*0.7, self.simulator.pv_capacity], 'color': '#4d4d4d'}
                ],
                'threshold': {
                    'line': {'color': '#FF0000', 'width': 4},
                    'thickness': 0.75,
                    'value': self.simulator.pv_capacity * 0.9
                }
            }
        ), row=1, col=1)
        
        # 储能SOC仪表盘
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=state['soc'] * 100,
            title={'text': "🔋 储能SOC (%)", 'font': {'color': '#00CED1', 'size': 14}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#eee'},
                'bar': {'color': '#00CED1'},
                'bgcolor': '#16213e',
                'borderwidth': 2,
                'bordercolor': '#00CED1',
                'steps': [
                    {'range': [0, 20], 'color': '#8B0000'},
                    {'range': [20, 50], 'color': '#FFA500'},
                    {'range': [50, 100], 'color': '#006400'}
                ],
                'threshold': {
                    'line': {'color': '#FF0000', 'width': 4},
                    'thickness': 0.75,
                    'value': 15
                }
            }
        ), row=1, col=2)
        
        # 负荷仪表盘
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=state['load_power'],
            title={'text': "🏠 负荷消耗 (kW)", 'font': {'color': '#FF6347', 'size': 14}},
            delta={'reference': self.simulator.max_load * 0.5, 'relative': True},
            gauge={
                'axis': {'range': [0, self.simulator.max_load], 'tickcolor': '#eee'},
                'bar': {'color': '#FF6347'},
                'bgcolor': '#16213e',
                'borderwidth': 2,
                'bordercolor': '#FF6347',
                'steps': [
                    {'range': [0, self.simulator.max_load*0.5], 'color': '#2d2d2d'},
                    {'range': [self.simulator.max_load*0.5, self.simulator.max_load*0.8], 'color': '#3d3d3d'},
                    {'range': [self.simulator.max_load*0.8, self.simulator.max_load], 'color': '#4d4d4d'}
                ],
                'threshold': {
                    'line': {'color': '#FF0000', 'width': 4},
                    'thickness': 0.75,
                    'value': self.simulator.max_load * 0.95
                }
            }
        ), row=1, col=3)
        
        # 3D缩略视图
        # 简化的3D元素
        # 光伏
        fig.add_trace(go.Scatter3d(
            x=[0, 1, 2], y=[0, 0, 0], z=[1, 1.2, 1],
            mode='markers+lines',
            marker=dict(size=10, color='#FFD700', symbol='diamond'),
            line=dict(color='#FFD700', width=3),
            name='光伏',
            showlegend=False
        ), row=2, col=1)
        
        # 储能
        fig.add_trace(go.Scatter3d(
            x=[4, 4.5, 5], y=[0, 0, 0], z=[0.5, 0.5, 0.5],
            mode='markers',
            marker=dict(size=15, color='#00CED1', symbol='square'),
            name='储能',
            showlegend=False
        ), row=2, col=1)
        
        # 负荷
        fig.add_trace(go.Scatter3d(
            x=[7, 8, 9], y=[0, 0, 0], z=[0.8, 1.5, 1.0],
            mode='markers',
            marker=dict(size=[12, 20, 15], color='#FF6347', symbol='square'),
            name='负荷',
            showlegend=False
        ), row=2, col=1)
        
        # 能量流动线
        fig.add_trace(go.Scatter3d(
            x=[1, 3, 4.5, 6, 8],
            y=[0, 0, 0, 0, 0],
            z=[1, 0.7, 0.5, 0.6, 1.0],
            mode='lines+markers',
            line=dict(color='#00FF00', width=5),
            marker=dict(size=5, color='#00FF00'),
            name='能量流',
            showlegend=False
        ), row=2, col=1)
        
        # 能量构成饼图
        pv_energy = max(0.1, state['pv_power'])
        battery_energy = max(0.1, abs(state['battery_power']))
        grid_energy = max(0.1, abs(state['grid_power']))
        
        fig.add_trace(go.Pie(
            labels=['光伏', '储能', '电网'],
            values=[pv_energy, battery_energy, grid_energy],
            hole=0.4,
            marker=dict(colors=['#FFD700', '#00CED1', '#9370DB']),
            textinfo='label+percent',
            textfont=dict(color='#eee')
        ), row=2, col=3)
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text=f'微电网数字孪生仪表盘 - {state["time"].strftime("%Y-%m-%d %H:%M")}',
                font=dict(size=22, color='#00CED1'),
                x=0.5
            ),
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#16213e',
            font=dict(color='#eee'),
            height=700,
            scene=dict(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, 
                          title='', showbackground=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, 
                          title='', showbackground=False),
                zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, 
                          title='', showbackground=False),
                bgcolor='#0a0a1a',
                camera=dict(eye=dict(x=0, y=-2, z=0.5))
            ),
            showlegend=False
        )
        
        return fig
    
    def display(self):
        """显示数字孪生界面"""
        # 初始化数据
        for _ in range(60):
            self.simulator.simulate_step()
        self.current_state = self.simulator.history['pv_power'] and {
            'pv_power': self.simulator.history['pv_power'][-1],
            'battery_power': self.simulator.history['battery_power'][-1],
            'load_power': self.simulator.history['load_power'][-1],
            'grid_power': self.simulator.history['grid_power'][-1],
            'soc': self.simulator.history['soc'][-1],
            'time': self.simulator.history['time'][-1]
        }
        
        # 显示控制面板
        display(self.control_panel)
        
        # 初始更新
        self._update_display()


# ============================================================================
# 快速启动函数
# ============================================================================

def run_microgrid_digital_twin():
    """
    运行微电网数字孪生系统
    
    在Google Colab中使用:
    ```python
    !pip install plotly ipywidgets
    from microgrid_digital_twin import run_microgrid_digital_twin
    run_microgrid_digital_twin()
    ```
    """
    print("🔄 正在初始化微电网数字孪生系统...")
    
    # 创建并显示系统
    twin = MicrogridDigitalTwin()
    twin.display()
    
    print("✅ 系统已启动! 使用控件调整参数，点击'更新视图'查看变化。")
    
    return twin


def create_static_3d_view(pv_power=50, battery_soc=0.7, load_power=80):
    """
    创建静态3D视图（不需要交互组件）
    
    适用于简单展示
    """
    simulator = MicrogridSimulator()
    simulator.battery_soc = battery_soc
    
    # 手动设置状态
    state = {
        'pv_power': pv_power,
        'battery_power': 0,
        'load_power': load_power,
        'grid_power': load_power - pv_power,
        'soc': battery_soc,
        'time': datetime.now()
    }
    
    fig = go.Figure()
    
    # 添加地面
    fig.add_trace(create_ground_plane())
    
    # 添加光伏阵列
    for panel in create_solar_panel_array(rows=2, cols=3):
        fig.add_trace(panel)
    
    # 添加储能系统
    for battery in create_battery_bank(count=4, soc_list=[battery_soc]*4):
        fig.add_trace(battery)
    
    # 添加负荷区域
    for building in create_load_district():
        fig.add_trace(building)
    
    # 添加电网
    for element in create_power_grid_tower(-2, 5):
        fig.add_trace(element)
    
    # 添加能量流动
    for flow in create_energy_flow_lines(pv_power, 0, state['grid_power'], load_power):
        fig.add_trace(flow)
    
    # 设置布局
    fig.update_layout(
        title=dict(
            text='微电网数字孪生 - 3D系统视图',
            font=dict(size=20, color='#00CED1')
        ),
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
            bgcolor='#0a0a1a',
            camera=dict(eye=dict(x=1.5, y=-1.5, z=0.8)),
            aspectmode='data'
        ),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        showlegend=True,
        legend=dict(font=dict(color='#eee'), bgcolor='rgba(22, 33, 62, 0.8)')
    )
    
    return fig


# ============================================================================
# 主程序入口
# ============================================================================

if __name__ == "__main__":
    # 本地测试
    print("微电网数字孪生系统")
    print("=" * 50)
    print("请在Jupyter Notebook或Google Colab中运行以获得完整交互体验")
    print()
    print("快速启动:")
    print("  from microgrid_digital_twin import run_microgrid_digital_twin")
    print("  twin = run_microgrid_digital_twin()")
