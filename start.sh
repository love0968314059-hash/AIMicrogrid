#!/bin/bash
# Startup script for Microgrid Digital Twin System

echo "=========================================="
echo "微网数字孪生系统启动脚本"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "激活虚拟环境..."
source venv/bin/activate

# Install dependencies
echo "安装依赖..."
pip install -q -r requirements.txt

# Run tests (optional)
if [ "$1" == "--test" ]; then
    echo "运行测试..."
    python test_system.py
fi

# Start the application
echo "启动应用..."
echo "访问 http://localhost:5000 查看界面"
python app.py
