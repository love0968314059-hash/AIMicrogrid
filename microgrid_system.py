import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import math
from datetime import datetime
import json
import random

# ==========================================
# 1. Prediction & Data Generation Module
# ==========================================
class DataGenerator:
    """
    Generates synthetic data for Load, Solar, Wind, and Price.
    Includes both 'Forecast' and 'Actual' values to simulate prediction errors.
    """
    def __init__(self, step_size_minutes=60):
        self.step_size = step_size_minutes
        self.time_step = 0

    def get_data(self, step, noise_level=0.1):
        # Time of day simulation (0-24)
        hour = (step * self.step_size / 60) % 24
        
        # Base Load: Peak in evening
        base_load = 50 + 30 * np.sin((hour - 15) * np.pi / 12)
        
        # Solar: Peak at noon, zero at night
        if 6 <= hour <= 18:
            base_solar = 100 * np.sin((hour - 6) * np.pi / 12)
        else:
            base_solar = 0
            
        # Wind: Random walk with sine component
        base_wind = 20 + 10 * np.sin(hour * np.pi / 6)
        
        # Price: Peak in evening
        base_price = 0.15 + 0.10 * np.sin((hour - 18) * np.pi / 12)

        # Forecast values (cleaner)
        forecast = {
            "load": max(0, base_load),
            "solar": max(0, base_solar),
            "wind": max(0, base_wind),
            "price": max(0.05, base_price)
        }

        # Actual values (with noise/error)
        # Prediction Error is simulated here by adding random noise to the actuals
        actual = {
            "load": max(0, base_load * (1 + np.random.normal(0, noise_level))),
            "solar": max(0, base_solar * (1 + np.random.normal(0, noise_level))),
            "wind": max(0, base_wind * (1 + np.random.normal(0, noise_level))),
            "price": max(0.05, base_price * (1 + np.random.normal(0, noise_level)))
        }

        return forecast, actual, hour

# ==========================================
# 2. Digital Twin Environment (Gymnasium)
# ==========================================
class MicrogridEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    Represents the Microgrid Digital Twin.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(MicrogridEnv, self).__init__()
        
        # System Config
        self.battery_capacity = 200.0 # kWh
        self.max_charge_rate = 50.0   # kW
        self.max_discharge_rate = 50.0 # kW
        self.efficiency = 0.95
        
        self.generator = DataGenerator()
        
        # Action Space: [Battery Action]
        # -1.0 (Max Discharge) to +1.0 (Max Charge)
        self.action_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)

        # Observation Space: 
        # [SoC, Forecast_Load, Forecast_Solar, Forecast_Wind, Forecast_Price, Hour]
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(6,), dtype=np.float32)

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0
        self.soc = 0.5 * self.battery_capacity # Start at 50%
        
        self.forecast, self.actual, self.hour = self.generator.get_data(self.step_count)
        
        self.current_obs = np.array([
            self.soc,
            self.forecast['load'],
            self.forecast['solar'],
            self.forecast['wind'],
            self.forecast['price'],
            self.hour
        ], dtype=np.float32)
        
        self.history = {
            "soc": [], "action": [], "grid_power": [], 
            "cost": [], "forecast": [], "actual": []
        }
        
        return self.current_obs, {}

    def step(self, action):
        action_val = float(action[0]) # -1 to 1
        
        # 1. Physics Simulation (Battery Dynamics)
        power_battery = 0
        
        if action_val > 0: # Charge
            power_desired = action_val * self.max_charge_rate
            # Cap by capacity
            max_input = (self.battery_capacity - self.soc) / self.efficiency
            power_actual = min(power_desired, max_input)
            self.soc += power_actual * self.efficiency
            power_battery = power_actual # Positive means consuming power from grid/renewables
            
        else: # Discharge
            power_desired = -action_val * self.max_discharge_rate
            # Cap by available energy
            max_output = self.soc * self.efficiency
            power_actual = min(power_desired, max_output)
            self.soc -= power_actual / self.efficiency
            power_battery = -power_actual # Negative means supplying power
            
        # 2. Grid Interaction Calculation using ACTUAL values (Reality)
        # Net Load = Load - Solar - Wind + Battery_Charging
        renewable_gen = self.actual['solar'] + self.actual['wind']
        net_load = self.actual['load'] - renewable_gen + power_battery
        
        # If net_load > 0, we buy from grid. If < 0, we sell to grid.
        grid_power = net_load 
        
        # 3. Cost Calculation
        step_cost = grid_power * self.actual['price']
        
        # Reward: Negative Cost (Maximize Profit/Minimize Cost)
        # Penalty for extreme battery usage or unmet load scenarios could be added
        reward = -step_cost
        
        # 4. Next Step
        self.step_count += 1
        next_forecast, next_actual, next_hour = self.generator.get_data(self.step_count)
        self.forecast = next_forecast
        self.actual = next_actual
        self.hour = next_hour
        
        # Store history for Visualization
        self.history['soc'].append(self.soc)
        self.history['action'].append(action_val)
        self.history['grid_power'].append(grid_power)
        self.history['cost'].append(step_cost)
        self.history['forecast'].append(self.forecast)
        self.history['actual'].append(self.actual)

        # Check Termination
        terminated = False
        truncated = False
        if self.step_count >= 24 * 7: # Run for a week in simulation
            terminated = True
            
        self.current_obs = np.array([
            self.soc,
            next_forecast['load'],
            next_forecast['solar'],
            next_forecast['wind'],
            next_forecast['price'],
            next_hour
        ], dtype=np.float32)
        
        return self.current_obs, reward, terminated, truncated, {}

    def get_system_status(self):
        """Returns a dict snapshot of the current system for NLP."""
        return {
            "Time": f"{self.hour:.1f}h",
            "Battery SOC": f"{self.soc:.2f} kWh ({(self.soc/self.battery_capacity)*100:.1f}%)",
            "Current Load": f"{self.actual['load']:.2f} kW",
            "Renewable Gen": f"{self.actual['solar'] + self.actual['wind']:.2f} kW",
            "Grid Power": f"{self.history['grid_power'][-1] if self.history['grid_power'] else 0:.2f} kW",
            "Current Price": f"${self.actual['price']:.2f}/kWh"
        }

