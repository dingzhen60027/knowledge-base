---
title: 机械臂 Peg-in-Hole 装配
aliases:
  - Peg-in-Hole
  - 力控装配
  - 学习装配
tags:
  - robotics
  - peg-in-hole
  - force-control
  - reinforcement-learning
  - assembly
status: active
deadline: 2026-08-01
---

# 机械臂 Peg-in-Hole 装配

> 基于视觉—力觉融合与模仿强化学习的机械臂精密装配控制研究。

## 实验平台

- UR7e 机械臂
- ROS2 + MoveIt
- 腕部 RealSense 相机
- SAM6D 位姿估计
- IsaacLab + PPO

## 技术路线

```
视觉粗定位(SAM6D) → 导纳控制(力觉柔顺) → BC 预训练 → PPO 微调补偿
```

## 当前进度

- [x] 传统规控尝试（SAM6D 位姿提取 + 位置插入）
- [x] IsaacLab + PPO 强化学习训练
- [ ] 阶段1：整理传统基线（进行中）
- [ ] 阶段2：导纳控制强 baseline
- [ ] 阶段3：PPO residual policy
- [ ] 阶段4：BC + PPO 模仿强化学习
- [ ] 阶段5：力觉时序接触状态识别

## 相关笔记

- [[机械臂 Peg-in-Hole 装配控制方法综述]]
- [[Peg-in-Hole 分阶段实现路线]]
