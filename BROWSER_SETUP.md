# 浏览器运行方案

如果Colab无法直接显示3D界面，可以使用以下方案：

## 方案1: 使用ngrok (推荐)

### 在Colab中：

```python
# 1. 安装ngrok
!pip install pyngrok

# 2. 启动系统
from colab_main import run_in_colab
import threading
thread = threading.Thread(target=run_in_colab, daemon=True)
thread.start()

# 3. 等待几秒让服务器启动
import time
time.sleep(5)

# 4. 使用ngrok暴露端口
from pyngrok import ngrok
public_url = ngrok.connect(5000)
print(f"访问地址: {public_url}")
```

然后在浏览器中打开ngrok提供的URL即可。

## 方案2: 下载到本地运行

### 步骤：

1. **下载所有文件**
   - 从Colab下载整个项目文件夹
   - 或使用git clone

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行系统**
```bash
python app.py
# 或
./start.sh
```

4. **访问界面**
   - 打开浏览器访问: http://localhost:5000

## 方案3: 使用Colab端口转发

### 在Colab中：

```python
# 启动系统
from colab_main import run_in_colab
import threading
thread = threading.Thread(target=run_in_colab, daemon=True)
thread.start()

# 使用Colab的端口转发
from google.colab import output
output.serve_kernel_port_as_window(5000, path='/')
```

## 方案4: 使用本地Jupyter + 远程服务器

1. 在Colab中只运行后端（不启动Flask）
2. 在本地运行Flask服务器
3. 修改前端代码中的API地址指向Colab后端

## 故障排除

### 问题: 3D场景不显示

**解决方案:**
1. 检查浏览器控制台是否有错误
2. 确保Three.js库正确加载
3. 尝试使用Chrome或Firefox浏览器
4. 检查WebGL是否启用

### 问题: API请求失败

**解决方案:**
1. 检查服务器是否正在运行
2. 检查CORS设置
3. 检查防火墙设置
4. 查看服务器日志

### 问题: 性能问题

**解决方案:**
1. 减少3D对象数量
2. 降低更新频率
3. 使用更简单的材质
4. 关闭不必要的视觉效果

## 推荐配置

### 浏览器要求:
- Chrome 90+ (推荐)
- Firefox 88+
- Edge 90+
- Safari 14+ (可能有限制)

### 系统要求:
- 2GB+ RAM
- 支持WebGL的显卡
- 稳定的网络连接

## 快速测试

运行测试脚本验证系统：

```bash
python test_system.py
```

如果所有测试通过，系统应该可以正常运行。
