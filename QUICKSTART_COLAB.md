# 🚀 Google Colab 快速启动指南

## 最简单的运行方式

### 方法 1: 使用 Jupyter Notebook（推荐）

1. 打开 Google Colab: https://colab.research.google.com/
2. 上传 `run_in_colab.ipynb` 文件
3. 按顺序运行每个单元格
4. 点击生成的公共链接访问系统

### 方法 2: 直接运行 Python 代码

在 Colab 新建笔记本，复制粘贴以下代码：

```python
# Cell 1: 安装依赖
!pip install -q torch numpy pandas plotly gradio scipy scikit-learn tqdm
print("✅ 依赖安装完成")

# Cell 2: 上传文件
from google.colab import files
import os

print("请上传以下5个Python文件:")
print("  1. microgrid_digital_twin.py")
print("  2. prediction_system.py")
print("  3. rl_energy_management.py")
print("  4. visualization_3d.py")
print("  5. main_app.py")
print("\n点击下方按钮上传文件...")

uploaded = files.upload()

# 检查文件
required = ['microgrid_digital_twin.py', 'prediction_system.py', 
            'rl_energy_management.py', 'visualization_3d.py', 'main_app.py']
            
for f in required:
    if f in uploaded:
        print(f"✓ {f}")
    else:
        print(f"✗ 缺少 {f}")

# Cell 3: 启动系统
!python main_app.py

# 系统会输出类似这样的信息：
# Running on public URL: https://xxxxx.gradio.live
# 点击这个链接即可访问系统！
```

---

## 📦 文件说明

系统包含以下核心文件：

| 文件名 | 大小 | 说明 |
|--------|------|------|
| `microgrid_digital_twin.py` | 15KB | 微网数字孪生核心仿真引擎 |
| `prediction_system.py` | 12KB | 功率/电价/负荷预测系统 |
| `rl_energy_management.py` | 16KB | 强化学习能量管理 |
| `visualization_3d.py` | 19KB | 3D可视化系统 |
| `main_app.py` | 19KB | 主应用和Gradio界面 |
| `requirements.txt` | 300B | 依赖包列表 |
| `run_in_colab.ipynb` | 9KB | Colab运行笔记本 |

---

## 🎯 系统界面导航

启动后，你会看到6个标签页：

### 1. 🎮 系统控制
- **控制模式选择**: RL（推荐）/ Rule / Manual
- **操作按钮**:
  - 🔄 重置系统
  - ▶️ 单步运行
  - 🚀 连续运行（设置步数）
  - 🎓 训练RL智能体

**首次使用建议**:
```
1. 点击"重置系统"
2. 设置运行步数为50
3. 点击"连续运行"
4. 观察系统状态变化
```

### 2. 🌍 3D可视化
- 实时3D微网场景
- 能量流动动画
- 桑基图能量流
- 可旋转/缩放交互

**颜色说明**:
- 🟡 金色 = 太阳能
- 🔵 蓝色 = 风电
- 🟢 绿色 = 电池
- 🟣 紫色 = 负荷
- 🔴 红色 = 电网

### 3. 📊 数据仪表盘
- 功率流动曲线
- 电池SOC变化
- 成本累积
- 可再生能源占比
- 电价变化
- 负荷与发电对比

### 4. 🔮 预测系统
- 设置预测范围（1-12步）
- 调整预测误差
- 查看预测vs实际值
- 支持太阳能/风电/负荷/电价

### 5. 💬 智能查询
输入中文查询，例如：
- "当前系统概览"
- "电池状态如何"
- "太阳能发电是多少"
- "总成本是多少"

---

## 📊 使用示例

### 示例 1: 快速体验系统

```markdown
1. 重置系统
2. 选择"RL"控制模式
3. 运行100步
4. 切换到"3D可视化"查看场景
5. 切换到"数据仪表盘"分析数据
```

### 示例 2: 训练RL智能体

```markdown
1. 重置系统
2. 设置训练episodes为5
3. 点击"训练RL智能体"
4. 等待训练完成（约1-2分钟）
5. 运行100步观察训练后的表现
6. 对比"RL"和"Rule"模式的效果
```

### 示例 3: 预测系统测试

```markdown
1. 运行系统50步（积累历史数据）
2. 切换到"预测系统"
3. 设置预测范围为4步
4. 调整太阳能误差为20%
5. 点击"进行预测"
6. 观察预测值与真实值的差异
```

### 示例 4: 手动控制模式

```markdown
1. 重置系统
2. 选择"Manual"控制模式
3. 调整电池动作滑块（-1到1）
4. 点击"单步运行"
5. 观察系统响应
6. 尝试不同策略
```

---

## 🔬 高级功能

### 训练自己的策略

