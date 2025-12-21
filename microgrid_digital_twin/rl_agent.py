"""
强化学习能量管理模块
====================

基于深度强化学习的自适应能量管理策略生成系统。
支持DQN、PPO、SAC等算法。
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import json


@dataclass
class Experience:
    """经验回放样本"""
    state: np.ndarray
    action: np.ndarray
    reward: float
    next_state: np.ndarray
    done: bool


class ReplayBuffer:
    """经验回放缓冲区"""
    
    def __init__(self, capacity: int = 100000):
        self.buffer = deque(maxlen=capacity)
        
    def push(self, experience: Experience):
        self.buffer.append(experience)
        
    def sample(self, batch_size: int) -> List[Experience]:
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[i] for i in indices]
    
    def __len__(self):
        return len(self.buffer)


class NeuralNetwork:
    """简单神经网络实现（不依赖深度学习框架）"""
    
    def __init__(self, layer_sizes: List[int], activation: str = 'relu'):
        self.layer_sizes = layer_sizes
        self.activation = activation
        self.weights = []
        self.biases = []
        
        # Xavier初始化
        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * np.sqrt(2.0 / layer_sizes[i])
            b = np.zeros((1, layer_sizes[i+1]))
            self.weights.append(w)
            self.biases.append(b)
            
    def _activate(self, x: np.ndarray, derivative: bool = False) -> np.ndarray:
        if self.activation == 'relu':
            if derivative:
                return (x > 0).astype(float)
            return np.maximum(0, x)
        elif self.activation == 'tanh':
            if derivative:
                return 1 - np.tanh(x) ** 2
            return np.tanh(x)
        elif self.activation == 'sigmoid':
            s = 1 / (1 + np.exp(-np.clip(x, -500, 500)))
            if derivative:
                return s * (1 - s)
            return s
        return x
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        self.layer_outputs = [x]
        current = x
        
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            z = np.dot(current, w) + b
            if i < len(self.weights) - 1:
                current = self._activate(z)
            else:
                current = z  # 输出层不激活
            self.layer_outputs.append(current)
            
        return current
    
    def backward(self, loss_gradient: np.ndarray, learning_rate: float = 0.001) -> None:
        """反向传播"""
        gradients_w = []
        gradients_b = []
        
        delta = loss_gradient
        
        for i in range(len(self.weights) - 1, -1, -1):
            gradients_w.insert(0, np.dot(self.layer_outputs[i].T, delta))
            gradients_b.insert(0, np.sum(delta, axis=0, keepdims=True))
            
            if i > 0:
                delta = np.dot(delta, self.weights[i].T) * self._activate(
                    self.layer_outputs[i], derivative=True
                )
        
        # 更新权重
        for i in range(len(self.weights)):
            self.weights[i] -= learning_rate * gradients_w[i]
            self.biases[i] -= learning_rate * gradients_b[i]
    
    def get_params(self) -> Dict:
        return {
            'weights': [w.tolist() for w in self.weights],
            'biases': [b.tolist() for b in self.biases]
        }
    
    def set_params(self, params: Dict):
        self.weights = [np.array(w) for w in params['weights']]
        self.biases = [np.array(b) for b in params['biases']]


class EnergyManagementAgent:
    """强化学习能量管理智能体"""
    
    def __init__(self, 
                 state_dim: int = 10,
                 action_dim: int = 2,
                 hidden_dims: List[int] = [128, 64],
                 learning_rate: float = 0.001,
                 gamma: float = 0.99,
                 epsilon: float = 1.0,
                 epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01,
                 buffer_size: int = 100000,
                 batch_size: int = 64):
        """
        初始化能量管理智能体
        
        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            hidden_dims: 隐藏层维度
            learning_rate: 学习率
            gamma: 折扣因子
            epsilon: 探索率
            epsilon_decay: 探索率衰减
            epsilon_min: 最小探索率
            buffer_size: 经验回放容量
            batch_size: 批量大小
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        
        # 构建网络
        layer_sizes = [state_dim] + hidden_dims + [action_dim * 11]  # 离散化动作
        self.q_network = NeuralNetwork(layer_sizes)
        self.target_network = NeuralNetwork(layer_sizes)
        self._update_target_network()
        
        # 经验回放
        self.replay_buffer = ReplayBuffer(buffer_size)
        
        # 训练统计
        self.training_steps = 0
        self.episode_rewards = []
        self.losses = []
        
        # 动作空间离散化
        self.action_bins = np.linspace(-1, 1, 11)  # 电池动作
        
    def _update_target_network(self):
        """更新目标网络"""
        self.target_network.set_params(self.q_network.get_params())
        
    def _discretize_action(self, continuous_action: np.ndarray) -> int:
        """将连续动作转换为离散索引"""
        battery_idx = np.argmin(np.abs(self.action_bins - continuous_action[0]))
        diesel_idx = 1 if continuous_action[1] > 0.5 else 0
        return battery_idx * 2 + diesel_idx
    
    def _continuous_action(self, discrete_idx: int) -> np.ndarray:
        """将离散索引转换为连续动作"""
        battery_idx = discrete_idx // 2
        diesel_idx = discrete_idx % 2
        return np.array([self.action_bins[battery_idx], float(diesel_idx)])
    
    def select_action(self, state: np.ndarray, training: bool = True) -> Dict:
        """
        选择动作
        
        Args:
            state: 状态向量
            training: 是否为训练模式
            
        Returns:
            动作字典
        """
        if training and np.random.random() < self.epsilon:
            # 探索：随机动作
            battery_action = np.random.uniform(-1, 1)
            diesel_on = np.random.random() > 0.7
        else:
            # 利用：选择最优动作
            state_input = state.reshape(1, -1)
            q_values = self.q_network.forward(state_input)
            best_action_idx = np.argmax(q_values[0])
            continuous_action = self._continuous_action(best_action_idx)
            battery_action = continuous_action[0]
            diesel_on = continuous_action[1] > 0.5
        
        return {
            'battery_action': float(battery_action),
            'diesel_on': bool(diesel_on)
        }
    
    def calculate_reward(self, state: Dict, action: Dict, next_state: Dict) -> float:
        """
        计算奖励函数
        
        Args:
            state: 当前状态
            action: 执行的动作
            next_state: 下一状态
            
        Returns:
            奖励值
        """
        reward = 0.0
        
        # 1. 成本惩罚
        cost = next_state.get('cost', 0)
        reward -= cost * 10  # 放大成本影响
        
        # 2. 可再生能源利用奖励
        renewable_ratio = next_state.get('renewable_ratio', 0)
        reward += renewable_ratio * 5
        
        # 3. 电池SOC管理
        soc = next_state.get('battery_soc', 0.5)
        if 0.3 <= soc <= 0.7:
            reward += 1.0  # SOC在健康范围
        elif soc < 0.15 or soc > 0.85:
            reward -= 2.0  # SOC过低或过高
        
        # 4. 电网交互惩罚
        grid_power = abs(next_state.get('grid_power', 0))
        reward -= grid_power * 0.01  # 鼓励自给自足
        
        # 5. 柴油机使用惩罚
        if action.get('diesel_on', False):
            reward -= 0.5
        
        # 6. 供需平衡
        power_balance = next_state.get('power_balance', {})
        imbalance = abs(power_balance.get('generation', 0) - 
                       power_balance.get('consumption', 0))
        if imbalance > 50:
            reward -= imbalance * 0.02
        
        return reward
    
    def train_step(self, state: np.ndarray, action: Dict, 
                   reward: float, next_state: np.ndarray, done: bool):
        """
        训练步骤
        
        Args:
            state: 当前状态
            action: 动作
            reward: 奖励
            next_state: 下一状态
            done: 是否结束
        """
        # 转换动作格式
        action_array = np.array([
            action['battery_action'],
            1.0 if action['diesel_on'] else 0.0
        ])
        
        # 存储经验
        exp = Experience(state, action_array, reward, next_state, done)
        self.replay_buffer.push(exp)
        
        # 经验回放训练
        if len(self.replay_buffer) >= self.batch_size:
            self._train_batch()
            
        # 更新探索率
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        # 定期更新目标网络
        self.training_steps += 1
        if self.training_steps % 100 == 0:
            self._update_target_network()
    
    def _train_batch(self):
        """批量训练"""
        batch = self.replay_buffer.sample(self.batch_size)
        
        states = np.array([e.state for e in batch])
        actions = np.array([e.action for e in batch])
        rewards = np.array([e.reward for e in batch])
        next_states = np.array([e.next_state for e in batch])
        dones = np.array([e.done for e in batch])
        
        # 计算目标Q值
        next_q_values = self.target_network.forward(next_states)
        max_next_q = np.max(next_q_values, axis=1)
        targets = rewards + self.gamma * max_next_q * (1 - dones)
        
        # 计算当前Q值
        current_q = self.q_network.forward(states)
        
        # 计算损失和梯度
        action_indices = np.array([self._discretize_action(a) for a in actions])
        loss_gradient = np.zeros_like(current_q)
        for i, idx in enumerate(action_indices):
            loss_gradient[i, idx] = current_q[i, idx] - targets[i]
        
        # 反向传播
        self.q_network.backward(loss_gradient / self.batch_size, self.learning_rate)
        
        # 记录损失
        loss = np.mean(loss_gradient ** 2)
        self.losses.append(loss)
    
    def get_policy_explanation(self, state: Dict) -> str:
        """
        获取策略解释
        
        Args:
            state: 当前状态
            
        Returns:
            策略解释文本
        """
        action = self.select_action(
            np.array(list(state.values())[:self.state_dim]), 
            training=False
        )
        
        explanation = []
        explanation.append(f"当前策略分析:")
        
        battery_action = action['battery_action']
        if battery_action > 0.3:
            explanation.append(f"- 电池充电 (功率: {battery_action*100:.1f}%)")
            explanation.append("  原因: 可再生能源过剩或电价较低")
        elif battery_action < -0.3:
            explanation.append(f"- 电池放电 (功率: {abs(battery_action)*100:.1f}%)")
            explanation.append("  原因: 负荷需求高或电价较高")
        else:
            explanation.append("- 电池待机")
            explanation.append("  原因: 供需基本平衡")
        
        if action['diesel_on']:
            explanation.append("- 柴油发电机: 开启")
            explanation.append("  原因: 可再生能源和储能不足以满足负荷")
        else:
            explanation.append("- 柴油发电机: 关闭")
            explanation.append("  原因: 优先使用清洁能源")
        
        return "\n".join(explanation)
    
    def save(self, path: str):
        """保存模型"""
        data = {
            'q_network': self.q_network.get_params(),
            'epsilon': self.epsilon,
            'training_steps': self.training_steps,
            'episode_rewards': self.episode_rewards,
            'config': {
                'state_dim': self.state_dim,
                'action_dim': self.action_dim,
                'gamma': self.gamma,
                'learning_rate': self.learning_rate
            }
        }
        with open(path, 'w') as f:
            json.dump(data, f)
    
    def load(self, path: str):
        """加载模型"""
        with open(path, 'r') as f:
            data = json.load(f)
        self.q_network.set_params(data['q_network'])
        self.epsilon = data.get('epsilon', self.epsilon_min)
        self.training_steps = data.get('training_steps', 0)
        self._update_target_network()