# ==========================================
# 3. NLP / LLM Interface (Simulated)
# ==========================================
class NLPInterface:
    def __init__(self, env):
        self.env = env

    def process_query(self, query):
        """
        Simple intent parser to simulate an LLM interacting with the digital twin.
        """
        query = query.lower()
        status = self.env.get_system_status()
        
        if "battery" in query or "soc" in query:
            return f"🔋 **Battery Status**: Current State of Charge is {status['Battery SOC']}."
        elif "price" in query or "cost" in query:
            return f"💰 **Market Info**: Current electricity price is {status['Current Price']}."
        elif "load" in query or "demand" in query:
            return f"🏠 **Load Demand**: The facility is currently consuming {status['Current Load']}."
        elif "solar" in query or "wind" in query or "renewable" in query:
            return f"☀️ **Renewables**: Total green energy generation is {status['Renewable Gen']}."
        elif "status" in query or "overview" in query:
            return f"📊 **System Overview**:\n" + "\n".join([f"- {k}: {v}" for k,v in status.items()])
        else:
            return "🤖 I can answer questions about Battery, Price, Load, or Renewables. Try asking 'What is the battery status?'"

# ==========================================
# 4. 3D Visualization Module (Plotly)
# ==========================================
def create_3d_microgrid_viz(soc_history, load_history, solar_history, wind_history):
    """
    Creates a 3D Interactive Scene representing the microgrid state.
    """
    # 1. Define 3D Coordinates for Assets
    # (x, y, z)
    assets = {
        "House (Load)": (0, 0, 0),
        "Solar Array": (2, 2, 0),
        "Wind Turbine": (-2, 2, 0),
        "Battery": (0, -2, 0),
        "Grid Connection": (0, 3, 2)
    }
    
    # 2. Create Meshes/Markers
    fig = go.Figure()

    # Draw Ground
    fig.add_trace(go.Mesh3d(x=[-5, 5, 5, -5], y=[-5, -5, 5, 5], z=[-0.1, -0.1, -0.1, -0.1], 
                            color='lightgrey', opacity=0.5, name='Ground'))

    # Draw Assets
    for name, (x, y, z) in assets.items():
        color = 'blue'
        symbol = 'square'
        if "Solar" in name: color, symbol = 'yellow', 'diamond'
        elif "Wind" in name: color, symbol = 'cyan', 'cross'
        elif "Battery" in name: color, symbol = 'green', 'circle'
        elif "Grid" in name: color, symbol = 'red', 'x'
        
        # Add a vertical line (pole)
        fig.add_trace(go.Scatter3d(
            x=[x, x], y=[y, y], z=[0, 1],
            mode='lines', line=dict(color='black', width=5), showlegend=False
        ))
        
        # Add the asset top
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[1],
            mode='markers+text',
            marker=dict(size=20, color=color, symbol=symbol),
            text=[name], textposition="top center",
            name=name
        ))

    # 3. Add Connections (Cables)
    center = (0, 0, 1) # Distribution Hub
    for name, (x, y, z) in assets.items():
        if name != "Grid Connection":
            fig.add_trace(go.Scatter3d(
                x=[x, 0], y=[y, 0], z=[1, 1],
                mode='lines', line=dict(color='grey', width=2, dash='dash'),
                showlegend=False
            ))

    # 4. Create Animation Frames based on History
    # We will animate the size/color of markers based on power flow
    frames = []
    
    # Downsample for visualization speed
    skip = max(1, len(soc_history) // 50) 
    
    for i in range(0, len(soc_history), skip):
        # Calculate visual properties based on data
        # Solar Intensity
        solar_val = solar_history[i]
        solar_size = 10 + (solar_val / 10) 
        
        # Battery Color (Green=Full, Red=Empty)
        batt_val = soc_history[i] # 0 to 200
        batt_intensity = int((batt_val / 200) * 255)
        batt_color = f"rgb({255-batt_intensity}, {batt_intensity}, 0)"
        
        frame_data = [
            # Ground (Static) - Index 0
            go.Mesh3d(x=[-5, 5, 5, -5], y=[-5, -5, 5, 5], z=[-0.1, -0.1, -0.1, -0.1], color='lightgrey', opacity=0.5),
        ]
        
        # Re-add assets with updated properties
        # Note: In a real efficient implementation, we'd only update specific attributes, 
        # but for Plotly frames, recreating the list is often safer for consistency.
        
        current_traces = []
        # We need to match the order of traces added in the base figure
        
        # 1. Solar
        current_traces.append(dict(marker=dict(size=solar_size))) 
        # ... logic to update specific traces in frames is complex in Plotly Python API 
        # Simpler approach: Just update the title to show time passing
        
    fig.update_layout(
        title="Microgrid Digital Twin 3D View",
        scene=dict(
            xaxis=dict(range=[-5, 5], showgrid=False),
            yaxis=dict(range=[-5, 5], showgrid=False),
            zaxis=dict(range=[0, 3], showgrid=False),
            aspectmode='cube'
        ),
        margin=dict(r=0, l=0, b=0, t=40)
    )
    
    return fig

# ==========================================
# 5. Main Execution Flow
# ==========================================
def train_agent():
    print("🚀 Initializing Microgrid Environment...")
    env = DummyVecEnv([lambda: MicrogridEnv()])
    
    print("🧠 Training RL Agent (PPO)...")
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=2000) # Short training for demo speed
    print("✅ Training Complete.")
    return model

