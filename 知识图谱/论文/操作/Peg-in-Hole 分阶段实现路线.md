---
title: Peg-in-Hole 分阶段实现路线
aliases:
  - 装配实现路线
  - 实验计划
tags:
  - robotics
  - peg-in-hole
  - implementation
  - roadmap
created: 2026-05-21
---

# Peg-in-Hole 分阶段实现路线

> UR7e + ROS2 + MoveIt + RealSense + SAM6D + IsaacLab/PPO。核心思路：视觉找孔、力控保安全、学习做补偿。

---

## 总体控制架构

最终控制律：

$$
x_{\text{cmd}}=x_{\text{vision}}+\Delta x_{\text{adm}}+\Delta x_{\text{learn}}
$$

| 项 | 来源 | 作用 |
| --- | ---- | ---- |
| $x_{\text{vision}}$ | SAM6D + MoveIt 规划 | 粗定位，把 peg 带到孔口 |
| $\Delta x_{\text{adm}}$ | 导纳控制 | 力觉柔顺，安全接触 |
| $\Delta x_{\text{learn}}$ | BC + PPO 策略 | 接触阶段自适应微调 |

> [!important] 学习策略不直接控制机械臂完成全部插孔，而是输出接触阶段的小范围补偿量。

---

## 阶段 1：搭建 ROS2 实机控制主链路

**目标**：机械臂、MoveIt、RealSense、TF、末端执行器全部跑通。

**时间**：第 1—2 周。

### 1.1 ROS2 节点结构

```
/realsense_camera_node       → 彩色图 + 深度图 + 内参
        ↓
/sam6d_pose_node             → /hole_pose_camera (PoseStamped)
        ↓
/pose_transform_node         → /hole_pose_base (PoseStamped)
        ↓
/moveit_planning_node        → 规划到预插入点
        ↓
/cartesian_servo_node         → 笛卡尔伺服执行
        ↓
/ur_robot_driver             → UR 机械臂驱动
```

后续扩展加入：

```
/force_state_node            → /wrench (力/力矩)
/admittance_control_node     → /servo_node/delta_twist_cmds
/learning_policy_node        → 学习策略输出
```

### 1.2 TF 坐标系

必须先固定这些 TF：

```
base_link
  └─ tool0
       └─ peg_tip_frame
  └─ camera_color_optical_frame
       └─ hole_frame (SAM6D 估计)
```

### 1.3 坐标变换

SAM6D 输出孔在相机坐标系下的位姿 ${}^{C}T_H$，手眼标定得 ${}^{B}T_C$：

$$
{}^{B}T_H = {}^{B}T_C \cdot {}^{C}T_H
$$

### 1.4 具体任务清单

- [ ] RealSense 在 ROS2 中发布彩色图、深度图、相机内参
- [ ] SAM6D 节点封装，输出 `geometry_msgs/PoseStamped`，话题 `/hole_pose_camera`
- [ ] 写 `pose_transform_node`，订阅 `/hole_pose_camera`，发布 `/hole_pose_base`
- [ ] 在 RViz2 中显示 `base_link`、`camera_frame`、`hole_frame`、`tool0`
- [ ] 确认孔位姿没有明显跳变、翻转或尺度错误
- [ ] MoveIt 规划到孔上方预插入点：${}^{B}T_{\text{pre}} = {}^{B}T_H \cdot T_{\text{offset}}$，offset 取 30~50 mm

> [!warning] 如果 TF 没对齐，后面所有力控和学习都建立在错误的坐标变换上。

---

## 阶段 2：传统视觉定位 + MoveIt 插入基线

**目标**：建立第一个 baseline — SAM6D 视觉定位 + MoveIt 规划 + 低速直线插入。

**时间**：第 1—2 周（与阶段 1 并行收尾）。

### 2.1 状态机流程

```
S0: 等待图像和孔位姿
S1: SAM6D 估计孔位姿
S2: MoveIt 规划到孔上方预插入点
S3: 末端姿态对准孔轴
S4: 低速沿孔轴下降
S5: 判断插入成功或失败
S6: 回撤
```

### 2.2 插入轨迹

插入阶段不用全局规划，用笛卡尔直线控制：

$$
x_d(t)=x_{\text{pre}}+v_z t
$$

MoveIt Servo 方式：实时发布 `geometry_msgs/TwistStamped`：

```yaml
linear.z: -0.002 ~ -0.01 m/s   # 从低速开始
```

### 2.3 安全保护

UR e 系列可读取 TCP force 估计（若无外置六维力传感器）：

