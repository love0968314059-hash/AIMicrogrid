# 快速开始指南

## 本地运行（推荐）

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行系统
```bash
python app.py
```

### 3. 访问界面
打开浏览器访问: http://localhost:5000

## Google Colab运行

### 方法1: 使用快速启动脚本

1. 上传所有项目文件到Colab
2. 运行以下代码：

```python
exec(open('quick_start_colab.py').read())
```

### 方法2: 使用Jupyter Notebook

1. 打开 `run_colab.ipynb`
2. 按顺序运行所有单元格

### 方法3: 手动设置

```python
# 1. 安装依赖
!pip install -q numpy pandas scikit-learn torch gym stable-baselines3 flask flask-cors matplotlib plotly dash dash-bootstrap-components pyngrok tornado

# 2. 启动系统
from colab_main import run_in_colab
import threading
thread = threading.Thread(target=run_in_colab, daemon=True)
thread.start()

# 3. 等待启动
import time
time.sleep(5)

# 4. 使用ngrok
from pyngrok import ngrok
public_url = ngrok.connect(5000)
print(f"访问地址: {public_url}")
```

## 功能使用

### 3D可视化
- **旋转视角**: 鼠标左键拖拽
- **缩放**: 鼠标滚轮
- **平移**: 鼠标右键拖拽（如果支持）

### 控制面板
- **开始**: 启动实时仿真
- **停止**: 停止仿真
- **重置**: 重置系统到初始状态

### 自然语言查询示例
- "系统状态如何？"
- "电池电量多少？"
- "当前发电和负荷情况？"
- "电价是多少？"
- "未来24小时预测"
- "评估RL策略性能"
- "系统统计数据"

## 测试系统

运行测试脚本验证安装：

```bash
python test_system.py
```

## 常见问题

### Q: Colab无法显示3D界面？
A: 使用ngrok获取公共URL，或下载代码在本地运行。

### Q: 系统运行缓慢？
A: 减少RL训练轮数，或降低可视化更新频率。

### Q: 预测不准确？
A: 这是正常的，系统模拟了预测误差。可以调整config.py中的误差参数。

### Q: 浏览器不支持WebGL？
A: 使用Chrome或Firefox浏览器，确保WebGL已启用。

## 系统要求

- Python 3.7+
- 2GB+ RAM
- 支持WebGL的浏览器
- 稳定的网络连接（Colab）

## 下一步

- 阅读完整文档: README.md
- 查看浏览器设置: BROWSER_SETUP.md
- 自定义配置: config.py
