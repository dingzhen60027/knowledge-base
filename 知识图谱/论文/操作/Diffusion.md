---
title: Diffusion — 扩散模型
date: 2026-05-05
tags:
  - paper
  - diffusion
  - generative-model
  - policy
  - embodied-ai
---

# Diffusion：从 DDPM 到 Diffusion Policy

## DDPM — 基础原理

> Ho et al. | NeurIPS 2020

### 前向过程（加噪）

逐步向数据 $x_0$ 加高斯噪声，T 步后变成纯噪声：

$$x_t = \sqrt{1-\beta_t} x_{t-1} + \sqrt{\beta_t} \epsilon$$

### 反向过程（去噪）

训练网络 $\epsilon_\theta(x_t, t)$ 预测每一步加的噪声：

$$\mathcal{L} = \|\epsilon - \epsilon_\theta(x_t, t)\|^2$$

### 推理

从 $x_T \sim \mathcal{N}(0, I)$ 开始，逐步去噪得到 $x_0$。

---

## Diffusion Policy — 具身智能应用

> Chi et al. | RSS 2023

### 为什么用 Diffusion 做策略

| 传统方法的问题 | Diffusion 的优势 |
|---------------|-----------------|
| 单峰假设（高斯分布） | 天然表达**多模态**分布 |
| 难以处理多解动作 | 多个去噪路径 = 多种可能动作 |
| 时序不连贯 | 可对动作序列建模 |

### 核心架构

```
观测 o_t → CNN/ViT 编码 → 条件 embedding
                                ↓
噪声动作块 x_T → U-Net 去噪 (条件) → x_0 = 预测动作序列
```

### 关键设计

- **Action Chunking**：预测动作序列而非单步（受 ACT 启发）
- **Denoising Diffusion**：用 DDPM 逐步细化动作
- **Classifier-free Guidance**：平衡多样性与确定性

### 实验结果

- 15 个任务（Push-T, Robomimic, 真机）
- 在复杂多模态任务上显著优于 BC、LSTM-GMM、ACT
- 真机任务成功率提升显著（如翻转杯子：BC 0% → DP 80%）

### Diffusion Policy vs ACT

| | ACT | Diffusion Policy |
|---|-----|-----------------|
| 生成方式 | CVAE + Transformer | DDPM + U-Net |
| 多模态 | 隐变量 z 控制 | 扩散过程自然表达 |
| 稳定性 | 需要 temporal ensemble | 更平滑 |
| 训练 | 更快 | 稍慢（多步去噪） |

## 关键进展

- **DDIM** — 加速采样，去噪步数可减少 10-50 倍
- **Latent Diffusion** — 在潜空间扩散，Stable Diffusion 的基础
- **Consistency Models** — 一步生成，去噪过程蒸馏

> 任务分类：[[通用方法/通用方法|通用方法]] | 回 [[论文/论文|论文阅读]]

## 相关笔记

- [[ACT|ACT]] — 动作块预测的先驱工作
- [[ViT|ViT]] — Vision Transformer（Diffusion Policy 的视觉 backbone）
