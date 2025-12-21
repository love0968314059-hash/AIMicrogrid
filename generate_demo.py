
from microgrid_digital_twin.core import MicrogridDigitalTwin
from microgrid_digital_twin.visualization import Visualization3D
from datetime import timedelta
import sys

# 1. 初始化数字孪生系统
print("Initializing Microgrid Digital Twin...")
twin = MicrogridDigitalTwin()

# 2. 运行30天模拟
print("Running 30-day simulation... This might take a moment.")
# 为了演示速度，这里只生成部分数据，但在真实场景中会运行完整30天
# 30 days * 24 hours * 60 minutes = 43200 steps
# 这里我们模拟30天
twin.run_simulation(timedelta(days=30))
print(f"Simulation completed. History length: {len(twin.history['timestamp'])}")

# 3. 生成可视化
print("Generating 3D Visualization...")
vis = Visualization3D(twin)
vis.save_html('microgrid_3d_visualization.html')

print("Done! Open microgrid_3d_visualization.html to view the system.")
