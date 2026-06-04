---
title: ACT - Action Chunking with Transformers
date: 2026-05-05
tags:
  - paper
  - imitation-learning
  - transformer
  - manipulation
  - embodied-ai
---

# ACT: Action Chunking with Transformers

> **Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware**
> Tony Z. Zhao, Vikash Kumar, Sergey Levine, Chelsea Finn | RSS 2023

## 核心问题

精细双手操作（bimanual manipulation）的模仿学习，难点在于**高精度**和**长时间序列**。

## 核心思想

用 Transformer 预测**动作块（action chunks）**而非单步动作，解决模仿学习中的**复合误差（compounding error）**问题。

```
输入: 图像序列 + 关节状态
  ↓ CVAE encoder (StyleGAN-like) → latent z
  ↓ Transformer decoder → 预测未来 k 步动作
输出: 动作块 [a_t, a_{t+1}, ..., a_{t+k}]
```

## 关键设计

| 组件 | 作用 |
|------|------|
| Action Chunking | 一次预测未来多步动作，减少累积误差 |
| CVAE Encoder | 从演示中学习动作风格/模式 |
| Transformer Decoder | 时序建模，处理长序列依赖 |
| Temporal Ensemble | 多步预测取加权平均，平滑动作 |

## 硬件方案

- 两个低成本手臂（ALOHA）
- 主从遥操作采集演示数据
- 低成本 = 可复现、可推广

## 实验结果

- 6 个精细操作任务（开瓶盖、穿绳、叠衣服等）
- 远超 BC（行为克隆）baseline
- 关键消融：action chunking > 单步预测

## 与具身智能的关系

- 证明了 Transformer + 模仿学习在精细操作上的可行性
- 低成本硬件思路降低了机器人学习门槛
- 动作块预测成为后续工作的标准范式

> 任务分类：[[操作/操作|操作 Manipulation]] | 回 [[论文/论文|论文阅读]]

## 相关笔记

- [[ViT|ViT]] — Transformer 在视觉中的基础工作
- [[Diffusion|Diffusion]] — 扩散模型用于动作生成