$$
F_z > F_{\text{safe}} \Rightarrow \text{停止下压并回撤}
$$

$$
\sqrt{F_x^2+F_y^2} > F_{xy,\text{safe}} \Rightarrow \text{停止或进入搜索}
$$

### 2.4 数据记录

```bash
ros2 bag record \
  /tf \
  /joint_states \
  /hole_pose_base \
  /wrench \
  /servo_node/delta_twist_cmds
```

每次实验记录：

| 字段 | 说明 |
| ---- | ---- |
| `hole_pose_base` | 孔在基坐标系位姿 |
| `tool_pose` | 末端位姿 |
| `force_torque` | 力/力矩 |
| `success/failure` | 成功/失败 |
| `insertion_time` | 插入时间 |
| `max_force` | 最大接触力 |
| `initial_error` | 初始偏差 |

### 2.5 预期结论

> [!note] 仅靠 SAM6D 位姿和传统位置控制，在孔轴存在小偏差或视觉位姿跳动时，成功率有限。失败主要来自孔口偏心接触、姿态误差和刚性下压。

---

## 阶段 3：加入传统力控，形成强 baseline

**目标**：实现导纳控制，建立后续 learning-based 方法的对比基准。

**时间**：第 3—4 周。

### 3.1 导纳控制公式

$$
M_d\Delta \ddot{x}+D_d\Delta \dot{x}+K_d\Delta x=F_{\text{ext}}
$$

$$
x_{\text{cmd}}=x_d+\Delta x_{\text{adm}}
$$

### 3.2 ROS2 节点设计

新增 `/admittance_control_node`：

| 方向 | 话题 |
| ---- | ---- |
| 订阅 | `/tool_pose`、`/wrench`、`/hole_pose_base` |
| 发布 | `/servo_node/delta_twist_cmds` |

控制频率：100~500 Hz。MoveIt Servo 跑 100 Hz 则先按 100 Hz 实现。

### 3.3 力坐标系转换

力控在孔坐标系或工具坐标系下做，不在 base 坐标系：

$$
F_H = R_{HB} F_B
$$

### 3.4 简化实现（先不写完整二阶系统）

**插入方向 (z)**：低速恒速下压 + 力限制。

$$
v_z = v_{\text{insert}}
$$

当 $F_z > F_{z,\text{safe}}$ 则停止或减速。

**横向 (x, y)**：比例式力反馈。

$$
\Delta v_x = -k_f F_x,\quad \Delta v_y = -k_f F_y
$$

### 3.5 螺旋搜索 fallback

若插入失败，启动螺旋搜索：

$$
x(t)=x_0+r(t)\cos(\omega t)
$$

$$
y(t)=y_0+r(t)\sin(\omega t)
$$

$$
r(t)=kt
$$

### 3.6 实验设计

设置不同初始误差：

$$
\Delta x_0,\Delta y_0 \in [-2\text{ mm}, 2\text{ mm}]
$$

$$
\Delta \theta_0 \in [-2^\circ, 2^\circ]
$$

三组对比：

| 组 | 方法 |
| --- | ---- |
| A | SAM6D + MoveIt 位置插入 |
| B | SAM6D + 力阈值保护 |
| C | SAM6D + 导纳控制 + 搜索 |

指标：

$$
\eta=\frac{N_{\text{success}}}{N_{\text{total}}},\quad F_{\max}=\max_t |F_t|,\quad T_{\text{insert}}=t_{\text{success}}-t_{\text{start}}
$$

> [!important] 这个阶段要得到一个稳定结论：视觉—力控规控能提高安全性和成功率，但参数固定，对不同初始偏差、摩擦和姿态误差仍然敏感。这就是 learning-based 的切入点。

---

## 阶段 4：IsaacLab + PPO 定位为 residual policy

**目标**：不让 PPO 直接控制整条机械臂，改成学习接触补偿。

**时间**：第 5—6 周。

### 4.1 控制结构

$$
x_{\text{cmd}}=x_d+\Delta x_{\text{adm}}+\Delta x_{\text{learn}}
$$

学习策略只输出微小补偿量：

$$
\Delta x_{\text{learn}}=[\Delta x,\Delta y,\Delta z,\Delta \alpha,\Delta \beta]
$$

或更保守：

$$
\Delta x_{\text{learn}}=[\Delta x,\Delta y]
$$

### 4.2 IsaacLab 任务建模

域随机化参数：

$$
\xi = [\Delta x_0,\Delta y_0,\Delta \theta_0,\mu,c,\epsilon_v]
$$

