# 微网数字孪生系统（预测 + 强化学习能量管理 + 3D 交互可视化 + 文本访问）

本项目提供一个**可在 Google Colab 运行**的 Demo：

- **微网数字孪生**：PV/风电/负荷/电价/电池/并网约束的仿真环境（支持随机扰动）
- **预测系统**：对功率、电价、负荷等进行短期预测，并显式注入**预测误差**
- **强化学习能量管理**：在存在预测误差条件下，使用 RL 生成自适应能量管理策略
- **策略执行效果生成与评估**：输出成本、弃电、SOC 约束违背、未满足负荷等指标与曲线
- **文本语言访问系统**：用中文/英文提问当前状态与评估结果（后端 `/query`）
- **3D 实时交互界面**：Three.js 3D 场景实时展示功率流、SOC、价格与策略效果，可交互控制

## 目录结构

- `microgrid_dt/`：数字孪生 + 预测 + RL + 评估 + 文本查询
- `server/`：FastAPI 服务（WebSocket 推送实时状态；REST 查询）
- `web/`：Three.js 前端（3D 交互界面）
- `colab_demo.ipynb`：Colab 一键演示（推荐）

## 本地运行（浏览器 3D 界面）

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m server.app
```

然后打开：`http://127.0.0.1:8000`

## Colab 运行

直接打开并运行 `colab_demo.ipynb`。

如果 Colab 不能直接内嵌 3D（浏览器策略/跨域等原因），Notebook 会输出一个 **ngrok** 的公网地址，直接在浏览器访问即可。