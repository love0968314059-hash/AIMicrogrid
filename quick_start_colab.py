"""
Quick Start Script for Google Colab
Run this cell to start the system
"""
import os
import sys
import subprocess
import threading
import time

def install_dependencies():
    """Install required packages"""
    print("安装依赖包...")
    packages = [
        'numpy', 'pandas', 'scikit-learn', 'torch', 'gym', 
        'stable-baselines3', 'flask', 'flask-cors', 
        'matplotlib', 'plotly', 'dash', 'dash-bootstrap-components',
        'pyngrok', 'tornado'
    ]
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"  安装 {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', package])

def start_server():
    """Start Flask server"""
    from app import app, initialize_system
    
    print("\n初始化系统...")
    initialize_system()
    
    print("\n启动Web服务器...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)

def main():
    """Main function"""
    print("=" * 60)
    print("微网数字孪生系统 - Colab快速启动")
    print("=" * 60)
    
    # Install dependencies
    install_dependencies()
    
    # Setup ngrok if available
    try:
        from pyngrok import ngrok
        print("\n设置ngrok...")
        public_url = ngrok.connect(5000)
        print(f"\n✓ 公共访问地址: {public_url}")
        print("请在浏览器中打开上述地址查看3D可视化界面")
    except Exception as e:
        print(f"\n警告: ngrok设置失败 ({e})")
        print("您可以使用Colab的端口转发功能或下载代码在本地运行")
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait a bit for server to start
    time.sleep(3)
    
    print("\n✓ 系统已启动!")
    print("服务器运行在 http://localhost:5000")
    print("\n提示:")
    print("- 使用ngrok URL访问3D界面")
    print("- 或使用Colab的端口转发功能")
    print("- 或下载代码在本地运行")
    
    # Keep script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n停止服务器...")

if __name__ == '__main__':
    main()