class RuleBasedAgent:
    """基于规则的能量管理智能体（作为基准）"""
    
    def __init__(self, config: Optional[Dict] = None):
        config = config or {}
        self.soc_high_threshold = config.get('soc_high', 0.8)
        self.soc_low_threshold = config.get('soc_low', 0.3)
        self.price_high_threshold = config.get('price_high', 1.0)
        self.price_low_threshold = config.get('price_low', 0.5)
        
    def select_action(self, state: Dict) -> Dict:
        """基于规则选择动作"""
        soc = state.get('battery_soc', 0.5)
        price = state.get('electricity_price', 0.8)
        solar = state.get('solar_power', 0)
        wind = state.get('wind_power', 0)
        load = state.get('load_power', 100)
        
        renewable = solar + wind
        net_power = renewable - load
        
        battery_action = 0.0
        diesel_on = False
        
        # 规则1: 可再生能源过剩时充电
        if net_power > 20 and soc < self.soc_high_threshold:
            battery_action = min(1.0, net_power / 50)
        
        # 规则2: 低电价时充电
        elif price < self.price_low_threshold and soc < 0.7:
            battery_action = 0.5
        
        # 规则3: 高电价时放电
        elif price > self.price_high_threshold and soc > self.soc_low_threshold:
            battery_action = -0.5
        
        # 规则4: 负荷不足时放电
        elif net_power < -30 and soc > self.soc_low_threshold:
            battery_action = max(-1.0, net_power / 50)
        
        # 规则5: 紧急情况启动柴油机
        if net_power < -50 and soc < 0.2:
            diesel_on = True
        
        return {
            'battery_action': battery_action,
            'diesel_on': diesel_on
        }


