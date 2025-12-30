"""
带页签的工业科技风格可视化模板
用于生成分页签的微网数字孪生界面
"""

def get_tabbed_html_template(state_json: str, history_json: str, strategy_json: str) -> str:
    """生成带页签的工业科技风格HTML模板"""
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微网数字孪生系统 - 工业控制中心</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', 'Consolas', monospace;
            background: #0a0e27;
            background-image: 
                linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            color: #e8e8e8;
            overflow: hidden;
            position: relative;
        }}
        
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.05) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(0, 255, 212, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }}
        
        #app-container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            position: relative;
            z-index: 1;
        }}
        
        /* 顶部标题栏 */
        #top-header {{
            height: 70px;
            background: linear-gradient(180deg, rgba(10, 14, 39, 0.98) 0%, rgba(15, 25, 55, 0.95) 100%);
            border-bottom: 2px solid #00d4ff;
            box-shadow: 0 2px 20px rgba(0, 212, 255, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 30px;
            position: relative;
            z-index: 100;
        }}
        
        #top-header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, 
                transparent 0%,
                #00d4ff 20%,
                #00ffd4 50%,
                #00d4ff 80%,
                transparent 100%);
            animation: scanline 3s linear infinite;
        }}
        
        @keyframes scanline {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        
        #logo-section {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        #logo-icon {{
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, #00d4ff, #00ffd4);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.5),
                        inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }}
        
        #system-title {{
            font-size: 1.8em;
            font-weight: 700;
            background: linear-gradient(135deg, #00d4ff, #00ffd4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
            letter-spacing: 2px;
        }}
        
        #header-info {{
            display: flex;
            align-items: center;
            gap: 30px;
        }}
        
        .info-item {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }}
        
        .info-label {{
            font-size: 0.75em;
            color: #7a8ca3;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .info-value {{
            font-size: 1.1em;
            color: #00d4ff;
            font-weight: 600;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }}
        
        /* 页签导航栏 */
        #tab-navigation {{
            height: 60px;
            background: rgba(15, 25, 55, 0.9);
            border-bottom: 1px solid rgba(0, 212, 255, 0.2);
            display: flex;
            align-items: center;
            padding: 0 20px;
            gap: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 99;
        }}
        
        .tab-button {{
            height: 50px;
            padding: 0 25px;
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            color: #7a8ca3;
            font-size: 0.95em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            display: flex;
            align-items: center;
            gap: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .tab-button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #00d4ff, #00ffd4);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }}
        
        .tab-button:hover {{
            color: #00d4ff;
            background: rgba(0, 212, 255, 0.05);
        }}
        
        .tab-button.active {{
            color: #00d4ff;
            border-bottom-color: #00d4ff;
            background: rgba(0, 212, 255, 0.1);
        }}
        
        .tab-button.active::before {{
            transform: scaleX(1);
        }}
        
        .tab-icon {{
            font-size: 1.2em;
        }}
        
        /* 内容区域 */
        #content-area {{
            flex: 1;
            position: relative;
            overflow: hidden;
        }}
        
        .tab-content {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            display: none;
        }}
        
        .tab-content.active {{
            opacity: 1;
            pointer-events: auto;
            display: block;
        }}
        
        /* 3D场景页签 */
        #tab-3d {{
            position: relative;
        }}
        
        #canvas-container {{
            width: 100%;
            height: 100%;
        }}
        
        /* 实时监控页签 */
        #tab-monitor {{
            padding: 30px;
            overflow-y: auto;
            background: rgba(10, 14, 39, 0.5);
        }}
        
        .monitor-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .monitor-card {{
            background: linear-gradient(135deg, rgba(15, 25, 55, 0.9), rgba(10, 20, 45, 0.9));
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 20px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }}
        
        .monitor-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00d4ff, transparent);
        }}
        
        .card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(0, 212, 255, 0.2);
        }}
        
        .card-title {{
            font-size: 1.1em;
            color: #00d4ff;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .card-value {{
            font-size: 1.8em;
            font-weight: 700;
            color: #00ffd4;
            text-shadow: 0 0 15px rgba(0, 255, 212, 0.5);
        }}
        
        .status-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        .status-label {{
            color: #7a8ca3;
            font-size: 0.9em;
        }}
        
        .status-value {{
            color: #e8e8e8;
            font-weight: 600;
        }}
        
        .status-value.good {{
            color: #00ffd4;
        }}
        
        .status-value.warning {{
            color: #ffa500;
        }}
        
        .status-value.danger {{
            color: #ff4757;
        }}
        
        .progress-bar-container {{
            margin-top: 10px;
            height: 8px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }}
        
        .progress-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #00ffd4);
            border-radius: 4px;
            transition: width 0.5s ease;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }}
        
        /* 能量管理页签 */
        #tab-control {{
            padding: 30px;
            overflow-y: auto;
            background: rgba(10, 14, 39, 0.5);
        }}
        
        .control-section {{
            background: linear-gradient(135deg, rgba(15, 25, 55, 0.9), rgba(10, 20, 45, 0.9));
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
        }}
        
        .section-title {{
            font-size: 1.2em;
            color: #00d4ff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(0, 212, 255, 0.2);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .slider-group {{
            margin: 20px 0;
        }}
        
        .slider-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            color: #7a8ca3;
            font-size: 0.9em;
        }}
        
        .slider-value {{
            color: #00d4ff;
            font-weight: 600;
        }}
        
        input[type="range"] {{
            width: 100%;
            height: 6px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 3px;
            outline: none;
            -webkit-appearance: none;
        }}
        
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: linear-gradient(135deg, #00d4ff, #00ffd4);
            cursor: pointer;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.8);
        }}
        
        .btn-group {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 20px;
        }}
        
        .control-btn {{
            padding: 15px 20px;
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 212, 0.1));
            color: #00d4ff;
            font-size: 0.95em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .control-btn:hover {{
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 255, 212, 0.2));
            border-color: #00d4ff;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            transform: translateY(-2px);
        }}
        
        .control-btn.active {{
            background: linear-gradient(135deg, #00d4ff, #00ffd4);
            color: #0a0e27;
            box-shadow: 0 0 25px rgba(0, 212, 255, 0.6);
        }}
        
        /* 数据分析页签 */
        #tab-analytics {{
            padding: 30px;
            overflow-y: auto;
            background: rgba(10, 14, 39, 0.5);
        }}
        
        .chart-container {{
            background: linear-gradient(135deg, rgba(15, 25, 55, 0.9), rgba(10, 20, 45, 0.9));
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, rgba(15, 25, 55, 0.9), rgba(10, 20, 45, 0.9));
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #00d4ff, #00ffd4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            color: #7a8ca3;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* 策略分析页签 */
        #tab-strategy {{
            padding: 30px;
            overflow-y: auto;
            background: rgba(10, 14, 39, 0.5);
        }}
        
        /* 智能助手页签 */
        #tab-assistant {{
            padding: 30px;
            display: flex;
            flex-direction: column;
            background: rgba(10, 14, 39, 0.5);
        }}
        
        .chat-container {{
            flex: 1;
            background: linear-gradient(135deg, rgba(15, 25, 55, 0.9), rgba(10, 20, 45, 0.9));
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            margin-bottom: 20px;
        }}
        
        #chat-messages {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 15px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }}
        
        .chat-message {{
            margin-bottom: 15px;
            padding: 12px 15px;
            border-radius: 8px;
            max-width: 80%;
            line-height: 1.5;
        }}
        
        .chat-message.user {{
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 255, 212, 0.2));
            border: 1px solid rgba(0, 212, 255, 0.3);
            margin-left: auto;
            color: #00d4ff;
        }}
        
        .chat-message.system {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #e8e8e8;
        }}
        
        .chat-input-group {{
            display: flex;
            gap: 10px;
        }}
        
        #chat-input {{
            flex: 1;
            padding: 12px 15px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 8px;
            color: #e8e8e8;
            font-size: 0.95em;
            outline: none;
        }}
        
        #chat-input:focus {{
            border-color: #00d4ff;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
        }}
        
        #send-btn {{
            padding: 12px 25px;
            background: linear-gradient(135deg, #00d4ff, #00ffd4);
            border: none;
            border-radius: 8px;
            color: #0a0e27;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        #send-btn:hover {{
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
            transform: translateY(-2px);
        }}
        
        /* 滚动条样式 */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: rgba(0, 0, 0, 0.2);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: rgba(0, 212, 255, 0.3);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(0, 212, 255, 0.5);
        }}
    </style>
