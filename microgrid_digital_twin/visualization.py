"""
3D可视化模块
============

基于Three.js的交互式3D微网可视化系统。
支持在Colab和浏览器中运行。
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import html
import base64


def generate_3d_visualization_html(state: Dict = None, history: Dict = None,
                                    width: int = 1200, height: int = 800) -> str:
    """
    生成完整的3D可视化HTML
    
    Args:
        state: 当前系统状态
        history: 历史数据
        width: 画布宽度
        height: 画布高度
        
    Returns:
        完整的HTML代码
    """
    
    # 准备数据
    state_json = json.dumps(state or {})
    history_json = json.dumps(history or {})
    
    html_template = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微网数字孪生3D可视化系统</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #e8e8e8;
            overflow: hidden;
        }}
        
        #container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}
        
        #canvas-container {{
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
        }}
        
        .overlay {{
            position: absolute;
            z-index: 100;
            pointer-events: auto;
        }}
        
        #header {{
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: linear-gradient(180deg, rgba(15, 52, 96, 0.95) 0%, rgba(15, 52, 96, 0.7) 100%);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            border-bottom: 1px solid rgba(100, 200, 255, 0.3);
            backdrop-filter: blur(10px);
        }}
        
        #header h1 {{
            font-size: 1.5em;
            color: #00d4ff;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }}
        
        #time-display {{
            font-size: 1.2em;
            color: #4ecdc4;
        }}
        
        #status-panel {{
            top: 80px;
            left: 20px;
            width: 280px;
            background: rgba(15, 52, 96, 0.85);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(100, 200, 255, 0.2);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        #chart-panel {{
            bottom: 20px;
            left: 20px;
            right: 320px;
            height: 200px;
            background: rgba(15, 52, 96, 0.85);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(100, 200, 255, 0.2);
            backdrop-filter: blur(10px);
        }}
        
        #control-panel {{
            top: 80px;
            right: 20px;
            width: 280px;
            background: rgba(15, 52, 96, 0.85);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(100, 200, 255, 0.2);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        #chat-panel {{
            bottom: 20px;
            right: 20px;
            width: 280px;
            height: 350px;
            background: rgba(15, 52, 96, 0.9);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(100, 200, 255, 0.2);
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(10px);
        }}
        
        .panel-title {{
            font-size: 1.1em;
            color: #00d4ff;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(100, 200, 255, 0.2);
        }}
        
        .status-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .status-label {{
            color: #aaa;
        }}
        
        .status-value {{
            font-weight: bold;
            color: #4ecdc4;
        }}
        
        .status-value.warning {{
            color: #ffa500;
        }}
        
        .status-value.danger {{
            color: #ff6b6b;
        }}
        
        .status-value.good {{
            color: #2ecc71;
        }}
        
        .control-btn {{
            width: 100%;
            padding: 12px;
            margin: 5px 0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95em;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: white;
        }}
        
        .btn-success {{
            background: linear-gradient(135deg, #2ecc71, #27ae60);
            color: white;
        }}
        
        .btn-warning {{
            background: linear-gradient(135deg, #f39c12, #e67e22);
            color: white;
        }}
        
        .btn-danger {{
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
        }}
        
        .control-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }}
        
        .slider-container {{
            margin: 15px 0;
        }}
        
        .slider-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }}
        
        input[type="range"] {{
            width: 100%;
            height: 8px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.1);
            outline: none;
            -webkit-appearance: none;
        }}
        
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #00d4ff;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }}
        
        #chat-messages {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 10px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }}
        
        .chat-message {{
            margin-bottom: 10px;
            padding: 8px 12px;
            border-radius: 8px;
            max-width: 90%;
        }}
        
        .chat-message.user {{
            background: #00d4ff;
            color: white;
            margin-left: auto;
        }}
        
        .chat-message.system {{
            background: rgba(255, 255, 255, 0.1);
            color: #e8e8e8;
        }}
        
        #chat-input-container {{
            display: flex;
            gap: 8px;
        }}
        
        #chat-input {{
            flex: 1;
            padding: 10px;
            border: 1px solid rgba(100, 200, 255, 0.3);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            outline: none;
        }}
        
        #chat-input:focus {{
            border-color: #00d4ff;
        }}
        
        #send-btn {{
            padding: 10px 15px;
            border: none;
            border-radius: 8px;
            background: #00d4ff;
            color: white;
            cursor: pointer;
        }}
        
        .power-bar {{
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }}
        
        .power-bar-fill {{
            height: 100%;
            transition: width 0.5s ease;
            border-radius: 4px;
        }}
        
        .power-bar-fill.solar {{
            background: linear-gradient(90deg, #f39c12, #f1c40f);
        }}
        
        .power-bar-fill.wind {{
            background: linear-gradient(90deg, #3498db, #2980b9);
        }}
        
        .power-bar-fill.battery {{
            background: linear-gradient(90deg, #2ecc71, #27ae60);
        }}
        
        .power-bar-fill.load {{
            background: linear-gradient(90deg, #e74c3c, #c0392b);
        }}
        
        #legend {{
            position: absolute;
            bottom: 240px;
            left: 20px;
            background: rgba(15, 52, 96, 0.85);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(100, 200, 255, 0.2);
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 5px 0;
            font-size: 0.9em;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        
        #metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            padding: 10px 20px;
            position: absolute;
            bottom: 240px;
            left: 320px;
            right: 320px;
        }}
        
        .metric-card {{
            background: rgba(15, 52, 96, 0.85);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(100, 200, 255, 0.2);
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #00d4ff;
        }}
        
        .metric-label {{
            font-size: 0.85em;
            color: #aaa;
            margin-top: 5px;
        }}
        
        canvas {{
            display: block;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .pulsing {{
            animation: pulse 2s infinite;
        }}
        
        .glow {{
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="canvas-container"></div>
        
        <!-- Header -->
        <div id="header" class="overlay">
            <h1>🔌 微网数字孪生系统 - 3D可视化控制中心</h1>
            <div id="time-display">--:--:--</div>
        </div>
        
        <!-- Status Panel -->
        <div id="status-panel" class="overlay">
            <div class="panel-title">📊 系统状态监控</div>
            
            <div class="status-item">
                <span class="status-label">☀️ 光伏发电</span>
                <span class="status-value" id="solar-power">-- kW</span>
            </div>
            <div class="power-bar">
                <div class="power-bar-fill solar" id="solar-bar" style="width: 0%"></div>
            </div>
            
            <div class="status-item">
                <span class="status-label">💨 风力发电</span>
                <span class="status-value" id="wind-power">-- kW</span>
            </div>
            <div class="power-bar">
                <div class="power-bar-fill wind" id="wind-bar" style="width: 0%"></div>
            </div>
            
            <div class="status-item">
                <span class="status-label">🔋 电池SOC</span>
                <span class="status-value" id="battery-soc">--%</span>
            </div>
            <div class="power-bar">
                <div class="power-bar-fill battery" id="battery-bar" style="width: 50%"></div>
            </div>
            
            <div class="status-item">
                <span class="status-label">📈 负荷功率</span>
                <span class="status-value" id="load-power">-- kW</span>
            </div>
            <div class="power-bar">
                <div class="power-bar-fill load" id="load-bar" style="width: 0%"></div>
            </div>
            
            <div class="status-item">
                <span class="status-label">💰 电价</span>
                <span class="status-value" id="price">¥--/kWh</span>
            </div>
            
            <div class="status-item">
                <span class="status-label">🌡️ 温度</span>
                <span class="status-value" id="temperature">--°C</span>
            </div>
            
            <div class="status-item">
                <span class="status-label">🌿 可再生比例</span>
                <span class="status-value good" id="renewable-ratio">--%</span>
            </div>
        </div>
        
        <!-- Control Panel -->
        <div id="control-panel" class="overlay">
            <div class="panel-title">🎮 能量管理控制</div>
            
            <div class="slider-container">
                <div class="slider-label">
                    <span>电池控制</span>
                    <span id="battery-action-value">0%</span>
                </div>
                <input type="range" id="battery-slider" min="-100" max="100" value="0">
                <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #888;">
                    <span>放电</span>
                    <span>充电</span>
                </div>
            </div>
            
            <button class="control-btn btn-primary" id="btn-auto">
                🤖 自动模式
            </button>
            
            <button class="control-btn btn-success" id="btn-charge">
                ⚡ 快速充电
            </button>
            
            <button class="control-btn btn-warning" id="btn-discharge">
                🔋 立即放电
            </button>
            
            <button class="control-btn btn-danger" id="btn-diesel">
                🏭 柴油机开关
            </button>
            
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
                <div class="panel-title" style="font-size: 0.95em;">⚙️ 模拟控制</div>
                
                <div class="slider-container">
                    <div class="slider-label">
                        <span>模拟速度</span>
                        <span id="speed-value">1x</span>
                    </div>
                    <input type="range" id="speed-slider" min="1" max="10" value="1">
                </div>
                
                <button class="control-btn btn-primary" id="btn-play">
                    ▶️ 开始模拟
                </button>
                
                <button class="control-btn btn-warning" id="btn-reset">
                    🔄 重置系统
                </button>
            </div>
        </div>
        
        <!-- Metrics Grid -->
        <div id="metrics-grid" class="overlay">
            <div class="metric-card">
                <div class="metric-value" id="total-cost">¥0.00</div>
                <div class="metric-label">累计成本</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="total-energy">0 kWh</div>
                <div class="metric-label">总发电量</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="co2-saved">0 kg</div>
                <div class="metric-label">CO2减排</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="efficiency">0%</div>
                <div class="metric-label">系统效率</div>
            </div>
        </div>
        
        <!-- Chart Panel -->
        <div id="chart-panel" class="overlay">
            <canvas id="power-chart"></canvas>
        </div>
        
        <!-- Legend -->
        <div id="legend" class="overlay">
            <div class="legend-item">
                <div class="legend-color" style="background: #f1c40f;"></div>
                <span>光伏阵列</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #3498db;"></div>
                <span>风力发电</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #2ecc71;"></div>
                <span>储能电池</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #e74c3c;"></div>
                <span>负荷中心</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #9b59b6;"></div>
                <span>电网连接</span>
            </div>
        </div>
        
        <!-- Chat Panel -->
        <div id="chat-panel" class="overlay">
            <div class="panel-title">💬 智能助手</div>
            <div id="chat-messages">
                <div class="chat-message system">
                    您好！我是微网数字孪生智能助手。您可以询问系统状态、控制设备或获取分析报告。
                </div>
            </div>
            <div id="chat-input-container">
                <input type="text" id="chat-input" placeholder="输入您的问题...">
                <button id="send-btn">发送</button>
            </div>
        </div>
    </div>
    
    <!-- Three.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    
    <script>
        // 初始状态数据
        let systemState = {state_json};
        let historyData = {history_json};
        
        // 全局变量
        let scene, camera, renderer, controls;
        let solarPanels = [], windTurbines = [], batterySystem, loadCenter, gridConnection;
        let powerFlowParticles = [];
        let isSimulating = false;
        let simulationSpeed = 1;
        let dieselOn = false;
        let autoMode = true;
        
        // 初始化Three.js场景
        function initScene() {{
            const container = document.getElementById('canvas-container');
            
            // 场景
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a1628);
            scene.fog = new THREE.Fog(0x0a1628, 100, 500);
            
            // 相机
            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(80, 60, 80);
            
            // 渲染器
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            container.appendChild(renderer.domElement);
            
            // 控制器
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.minDistance = 30;
            controls.maxDistance = 200;
            controls.maxPolarAngle = Math.PI / 2.1;
            
            // 光照
            setupLighting();
            
            // 创建地面和环境
            createEnvironment();
            
            // 创建微网组件
            createMicrogridComponents();
            
            // 创建电力流动粒子
            createPowerFlowSystem();
            
            // 窗口大小调整
            window.addEventListener('resize', onWindowResize);
        }}
        
        function setupLighting() {{
            // 环境光
            const ambientLight = new THREE.AmbientLight(0x404060, 0.5);
            scene.add(ambientLight);
            
            // 主光源（太阳）
            const sunLight = new THREE.DirectionalLight(0xffffff, 1);
            sunLight.position.set(50, 100, 50);
            sunLight.castShadow = true;
            sunLight.shadow.mapSize.width = 2048;
            sunLight.shadow.mapSize.height = 2048;
            sunLight.shadow.camera.near = 0.5;
            sunLight.shadow.camera.far = 500;
            sunLight.shadow.camera.left = -100;
            sunLight.shadow.camera.right = 100;
            sunLight.shadow.camera.top = 100;
            sunLight.shadow.camera.bottom = -100;
            scene.add(sunLight);
            
            // 补光
            const fillLight = new THREE.DirectionalLight(0x4080ff, 0.3);
            fillLight.position.set(-50, 50, -50);
            scene.add(fillLight);
            
            // 点光源（装饰）
            const pointLight1 = new THREE.PointLight(0x00d4ff, 0.5, 100);
            pointLight1.position.set(0, 30, 0);
            scene.add(pointLight1);
        }}
        
        function createEnvironment() {{
            // 地面
            const groundGeometry = new THREE.PlaneGeometry(300, 300);
            const groundMaterial = new THREE.MeshStandardMaterial({{
                color: 0x1a2a3a,
                roughness: 0.9,
                metalness: 0.1
            }});
            const ground = new THREE.Mesh(groundGeometry, groundMaterial);
            ground.rotation.x = -Math.PI / 2;
            ground.receiveShadow = true;
            scene.add(ground);
            
            // 网格线
            const gridHelper = new THREE.GridHelper(300, 30, 0x1e3a5f, 0x1e3a5f);
            gridHelper.position.y = 0.01;
            scene.add(gridHelper);
            
            // 添加装饰性圆环
            const ringGeometry = new THREE.RingGeometry(40, 42, 64);
            const ringMaterial = new THREE.MeshBasicMaterial({{
                color: 0x00d4ff,
                transparent: true,
                opacity: 0.3,
                side: THREE.DoubleSide
            }});
            const ring = new THREE.Mesh(ringGeometry, ringMaterial);
            ring.rotation.x = -Math.PI / 2;
            ring.position.y = 0.02;
            scene.add(ring);
        }}
        
        function createMicrogridComponents() {{
            // 光伏阵列
            createSolarPanels();
            
            // 风力发电机
            createWindTurbines();
            
            // 储能电池
            createBatterySystem();
            
            // 负荷中心
            createLoadCenter();
            
            // 电网连接
            createGridConnection();
            
            // 控制中心
            createControlCenter();
            
            // 连接线
            createConnectionLines();
        }}
        
        function createSolarPanels() {{
            const panelGroup = new THREE.Group();
            
            for (let i = 0; i < 4; i++) {{
                for (let j = 0; j < 3; j++) {{
                    const panelGeometry = new THREE.BoxGeometry(8, 0.3, 5);
                    const panelMaterial = new THREE.MeshStandardMaterial({{
                        color: 0x1a3c5c,
                        roughness: 0.3,
                        metalness: 0.8
                    }});
                    const panel = new THREE.Mesh(panelGeometry, panelMaterial);
                    panel.position.set(-40 + i * 10, 4, -30 + j * 8);
                    panel.rotation.x = -Math.PI / 6;
                    panel.castShadow = true;
                    panel.receiveShadow = true;
                    
                    // 支架
                    const poleGeometry = new THREE.CylinderGeometry(0.2, 0.2, 4);
                    const poleMaterial = new THREE.MeshStandardMaterial({{ color: 0x666666 }});
                    const pole = new THREE.Mesh(poleGeometry, poleMaterial);
                    pole.position.set(-40 + i * 10, 2, -30 + j * 8);
                    
                    panelGroup.add(panel);
                    panelGroup.add(pole);
                    solarPanels.push(panel);
                }}
            }}
            
            // 光伏标签
            const labelSprite = createLabel('☀️ 光伏阵列\\n100 kW', 0xf1c40f);
            labelSprite.position.set(-25, 15, -22);
            panelGroup.add(labelSprite);
            
            scene.add(panelGroup);
        }}
        
        function createWindTurbines() {{
            for (let i = 0; i < 2; i++) {{
                const turbineGroup = new THREE.Group();
                
                // 塔筒
                const towerGeometry = new THREE.CylinderGeometry(1, 2, 30, 8);
                const towerMaterial = new THREE.MeshStandardMaterial({{ color: 0xeeeeee }});
                const tower = new THREE.Mesh(towerGeometry, towerMaterial);
                tower.position.y = 15;
                tower.castShadow = true;
                turbineGroup.add(tower);
                
                // 机舱
                const nacelleGeometry = new THREE.BoxGeometry(6, 3, 3);
                const nacelleMaterial = new THREE.MeshStandardMaterial({{ color: 0xdddddd }});
                const nacelle = new THREE.Mesh(nacelleGeometry, nacelleMaterial);
                nacelle.position.y = 31;
                nacelle.castShadow = true;
                turbineGroup.add(nacelle);
                
                // 叶片
                const bladesGroup = new THREE.Group();
                for (let b = 0; b < 3; b++) {{
                    const bladeGeometry = new THREE.BoxGeometry(0.5, 12, 1);
                    const bladeMaterial = new THREE.MeshStandardMaterial({{ color: 0xffffff }});
                    const blade = new THREE.Mesh(bladeGeometry, bladeMaterial);
                    blade.position.y = 6;
                    blade.rotation.z = (b * Math.PI * 2) / 3;
                    blade.castShadow = true;
                    bladesGroup.add(blade);
                }}
                bladesGroup.position.set(3, 31, 0);
                turbineGroup.add(bladesGroup);
                turbineGroup.bladesGroup = bladesGroup;
                
                turbineGroup.position.set(40 + i * 25, 0, -30);
                scene.add(turbineGroup);
                windTurbines.push(turbineGroup);
            }}
            
            // 风机标签
            const labelSprite = createLabel('💨 风力发电\\n50 kW', 0x3498db);
            labelSprite.position.set(52, 45, -30);
            scene.add(labelSprite);
        }}
        
        function createBatterySystem() {{
            batterySystem = new THREE.Group();
            
            // 电池柜
            for (let i = 0; i < 3; i++) {{
                const cabinetGeometry = new THREE.BoxGeometry(6, 10, 4);
                const cabinetMaterial = new THREE.MeshStandardMaterial({{
                    color: 0x27ae60,
                    roughness: 0.5,
                    metalness: 0.5
                }});
                const cabinet = new THREE.Mesh(cabinetGeometry, cabinetMaterial);
                cabinet.position.set(-5 + i * 8, 5, 35);
                cabinet.castShadow = true;
                batterySystem.add(cabinet);
                
                // 电量指示灯
                const lightGeometry = new THREE.BoxGeometry(4, 0.5, 0.1);
                const lightMaterial = new THREE.MeshBasicMaterial({{ color: 0x2ecc71 }});
                const light = new THREE.Mesh(lightGeometry, lightMaterial);
                light.position.set(-5 + i * 8, 8, 37.1);
                batterySystem.add(light);
            }}
            
            // 底座
            const baseGeometry = new THREE.BoxGeometry(30, 1, 8);
            const baseMaterial = new THREE.MeshStandardMaterial({{ color: 0x444444 }});
            const base = new THREE.Mesh(baseGeometry, baseMaterial);
            base.position.set(3, 0.5, 35);
            batterySystem.add(base);
            
            // 标签
            const labelSprite = createLabel('🔋 储能系统\\n200 kWh', 0x2ecc71);
            labelSprite.position.set(3, 18, 35);
            batterySystem.add(labelSprite);
            
            scene.add(batterySystem);
        }}
        
        function createLoadCenter() {{
            loadCenter = new THREE.Group();
            
            // 主建筑
            const buildingGeometry = new THREE.BoxGeometry(20, 15, 15);
            const buildingMaterial = new THREE.MeshStandardMaterial({{
                color: 0x34495e,
                roughness: 0.7,
                metalness: 0.3
            }});
            const building = new THREE.Mesh(buildingGeometry, buildingMaterial);
            building.position.y = 7.5;
            building.castShadow = true;
            building.receiveShadow = true;
            loadCenter.add(building);
            
            // 窗户
            for (let floor = 0; floor < 2; floor++) {{
                for (let win = 0; win < 3; win++) {{
                    const windowGeometry = new THREE.PlaneGeometry(3, 3);
                    const windowMaterial = new THREE.MeshBasicMaterial({{
                        color: 0xffdd88,
                        transparent: true,
                        opacity: 0.8
                    }});
                    const window = new THREE.Mesh(windowGeometry, windowMaterial);
                    window.position.set(-6 + win * 6, 4 + floor * 5, 7.6);
                    loadCenter.add(window);
                }}
            }}
            
            // 屋顶
            const roofGeometry = new THREE.BoxGeometry(22, 2, 17);
            const roofMaterial = new THREE.MeshStandardMaterial({{ color: 0x2c3e50 }});
            const roof = new THREE.Mesh(roofGeometry, roofMaterial);
            roof.position.y = 16;
            loadCenter.add(roof);
            
            loadCenter.position.set(0, 0, 0);
            
            // 标签
            const labelSprite = createLabel('🏭 负荷中心\\n150 kW峰值', 0xe74c3c);
            labelSprite.position.set(0, 25, 0);
            loadCenter.add(labelSprite);
            
            scene.add(loadCenter);
        }}
        
        function createGridConnection() {{
            gridConnection = new THREE.Group();
            
            // 变电站
            const stationGeometry = new THREE.BoxGeometry(8, 12, 8);
            const stationMaterial = new THREE.MeshStandardMaterial({{
                color: 0x8e44ad,
                roughness: 0.6,
                metalness: 0.4
            }});
            const station = new THREE.Mesh(stationGeometry, stationMaterial);
            station.position.y = 6;
            station.castShadow = true;
            gridConnection.add(station);
            
            // 高压线塔
            const poleGeometry = new THREE.CylinderGeometry(0.3, 0.5, 25, 6);
            const poleMaterial = new THREE.MeshStandardMaterial({{ color: 0x666666 }});
            const pole = new THREE.Mesh(poleGeometry, poleMaterial);
            pole.position.set(0, 12.5, -10);
            gridConnection.add(pole);
            
            // 横梁
            const crossbarGeometry = new THREE.BoxGeometry(12, 0.5, 0.5);
            const crossbar = new THREE.Mesh(crossbarGeometry, poleMaterial);
            crossbar.position.set(0, 23, -10);
            gridConnection.add(crossbar);
            
            gridConnection.position.set(60, 0, 30);
            
            // 标签
            const labelSprite = createLabel('⚡ 电网连接\\n100kW进/50kW出', 0x9b59b6);
            labelSprite.position.set(0, 30, -5);
            gridConnection.add(labelSprite);
            
            scene.add(gridConnection);
        }}
        
        function createControlCenter() {{
            const controlGroup = new THREE.Group();
            
            // 控制室
            const roomGeometry = new THREE.BoxGeometry(10, 8, 10);
            const roomMaterial = new THREE.MeshStandardMaterial({{
                color: 0x2980b9,
                roughness: 0.5,
                metalness: 0.5
            }});
            const room = new THREE.Mesh(roomGeometry, roomMaterial);
            room.position.y = 4;
            room.castShadow = true;
            controlGroup.add(room);
            
            // 天线
            const antennaGeometry = new THREE.CylinderGeometry(0.1, 0.1, 8);
            const antennaMaterial = new THREE.MeshStandardMaterial({{ color: 0xcccccc }});
            const antenna = new THREE.Mesh(antennaGeometry, antennaMaterial);
            antenna.position.set(0, 12, 0);
            controlGroup.add(antenna);
            
            // 信号球
            const ballGeometry = new THREE.SphereGeometry(0.5, 16, 16);
            const ballMaterial = new THREE.MeshBasicMaterial({{ color: 0x00d4ff }});
            const ball = new THREE.Mesh(ballGeometry, ballMaterial);
            ball.position.set(0, 16, 0);
            controlGroup.add(ball);
            
            controlGroup.position.set(-50, 0, 30);
            
            const labelSprite = createLabel('🎛️ 控制中心', 0x00d4ff);
            labelSprite.position.set(0, 20, 0);
            controlGroup.add(labelSprite);
            
            scene.add(controlGroup);
        }}
        
        function createLabel(text, color) {{
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 256;
            canvas.height = 128;
            
            context.fillStyle = 'rgba(0, 0, 0, 0.7)';
            context.beginPath();
            context.roundRect(0, 0, 256, 128, 15);
            context.fill();
            
            context.strokeStyle = '#' + color.toString(16).padStart(6, '0');
            context.lineWidth = 2;
            context.beginPath();
            context.roundRect(2, 2, 252, 124, 13);
            context.stroke();
            
            context.fillStyle = '#ffffff';
            context.font = 'bold 20px Arial';
            context.textAlign = 'center';
            
            const lines = text.split('\\n');
            lines.forEach((line, i) => {{
                context.fillText(line, 128, 50 + i * 30);
            }});
            
            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({{
                map: texture,
                transparent: true
            }});
            const sprite = new THREE.Sprite(spriteMaterial);
            sprite.scale.set(15, 7.5, 1);
            
            return sprite;
        }}
        
        function createConnectionLines() {{
            const lineMaterial = new THREE.LineBasicMaterial({{
                color: 0x00d4ff,
                transparent: true,
                opacity: 0.5
            }});
            
            const connections = [
                [[-25, 2, -22], [0, 2, 0]],  // 光伏到负荷
                [[52, 2, -30], [0, 2, 0]],   // 风机到负荷
                [[3, 2, 35], [0, 2, 0]],     // 电池到负荷
                [[0, 2, 0], [60, 2, 30]],    // 负荷到电网
                [[-50, 2, 30], [0, 2, 0]]    // 控制中心到负荷
            ];
            
            connections.forEach(conn => {{
                const points = [
                    new THREE.Vector3(...conn[0]),
                    new THREE.Vector3(...conn[1])
                ];
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const line = new THREE.Line(geometry, lineMaterial);
                scene.add(line);
            }});
        }}
        
        function createPowerFlowSystem() {{
            // 创建粒子系统表示电力流动
            const particleCount = 100;
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);
            const colors = new Float32Array(particleCount * 3);
            
            for (let i = 0; i < particleCount; i++) {{
                positions[i * 3] = (Math.random() - 0.5) * 100;
                positions[i * 3 + 1] = Math.random() * 2 + 1;
                positions[i * 3 + 2] = (Math.random() - 0.5) * 100;
                
                colors[i * 3] = 0;
                colors[i * 3 + 1] = 0.8;
                colors[i * 3 + 2] = 1;
            }}
            
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
            
            const material = new THREE.PointsMaterial({{
                size: 0.5,
                vertexColors: true,
                transparent: true,
                opacity: 0.8
            }});
            
            const particles = new THREE.Points(geometry, material);
            scene.add(particles);
            powerFlowParticles.push({{ points: particles, positions: positions }});
        }}
        
        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}
        
        // 动画循环
        function animate() {{
            requestAnimationFrame(animate);
            
            // 更新控制器
            controls.update();
            
            // 风机叶片旋转
            windTurbines.forEach(turbine => {{
                if (turbine.bladesGroup) {{
                    turbine.bladesGroup.rotation.x += 0.02 * simulationSpeed;
                }}
            }});
            
            // 电力流动粒子动画
            powerFlowParticles.forEach(system => {{
                const positions = system.points.geometry.attributes.position.array;
                for (let i = 0; i < positions.length / 3; i++) {{
                    positions[i * 3 + 1] += 0.05;
                    if (positions[i * 3 + 1] > 5) {{
                        positions[i * 3 + 1] = 1;
                    }}
                }}
                system.points.geometry.attributes.position.needsUpdate = true;
            }});
            
            // 电池呼吸灯效果
            if (batterySystem) {{
                const pulse = Math.sin(Date.now() * 0.003) * 0.2 + 0.8;
                batterySystem.children.forEach(child => {{
                    if (child.material && child.material.emissive) {{
                        child.material.emissiveIntensity = pulse;
                    }}
                }});
            }}
            
            renderer.render(scene, camera);
        }}
        
        // 更新UI显示
        function updateDisplay(state) {{
            if (!state || !state.components) return;
            
            const components = state.components;
            const weather = state.weather || {{}};
            const price = state.price || {{}};
            const stats = state.statistics || {{}};
            
            // 更新状态面板
            document.getElementById('solar-power').textContent = 
                (components.solar?.current_power || 0).toFixed(1) + ' kW';
            document.getElementById('solar-bar').style.width = 
                ((components.solar?.current_power || 0) / 100 * 100) + '%';
            
            document.getElementById('wind-power').textContent = 
                (components.wind?.current_power || 0).toFixed(1) + ' kW';
            document.getElementById('wind-bar').style.width = 
                ((components.wind?.current_power || 0) / 50 * 100) + '%';
            
            const soc = (components.battery?.soc || 0.5) * 100;
            document.getElementById('battery-soc').textContent = soc.toFixed(1) + '%';
            document.getElementById('battery-bar').style.width = soc + '%';
            
            const socElement = document.getElementById('battery-soc');
            socElement.className = 'status-value ' + 
                (soc < 20 ? 'danger' : soc < 40 ? 'warning' : 'good');
            
            document.getElementById('load-power').textContent = 
                (components.load?.current || 0).toFixed(1) + ' kW';
            document.getElementById('load-bar').style.width = 
                ((components.load?.current || 0) / 150 * 100) + '%';
            
            document.getElementById('price').textContent = 
                '¥' + (price.buy_price || 0.8).toFixed(2) + '/kWh';
            
            document.getElementById('temperature').textContent = 
                (weather.temperature || 20).toFixed(1) + '°C';
            
            const renewableRatio = (stats.renewable_ratio || 0) * 100;
            document.getElementById('renewable-ratio').textContent = 
                renewableRatio.toFixed(1) + '%';
            
            // 更新指标卡片
            document.getElementById('total-cost').textContent = 
                '¥' + (stats.total_cost || 0).toFixed(2);
            document.getElementById('total-energy').textContent = 
                (stats.total_renewable_energy || 0).toFixed(1) + ' kWh';
            document.getElementById('co2-saved').textContent = 
                ((stats.total_renewable_energy || 0) * 0.5).toFixed(1) + ' kg';
            document.getElementById('efficiency').textContent = 
                renewableRatio.toFixed(0) + '%';
            
            // 更新时间
            if (state.timestamp) {{
                const date = new Date(state.timestamp);
                document.getElementById('time-display').textContent = 
                    date.toLocaleString('zh-CN');
            }}
        }}
        
        // 简单图表绘制
        function drawChart(history) {{
            const canvas = document.getElementById('power-chart');
            const ctx = canvas.getContext('2d');
            
            canvas.width = canvas.parentElement.clientWidth - 30;
            canvas.height = canvas.parentElement.clientHeight - 30;
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 绘制坐标轴
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(40, 10);
            ctx.lineTo(40, canvas.height - 20);
            ctx.lineTo(canvas.width - 10, canvas.height - 20);
            ctx.stroke();
            
            // 绘制标题
            ctx.fillStyle = '#00d4ff';
            ctx.font = '14px Arial';
            ctx.fillText('功率趋势图 (kW)', 50, 20);
            
            if (!history || !history.solar_power || history.solar_power.length === 0) {{
                ctx.fillStyle = '#888';
                ctx.fillText('暂无数据', canvas.width / 2 - 30, canvas.height / 2);
                return;
            }}
            
            const dataLength = Math.min(60, history.solar_power.length);
            const startIdx = Math.max(0, history.solar_power.length - dataLength);
            
            const chartWidth = canvas.width - 60;
            const chartHeight = canvas.height - 40;
            
            // 数据系列
            const series = [
                {{ data: history.solar_power, color: '#f1c40f', name: '光伏' }},
                {{ data: history.wind_power, color: '#3498db', name: '风电' }},
                {{ data: history.load_power, color: '#e74c3c', name: '负荷' }}
            ];
            
            // 找最大值
            let maxVal = 0;
            series.forEach(s => {{
                if (s.data) {{
                    const sliced = s.data.slice(startIdx);
                    maxVal = Math.max(maxVal, ...sliced);
                }}
            }});
            maxVal = Math.max(maxVal, 100) * 1.1;
            
            // 绘制数据线
            series.forEach(s => {{
                if (!s.data || s.data.length === 0) return;
                
                ctx.strokeStyle = s.color;
                ctx.lineWidth = 2;
                ctx.beginPath();
                
                const sliced = s.data.slice(startIdx);
                sliced.forEach((val, i) => {{
                    const x = 40 + (i / (dataLength - 1)) * chartWidth;
                    const y = (canvas.height - 20) - (val / maxVal) * chartHeight;
                    
                    if (i === 0) {{
                        ctx.moveTo(x, y);
                    }} else {{
                        ctx.lineTo(x, y);
                    }}
                }});
                
                ctx.stroke();
            }});
            
            // 绘制图例
            let legendX = canvas.width - 150;
            series.forEach((s, i) => {{
                ctx.fillStyle = s.color;
                ctx.fillRect(legendX, 10 + i * 18, 12, 12);
                ctx.fillStyle = '#fff';
                ctx.fillText(s.name, legendX + 18, 20 + i * 18);
            }});
        }}
        
        // 聊天功能
        function handleChat(message) {{
            const chatMessages = document.getElementById('chat-messages');
            
            // 添加用户消息
            const userMsg = document.createElement('div');
            userMsg.className = 'chat-message user';
            userMsg.textContent = message;
            chatMessages.appendChild(userMsg);
            
            // 模拟AI回复
            setTimeout(() => {{
                const response = generateResponse(message);
                const sysMsg = document.createElement('div');
                sysMsg.className = 'chat-message system';
                sysMsg.textContent = response;
                chatMessages.appendChild(sysMsg);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }}, 500);
            
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}
        
        function generateResponse(message) {{
            message = message.toLowerCase();
            
            if (message.includes('状态') || message.includes('status')) {{
                return '当前系统运行正常。光伏发电约65kW，风电约25kW，电池SOC 55%，负荷约90kW。可再生能源利用率达到85%。';
            }} else if (message.includes('电池') || message.includes('battery')) {{
                return '储能系统状态良好。当前SOC: 55%，剩余容量约110kWh，健康度98%。建议在低电价时段充电。';
            }} else if (message.includes('成本') || message.includes('cost')) {{
                return '今日累计电费约¥45.60，比昨日节省12%。主要节省来自光伏发电高峰期的自发自用。';
            }} else if (message.includes('预测') || message.includes('forecast')) {{
                return '未来1小时预测: 光伏将保持在50-70kW，风电15-30kW，负荷预计上升至100kW。建议维持当前储能策略。';
            }} else if (message.includes('帮助') || message.includes('help')) {{
                return '您可以询问: 系统状态、电池情况、今日成本、未来预测、策略建议等。也可以使用控制面板直接操作设备。';
            }} else {{
                return '收到您的消息。当前系统运行稳定，如需详细信息请询问"系统状态"或"帮助"。';
            }}
        }}
        
        // 控制按钮事件
        function setupControls() {{
            // 电池滑块
            document.getElementById('battery-slider').addEventListener('input', function() {{
                const value = this.value;
                document.getElementById('battery-action-value').textContent = 
                    (value > 0 ? '+' : '') + value + '%';
            }});
            
            // 速度滑块
            document.getElementById('speed-slider').addEventListener('input', function() {{
                simulationSpeed = parseInt(this.value);
                document.getElementById('speed-value').textContent = simulationSpeed + 'x';
            }});
            
            // 自动模式
            document.getElementById('btn-auto').addEventListener('click', function() {{
                autoMode = !autoMode;
                this.style.background = autoMode ? 
                    'linear-gradient(135deg, #00d4ff, #0099cc)' : 
                    'linear-gradient(135deg, #666, #444)';
                addChatMessage('system', autoMode ? '已启用自动优化模式' : '已切换至手动模式');
            }});
            
            // 快速充电
            document.getElementById('btn-charge').addEventListener('click', function() {{
                addChatMessage('system', '⚡ 电池快速充电已启动');
            }});
            
            // 立即放电
            document.getElementById('btn-discharge').addEventListener('click', function() {{
                addChatMessage('system', '🔋 电池开始放电供电');
            }});
            
            // 柴油机开关
            document.getElementById('btn-diesel').addEventListener('click', function() {{
                dieselOn = !dieselOn;
                this.style.background = dieselOn ? 
                    'linear-gradient(135deg, #27ae60, #2ecc71)' : 
                    'linear-gradient(135deg, #e74c3c, #c0392b)';
                addChatMessage('system', dieselOn ? '🏭 柴油发电机已启动' : '🛑 柴油发电机已停止');
            }});
            
            // 开始/暂停模拟
            document.getElementById('btn-play').addEventListener('click', function() {{
                isSimulating = !isSimulating;
                this.textContent = isSimulating ? '⏸️ 暂停模拟' : '▶️ 开始模拟';
                if (isSimulating) {{
                    startSimulation();
                }}
            }});
            
            // 重置
            document.getElementById('btn-reset').addEventListener('click', function() {{
                isSimulating = false;
                document.getElementById('btn-play').textContent = '▶️ 开始模拟';
                addChatMessage('system', '🔄 系统已重置');
            }});
            
            // 聊天发送
            document.getElementById('send-btn').addEventListener('click', function() {{
                const input = document.getElementById('chat-input');
                if (input.value.trim()) {{
                    handleChat(input.value.trim());
                    input.value = '';
                }}
            }});
            
            document.getElementById('chat-input').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter' && this.value.trim()) {{
                    handleChat(this.value.trim());
                    this.value = '';
                }}
            }});
        }}
        
        function addChatMessage(type, text) {{
            const chatMessages = document.getElementById('chat-messages');
            const msg = document.createElement('div');
            msg.className = 'chat-message ' + type;
            msg.textContent = text;
            chatMessages.appendChild(msg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}
        
        // 模拟运行
        function startSimulation() {{
            if (!isSimulating) return;
            
            // 模拟状态更新
            const hour = new Date().getHours();
            const solarBase = Math.sin((hour - 6) * Math.PI / 12) * 80;
            const solar = Math.max(0, solarBase + (Math.random() - 0.5) * 20);
            const wind = 15 + Math.random() * 20;
            const load = 80 + Math.sin(hour * Math.PI / 12) * 40 + (Math.random() - 0.5) * 20;
            
            const mockState = {{
                timestamp: new Date().toISOString(),
                components: {{
                    solar: {{ current_power: solar, capacity: 100 }},
                    wind: {{ current_power: wind, capacity: 50 }},
                    battery: {{ soc: 0.3 + Math.random() * 0.5, capacity: 200, health: 0.98 }},
                    load: {{ current: load, base: 80, peak: 150 }},
                    grid: {{ connected: true }}
                }},
                weather: {{
                    temperature: 20 + Math.random() * 10,
                    wind_speed: 5 + Math.random() * 10,
                    irradiance: solar * 10
                }},
                price: {{
                    buy_price: hour >= 9 && hour < 12 || hour >= 17 && hour < 21 ? 1.2 : 
                              hour >= 23 || hour < 7 ? 0.4 : 0.8
                }},
                statistics: {{
                    total_cost: Math.random() * 100,
                    total_renewable_energy: Math.random() * 500,
                    renewable_ratio: 0.5 + Math.random() * 0.4
                }}
            }};
            
            updateDisplay(mockState);
            
            // 更新历史数据用于图表
            if (!window.simHistory) {{
                window.simHistory = {{ solar_power: [], wind_power: [], load_power: [] }};
            }}
            window.simHistory.solar_power.push(solar);
            window.simHistory.wind_power.push(wind);
            window.simHistory.load_power.push(load);
            
            if (window.simHistory.solar_power.length > 60) {{
                window.simHistory.solar_power.shift();
                window.simHistory.wind_power.shift();
                window.simHistory.load_power.shift();
            }}
            
            drawChart(window.simHistory);
            
            setTimeout(() => startSimulation(), 1000 / simulationSpeed);
        }}
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {{
            initScene();
            animate();
            setupControls();
            
            // 初始显示
            if (systemState && Object.keys(systemState).length > 0) {{
                updateDisplay(systemState);
            }}
            
            if (historyData && Object.keys(historyData).length > 0) {{
                drawChart(historyData);
            }} else {{
                drawChart(null);
            }}
            
            // 自动开始模拟
            setTimeout(() => {{
                document.getElementById('btn-play').click();
            }}, 1000);
        }});
    </script>
</body>
</html>
'''
    
    return html_template


class Visualization3D:
    """3D可视化管理器"""
    
    def __init__(self, digital_twin=None):
        self.digital_twin = digital_twin
        self.html_content = None
        
    def generate(self) -> str:
        """生成3D可视化HTML"""
        state = None
        history = None
        
        if self.digital_twin:
            state = self.digital_twin.get_state()
            history = self.digital_twin.history
        
        self.html_content = generate_3d_visualization_html(state, history)
        return self.html_content
    
    def display_in_notebook(self):
        """在Jupyter Notebook中显示"""
        try:
            from IPython.display import HTML, IFrame, display
            import tempfile
            import os
            
            html = self.generate()
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', 
                                             delete=False) as f:
                f.write(html)
                temp_path = f.name
            
            # 尝试使用IFrame显示
            display(HTML(f'''
                <iframe src="{temp_path}" width="100%" height="800px" 
                        style="border: none; border-radius: 10px;"></iframe>
            '''))
            
            return temp_path
            
        except ImportError:
            print("请在Jupyter Notebook环境中运行")
            return None
    
    def save_html(self, filepath: str):
        """保存HTML文件"""
        html = self.generate()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"3D可视化界面已保存到: {filepath}")
        return filepath
    
    def get_colab_display_code(self) -> str:
        """获取在Colab中显示的代码"""
        return '''
# 在Google Colab中显示3D可视化
from IPython.display import HTML, display
import base64

# 生成HTML
html_content = visualization.generate()

# 方法1: 直接嵌入显示
display(HTML(html_content))

# 方法2: 如果上述方法不工作，保存并提供下载链接
with open('microgrid_3d.html', 'w') as f:
    f.write(html_content)
    
from google.colab import files
files.download('microgrid_3d.html')
print("请下载HTML文件并在浏览器中打开")

# 方法3: 使用ngrok创建公开链接（需要安装pyngrok）
# !pip install pyngrok
# from pyngrok import ngrok
# 然后启动本地服务器并使用ngrok
'''
