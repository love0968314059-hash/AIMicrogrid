"""
Reinforcement Learning based Energy Management System
Uses DQN to learn optimal energy management strategies
"""
import numpy as np
import gym
from gym import spaces
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random


class MicrogridEnv(gym.Env):
    """Microgrid environment for RL training"""
    
    def __init__(self, config=None, predictor=None):
        if config is None:
            from config import SYSTEM_CONFIG
            config = SYSTEM_CONFIG
        
        self.config = config
        self.predictor = predictor
        
        # State space: [battery_soc, pv_power, wind_power, load, price, hour]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0]),
            high=np.array([1, config['pv_capacity'], config['wind_capacity'], 
                          200, 0.3, 23]),
            dtype=np.float32
        )
        
        # Action space: battery power (discharge positive, charge negative)
        self.action_space = spaces.Box(
            low=-config['battery_max_power'],
            high=config['battery_max_power'],
            dtype=np.float32
        )
        
        self.reset()
    
    def reset(self):
        """Reset environment"""
        self.battery_soc = self.config['initial_battery_soc']
        self.hour = 0
        self.total_cost = 0.0
        self.total_reward = 0.0
        self.history = []
        
        if self.predictor:
            pred = self.predictor.predict(self.hour)
            self.state = np.array([
                self.battery_soc,
                pred['pv_power'],
                pred['wind_power'],
                pred['load'],
                pred['price'],
                self.hour / 24.0
            ], dtype=np.float32)
        else:
            self.state = np.array([self.battery_soc, 0, 0, 50, 0.12, 0], dtype=np.float32)
        
        return self.state
    
    def step(self, action):
        """Execute one time step"""
        # Clip action to valid range
        battery_power = np.clip(
            action[0] if isinstance(action, (list, np.ndarray)) else action,
            -self.config['battery_max_power'],
            self.config['battery_max_power']
        )
        
        # Get predictions
        if self.predictor:
            pred = self.predictor.predict(self.hour)
            pv_power = pred['pv_power']
            wind_power = pred['wind_power']
            load = pred['load']
            price = pred['price']
        else:
            pv_power = 40
            wind_power = 30
            load = 50
            price = 0.12
        
        # Calculate net power
        renewable_power = pv_power + wind_power
        net_load = load - renewable_power
        
        # Battery operation
        if battery_power > 0:  # Discharge
            actual_discharge = min(
                battery_power,
                self.battery_soc * self.config['battery_capacity'] / self.config['time_step'],
                self.config['battery_max_power']
            )
            energy_discharged = actual_discharge * self.config['time_step']
            self.battery_soc -= energy_discharged / self.config['battery_capacity']
        else:  # Charge
            actual_charge = max(
                battery_power,
                -(1 - self.battery_soc) * self.config['battery_capacity'] / self.config['time_step'],
                -self.config['battery_max_power']
            )
            energy_charged = -actual_charge * self.config['time_step'] * self.config['battery_efficiency']
            self.battery_soc += energy_charged / self.config['battery_capacity']
        
        self.battery_soc = np.clip(self.battery_soc, 0, 1)
        
        # Grid power
        grid_power = net_load - battery_power
        grid_power = np.clip(grid_power, self.config['grid_min_power'], self.config['grid_max_power'])
        
        # Calculate cost
        if grid_power > 0:  # Import from grid
            cost = grid_power * price * self.config['time_step']
        else:  # Export to grid
            cost = grid_power * price * 0.7 * self.config['time_step']  # Lower export price
        
        self.total_cost += cost
        
        # Reward: negative cost + battery health bonus
        reward = -cost / 10.0  # Scale reward
        if 0.2 < self.battery_soc < 0.9:
            reward += 0.1  # Battery health bonus
        
        # Penalty for extreme SOC
        if self.battery_soc < 0.1 or self.battery_soc > 0.95:
            reward -= 0.5
        
        self.total_reward += reward
        
        # Update state
        self.hour = (self.hour + 1) % 24
        
        if self.predictor:
            next_pred = self.predictor.predict(self.hour)
            next_state = np.array([
                self.battery_soc,
                next_pred['pv_power'],
                next_pred['wind_power'],
                next_pred['load'],
                next_pred['price'],
                self.hour / 24.0
            ], dtype=np.float32)
        else:
            next_state = np.array([self.battery_soc, 0, 0, 50, 0.12, self.hour/24.0], dtype=np.float32)
        
        self.state = next_state
        
        # Store history
        self.history.append({
            'hour': self.hour,
            'battery_soc': self.battery_soc,
            'pv_power': pv_power,
            'wind_power': wind_power,
            'load': load,
            'price': price,
            'battery_power': battery_power,
            'grid_power': grid_power,
            'cost': cost,
            'reward': reward
        })
        
        done = len(self.history) >= 24  # One day simulation
        
        return next_state, reward, done, {
            'cost': cost,
            'total_cost': self.total_cost,
            'battery_soc': self.battery_soc,
            'grid_power': grid_power
        }