</head>
<body>
    <div id="app-container">
        <!-- 顶部标题栏 -->
        <div id="top-header">
            <div id="logo-section">
                <div id="logo-icon">⚡</div>
                <div id="system-title">微网数字孪生系统</div>
            </div>
            <div id="header-info">
                <div class="info-item">
                    <div class="info-label">系统时间</div>
                    <div class="info-value" id="time-display">--:--:--</div>
                </div>
                <div class="info-item">
                    <div class="info-label">运行状态</div>
                    <div class="info-value" id="system-status">运行中</div>
                </div>
            </div>
        </div>
        
        <!-- 页签导航栏 -->
        <div id="tab-navigation">
            <button class="tab-button active" data-tab="3d">
                <span class="tab-icon">🌐</span>
                <span>3D场景</span>
            </button>
            <button class="tab-button" data-tab="monitor">
                <span class="tab-icon">📊</span>
                <span>实时监控</span>
            </button>
            <button class="tab-button" data-tab="control">
                <span class="tab-icon">🎮</span>
                <span>能量管理</span>
            </button>
            <button class="tab-button" data-tab="analytics">
                <span class="tab-icon">📈</span>
                <span>数据分析</span>
            </button>
            <button class="tab-button" data-tab="strategy">
                <span class="tab-icon">🤖</span>
                <span>策略分析</span>
            </button>
            <button class="tab-button" data-tab="assistant">
                <span class="tab-icon">💬</span>
                <span>智能助手</span>
            </button>
        </div>
        
        <!-- 内容区域 -->
        <div id="content-area">
            <!-- 3D场景页签 -->
            <div id="tab-3d" class="tab-content active">
                <div id="canvas-container"></div>
            </div>
            
            <!-- 实时监控页签 -->
            <div id="tab-monitor" class="tab-content">
                <div class="monitor-grid">
                    <div class="monitor-card">
                        <div class="card-header">
                            <div class="card-title">☀️ 光伏发电系统</div>
                            <div class="card-value" id="monitor-solar-power">-- kW</div>
                        </div>
                        <div class="status-row">
                            <span class="status-label">装机容量</span>
                            <span class="status-value">100 kW</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">利用率</span>
                            <span class="status-value" id="monitor-solar-util">--%</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">环境温度</span>
                            <span class="status-value" id="monitor-temp">--°C</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" id="monitor-solar-bar" style="width: 0%"></div>
                        </div>
                    </div>
                    
                    <div class="monitor-card">
                        <div class="card-header">
                            <div class="card-title">💨 风力发电系统</div>
                            <div class="card-value" id="monitor-wind-power">-- kW</div>
                        </div>
                        <div class="status-row">
                            <span class="status-label">装机容量</span>
                            <span class="status-value">50 kW</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">利用率</span>
                            <span class="status-value" id="monitor-wind-util">--%</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">风速</span>
                            <span class="status-value" id="monitor-wind-speed">-- m/s</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" id="monitor-wind-bar" style="width: 0%"></div>
                        </div>
                    </div>
                    
                    <div class="monitor-card">
                        <div class="card-header">
                            <div class="card-title">🔋 储能系统</div>
                            <div class="card-value" id="monitor-battery-soc">--%</div>
                        </div>
                        <div class="status-row">
                            <span class="status-label">总容量</span>
                            <span class="status-value">200 kWh</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">剩余容量</span>
                            <span class="status-value" id="monitor-battery-remaining">-- kWh</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">充放电功率</span>
                            <span class="status-value" id="monitor-battery-power">-- kW</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">健康度</span>
                            <span class="status-value good" id="monitor-battery-health">--%</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" id="monitor-battery-bar" style="width: 50%"></div>
                        </div>
                    </div>
                    
                    <div class="monitor-card">
                        <div class="card-header">
                            <div class="card-title">📈 负荷系统</div>
                            <div class="card-value" id="monitor-load-power">-- kW</div>
                        </div>
                        <div class="status-row">
                            <span class="status-label">基础负荷</span>
                            <span class="status-value">80 kW</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">峰值负荷</span>
                            <span class="status-value">150 kW</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">负荷率</span>
                            <span class="status-value" id="monitor-load-rate">--%</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" id="monitor-load-bar" style="width: 0%"></div>
                        </div>
                    </div>
                    
                    <div class="monitor-card">
                        <div class="card-header">
                            <div class="card-title">🔌 电网连接</div>
                            <div class="card-value" id="monitor-grid-power">-- kW</div>
                        </div>
                        <div class="status-row">
                            <span class="status-label">连接状态</span>
                            <span class="status-value good" id="monitor-grid-status">已连接</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">当前电价</span>
                            <span class="status-value" id="monitor-price">¥--/kWh</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">电价时段</span>
                            <span class="status-value" id="monitor-price-period">--</span>
                        </div>
                    </div>
                    
                    <div class="monitor-card">
                        <div class="card-header">
                            <div class="card-title">🌿 系统指标</div>
                            <div class="card-value" id="monitor-renewable-ratio">--%</div>
                        </div>
                        <div class="status-row">
                            <span class="status-label">可再生能源比例</span>
                            <span class="status-value good" id="monitor-renewable-value">--%</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">累计成本</span>
                            <span class="status-value" id="monitor-total-cost">¥--</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">系统效率</span>
                            <span class="status-value" id="monitor-efficiency">--%</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 能量管理页签 -->
            <div id="tab-control" class="tab-content">
                <div class="control-section">
                    <div class="section-title">🔋 电池控制</div>
                    <div class="slider-group">
                        <div class="slider-label">
                            <span>充放电控制</span>
                            <span class="slider-value" id="control-battery-value">0%</span>
                        </div>
                        <input type="range" id="control-battery-slider" min="-100" max="100" value="0">
                        <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #7a8ca3; margin-top: 5px;">
                            <span>放电</span>
                            <span>充电</span>
                        </div>
                    </div>
                    <div class="btn-group">
                        <button class="control-btn" id="btn-quick-charge">⚡ 快速充电</button>
                        <button class="control-btn" id="btn-quick-discharge">🔋 立即放电</button>
                    </div>
                </div>
                
                <div class="control-section">
                    <div class="section-title">🏭 备用电源</div>
                    <div class="btn-group">
                        <button class="control-btn" id="btn-diesel-toggle">🏭 柴油机开关</button>
                        <button class="control-btn" id="btn-auto-mode">🤖 自动模式</button>
                    </div>
                </div>
                
                <div class="control-section">
                    <div class="section-title">⚙️ 模拟控制</div>
                    <div class="slider-group">
                        <div class="slider-label">
                            <span>模拟速度</span>
                            <span class="slider-value" id="control-speed-value">1x</span>
                        </div>
                        <input type="range" id="control-speed-slider" min="1" max="10" value="1">
                    </div>
                    <div class="btn-group">
                        <button class="control-btn" id="btn-play">▶️ 开始模拟</button>
                        <button class="control-btn" id="btn-reset">🔄 重置系统</button>
                    </div>
                </div>
            </div>
            
            <!-- 数据分析页签 -->
            <div id="tab-analytics" class="tab-content">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value" id="analytics-total-cost">¥0.00</div>
                        <div class="metric-label">累计成本</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="analytics-total-energy">0 kWh</div>
                        <div class="metric-label">总发电量</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="analytics-co2-saved">0 kg</div>
                        <div class="metric-label">CO2减排</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="analytics-efficiency">0%</div>
                        <div class="metric-label">系统效率</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="section-title">📊 功率趋势图</div>
                    <canvas id="analytics-chart" style="width: 100%; height: 400px;"></canvas>
                </div>
            </div>
            
            <!-- 策略分析页签 -->
            <div id="tab-strategy" class="tab-content">
                <div class="monitor-card">
                    <div class="card-header">
                        <div class="card-title">🤖 RL策略状态</div>
                    </div>
                    <div class="status-row">
                        <span class="status-label">运行模式</span>
                        <span class="status-value" id="strategy-mode">混合模式</span>
                    </div>
                    <div class="status-row">
                        <span class="status-label">RL置信度</span>
                        <span class="status-value" id="strategy-confidence">--%</span>
                    </div>
                    <div class="status-row">
                        <span class="status-label">探索率</span>
                        <span class="status-value" id="strategy-epsilon">--</span>
                    </div>
                    <div class="status-row">
                        <span class="status-label">训练步数</span>
                        <span class="status-value" id="strategy-steps">--</span>
                    </div>
                    <div class="status-row">
                        <span class="status-label">经验池大小</span>
                        <span class="status-value" id="strategy-buffer">--</span>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="section-title">📈 策略对比分析</div>
                    <canvas id="strategy-chart" style="width: 100%; height: 300px;"></canvas>
                </div>
            </div>
            
            <!-- 智能助手页签 -->
            <div id="tab-assistant" class="tab-content">
                <div class="chat-container">
                    <div id="chat-messages">
                        <div class="chat-message system">
                            您好！我是微网数字孪生智能助手。您可以询问系统状态、控制设备或获取分析报告。
                        </div>
                    </div>
                    <div class="chat-input-group">
                        <input type="text" id="chat-input" placeholder="输入您的问题...">
                        <button id="send-btn">发送</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Three.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    
    <script>
        // 页签切换功能
        document.querySelectorAll('.tab-button').forEach(button => {{
            button.addEventListener('click', function() {{
                const tabName = this.getAttribute('data-tab');
                
                // 更新按钮状态
                document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // 更新内容显示
                document.querySelectorAll('.tab-content').forEach(content => {{
                    content.classList.remove('active');
                }});
                document.getElementById(`tab-${{tabName}}`).classList.add('active');
            }});
        }});
        
        // 初始状态数据
        let systemState = {state_json};
        let historyData = {history_json};
        let strategyData = {strategy_json};
        
        // 全局变量
        let scene, camera, renderer, controls;
        let solarPanels = [], windTurbines = [], batterySystem, loadCenter, gridConnection;
        let powerFlowParticles = [];
        let isSimulating = false;
        let simulationSpeed = 1;
        let dieselOn = false;
        let autoMode = true;
        
        // 注意：这里需要从原有的HTML文件中复制完整的Three.js初始化代码
        // 包括 initScene, animate, setupControls, updateDisplay, drawChart 等函数
        // 由于代码太长，建议直接使用原有的JavaScript代码，并添加页签更新逻辑
        
        // 更新所有页签的显示
        function updateAllTabs(state) {{
            if (!state || !state.components) return;
            
            const comp = state.components;
            const weather = state.weather || {{}};
            const price = state.price || {{}};
            const stats = state.statistics || {{}};
            
            // 更新实时监控页签
            const solarPower = comp.solar?.current_power || 0;
            const solarEl = document.getElementById('monitor-solar-power');
            if (solarEl) {{
                solarEl.textContent = solarPower.toFixed(1) + ' kW';
                document.getElementById('monitor-solar-util').textContent = (solarPower / 100 * 100).toFixed(1) + '%';
                document.getElementById('monitor-solar-bar').style.width = (solarPower / 100 * 100) + '%';
            }}
            const tempEl = document.getElementById('monitor-temp');
            if (tempEl) tempEl.textContent = (weather.temperature || 20).toFixed(1) + '°C';
            
            const windPower = comp.wind?.current_power || 0;
            const windEl = document.getElementById('monitor-wind-power');
            if (windEl) {{
                windEl.textContent = windPower.toFixed(1) + ' kW';
                document.getElementById('monitor-wind-util').textContent = (windPower / 50 * 100).toFixed(1) + '%';
                document.getElementById('monitor-wind-bar').style.width = (windPower / 50 * 100) + '%';
                document.getElementById('monitor-wind-speed').textContent = (weather.wind_speed || 8).toFixed(1) + ' m/s';
            }}
            
            const soc = (comp.battery?.soc || 0.5) * 100;
            const batterySocEl = document.getElementById('monitor-battery-soc');
            if (batterySocEl) {{
                batterySocEl.textContent = soc.toFixed(1) + '%';
                document.getElementById('monitor-battery-remaining').textContent = ((comp.battery?.soc || 0.5) * 200).toFixed(1) + ' kWh';
                document.getElementById('monitor-battery-bar').style.width = soc + '%';
                document.getElementById('monitor-battery-health').textContent = ((comp.battery?.health || 1) * 100).toFixed(0) + '%';
            }}
            
            const loadPower = comp.load?.current || 0;
            const loadEl = document.getElementById('monitor-load-power');
            if (loadEl) {{
                loadEl.textContent = loadPower.toFixed(1) + ' kW';
                document.getElementById('monitor-load-rate').textContent = (loadPower / 150 * 100).toFixed(1) + '%';
                document.getElementById('monitor-load-bar').style.width = (loadPower / 150 * 100) + '%';
            }}
            
            const priceEl = document.getElementById('monitor-price');
            if (priceEl) {{
                priceEl.textContent = '¥' + (price.buy_price || 0.8).toFixed(2) + '/kWh';
                document.getElementById('monitor-price-period').textContent = price.period || '平段';
            }}
            
            const renewableRatio = (stats.renewable_ratio || 0) * 100;
            const renewableEl = document.getElementById('monitor-renewable-ratio');
            if (renewableEl) {{
                renewableEl.textContent = renewableRatio.toFixed(1) + '%';
                document.getElementById('monitor-renewable-value').textContent = renewableRatio.toFixed(1) + '%';
                document.getElementById('monitor-total-cost').textContent = '¥' + (stats.total_cost || 0).toFixed(2);
                document.getElementById('monitor-efficiency').textContent = renewableRatio.toFixed(0) + '%';
            }}
            
            // 更新数据分析页签
            const analyticsCostEl = document.getElementById('analytics-total-cost');
            if (analyticsCostEl) {{
                analyticsCostEl.textContent = '¥' + (stats.total_cost || 0).toFixed(2);
                document.getElementById('analytics-total-energy').textContent = (stats.total_renewable_energy || 0).toFixed(1) + ' kWh';
                document.getElementById('analytics-co2-saved').textContent = ((stats.total_renewable_energy || 0) * 0.5).toFixed(1) + ' kg';
                document.getElementById('analytics-efficiency').textContent = renewableRatio.toFixed(0) + '%';
            }}
            
            // 更新策略分析页签
            if (strategyData) {{
                const strategyModeEl = document.getElementById('strategy-mode');
                if (strategyModeEl) {{
                    strategyModeEl.textContent = strategyData.mode || '混合模式';
                    document.getElementById('strategy-confidence').textContent = ((strategyData.rl_confidence || 0.5) * 100).toFixed(1) + '%';
                    document.getElementById('strategy-epsilon').textContent = (strategyData.epsilon || 0.3).toFixed(3);
                    document.getElementById('strategy-steps').textContent = (strategyData.training_steps || 0).toLocaleString();
                    document.getElementById('strategy-buffer').textContent = (strategyData.buffer_size || 0).toLocaleString();
                }}
            }}
            
            // 更新时间显示
            if (state.timestamp) {{
                const date = new Date(state.timestamp);
                const timeEl = document.getElementById('time-display');
                if (timeEl) timeEl.textContent = date.toLocaleString('zh-CN');
            }}
        }}
        
        // 初始化Three.js场景
        function initScene() {{
            const container = document.getElementById('canvas-container');
            if (!container) return;
            
            // 场景
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a1628);
            scene.fog = new THREE.Fog(0x0a1628, 100, 500);
            
            // 相机
            camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(80, 60, 80);
            
            // 渲染器
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
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
            const ambientLight = new THREE.AmbientLight(0x404060, 0.5);
            scene.add(ambientLight);
            
            const sunLight = new THREE.DirectionalLight(0xffffff, 1);
            sunLight.position.set(50, 100, 50);
            sunLight.castShadow = true;
            sunLight.shadow.mapSize.width = 2048;
            sunLight.shadow.mapSize.height = 2048;
            scene.add(sunLight);
            
            const fillLight = new THREE.DirectionalLight(0x4080ff, 0.3);
            fillLight.position.set(-50, 50, -50);
            scene.add(fillLight);
            
            const pointLight1 = new THREE.PointLight(0x00d4ff, 0.5, 100);
            pointLight1.position.set(0, 30, 0);
            scene.add(pointLight1);
        }}
        
        function createEnvironment() {{
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
            
            const gridHelper = new THREE.GridHelper(300, 30, 0x1e3a5f, 0x1e3a5f);
            gridHelper.position.y = 0.01;
            scene.add(gridHelper);
        }}
        
        function createMicrogridComponents() {{
            createSolarPanels();
            createWindTurbines();
            createBatterySystem();
            createLoadCenter();
            createGridConnection();
            createControlCenter();
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
                    panelGroup.add(panel);
                    solarPanels.push(panel);
                }}
            }}
            scene.add(panelGroup);
        }}
        
        function createWindTurbines() {{
            for (let i = 0; i < 2; i++) {{
                const turbineGroup = new THREE.Group();
                const towerGeometry = new THREE.CylinderGeometry(1, 2, 30, 8);
                const tower = new THREE.Mesh(towerGeometry, new THREE.MeshStandardMaterial({{ color: 0xeeeeee }}));
                tower.position.y = 15;
                turbineGroup.add(tower);
                
                const bladesGroup = new THREE.Group();
                for (let b = 0; b < 3; b++) {{
                    const blade = new THREE.Mesh(
                        new THREE.BoxGeometry(0.5, 12, 1),
                        new THREE.MeshStandardMaterial({{ color: 0xffffff }})
                    );
                    blade.position.y = 6;
                    blade.rotation.z = (b * Math.PI * 2) / 3;
                    bladesGroup.add(blade);
                }}
                bladesGroup.position.set(3, 31, 0);
                turbineGroup.add(bladesGroup);
                turbineGroup.bladesGroup = bladesGroup;
                turbineGroup.position.set(40 + i * 25, 0, -30);
                scene.add(turbineGroup);
                windTurbines.push(turbineGroup);
            }}
        }}
        
        function createBatterySystem() {{
            batterySystem = new THREE.Group();
            for (let i = 0; i < 3; i++) {{
                const cabinet = new THREE.Mesh(
                    new THREE.BoxGeometry(6, 10, 4),
                    new THREE.MeshStandardMaterial({{ color: 0x27ae60 }})
                );
                cabinet.position.set(-5 + i * 8, 5, 35);
                batterySystem.add(cabinet);
            }}
            scene.add(batterySystem);
        }}
        
        function createLoadCenter() {{
            loadCenter = new THREE.Group();
            const building = new THREE.Mesh(
                new THREE.BoxGeometry(20, 15, 15),
                new THREE.MeshStandardMaterial({{ color: 0x34495e }})
            );
            building.position.y = 7.5;
            loadCenter.add(building);
            loadCenter.position.set(0, 0, 0);
            scene.add(loadCenter);
        }}
        
        function createGridConnection() {{
            gridConnection = new THREE.Group();
            const station = new THREE.Mesh(
                new THREE.BoxGeometry(8, 12, 8),
                new THREE.MeshStandardMaterial({{ color: 0x8e44ad }})
            );
            station.position.y = 6;
            gridConnection.add(station);
            gridConnection.position.set(60, 0, 30);
            scene.add(gridConnection);
        }}
        
        function createControlCenter() {{
            const controlGroup = new THREE.Group();
            const room = new THREE.Mesh(
                new THREE.BoxGeometry(10, 8, 10),
                new THREE.MeshStandardMaterial({{ color: 0x2980b9 }})
            );
            room.position.y = 4;
            controlGroup.add(room);
            controlGroup.position.set(-50, 0, 30);
            scene.add(controlGroup);
        }}
        
        function createConnectionLines() {{
            const lineMaterial = new THREE.LineBasicMaterial({{
                color: 0x00d4ff,
                transparent: true,
                opacity: 0.5
            }});
            const connections = [
                [[-25, 2, -22], [0, 2, 0]],
                [[52, 2, -30], [0, 2, 0]],
                [[3, 2, 35], [0, 2, 0]],
                [[0, 2, 0], [60, 2, 30]]
            ];
            connections.forEach(conn => {{
                const geometry = new THREE.BufferGeometry().setFromPoints([
                    new THREE.Vector3(...conn[0]),
                    new THREE.Vector3(...conn[1])
                ]);
                scene.add(new THREE.Line(geometry, lineMaterial));
            }});
        }}
        
        function createPowerFlowSystem() {{
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
            const particles = new THREE.Points(
                geometry,
                new THREE.PointsMaterial({{ size: 0.5, vertexColors: true, transparent: true, opacity: 0.8 }})
            );
            scene.add(particles);
            powerFlowParticles.push({{ points: particles, positions: positions }});
        }}
        
        function onWindowResize() {{
            const container = document.getElementById('canvas-container');
            if (!container || !camera || !renderer) return;
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            if (controls) controls.update();
            
            windTurbines.forEach(turbine => {{
                if (turbine.bladesGroup) {{
                    turbine.bladesGroup.rotation.x += 0.02 * simulationSpeed;
                }}
            }});
            
            powerFlowParticles.forEach(system => {{
                const positions = system.points.geometry.attributes.position.array;
                for (let i = 0; i < positions.length / 3; i++) {{
                    positions[i * 3 + 1] += 0.05;
                    if (positions[i * 3 + 1] > 5) positions[i * 3 + 1] = 1;
                }}
                system.points.geometry.attributes.position.needsUpdate = true;
            }});
            
            if (renderer && scene && camera) renderer.render(scene, camera);
        }}
        
        function drawAnalyticsChart(history) {{
            const canvas = document.getElementById('analytics-chart');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const container = canvas.parentElement;
            canvas.width = container.clientWidth - 50;
            canvas.height = 400;
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = 'rgba(0, 212, 255, 0.3)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(50, 20);
            ctx.lineTo(50, canvas.height - 30);
            ctx.lineTo(canvas.width - 20, canvas.height - 30);
            ctx.stroke();
            
            if (!history || !history.solar_power || history.solar_power.length === 0) {{
                ctx.fillStyle = '#7a8ca3';
                ctx.font = '16px Arial';
                ctx.fillText('暂无数据', canvas.width / 2 - 40, canvas.height / 2);
                return;
            }}
            
            const dataLength = Math.min(60, history.solar_power.length);
            const startIdx = Math.max(0, history.solar_power.length - dataLength);
            const chartWidth = canvas.width - 80;
            const chartHeight = canvas.height - 60;
            
            const series = [
                {{ data: history.solar_power, color: '#f1c40f', name: '光伏' }},
                {{ data: history.wind_power, color: '#3498db', name: '风电' }},
                {{ data: history.load_power, color: '#e74c3c', name: '负荷' }}
            ];
            
            let maxVal = 0;
            series.forEach(s => {{
                if (s.data) {{
                    const sliced = s.data.slice(startIdx);
                    maxVal = Math.max(maxVal, ...sliced);
                }}
            }});
            maxVal = Math.max(maxVal, 100) * 1.1;
            
            series.forEach(s => {{
                if (!s.data || s.data.length === 0) return;
                ctx.strokeStyle = s.color;
                ctx.lineWidth = 2;
                ctx.beginPath();
                const sliced = s.data.slice(startIdx);
                sliced.forEach((val, i) => {{
                    const x = 50 + (i / (dataLength - 1)) * chartWidth;
                    const y = (canvas.height - 30) - (val / maxVal) * chartHeight;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }});
                ctx.stroke();
            }});
        }}
        
        function startSimulation() {{
            if (!isSimulating) return;
            
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
                              hour >= 23 || hour < 7 ? 0.4 : 0.8,
                    period: hour >= 9 && hour < 12 || hour >= 17 && hour < 21 ? '高峰' : 
                           hour >= 23 || hour < 7 ? '低谷' : '平段'
                }},
                statistics: {{
                    total_cost: (Math.random() * 100 + 50),
                    total_renewable_energy: (Math.random() * 500 + 200),
                    renewable_ratio: 0.5 + Math.random() * 0.4
                }}
            }};
            
            updateAllTabs(mockState);
            
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
            
            drawAnalyticsChart(window.simHistory);
            
            setTimeout(() => startSimulation(), 1000 / simulationSpeed);
        }}
        
        function handleChat(message) {{
            const chatMessages = document.getElementById('chat-messages');
            if (!chatMessages) return;
            
            const userMsg = document.createElement('div');
            userMsg.className = 'chat-message user';
            userMsg.textContent = message;
            chatMessages.appendChild(userMsg);
            
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
        
        function setupTabbedControls() {{
            const batterySlider = document.getElementById('control-battery-slider');
            if (batterySlider) {{
                batterySlider.addEventListener('input', function() {{
                    document.getElementById('control-battery-value').textContent = this.value + '%';
                }});
            }}
            
            const speedSlider = document.getElementById('control-speed-slider');
            if (speedSlider) {{
                speedSlider.addEventListener('input', function() {{
                    simulationSpeed = parseInt(this.value);
                    document.getElementById('control-speed-value').textContent = simulationSpeed + 'x';
                }});
            }}
            
            const btnPlay = document.getElementById('btn-play');
            if (btnPlay) {{
                btnPlay.addEventListener('click', function() {{
                    isSimulating = !isSimulating;
                    this.textContent = isSimulating ? '⏸️ 暂停模拟' : '▶️ 开始模拟';
                    if (isSimulating) startSimulation();
                }});
            }}
            
            const btnReset = document.getElementById('btn-reset');
            if (btnReset) {{
                btnReset.addEventListener('click', function() {{
                    isSimulating = false;
                    if (btnPlay) btnPlay.textContent = '▶️ 开始模拟';
                }});
            }}
            
            const btnQuickCharge = document.getElementById('btn-quick-charge');
            if (btnQuickCharge) {{
                btnQuickCharge.addEventListener('click', function() {{
                    if (batterySlider) batterySlider.value = 100;
                    document.getElementById('control-battery-value').textContent = '100%';
                }});
            }}
            
            const btnQuickDischarge = document.getElementById('btn-quick-discharge');
            if (btnQuickDischarge) {{
                btnQuickDischarge.addEventListener('click', function() {{
                    if (batterySlider) batterySlider.value = -100;
                    document.getElementById('control-battery-value').textContent = '-100%';
                }});
            }}
            
            const sendBtn = document.getElementById('send-btn');
            if (sendBtn) {{
                sendBtn.addEventListener('click', function() {{
                    const input = document.getElementById('chat-input');
                    if (input && input.value.trim()) {{
                        handleChat(input.value.trim());
                        input.value = '';
                    }}
                }});
            }}
            
            const chatInput = document.getElementById('chat-input');
            if (chatInput) {{
                chatInput.addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter' && this.value.trim()) {{
                        handleChat(this.value.trim());
                        this.value = '';
                    }}
                }});
            }}
        }}
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {{
            initScene();
            animate();
            setupTabbedControls();
            
            if (systemState && Object.keys(systemState).length > 0) {{
                updateAllTabs(systemState);
            }}
            
            if (historyData && Object.keys(historyData).length > 0) {{
                drawAnalyticsChart(historyData);
            }}
            
            setTimeout(() => {{
                const btnPlay = document.getElementById('btn-play');
                if (btnPlay) btnPlay.click();
            }}, 1000);
        }});
    </script>
</body>
</html>'''
    
    return html

