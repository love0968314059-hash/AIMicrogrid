"""
Main entry point for running in Google Colab
This script sets up the system and provides options for visualization
"""
import os
import sys
from flask import Flask
from app import app, initialize_system
import threading
import time

def run_in_colab():
    """Run the system in Colab environment"""
    print("=" * 60)
    print("微网数字孪生系统 - Colab版本")
    print("=" * 60)
    
    # Initialize system
    print("\n正在初始化系统...")
    initialize_system()
    
    # Start Flask server
    print("\n启动Web服务器...")
    print("注意: Colab可能需要使用ngrok来暴露端口")
    
    # Try to use pyngrok if available
    try:
        from pyngrok import ngrok
        port = 5000
        public_url = ngrok.connect(port)
        print(f"\n✓ 服务器已启动!")
        print(f"✓ 访问地址: {public_url}")
        print(f"\n请在浏览器中打开上述地址查看3D可视化界面")
    except ImportError:
        print("\n未安装pyngrok，使用标准端口")
        print("在Colab中，您需要:")
        print("1. 运行: !pip install pyngrok")
        print("2. 或者使用Colab的端口转发功能")
        print("3. 或者下载代码在本地运行")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)


def run_local():
    """Run the system locally"""
    print("=" * 60)
    print("微网数字孪生系统 - 本地版本")
    print("=" * 60)
    
    # Initialize system
    print("\n正在初始化系统...")
    initialize_system()
    
    # Start Flask server
    print("\n启动Web服务器...")
    print("服务器将在 http://localhost:5000 启动")
    print("请在浏览器中打开上述地址查看3D可视化界面")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)


if __name__ == '__main__':
    # Check if running in Colab
    try:
        import google.colab
        IN_COLAB = True
    except ImportError:
        IN_COLAB = False
    
    if IN_COLAB:
        run_in_colab()
    else:
        run_local()
