# 🔌 微网数字孪生系统 (Microgrid Digital Twin System)

一个完整的微网数字孪生系统，集成了预测、强化学习能量管理、3D可视化和自然语言交互功能。

## ✨ 功能特点

### 🏗️ 微网核心模拟
- **光伏发电系统** - 考虑辐照度、温度影响的发电模型
- **风力发电系统** - 基于风速的功率曲线模型
- **电池储能系统** - 包含充放电效率、SOC管理、健康度监控
- **柴油发电机** - 备用电源模型
- **负荷模型** - 基于典型日负荷曲线的负荷模拟
- **电网连接** - 支持购/售电功能

### 🔮 预测系统
- 光伏功率预测（考虑天气因素）
- 风电功率预测（趋势分析）
- 负荷预测（日周期模式）
- 电价预测（分时电价）
- **不确定性估计** - 提供预测区间

### 🤖 强化学习能量管理
- **DQN智能体** - 自主学习最优调度策略
- **规则策略** - 基于专家规则的基准策略
- **自适应管理器** - 智能融合RL和规则策略
- **多目标奖励** - 平衡成本、可再生能源利用、电池健康

### 📊 策略评估
- 成本分析（购电成本、售电收入）
- 能源利用率评估
- 电网依赖度分析
- 电池健康管理评估
- CO2排放计算
- 综合评分与改进建议

### 💬 自然语言交互
- 状态查询（"查看系统状态"）
- 设备控制（"开始充电"）
- 分析报告（"生成评估报告"）
- 预测查询（"预测未来1小时"）
- 多种命令模式支持

### 🎮 3D可视化界面
- **Three.js驱动** - 实时3D渲染
- **交互控制** - 鼠标旋转/缩放
- **实时数据显示** - 功率、SOC、电价等
- **动态效果** - 风机旋转、电力流动粒子
- **控制面板** - 模拟控制和设备操作
- **智能聊天** - 集成NLP交互

## 📁 项目结构

```
workspace/
├── microgrid_digital_twin/          # 核心模块
│   ├── __init__.py                  # 包初始化
│   ├── core.py                      # 微网核心组件模型
│   ├── prediction.py                # 预测模块
│   ├── rl_agent.py                  # 强化学习智能体
│   ├── evaluation.py                # 策略评估模块
│   ├── nlp_interface.py             # 自然语言接口
│   └── visualization.py             # 3D可视化生成
├── microgrid_digital_twin_demo.ipynb # Colab演示notebook
└── README.md                        # 本文档
```

## 🚀 快速开始

### 方式一：Google Colab（推荐）

1. 上传 `microgrid_digital_twin/` 文件夹到Colab
2. 上传并运行 `microgrid_digital_twin_demo.ipynb`
3. 按顺序执行各个单元格

### 方式二：本地运行

```bash
# 克隆项目
git clone <repository-url>
cd workspace

# 安装依赖
pip install numpy

# 使用Jupyter运行
jupyter notebook microgrid_digital_twin_demo.ipynb
```

### 方式三：Python脚本

```python
from microgrid_digital_twin.core import MicrogridDigitalTwin
from microgrid_digital_twin.rl_agent import AdaptiveEnergyManager
from microgrid_digital_twin.visualization import Visualization3D

# 创建系统
digital_twin = MicrogridDigitalTwin()

# 创建能量管理器
manager = AdaptiveEnergyManager()

# 运行模拟
for _ in range(60):
    obs = digital_twin.get_observation()
    state = digital_twin.get_state()
    action = manager.select_action(obs, state)
    result = digital_twin.step(action)

# 生成可视化
viz = Visualization3D(digital_twin)
viz.save_html("visualization.html")
```

## 📖 模块使用指南

### 1. 核心模拟系统