```python
# 在Colab新cell中运行
from main_app import system

# 训练更多episodes
results = system.rl_manager.train(system.microgrid, num_episodes=20)

# 查看训练曲线
import matplotlib.pyplot as plt
rewards = [r['reward'] for r in results]
plt.plot(rewards)
plt.title('Training Progress')
plt.xlabel('Episode')
plt.ylabel('Total Reward')
plt.show()

# 评估策略
eval_results = system.rl_manager.evaluate(system.microgrid, num_episodes=5)
print(f"平均奖励: {np.mean([r['reward'] for r in eval_results]):.2f}")
print(f"平均成本: ¥{np.mean([r['cost'] for r in eval_results]):.2f}")
```

### 导出数据分析

```python
# 导出运行历史
import pandas as pd

history_data = [s.to_dict() for s in system.microgrid.history]
df = pd.DataFrame(history_data)

# 保存到CSV
df.to_csv('microgrid_history.csv', index=False)

# 统计分析
print(df.describe())

# 下载文件
from google.colab import files
files.download('microgrid_history.csv')
```

### 自定义参数

```python
# 修改微网配置
system.microgrid.config['solar_capacity'] = 150  # 增加太阳能容量
system.microgrid.config['battery_capacity'] = 300  # 增加电池容量

# 重置系统应用新配置
system.reset_system()

# 修改预测误差
system.predictor.set_error_levels(
    solar_err=0.25,  # 25%误差
    wind_err=0.30,
    load_err=0.15,
    price_err=0.10
)
```

---

## 💡 性能优化建议

### Colab免费版

- 运行步数: 50-200步
- 训练episodes: 5-10个
- 3D刷新频率: 每20-50步

### Colab Pro

- 运行步数: 500-1000步
- 训练episodes: 20-50个
- 3D刷新频率: 实时

---

## 🐛 常见问题

### Q1: Gradio链接无法访问？

**A**: 
- 检查是否使用了 `share=True` 参数
- 链接有效期约72小时，过期需重新运行
- 尝试重新运行最后一个cell

### Q2: 训练时间太长？

**A**: 
- 减少episodes数（从5开始）
- 使用GPU加速（Runtime > Change runtime type > GPU）
- 减少仿真步数

### Q3: 3D可视化显示不全？

**A**: 
- 点击"刷新3D视图"按钮
- 使用Chrome或Firefox浏览器
- 清除浏览器缓存
- 确保运行了至少几个时间步

### Q4: 预测结果异常？

**A**: 
- 确保运行了足够的步数（至少20步）
- 检查预测误差设置是否合理
- 重新初始化预测器

### Q5: 内存不足？

**A**: 
- 重启Colab Runtime
- 减少训练episodes
- 清除变量: `system.microgrid.history = []`

### Q6: 想要离线运行？

**A**: 
```python
# 保存RL模型
system.rl_manager.save_model('my_model.pth')

# 下载模型
from google.colab import files
files.download('my_model.pth')

# 之后加载模型
system.rl_manager.load_model('my_model.pth')
```

---

## 📈 效果评估指标

### 经济性指标
- **总成本**: 越低越好
- **峰谷电价利用率**: 越高越好（低价时充电，高价时放电）

### 环境性指标
- **可再生能源占比**: 越高越好（目标>70%）
- **电网依赖度**: 越低越好

### 技术性指标
- **电池SOC范围**: 保持在20%-90%为健康
- **功率平衡**: 供需匹配程度

### RL训练指标
- **Episode奖励**: 逐渐增加表示学习效果好
- **成本下降**: 对比Rule模式应有10-30%改善

---

## 🎓 学习路径

### 初学者（30分钟）
1. ✅ 运行系统看效果
2. ✅ 尝试不同控制模式
3. ✅ 查看3D可视化
4. ✅ 使用智能查询

### 进阶（1小时）
1. ✅ 训练RL智能体
2. ✅ 对比RL vs Rule性能
3. ✅ 调整预测误差观察影响
4. ✅ 分析仪表盘数据

### 高级（2小时+）
1. ✅ 修改系统参数
2. ✅ 导出数据深度分析
3. ✅ 训练更多episodes
4. ✅ 实现自定义控制策略

---

## 📚 扩展阅读

- **强化学习**: PPO算法原理
- **微网技术**: 分布式能源系统
- **预测方法**: LSTM时间序列预测
- **优化控制**: 能量管理策略

---

## 🌟 系统特点总结

✅ **真实物理建模**: 基于实际微网参数和约束  
✅ **AI智能控制**: 强化学习自适应策略  
✅ **预测误差处理**: 更接近实际应用场景  
✅ **美观3D界面**: 直观展示系统运行  
✅ **中文交互**: 自然语言查询系统状态  
✅ **完全开源**: 可自由修改和扩展  

---

## 🎉 开始探索

现在你已经准备好了！上传文件，运行系统，开始探索微网数字孪生的世界吧！

**祝使用愉快！** 🌐⚡🔋

---

*最后更新: 2025-12-21*
