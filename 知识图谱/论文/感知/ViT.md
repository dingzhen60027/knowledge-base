---
title: ViT - Vision Transformer
date: 2026-05-05
tags:
  - paper
  - vision
  - transformer
  - foundation-model
---

# ViT: An Image is Worth 16x16 Words

> **Transformers for Image Recognition at Scale**
> Dosovitskiy et al. | ICLR 2021

## 核心问题

CNN 长期统治计算机视觉。能否用纯 Transformer 替代？

## 核心思想

把图像切成 patch（16×16），将每个 patch 当作 NLP 里的 token，送入标准 Transformer。

```
图像 H×W×C
  → 切成 N 个 P×P patch
  → 每个 patch 展平 + 线性投影 = patch embedding
  → 加 position embedding + [CLS] token
  → Transformer Encoder × L 层
  → [CLS] 输出 → MLP head → 分类
```

## 关键发现

| 结论 | 说明 |
|------|------|
| 大数据集上 ViT > CNN | JFT-300M 预训练后超越 ResNet |
| 小数据不如 CNN | ViT 缺少 CNN 的归纳偏置（局部性、平移不变性） |
| 预训练至关重要 | ImageNet 上 ViT 不如 ResNet；大数据上反超 |

## ViT 变体演进

- **DeiT** — 蒸馏训练，减少数据需求
- **Swin Transformer** — 分层 + 窗口注意力，适合检测/分割
- **MAE** — 掩码自编码器，高效的 self-supervised 预训练
- **DINO / DINOv2** — 自监督 ViT，学习到的特征图包含语义分割信息

## 与具身智能的关系

- ViT 是机器人感知的主流 backbone
- DINOv2 特征广泛用于机器人视觉表示
- 3D ViT 变体用于点云、多视图
- 策略网络常以 ViT 编码图像 → Transformer decoder 输出动作

> 任务分类：[[感知/感知|感知 Perception]] | 回 [[论文/论文|论文阅读]]

## 相关笔记

- [[ACT|ACT]] — Transformer 用于动作预测
- [[Diffusion|Diffusion]] — 扩散模型 + ViT backbone