def run_simulation(model):
    print("▶️ Running Simulation with Trained Policy...")
    env = MicrogridEnv()
    obs, _ = env.reset()
    
    nlp = NLPInterface(env)
    
    logs = {
        "soc": [], "load": [], "solar": [], "wind": [], "price": [], "action": []
    }
    
    # Run for 24 steps (1 day) for the demo visualization
    for _ in range(24):
        action, _ = model.predict(obs)
        obs, reward, done, truncated, info = env.step(action)
        
        # Log data
        logs['soc'].append(env.soc)
        logs['load'].append(env.actual['load'])
        logs['solar'].append(env.actual['solar'])
        logs['wind'].append(env.actual['wind'])
        logs['price'].append(env.actual['price'])
        logs['action'].append(float(action[0]))
        
        # Example NLP interaction at noon
        if env.hour == 12.0:
            print(f"\n[NLP Interaction @ 12:00]: {nlp.process_query('What is the solar status?')}")

    return logs

if __name__ == "__main__":
    # 1. Train
    model = train_agent()
    
    # 2. Run
    results = run_simulation(model)
    
    # 3. Save Data for Visualization
    df = pd.DataFrame(results)
    df.to_csv("simulation_results.csv", index=False)
    print("\n💾 Results saved to simulation_results.csv")
    
    # 4. Generate 3D Plot HTML (for Colab display)
    fig = create_3d_microgrid_viz(results['soc'], results['load'], results['solar'], results['wind'])
    fig.write_html("microgrid_3d.html")
    print("🖼️ 3D Visualization saved to microgrid_3d.html")