```python
from microgrid_digital_twin.core import MicrogridDigitalTwin

# 自定义配置
config = {
    'solar': {'capacity_kw': 100.0},
    'wind': {'capacity_kw': 50.0},
    'battery': {'capacity_kwh': 200.0, 'soc': 0.5}
}

# 创建系统
dt = MicrogridDigitalTwin(config)

# 执行一步模拟
action = {'battery_action': 0.5, 'diesel_on': False}
state = dt.step(action)

# 获取状态
print(dt.get_state())
```

### 2. 预测系统

```python
from microgrid_digital_twin.prediction import IntegratedForecaster

forecaster = IntegratedForecaster(prediction_horizon=60)
forecasts = forecaster.forecast_all(hour=12, minute=0)

print(f"光伏预测: {forecasts['solar']['mean'].mean():.1f} kW")
print(f"负荷预测: {forecasts['load']['mean'].mean():.1f} kW")
```

### 3. 强化学习

```python
from microgrid_digital_twin.rl_agent import EnergyManagementAgent

agent = EnergyManagementAgent(state_dim=10, action_dim=2)

# 训练循环
for episode in range(100):
    obs = digital_twin.get_observation()
    action = agent.select_action(obs, training=True)
    next_state = digital_twin.step(action)
    reward = agent.calculate_reward(state, action, next_state)
    agent.train_step(obs, action, reward, next_obs, done)
```

### 4. 自然语言交互

```python
from microgrid_digital_twin.nlp_interface import NLPInterface

nlp = NLPInterface(digital_twin=dt)

# 自然语言查询
print(nlp.process("查看系统状态"))
print(nlp.process("电池电量怎么样"))
print(nlp.process("帮助"))
```

### 5. 3D可视化

```python
from microgrid_digital_twin.visualization import Visualization3D

viz = Visualization3D(digital_twin)

# 在Notebook中显示
viz.display_in_notebook()

# 保存HTML文件
viz.save_html("microgrid_3d.html")
```

## 🎮 3D界面功能

打开生成的HTML文件，可以体验：

- **视角控制** - 鼠标拖动旋转，滚轮缩放
- **状态监控** - 实时显示各组件功率和SOC
- **控制面板** - 电池充放电、柴油机开关
- **功率图表** - 历史趋势可视化
- **智能聊天** - 输入问题获取系统信息

## 📊 系统指标

| 指标 | 说明 |
|------|------|
| 光伏容量 | 100 kW |
| 风电容量 | 50 kW |
| 储能容量 | 200 kWh |
| 峰值负荷 | 150 kW |
| 电网交互 | 购100kW / 售50kW |

## 🔧 自定义配置

可以通过配置字典自定义系统参数：

```python
config = {
    'solar': {
        'capacity_kw': 150.0,
        'efficiency': 0.20,
        'panel_area': 750.0
    },
    'wind': {
        'capacity_kw': 80.0,
        'cut_in_speed': 3.0,
        'rated_speed': 12.0,
        'cut_out_speed': 25.0
    },
    'battery': {
        'capacity_kwh': 300.0,
        'max_charge_rate': 75.0,
        'max_discharge_rate': 75.0,
        'soc': 0.6,
        'soc_min': 0.15,
        'soc_max': 0.85
    },
    'load': {
        'base_load': 100.0,
        'peak_load': 200.0
    }
}
```

## 📝 自然语言命令示例

| 命令 | 功能 |
|------|------|
| "查看系统状态" | 显示完整系统状态 |
| "电池电量" | 查看储能SOC |
| "当前电价" | 显示实时电价 |
| "天气情况" | 显示天气参数 |
| "可再生能源利用率" | 查看清洁能源比例 |
| "生成报告" | 输出评估报告 |
| "预测未来1小时" | 获取预测结果 |
| "开始充电" | 启动电池充电 |
| "启动柴油发电机" | 启动备用电源 |
| "帮助" | 显示帮助信息 |

## 🛠️ 技术栈

- **Python 3.7+**
- **NumPy** - 数值计算
- **Three.js** - 3D可视化
- **IPython** - Notebook支持

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交Issue和Pull Request！

---

**微网数字孪生系统** - 智能能源管理的未来 🌱
