# 🔌 微网数字孪生系统 (Microgrid Digital Twin System)

一个完整的微网数字孪生系统，集成了预测、强化学习能量管理、3D可视化和自然语言交互功能。采用工业科技风格的带页签界面设计，提供完整的实时监控、能量管理、数据分析和策略优化功能。

---

## 📋 目录

- [功能特点](#-功能特点)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
- [界面使用指南](#-界面使用指南)
- [模块使用指南](#-模块使用指南)
- [系统配置](#-系统配置)
- [技术栈](#-技术栈)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)

---

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
- **30天运行周期** - 长期模拟和策略对比

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

### 🎮 工业科技风格3D可视化界面

**带页签的现代化界面设计**：
- **3D场景页签** - Three.js驱动的实时3D渲染，交互控制（旋转/缩放/平移）
- **实时监控页签** - 所有系统组件的实时数据监控卡片
- **能量管理页签** - 电池控制、模拟控制、设备操作
- **数据分析页签** - 指标卡片和功率趋势图表
- **策略分析页签** - RL策略状态、训练统计、30天对比分析
- **智能助手页签** - 自然语言交互聊天界面

**界面特色**：
- 深色工业科技风格主题
- 青色/蓝色发光效果
- 金属质感边框和卡片
- 科技网格背景
- 扫描线动画效果

---

## 📁 项目结构

```
AIMicrogrid/
├── microgrid_digital_twin/          # 核心模块
│   ├── __init__.py                  # 包初始化
│   ├── core.py                      # 微网核心组件模型
│   ├── prediction.py                # 预测模块
│   ├── rl_agent.py                  # 强化学习智能体
│   ├── evaluation.py                # 策略评估模块
│   ├── nlp_interface.py             # 自然语言接口
│   ├── visualization.py             # 3D可视化生成
│   └── tabbed_visualization_template.py  # 带页签模板
├── demo_enhanced.py                 # 完整30天演示脚本
├── run_demo.py                      # 快速1小时演示脚本
├── microgrid_3d_tabbed.html        # 最新的带页签可视化界面
├── requirements.txt                 # Python依赖
└── README.md                        # 本文档
```

### 核心模块说明

- **`core.py`** - 微网数字孪生核心模拟系统，包含所有组件模型（光伏、风电、电池、负荷、电网等）
- **`rl_agent.py`** - 强化学习能量管理，包含DQN智能体、规则策略和自适应管理器
- **`prediction.py`** - 预测模块，支持光伏/风电功率预测、负荷预测、电价预测
- **`evaluation.py`** - 策略评估模块，成本分析、性能评估
- **`visualization.py`** - 可视化模块，3D可视化管理器和HTML生成
- **`tabbed_visualization_template.py`** - 带页签的工业科技风格模板

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装NumPy
pip3 install numpy

# 或使用requirements.txt
pip3 install -r requirements.txt
```

### 2. 运行演示

#### 方式一：快速演示（1小时模拟，推荐首次使用）

```bash
python3 run_demo.py
```

运行一个1小时的模拟演示，展示系统基本功能。

#### 方式二：完整演示（30天模拟）

```bash
python3 demo_enhanced.py
```

运行完整的30天模拟，对比RL策略和规则策略的性能。

**注意**: 完整模拟需要较长时间（10-30分钟）

#### 方式三：直接打开可视化界面

```bash
# macOS
open microgrid_3d_tabbed.html

# Linux
xdg-open microgrid_3d_tabbed.html

# Windows
start microgrid_3d_tabbed.html
```

或在文件管理器中双击该文件。

### 3. 在Cursor/IDE中运行

1. **打开终端**: 在Cursor中按 `Ctrl+`` 或 `Cmd+J` 打开终端

2. **进入项目目录**:
   ```bash
   cd /Users/chenyu/Documents/WYB/Git-AImicrogrid/AIMicrogrid
   ```

3. **安装依赖**（如果还没安装）:
   ```bash
   pip3 install numpy
   ```

4. **运行演示**:
   ```bash
   python3 run_demo.py
   ```

---

## 🎮 界面使用指南

### 页签导航

界面顶部有6个功能页签，点击切换不同功能模块：

1. **🌐 3D场景** - 查看3D微网模型
2. **📊 实时监控** - 查看系统状态
3. **🎮 能量管理** - 控制系统设备
4. **📈 数据分析** - 查看趋势图表
5. **🤖 策略分析** - 查看RL策略状态
6. **💬 智能助手** - 自然语言交互

### 3D场景操作

- **旋转视角**: 鼠标左键拖动
- **缩放**: 鼠标滚轮
- **平移**: 鼠标右键拖动（如果支持）

### 能量管理控制

在"能量管理"页签中：

- **电池控制**: 拖动滑块控制充放电（-100%放电 到 +100%充电）
- **快速充电/放电**: 一键操作按钮
- **自动模式**: 启用AI自动优化
- **柴油机开关**: 应急电源控制
- **模拟速度**: 调整模拟速度（1-10倍）
- **开始/暂停**: 控制模拟运行

### 智能助手

在"智能助手"页签中输入问题，支持查询：
- "系统状态" - 查看整体状态
- "电池情况" - 查看电池详情
- "成本" - 查看成本统计
- "预测" - 查看未来预测
- "帮助" - 获取使用帮助

### 推荐体验流程

**5分钟快速体验**:
1. 打开 `microgrid_3d_tabbed.html`
2. 点击"能量管理"页签，点击"开始模拟"
3. 切换到"实时监控"页签查看数据
4. 切换到"3D场景"页签查看3D模型

**15分钟深度体验**:
1. 完成快速体验
2. 调整模拟速度到5-10倍
3. 观察"数据分析"页签的图表变化
4. 尝试手动控制电池充放电
5. 查看"策略分析"页签的RL策略状态
6. 使用"智能助手"进行交互

---

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
from microgrid_digital_twin.rl_agent import EnergyManagementAgent, AdaptiveEnergyManager

# 创建智能体
agent = EnergyManagementAgent(state_dim=10, action_dim=2)

# 或使用自适应管理器
manager = AdaptiveEnergyManager()

# 训练循环
for episode in range(100):
    obs = digital_twin.get_observation()
    state = digital_twin.get_state()
    action = manager.select_action(obs, state, training=True)
    result = digital_twin.step(action)
    reward = manager.rl_agent.calculate_reward(state, action, result)
    next_obs = digital_twin.get_observation()
    manager.train(obs, action, reward, next_obs, False)
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

# 保存HTML文件（默认使用带页签模板）
viz.save_html("microgrid_3d.html", strategy_data=strategy_data)
```

---

## 🔧 系统配置

### 默认系统参数

| 指标 | 说明 |
|------|------|
| 光伏容量 | 100 kW |
| 风电容量 | 50 kW |
| 储能容量 | 200 kWh |
| 峰值负荷 | 150 kW |
| 电网交互 | 购100kW / 售50kW |
| 模拟周期 | 30天 |
| 时间步长 | 1分钟 |

### 自定义配置

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

digital_twin = MicrogridDigitalTwin(config)
```

### RL智能体参数

- **状态维度**: 10
- **动作维度**: 2（电池控制 + 柴油机开关）
- **学习率**: 0.001
- **折扣因子**: 0.99
- **经验回放容量**: 100,000
- **批量大小**: 64

---

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

---

## 🛠️ 技术栈

- **Python 3.7+** - 核心开发语言
- **NumPy** - 数值计算
- **Three.js** - 3D可视化
- **HTML5/CSS3/JavaScript** - 前端界面

---

## ❓ 常见问题

### Q: 提示 "ModuleNotFoundError: No module named 'numpy'"

**解决方案**: 
```bash
pip3 install numpy
```

如果使用虚拟环境，先激活环境：
```bash
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
pip install numpy
```

### Q: 权限错误

如果遇到权限错误，尝试：
```bash
pip3 install --user numpy
```

### Q: Python版本问题

确保使用Python 3.7+：
```bash
python3 --version
```

### Q: 界面无法显示

- 确保使用现代浏览器（Chrome 90+, Firefox 88+, Edge 90+）
- 检查JavaScript是否启用
- 确保Three.js库可以正常加载
- 检查浏览器控制台是否有错误

### Q: 3D场景无法交互

- 确保点击的是3D场景区域
- 尝试缩放视角获得更好的交互区域
- 检查浏览器是否支持WebGL

### Q: 数据不更新

- 确保模拟已经开始运行
- 等待一段时间积累足够数据
- 检查浏览器控制台是否有错误

### Q: 模拟速度慢

- 在"能量管理"页签中调整模拟速度滑块
- 最高可以10倍速运行
- 完整30天模拟建议使用5-10倍速

---

## 📈 性能优势

通过30天对比测试，RL策略相比传统规则策略：

- ✅ **成本节省**: 平均节省 10-15%
- ✅ **可再生能源利用率**: 提升 3-5%
- ✅ **系统稳定性**: SOC维持在健康范围
- ✅ **自适应能力**: 随着训练不断优化

---

## 📄 更新日志

详细的版本更新记录请查看 [CHANGELOG.md](CHANGELOG.md)

### 最新版本特性 (v2.0)

- ✨ 带页签的工业科技风格界面
- ✨ 6个功能页签：3D场景、实时监控、能量管理、数据分析、策略分析、智能助手
- ✨ 完整的数据显示逻辑
- ✨ 30天运行周期支持
- ✨ RL策略与规则策略对比分析
- ✨ 优化的代码结构和项目清理

---

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交Issue和Pull Request！

---

**微网数字孪生系统** - 智能能源管理的未来 🌱

如有问题或建议，欢迎反馈！ 🚀