class DQN(nn.Module):
    """Deep Q-Network"""
    
    def __init__(self, state_dim, action_dim, hidden_dim=128):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, hidden_dim)
        self.fc4 = nn.Linear(hidden_dim, action_dim)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        return self.fc4(x)


class DQNAgent:
    """DQN Agent for energy management"""
    
    def __init__(self, state_dim, action_dim, config=None):
        if config is None:
            from config import RL_CONFIG
            config = RL_CONFIG
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Networks
        self.q_network = DQN(state_dim, action_dim).to(self.device)
        self.target_network = DQN(state_dim, action_dim).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=config['learning_rate'])
        
        # Replay buffer
        self.replay_buffer = deque(maxlen=config['buffer_size'])
        
        # Training parameters
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.gamma = config['gamma']
        self.batch_size = config['batch_size']
        self.tau = config['tau']
        
        # Discretize action space for DQN
        self.action_space = np.linspace(-50, 50, 21)  # 21 discrete actions
    
    def select_action(self, state, training=True):
        """Select action using epsilon-greedy policy"""
        if training and random.random() < self.epsilon:
            return random.choice(self.action_space)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
            action_idx = q_values.argmax().item()
        
        return self.action_space[action_idx]
    
    def store_transition(self, state, action, reward, next_state, done):
        """Store transition in replay buffer"""
        # Find closest discrete action
        action_idx = np.argmin(np.abs(self.action_space - action))
        self.replay_buffer.append((state, action_idx, reward, next_state, done))
    
    def train(self):
        """Train the agent"""
        if len(self.replay_buffer) < self.batch_size:
            return
        
        batch = random.sample(self.replay_buffer, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.BoolTensor(dones).to(self.device)
        
        # Current Q values
        q_values = self.q_network(states)
        q_value = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Next Q values from target network
        with torch.no_grad():
            next_q_values = self.target_network(next_states)
            next_q_value = next_q_values.max(1)[0]
            target_q_value = rewards + (1 - dones.float()) * self.gamma * next_q_value
        
        # Compute loss
        loss = nn.MSELoss()(q_value, target_q_value)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        # Soft update target network
        for target_param, param in zip(self.target_network.parameters(), self.q_network.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
        
        return loss.item()
    
    def save(self, path):
        """Save model"""
        torch.save({
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }, path)
    
    def load(self, path):
        """Load model"""
        checkpoint = torch.load(path, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])


class RLEnergyManager:
    """RL-based Energy Management System"""
    
    def __init__(self, config=None, predictor=None):
        self.config = config
        self.predictor = predictor
        self.env = MicrogridEnv(config, predictor)
        self.agent = DQNAgent(
            state_dim=self.env.observation_space.shape[0],
            action_dim=21,  # Discretized actions
            config=config
        )
        self.trained = False
    
    def train(self, episodes=100):
        """Train the RL agent"""
        print("Training RL agent...")
        for episode in range(episodes):
            state = self.env.reset()
            total_reward = 0
            
            while True:
                action = self.agent.select_action(state, training=True)
                next_state, reward, done, info = self.env.step(action)
                self.agent.store_transition(state, action, reward, next_state, done)
                
                loss = self.agent.train()
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            if (episode + 1) % 10 == 0:
                print(f"Episode {episode + 1}/{episodes}, Total Reward: {total_reward:.2f}, "
                      f"Total Cost: {self.env.total_cost:.2f}, Epsilon: {self.agent.epsilon:.3f}")
        
        self.trained = True
        print("Training completed!")
    
    def get_action(self, state):
        """Get action for given state"""
        if not self.trained:
            # Use simple heuristic if not trained
            battery_soc = state[0]
            net_load = state[3] - state[1] - state[2]  # load - pv - wind
            
            if net_load > 0 and battery_soc > 0.3:
                return min(net_load, 50)  # Discharge
            elif net_load < 0 and battery_soc < 0.8:
                return max(net_load, -50)  # Charge
            else:
                return 0
        
        return self.agent.select_action(state, training=False)
    
    def evaluate_strategy(self, horizon=24):
        """Evaluate the current strategy"""
        state = self.env.reset()
        results = []
        
        for _ in range(horizon):
            action = self.get_action(state)
            next_state, reward, done, info = self.env.step(action)
            results.append(info.copy())
            state = next_state
            if done:
                break
        
        return {
            'total_cost': self.env.total_cost,
            'total_reward': self.env.total_reward,
            'history': self.env.history,
            'final_soc': self.env.battery_soc
        }
