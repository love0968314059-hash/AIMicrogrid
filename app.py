import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
from microgrid_system import train_agent, MicrogridEnv, NLPInterface, DataGenerator
import numpy as np

# Set page to wide mode
st.set_page_config(layout="wide", page_title="Microgrid Digital Twin")

st.title("⚡ Microgrid Digital Twin & Adaptive EMS")
st.markdown("""
This system demonstrates an **Adaptive Energy Management System (EMS)** using Reinforcement Learning (PPO).
It simulates a microgrid with Solar, Wind, Battery, and Load, handling prediction errors in real-time.
""")

# Sidebar for Controls
st.sidebar.header("⚙️ Simulation Controls")
train_btn = st.sidebar.button("Train New Agent")
run_btn = st.sidebar.button("Run Simulation")
noise_level = st.sidebar.slider("Prediction Error (Noise Level)", 0.0, 0.5, 0.1)

# Global State
if 'model' not in st.session_state:
    st.session_state.model = None

if train_btn:
    with st.spinner("Training RL Agent..."):
        st.session_state.model = train_agent()
    st.success("Training Complete!")

# Main Dashboard Interface
col1, col2 = st.columns([2, 1])

if run_btn and st.session_state.model:
    # Run Simulation live
    env = MicrogridEnv()
    # Override noise level in generator for this run
    env.generator = DataGenerator() # Reset
    # Monkey patch the get_data to use slider noise (simplified for demo)
    original_get_data = env.generator.get_data
    def get_data_with_noise(step, noise=noise_level):
        return original_get_data(step, noise_level=noise)
    env.generator.get_data = get_data_with_noise
    
    obs, _ = env.reset()
    nlp = NLPInterface(env)
    
    # Placeholders for live updates
    with col1:
        st.subheader("Interactive 3D Grid View")
        map_placeholder = st.empty()
        
    with col2:
        st.subheader("System Parameters")
        metrics_placeholder = st.empty()
        st.subheader("💬 AI Command Center")
        chat_placeholder = st.empty()
        user_input = st.text_input("Ask the system:", key="chat_input")

    history = {"soc": [], "load": [], "price": [], "gen": []}
    
    # Progress Bar
    progress_bar = st.progress(0)
    
    steps = 48 # 48 hours
    for i in range(steps):
        # RL Step
        action, _ = st.session_state.model.predict(obs)
        obs, reward, done, truncated, info = env.step(action)
        
        # Update Data
        status = env.get_system_status()
        history['soc'].append(env.soc)
        history['load'].append(env.actual['load'])
        history['price'].append(env.actual['price'])
        history['gen'].append(env.actual['solar'] + env.actual['wind'])
        
        # 1. Update Metrics
        with metrics_placeholder.container():
            c1, c2 = st.columns(2)
            c1.metric("Battery SoC", status['Battery SOC'].split(' ')[0] + " kWh")
            c2.metric("Net Revenue", f"${-sum(env.history['cost']):.2f}")
            c3, c4 = st.columns(2)
            c3.metric("Current Price", status['Current Price'])
            c4.metric("Renewable Gen", status['Renewable Gen'])

        # 2. Update 3D Visuals
        # Create a dynamic 3D plot
        fig = go.Figure()
        
        # Assets Coordinates
        assets = {
            "Solar": (2, 2, 0, 'yellow', env.actual['solar']),
            "Wind": (-2, 2, 0, 'cyan', env.actual['wind']),
            "Load": (0, 0, 0, 'blue', env.actual['load']),
            "Battery": (0, -2, 0, 'green', env.soc),
            "Grid": (0, 3, 2, 'red', env.history['grid_power'][-1])
        }
        
        # Ground
        fig.add_trace(go.Mesh3d(x=[-5, 5, 5, -5], y=[-5, -5, 5, 5], z=[-0.1, -0.1, -0.1, -0.1], 
                            color='lightgrey', opacity=0.5, name='Ground'))
        
        for name, (x, y, z, color, val) in assets.items():
            # Scale size by value
            size = 20 + (val / 10) if name != "Price" else 20
            fig.add_trace(go.Scatter3d(
                x=[x], y=[y], z=[1],
                mode='markers+text',
                marker=dict(size=size, color=color),
                text=[f"{name}<br>{val:.1f}"],
                textposition="top center",
                name=name
            ))
            # Pole
            fig.add_trace(go.Scatter3d(
                x=[x, x], y=[y, y], z=[0, 1],
                mode='lines', line=dict(color='black', width=5), showlegend=False
            ))
            # Connection to center
            fig.add_trace(go.Scatter3d(
                x=[x, 0], y=[y, 0], z=[1, 1],
                mode='lines', line=dict(color=color, width=2), showlegend=False
            ))

        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[-5, 5], visible=False),
                yaxis=dict(range=[-5, 5], visible=False),
                zaxis=dict(range=[0, 4], visible=False),
                aspectmode='cube'
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            height=400
        )
        map_placeholder.plotly_chart(fig, use_container_width=True)
        
        # 3. Update Chat
        if user_input:
            response = nlp.process_query(user_input)
            chat_placeholder.info(f"User: {user_input}\n\nSystem: {response}")
        
        progress_bar.progress((i + 1) / steps)
        time.sleep(0.1) # Simulate real-time speed

    # Final Charts
    st.subheader("📊 Performance Analysis")
    df_res = pd.DataFrame(history)
    st.line_chart(df_res)

elif not st.session_state.model:
    st.info("👈 Please click 'Train New Agent' to start.")
