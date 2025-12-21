"""
基于强化学习的自适应能量管理系统
使用PPO (Proximal Policy Optimization) 算法
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Normal
from typing import List, Tuple, Dict
import json


class ActorCritic(nn.Module):
    """Actor-Critic 网络"""
    
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super(ActorCritic, self).__init__()
        
        # Actor网络（策略网络）
        self.actor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim)
        )
        
        # Actor的对数标准差（学习的）
        self.log_std = nn.Parameter(torch.zeros(action_dim))
        
        # Critic网络（价值网络）
        self.critic = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
    
    def forward(self, state):
        """前向传播"""
        # Actor输出动作均值
        action_mean = self.actor(state)
        action_std = torch.exp(self.log_std)
        
        # Critic输出状态价值
        value = self.critic(state)
        
        return action_mean, action_std, value
    
    def get_action(self, state, deterministic=False):
        """获取动作"""
        action_mean, action_std, value = self.forward(state)
        
        if deterministic:
            action = torch.tanh(action_mean)
        else:
            # 创建正态分布
            dist = Normal(action_mean, action_std)
            action_sample = dist.sample()
            action = torch.tanh(action_sample)  # 限制在[-1, 1]
            
        return action, value
    
    def evaluate(self, state, action):
        """评估动作"""
        action_mean, action_std, value = self.forward(state)
        
        # 逆tanh变换
        action_transformed = torch.atanh(torch.clamp(action, -0.9999, 0.9999))
        
        # 计算对数概率
        dist = Normal(action_mean, action_std)
        log_prob = dist.log_prob(action_transformed)
        
        # 考虑tanh变换的雅可比行列式
        log_prob = log_prob - torch.log(1 - action**2 + 1e-6)
        log_prob = log_prob.sum(dim=-1, keepdim=True)
        
        # 计算熵
        entropy = dist.entropy().sum(dim=-1, keepdim=True)
        
        return log_prob, value, entropy


class PPOAgent:
    """PPO强化学习智能体"""
    
    def __init__(self, state_dim, action_dim, device='cpu', 
                 lr=3e-4, gamma=0.99, eps_clip=0.2, k_epochs=10):
        self.device = device
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.k_epochs = k_epochs
        
        # 创建网络
        self.policy = ActorCritic(state_dim, action_dim).to(device)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        
        # 旧策略用于计算重要性采样比率
        self.policy_old = ActorCritic(state_dim, action_dim).to(device)
        self.policy_old.load_state_dict(self.policy.state_dict())
        
        # 经验缓冲
        self.buffer = {
            'states': [],
            'actions': [],
            'rewards': [],
            'dones': [],
            'log_probs': []
        }
        
        # 训练统计
        self.training_stats = {
            'episodes': 0,
            'total_reward': [],
            'actor_loss': [],
            'critic_loss': [],
            'avg_reward': 0
        }
    
    def select_action(self, state, deterministic=False):
        """选择动作"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            action, _ = self.policy_old.get_action(state, deterministic)
        
        return action.cpu().numpy()[0]
    
    def store_transition(self, state, action, reward, done):
        """存储经验"""
        self.buffer['states'].append(state)
        self.buffer['actions'].append(action)
        self.buffer['rewards'].append(reward)
        self.buffer['dones'].append(done)
    
    def compute_returns(self, rewards, dones):
        """计算回报"""
        returns = []
        R = 0
        
        for reward, done in zip(reversed(rewards), reversed(dones)):
            if done:
                R = 0
            R = reward + self.gamma * R
            returns.insert(0, R)
        
        return returns
    
    def update(self):
        """更新策略"""
        if len(self.buffer['states']) == 0:
            return
        
        # 转换为tensor
        states = torch.FloatTensor(np.array(self.buffer['states'])).to(self.device)
        actions = torch.FloatTensor(np.array(self.buffer['actions'])).to(self.device)
        rewards = self.buffer['rewards']
        dones = self.buffer['dones']
        
        # 计算回报
        returns = self.compute_returns(rewards, dones)
        returns = torch.FloatTensor(returns).unsqueeze(1).to(self.device)
        
        # 标准化回报
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        
        # 用旧策略计算对数概率
        with torch.no_grad():
            old_log_probs, _, _ = self.policy_old.evaluate(states, actions)
        
        # PPO更新
        for _ in range(self.k_epochs):
            # 评估当前策略
            log_probs, values, entropy = self.policy.evaluate(states, actions)
            
            # 计算优势函数
            advantages = returns - values.detach()
            
            # 重要性采样比率
            ratios = torch.exp(log_probs - old_log_probs.detach())
            
            # PPO损失
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
            actor_loss = -torch.min(surr1, surr2).mean()
            
            # Critic损失
            critic_loss = nn.MSELoss()(values, returns)
            
            # 总损失
            loss = actor_loss + 0.5 * critic_loss - 0.01 * entropy.mean()
            
            # 更新网络
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
            self.optimizer.step()
        
        # 更新旧策略
        self.policy_old.load_state_dict(self.policy.state_dict())
        
        # 统计
        self.training_stats['actor_loss'].append(actor_loss.item())
        self.training_stats['critic_loss'].append(critic_loss.item())
        self.training_stats['total_reward'].append(sum(rewards))
        self.training_stats['avg_reward'] = np.mean(self.training_stats['total_reward'][-100:])
        self.training_stats['episodes'] += 1
        
        # 清空缓冲
        self.buffer = {
            'states': [],
            'actions': [],
            'rewards': [],
            'dones': [],
            'log_probs': []
        }
    
    def save(self, filepath):
        """保存模型"""
        torch.save({
            'policy_state_dict': self.policy.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_stats': self.training_stats
        }, filepath)
    
    def load(self, filepath):
        """加载模型"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.policy.load_state_dict(checkpoint['policy_state_dict'])
        self.policy_old.load_state_dict(checkpoint['policy_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.training_stats = checkpoint['training_stats']
    
    def get_stats(self) -> Dict:
        """获取训练统计"""
        return {
            'episodes': self.training_stats['episodes'],
            'avg_reward': self.training_stats['avg_reward'],
            'recent_rewards': self.training_stats['total_reward'][-10:] if self.training_stats['total_reward'] else [],
            'actor_loss': self.training_stats['actor_loss'][-1] if self.training_stats['actor_loss'] else 0,
            'critic_loss': self.training_stats['critic_loss'][-1] if self.training_stats['critic_loss'] else 0,
        }


class RLEnergyManager:
    """强化学习能量管理器"""
    
    def __init__(self, state_dim=9, action_dim=2, device='cpu'):
        self.agent = PPOAgent(state_dim, action_dim, device)
        self.training_mode = True
        self.episode_count = 0
        self.performance_history = []
        
    def get_action(self, state: np.ndarray) -> np.ndarray:
        """获取能量管理动作"""
        if self.training_mode:
            action = self.agent.select_action(state, deterministic=False)
        else:
            action = self.agent.select_action(state, deterministic=True)
        return action
    
    def train_episode(self, env, max_steps=672):  # 一周的15分钟步长
        """训练一个episode"""
        state = env.reset()
        episode_reward = 0
        episode_cost = 0
        episode_renewable_ratio = []
        
        for step in range(max_steps):
            # 选择动作
            action = self.get_action(state)
            
            # 执行动作
            next_state, reward, done, info = env.step(action)
            
            # 存储经验
            self.agent.store_transition(state, action, reward, done)
            
            # 更新统计
            episode_reward += reward
            episode_cost += info['cost']
            episode_renewable_ratio.append(info['renewable_ratio'])
            
            state = next_state
            
            if done:
                break
        
        # 更新策略
        self.agent.update()
        
        # 记录性能
        performance = {
            'episode': self.episode_count,
            'reward': episode_reward,
            'cost': episode_cost,
            'avg_renewable_ratio': np.mean(episode_renewable_ratio),
            'steps': step + 1
        }
        self.performance_history.append(performance)
        self.episode_count += 1
        
        return performance
    
    def train(self, env, num_episodes=10):
        """训练多个episodes"""
        self.training_mode = True
        results = []
        
        print(f"开始训练 {num_episodes} 个episodes...")
        for ep in range(num_episodes):
            performance = self.train_episode(env)
            results.append(performance)
            
            if (ep + 1) % 5 == 0:
                print(f"Episode {ep+1}/{num_episodes}: "
                      f"Reward={performance['reward']:.2f}, "
                      f"Cost=¥{performance['cost']:.2f}, "
                      f"Renewable={performance['avg_renewable_ratio']*100:.1f}%")
        
        return results
    
    def evaluate(self, env, num_episodes=5):
        """评估策略"""
        self.training_mode = False
        results = []
        
        for ep in range(num_episodes):
            state = env.reset()
            episode_reward = 0
            episode_cost = 0
            episode_renewable_ratio = []
            
            done = False
            steps = 0
            max_steps = 672
            
            while not done and steps < max_steps:
                action = self.get_action(state)
                next_state, reward, done, info = env.step(action)
                
                episode_reward += reward
                episode_cost += info['cost']
                episode_renewable_ratio.append(info['renewable_ratio'])
                
                state = next_state
                steps += 1
            
            results.append({
                'episode': ep,
                'reward': episode_reward,
                'cost': episode_cost,
                'avg_renewable_ratio': np.mean(episode_renewable_ratio),
                'steps': steps
            })
        
        return results
    
    def get_performance_summary(self) -> Dict:
        """获取性能摘要"""
        if not self.performance_history:
            return {}
        
        recent = self.performance_history[-10:]
        
        return {
            'total_episodes': self.episode_count,
            'avg_reward': np.mean([p['reward'] for p in recent]),
            'avg_cost': np.mean([p['cost'] for p in recent]),
            'avg_renewable_ratio': np.mean([p['avg_renewable_ratio'] for p in recent]),
            'best_reward': max([p['reward'] for p in self.performance_history]),
            'best_cost': min([p['cost'] for p in self.performance_history]),
        }
    
    def save_model(self, filepath='rl_model.pth'):
        """保存模型"""
        self.agent.save(filepath)
        print(f"模型已保存到 {filepath}")
    
    def load_model(self, filepath='rl_model.pth'):
        """加载模型"""
        self.agent.load(filepath)
        print(f"模型已从 {filepath} 加载")


class RuleBasedController:
    """基于规则的控制器（用于对比）"""
    
    def __init__(self):
        self.name = "Rule-based Controller"
    
    def get_action(self, state: np.ndarray) -> np.ndarray:
        """基于规则生成动作"""
        solar = state[0]
        wind = state[1]
        load = state[2]
        price = state[3]
        soc = state[4]
        
        renewable_gen = (solar + wind) * 100  # 反归一化
        load_demand = load * 100
        
        # 电池动作
        if price < 0.6:  # 低电价
            if soc < 0.8:
                battery_action = 0.8  # 充电
            else:
                battery_action = 0.0
        elif price > 1.0:  # 高电价
            if soc > 0.3:
                battery_action = -0.8  # 放电
            else:
                battery_action = 0.0
        else:
            # 根据可再生能源决定
            if renewable_gen > load_demand and soc < 0.9:
                battery_action = 0.5
            elif renewable_gen < load_demand and soc > 0.2:
                battery_action = -0.5
            else:
                battery_action = 0.0
        
        # 电网动作（由系统自动计算）
        grid_action = 0.0
        
        return np.array([battery_action, grid_action])


if __name__ == "__main__":
    # 测试RL能量管理器
    print("===== RL能量管理系统测试 =====\n")
    
    # 创建简单的测试环境
    class DummyEnv:
        def __init__(self):
            self.state_dim = 9
            self.action_dim = 2
            self.step_count = 0
            
        def reset(self):
            self.step_count = 0
            return np.random.rand(self.state_dim).astype(np.float32)
        
        def step(self, action):
            self.step_count += 1
            next_state = np.random.rand(self.state_dim).astype(np.float32)
            reward = np.random.randn()
            done = self.step_count >= 100
            info = {'cost': 10.0, 'renewable_ratio': 0.7}
            return next_state, reward, done, info
    
    env = DummyEnv()
    manager = RLEnergyManager()
    
    print("训练2个episodes...")
    results = manager.train(env, num_episodes=2)
    
    print("\n性能摘要:")
    summary = manager.get_performance_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n基于规则的控制器测试:")
    rule_controller = RuleBasedController()
    test_state = np.array([0.5, 0.3, 0.7, 1.1, 0.6, 0.5, 0.3, 0.7, 1.0])
    action = rule_controller.get_action(test_state)
    print(f"  测试动作: {action}")
