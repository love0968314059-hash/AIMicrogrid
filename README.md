# ⚡ 微电网数字孪生系统 | Microgrid Digital Twin System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.0+-green.svg)
![Colab](https://img.shields.io/badge/Google%20Colab-Ready-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**一个可在 Google Colab 中运行的交互式微电网3D可视化系统**

[🚀 在Colab中打开](#-快速开始) | [📖 功能介绍](#-功能特性) | [🎮 使用说明](#-使用说明)

</div>

---

## 📋 目录

- [功能特性](#-功能特性)
- [快速开始](#-快速开始)
- [系统架构](#-系统架构)
- [使用说明](#-使用说明)
- [文件结构](#-文件结构)
- [技术栈](#-技术栈)
- [自定义配置](#-自定义配置)

---

## 🎯 功能特性

### ☀️ 光伏发电系统
- 3D太阳能电池板阵列可视化
- 基于时间的太阳辐照度模拟
- 可调节装机容量 (10-500 kW)

### 🔋 储能系统
- 电池组3D模型展示
- 实时SOC (荷电状态) 监控
- 智能充放电策略模拟
- 可调节储能容量 (50-1000 kWh)

### 🏠 负荷管理
- 多类型建筑负荷模型 (住宅/商业/工业)
- 典型日负荷曲线模拟
- 可调节最大负荷 (50-500 kW)

### ⚡ 电网交互
- 购电/售电能量流动可视化
- 电网功率平衡计算
- 能量交互统计分析

### 📊 数据可视化
- **3D系统视图**: 完整微电网场景的3D展示
- **综合仪表盘**: 实时功率表盘和趋势图
- **能量流动图**: 桑基图展示能量流向
- **24小时分析**: 全天运行数据统计

---

## 🚀 快速开始

### 方式一: Google Colab (推荐)

1. 上传 `Microgrid_Digital_Twin_Colab.ipynb` 到 Google Colab
2. 按顺序运行所有代码单元格
3. 使用交互式控件操作系统

### 方式二: 本地 Jupyter Notebook

```bash
# 安装依赖
pip install plotly ipywidgets numpy

# 启动 Jupyter
jupyter notebook Microgrid_Digital_Twin_Colab.ipynb
```

### 方式三: Python 脚本

```python
from microgrid_digital_twin import run_microgrid_digital_twin

# 启动交互式系统
twin = run_microgrid_digital_twin()
```

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    微电网数字孪生系统                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ☀️ 光伏发电    ─────►  🔌 能量中心  ◄─────  ⚡ 电网        │
│   (PV Array)              │            (Power Grid)        │
│                           │                                 │
│                           │                                 │
│   🔋 储能系统   ◄────────┼────────►  🏠 负荷               │
│   (Battery)               │           (Load)               │
│                           ▼                                 │
│                  📊 数据监控与可视化                          │
│                  (Monitoring & Visualization)               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 能量流动逻辑

1. **光伏优先**: 光伏发电首先供应负荷
2. **储能调节**: 
   - 发电盈余时 → 储能充电
   - 发电不足时 → 储能放电
3. **电网平衡**: 剩余缺口由电网补充，盈余向电网售电

---

## 🎮 使用说明

### 交互式控件

| 控件 | 功能 | 范围 |
|------|------|------|
| 光伏容量 | 调节光伏装机容量 | 10-500 kW |
| 储能容量 | 调节储能系统容量 | 50-1000 kWh |
| 最大负荷 | 调节负荷峰值 | 50-500 kW |
| 模拟时间 | 选择一天中的时间点 | 0-23 时 |
| 视图模式 | 切换显示视图 | 3D/仪表盘/流动图 |

### 视图模式

1. **🏗️ 3D系统视图**
   - 完整的微电网3D场景
   - 可旋转、缩放视角
   - 能量流动线条动态显示

2. **📊 综合仪表盘**
   - 三个实时功率仪表盘
   - 历史功率曲线
   - 能量构成饼图

3. **🔄 能量流动图**
   - 桑基图展示能量流向
   - 直观显示各部分能量分配

---

## 📁 文件结构

```
workspace/
├── README.md                           # 项目说明文档
├── microgrid_digital_twin.py          # Python 主模块
└── Microgrid_Digital_Twin_Colab.ipynb # Colab 笔记本
```

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| **Python 3.7+** | 编程语言 |
| **Plotly** | 3D图形和交互式图表 |
| **ipywidgets** | 交互式控件 |
| **NumPy** | 数值计算 |
| **Jupyter/Colab** | 运行环境 |

---

## ⚙️ 自定义配置

### 修改默认参数

```python
from microgrid_digital_twin import MicrogridSimulator

# 创建自定义模拟器
simulator = MicrogridSimulator(
    pv_capacity=200,      # 光伏容量 200 kW
    battery_capacity=500,  # 储能容量 500 kWh
    max_load=180           # 最大负荷 180 kW
)
```

### 创建静态视图

```python
from microgrid_digital_twin import create_static_3d_view

# 生成指定参数的3D视图
fig = create_static_3d_view(
    pv_power=80,       # 当前光伏出力
    battery_soc=0.65,  # 电池SOC
    load_power=100     # 当前负荷
)
fig.show()
```

### 运行24小时模拟

```python
from microgrid_digital_twin import MicrogridSimulator

sim = MicrogridSimulator()

# 运行24小时
for _ in range(24 * 60):
    state = sim.simulate_step()

# 获取历史数据
history = sim.history
print(f"总发电量: {sum(history['pv_power'])/60:.1f} kWh")
```

---

## 📊 示例输出

### 3D系统视图
- 金色太阳能板阵列
- 青色储能电池组 (颜色随SOC变化)
- 蓝/绿/灰色负荷建筑
- 能量流动线条

### 综合仪表盘
- 光伏/储能/负荷仪表盘
- 实时功率曲线图
- 能量构成饼图

### 24小时分析
- 全天功率曲线
- SOC变化趋势
- 购电/售电统计
- 自发自用率计算

---

## 📝 开发说明

### 核心类

| 类名 | 功能 |
|------|------|
| `MicrogridSimulator` | 微电网数据模拟器 |
| `MicrogridDigitalTwin` | 数字孪生主类 (含UI) |

### 主要函数

| 函数 | 功能 |
|------|------|
| `create_solar_panel_3d()` | 创建3D太阳能板 |
| `create_battery_storage_3d()` | 创建3D储能电池 |
| `create_load_building_3d()` | 创建3D负荷建筑 |
| `create_energy_flow_lines()` | 创建能量流动线 |
| `run_microgrid_digital_twin()` | 启动完整系统 |

---

## 📜 许可证

MIT License

---

<div align="center">

**⚡ 微电网数字孪生系统 ⚡**

Made with ❤️ for Clean Energy

</div>
