---
title: FASTer-LIO PCD倾斜问题排查与解决方案
tags:
  - faster-lio
  - slam
  - mid360
  - pointcloud
  - calibration
  - robot-dog
created: 2026-07-01
aliases:
  - PCD倾斜问题
  - FASTer-LIO重力对齐
  - LiDAR安装角度补偿
project: 多机器狗巡检
---

## 背景

FASTer-LIO 建图输出的 PCD（点云）不在水平坐标系中，而是相对于 IMU 启动时的姿态。当 LiDAR 物理安装倾斜时（如 Livox MID360 装在机器狗上），PCD 天然就是斜的，导致后续 2D 地图投影范围缩小，导航地图截断。

本项目隶属于 [[项目/多机器狗巡检|多机器狗巡检]] 项目。

---

## 根因分析

### PCD 坐标系

FASTer-LIO 的 `PointBodyToWorld` 变换链：

```cpp
p_global = state_point_.rot * (offset_R_L_I * p_body + offset_T_L_I) + state_point_.pos
```

- `state_point_.rot` 在启动时为 **单位阵**（identity）
- `extrinsic_R = identity`（默认配置下 LiDAR 与 IMU 视为同一朝向）

> [!important] 结论
> PCD 的参考坐标系是 **启动时 MID360 内置 IMU 的坐标系**，不是重力对齐的水平坐标系。

### 安装倾斜的影响

MID360 物理安装倾斜 θ°（如绕 Y 轴 18°）：

1. IMU 和 LiDAR 共享同一倾斜（内置 IMU）
2. IMU 测到的重力方向包含倾斜分量
3. 世界坐标系 z 轴 = IMU 启动时 z 轴 ≠ 重力方向
4. PCD 整体偏转 θ°，2D 投影范围缩小 cos(θ) 倍

### 为什么直接修改 EKF 状态无效？

在 IMU 初始化时强制修改 `state_point_.rot`：

```cpp
R_grav = FromTwoVectors(up_dir, (0,0,1));
init_state.rot = R_grav;  // 强制对齐
```

- 初始化时重力对齐正确
- 但后续 EKF 的 LiDAR 扫描匹配逐步更新 `rot`
- 由于 EKF 无显式 z 轴约束，`rot` 随时间漂移回倾斜状态
- PCD 累积后仍有残余倾斜（~7~10°）

> [!warning] 教训
> 修改 EKF 状态变量的方式不可靠，EKF 会在后续迭代中覆盖修改。

---

## 解决方案：自动校平

### 原理

不改动 EKF 状态，在 **保存 PCD 时** 用 IMU 测到的重力方向做一次旋转校平。

### 实现

#### 1. IMU 初始化时存储重力旋转矩阵

在 `imu_processing.hpp` 中添加成员变量：

```cpp
// 公有成员
common::M3D gravity_rotation_;  // IMU朝上 → 世界+z 的旋转矩阵
```

在 `IMUInit()` 中计算：

```cpp
up_dir = mean_acc_.normalized();  // IMU 测到的"上"方向
gravity_rotation_ = Eigen::Quaterniond::FromTwoVectors(
    up_dir, Eigen::Vector3d::UnitZ()).toRotationMatrix();
```

#### 2. 保存 PCD 时应用旋转

在 `laser_mapping.cc` 的 `Finish()` 中：

```cpp
if (!p_imu_->gravity_rotation_.isIdentity(1e-6)) {
    Eigen::Affine3f T = Eigen::Affine3f::Identity();
    T.rotate(p_imu_->gravity_rotation_.cast<float>());
    pcl::transformPointCloud(*pcl_wait_save_, *pcd_to_save, T);
}
```

### 关键设计决策

| 决策 | 理由 |
|------|------|
| 不改 EKF 状态 | 避免干扰 EKF 收敛和定位精度 |
| 只在保存时旋转 | 不影响建图过程中的实时数据 |
| 用 IMU 自动检测倾角 | 无需手动测量安装角度 |
| 双轴校平 | 支持绕 X 和绕 Y 的同时倾斜 |

---

## 效果验证

| 阶段 | 绕 Y 倾斜 | 绕 X 倾斜 |
|------|-----------|-----------|
| 原始 PCD | ~18° | ~3.6° |
| 校平后 | <1° | <1° |

> [!note]
> 剩余 <1° 为 IMU 噪声和地面真实坡度，不影响导航。

---

## 文件改动

```
src/faster-lio/include/imu_processing.hpp  — 新增 gravity_rotation_ 成员 + 计算
src/faster-lio/src/laser_mapping.cc        — Finish() 中应用旋转
```

## 使用流程

```bash
./start_mapping.sh  # 建图
# Ctrl+C 退出，PCD 自动校平

./pcd2pgm.sh        # 转 2D 导航地图
```

## 相关笔记

- [[MID360 安装与配置]]