| 参数 | 含义 |
| ---- | ---- |
| $\Delta x_0,\Delta y_0$ | 初始孔位偏差 |
| $\Delta \theta_0$ | 初始姿态偏差 |
| $\mu$ | 摩擦系数 |
| $c$ | 孔轴间隙 |
| $\epsilon_v$ | 视觉估计误差 |

### 4.3 状态空间

$$
s_t=[e_p,e_R,F_t,M_t,z_t,\dot{x}_t,a_{t-1}]
$$

| 分量 | 含义 |
| ---- | ---- |
| $e_p$ | 末端与目标孔位的位置误差 |
| $e_R$ | 姿态误差 |
| $F_t$ | 三维力 |
| $M_t$ | 三维力矩 |
| $z_t$ | 插入深度 |
| $\dot{x}_t$ | 末端速度 |
| $a_{t-1}$ | 上一时刻动作 |

### 4.4 动作空间

动作限制得很小：

$$
a_t=[\Delta x_t,\Delta y_t,\Delta z_t]
$$

$$
\Delta x_t,\Delta y_t \in [-0.2\text{ mm},0.2\text{ mm}]
$$

$$
\Delta z_t \in [-0.1\text{ mm},0.1\text{ mm}]
$$

> [!warning] 动作太大会导致策略学成乱撞。

### 4.5 奖励函数

不要只给成功奖励（太稀疏）：

$$
r_t = r_{\text{depth}} + r_{\text{align}} + r_{\text{success}} - r_{\text{force}} - r_{\text{action}} - r_{\text{time}}
$$

各项定义：

$$
r_{\text{depth}} = k_z(z_t - z_{t-1})
$$

$$
r_{\text{align}} = -k_e\sqrt{e_x^2 + e_y^2}
$$

$$
r_{\text{force}} = k_f\max(0,|F_t|-F_{\text{safe}})
$$

$$
r_{\text{action}} = k_a|a_t - a_{t-1}|^2
$$

$$
r_{\text{success}} =
\begin{cases}
R_s, & z_t > z_{\text{target}} \text{ 且 } |F_t| < F_{\text{safe}} \\
0, & \text{其他}
\end{cases}
$$

### 4.6 实验对比

| 组 | 方法 |
| --- | ---- |
| 传统 | 导纳控制（阶段3） |
| PPO scratch | 纯 PPO 从零训练 |
| 导纳 + PPO | 导纳控制底层 + PPO residual |

### 4.7 预期判断

如果 PPO from scratch 不好，**不是失败**，而是说明：

> 纯强化学习不适合直接解决高精度接触装配；它更适合作为传统力控框架中的 residual policy。

---

## 阶段 5：加入模仿学习，BC + PPO

**目标**：解决 PPO 从零探索效率低的问题。

**时间**：第 7—8 周。

### 5.1 专家数据来源

| 来源 | 说明 |
| ---- | ---- |
| 传统导纳控制成功轨迹 | 阶段3 采集 |
| 人工遥操作成功轨迹 | 手动示教 |
| 仿真规则策略轨迹 | IsaacLab 中调好参数的规控 |

### 5.2 数据格式

每条数据保存 $(s_t, a_t)$，动作不用机械臂绝对位姿，用相邻时刻位姿增量：

$$
a_t = x_{t+1} - x_t
$$

或只保存横向修正量：

$$
a_t = [\Delta x_t, \Delta y_t]
$$

> [!tip] 动作空间越小，学习任务越容易。

### 5.3 行为克隆

$$
L_{BC} = \frac{1}{N}\sum_{t=1}^{N}\left|a_t - \pi_\theta(s_t)\right|^2
$$

得到初始策略：

$$
a_t = \pi_\theta(s_t)
$$

### 5.4 PPO 微调

将 BC 网络参数作为 PPO 初始策略：

$$
\theta_0 = \theta_{BC}
$$

继续 PPO：

$$
\theta^* = \arg\max_\theta \mathbb{E}_{\pi_\theta}\left[\sum_{t=0}^{T}\gamma^t r_t\right]
$$

### 5.5 对比实验（必做）

| 组 | 方法 |
| --- | ---- |
| PPO from scratch | 从零训练 |
| BC only | 仅行为克隆 |
| BC + PPO | 预训练 + 微调 |

### 5.6 预期结论

> [!important] BC + PPO 收敛更快、成功率更高、接触力更小、对偏差更鲁棒。如果这三个都成立，learning-based 的意义就站住了。

---

## 阶段 6：前沿增强 — 力觉时序接触状态识别

**目标**：让课题不止于 BC + PPO，加入接触状态理解。

**时间**：第 9—10 周。