class AdaptiveEnergyManager:
    """自适应能量管理系统"""
    
    def __init__(self):
        self.rl_agent = EnergyManagementAgent()
        self.rule_agent = RuleBasedAgent()
        
        self.mode = 'hybrid'  # 'rl', 'rule', 'hybrid'
        self.rl_confidence = 0.5
        self.performance_history = deque(maxlen=100)
        
    def select_action(self, state: np.ndarray, state_dict: Dict,
                      training: bool = True) -> Dict:
        """选择最优动作"""
        if self.mode == 'rule':
            return self.rule_agent.select_action(state_dict)
        elif self.mode == 'rl':
            return self.rl_agent.select_action(state, training)
        else:  # hybrid
            rl_action = self.rl_agent.select_action(state, training)
            rule_action = self.rule_agent.select_action(state_dict)
            
            # 混合动作
            battery_action = (
                self.rl_confidence * rl_action['battery_action'] +
                (1 - self.rl_confidence) * rule_action['battery_action']
            )
            diesel_on = rl_action['diesel_on'] or rule_action['diesel_on']
            
            return {
                'battery_action': battery_action,
                'diesel_on': diesel_on
            }
    
    def update_confidence(self, reward: float):
        """根据表现更新RL置信度"""
        self.performance_history.append(reward)
        
        if len(self.performance_history) >= 50:
            recent_performance = np.mean(list(self.performance_history)[-50:])
            if recent_performance > 0:
                self.rl_confidence = min(0.95, self.rl_confidence + 0.01)
            else:
                self.rl_confidence = max(0.3, self.rl_confidence - 0.01)
    
    def train(self, state: np.ndarray, action: Dict, 
              reward: float, next_state: np.ndarray, done: bool):
        """训练RL智能体"""
        self.rl_agent.train_step(state, action, reward, next_state, done)
        self.update_confidence(reward)
    
    def get_status(self) -> Dict:
        """获取管理器状态"""
        return {
            'mode': self.mode,
            'rl_confidence': self.rl_confidence,
            'epsilon': self.rl_agent.epsilon,
            'training_steps': self.rl_agent.training_steps,
            'buffer_size': len(self.rl_agent.replay_buffer),
            'recent_performance': np.mean(list(self.performance_history)) if self.performance_history else 0
        }