### 6.1 动机

传统规控用瞬时阈值判断接触：

$$
F_z > F_{\text{th}}
$$

但实际接触状态有多种，一个瞬时力值判断不了：

```
自由接近 → 孔口接触 → 单边接触 → 双边接触 → 卡滞 → 成功插入
```

### 6.2 构造力觉序列

最近 $H$ 步的力/力矩序列：

$$
\mathcal{W}_{t-H:t} = \{[F_\tau, M_\tau]\}_{\tau=t-H}^{t}
$$

### 6.3 接触状态分类器

用小网络（1D-CNN / GRU / LSTM）：

$$
m_t = g_\phi(\mathcal{W}_{t-H:t})
$$

$m_t$ 为接触状态类别。

### 6.4 基于接触状态自适应导纳

$$
M_d, D_d, K_d = \pi_\theta(m_t, s_t)
$$

或先用规则版本验证思路：

| 接触状态 | 策略 |
| -------- | ---- |
| 自由接近 | 较快下压，横向刚度较高 |
| 孔口接触 | 降低下压速度 |
| 单边接触 | 增加横向柔顺 |
| 卡滞 | 停止下压，横向微搜索 |
| 成功插入 | 继续低速压入 |

### 6.5 产出

1. 不同失败类型下的力/力矩曲线
2. 接触状态分类准确率
3. 基于接触状态的导纳参数调整结果

---

## 完整系统架构（最终形态）

```
RealSense
  ↓
SAM6D 位姿估计
  ↓
TF 位姿转换
  ↓
MoveIt 规划预插入位姿
  ↓
MoveIt Servo 笛卡尔伺服插入
  ↓
UR 内置力 / 外置力传感反馈
  ↓
导纳控制生成 Δx_adm
  ↓
BC + PPO 策略生成 Δx_learn
  ↓
合成最终末端速度/位置指令
```

最终控制律：

$$
x_{\text{cmd}} = x_d + \Delta x_{\text{adm}} + \Delta x_{\text{learn}}
$$

$$
\Delta x_{\text{learn}} = \pi_\theta(s_t)
$$

状态：

$$
s_t = [e_p, e_R, F_t, M_t, z_t, \dot{x}_t, a_{t-1}]
$$

---

## 时间总表

| 周次 | 阶段 | 内容 | 产出 |
| ---- | ---- | ---- | ---- |
| 1—2 | 阶段1+2 | SAM6D + TF + MoveIt 视觉插入基线 | 视觉定位误差统计、仅位置插入成功率、失败案例 |
| 3—4 | 阶段3 | 导纳控制 + 力阈值保护 | A/B/C三组对比（位置/力保护/导纳） |
| 5—6 | 阶段4 | IsaacLab PPO → residual policy | PPO scratch vs 导纳+PPO 对比 |
| 7—8 | 阶段5 | 专家数据 + BC + PPO fine-tune | BC only / PPO only / BC+PPO 三组对比 |
| 9—10 | 阶段6 | 力觉时序接触状态识别 | 接触状态分类、自适应导纳参数调整 |

---

## 论文主线

> 本文面向机械臂 Peg-in-Hole 精密装配任务，构建基于腕部视觉、力觉反馈和学习策略补偿的装配控制框架。
>
> 首先，利用 RealSense 与 SAM6D 实现孔位姿估计，结合 ROS2 MoveIt 完成机械臂视觉引导粗定位；
>
> 其次，引入导纳控制实现接触阶段柔顺插入，降低视觉误差和机械臂定位误差带来的刚性碰撞风险；
>
> 最后，利用传统规控成功轨迹进行模仿学习预训练，并结合强化学习进行策略微调，使学习模块在导纳控制基础上输出接触阶段微小补偿量，从而提高系统在初始位姿偏差和接触不确定条件下的插入成功率与鲁棒性。

### 三个贡献点

1. 构建了基于 SAM6D 位姿估计的机械臂 Peg-in-Hole 视觉粗定位与装配控制框架，实现孔位姿识别、机械臂接近和插入执行的一体化流程。

2. 设计了视觉—力觉融合的柔顺装配控制方法，在视觉定位误差存在时，通过力觉反馈和导纳控制提高接触阶段的安全性和插入成功率。

3. 提出了模仿学习与强化学习结合的接触阶段策略优化方法，利用传统规控或人工示教成功轨迹初始化策略，通过强化学习进一步优化复杂初始偏差下的插入成功率、接触力峰值和装配效率。

---

## 相关笔记

- [[机械臂 Peg-in-Hole 装配控制方法综述]]
