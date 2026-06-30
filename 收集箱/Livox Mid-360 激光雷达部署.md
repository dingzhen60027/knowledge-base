---
title: Livox Mid-360 激光雷达部署
tags:
  - ros2
  - lidar
  - livox
  - mid360
  - slam
aliases:
  - Mid-360 部署
  - Livox ROS Driver 2
status: active
---

# Livox Mid-360 激光雷达部署

> 机器狗项目环境：ROS2 Humble (Ubuntu 22.04) + Cyclone DDS + 交换机组网

## 硬件连接

```
Mid-360 雷达 --(网线)--> 交换机 <--(网线)--> PC (192.168.123.222)
```

- 雷达 IP：`192.168.123.20`（SN 码推算得出）
- 电脑 IP：`192.168.123.222`（手动配置静态 IP）
- 电脑与雷达处于同一网段（`192.168.123.x`），通过交换机直连

> [!warning] 关键
> 电脑必须设置为静态 IP，且与雷达在同一网段。Livox 雷达不支持 DHCP。

## 一、Livox-SDK2 安装

```bash
git clone https://github.com/Livox-SDK/Livox-SDK2.git
cd ./Livox-SDK2/
mkdir build && cd build
cmake .. && make
sudo make install
```

安装位置：
- 动态库：`/usr/local/lib/liblivox_lidar_sdk_shared.so`
- 头文件：`/usr/local/include/livox_lidar_*.h`
- CMake 配置：`/usr/local/lib/cmake/livox_lidar_sdk/`

## 二、livox_ros_driver2 编译

```bash
git clone https://github.com/Livox-SDK/livox_ros_driver2.git ws_livox/src/livox_ros_driver2
cd ws_livox/src/livox_ros_driver2
./build.sh humble    # ROS2 Humble (本机环境)
# 或
./build.sh jazzy     # ROS2 Jazzy
```

## 三、IP 配置（关键）

驱动加载的 JSON 配置文件位于：
`ws_livox/src/livox_ros_driver2/config/MID360_config.json`

### 配置示例（非默认网段场景）

```json
{
  "lidar_summary_info": {
    "lidar_type": 8
  },
  "MID360": {
    "lidar_net_info": {
      "cmd_data_port": 56100,
      "push_msg_port": 56200,
      "point_data_port": 56300,
      "imu_data_port": 56400,
      "log_data_port": 56500
    },
    "host_net_info": {
      "cmd_data_ip": "192.168.123.222",
      "cmd_data_port": 56101,
      "push_msg_ip": "192.168.123.222",
      "push_msg_port": 56201,
      "point_data_ip": "192.168.123.222",
      "point_data_port": 56301,
      "imu_data_ip": "192.168.123.222",
      "imu_data_port": 56401,
      "log_data_ip": "",
      "log_data_port": 56501
    }
  },
  "lidar_configs": [
    {
      "ip": "192.168.123.20",
      "pcl_data_type": 1,
      "pattern_mode": 0,
      "extrinsic_parameter": {
        "roll": 0.0, "pitch": 0.0, "yaw": 0.0,
        "x": 0, "y": 0, "z": 0
      }
    }
  ]
}
```

> [!danger] 容易踩坑的地方
> `host_net_info` 中所有 IP 必须改为**电脑的实际 IP**（默认是 `192.168.1.5`）。如果忘记改，雷达会把点云数据发给不存在的地址，驱动显示 `Init lds lidar success` 但永远收不到数据。

### 检查通信

```bash
ping 192.168.123.20
```

能 ping 通说明物理层和 IP 配置没问题。

## 四、链接库问题

运行驱动时若遇到：

```
Could not load library: liblivox_lidar_sdk_shared.so: cannot open shared object file
```

原因是 SDK2 安装到了 `/usr/local/lib` 但系统缓存未更新。解决：

```bash
sudo ldconfig
```

无需重新编译，直接重新 launch 即可。

## 五、RMW 中间件配置（Zenoh → Cyclone DDS）

本机默认 RMW 是 Zenoh（`rmw_zenoh_cpp`），它需要启动 Zenoh Router 才能让节点间通信。Livox 驱动 + RViz2 本地调试的场景，切换为 Cyclone DDS 更直接。

### 永久切换

```bash
echo 'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp' >> ~/.bashrc
source ~/.bashrc
```

### Cyclone DDS 调优（Mid-360 大流量场景）

Mid-360 点云和 IMU 数据量大，需增大系统 UDP 接收缓冲区：

```bash
sudo sysctl -w net.core.rmem_max=8388608
sudo sysctl -w net.core.rmem_default=8388608
```

如需重启后保持生效，写入 `/etc/sysctl.conf`。

## 六、启动与验证

### 启动驱动 + RViz

```bash
ros2 launch livox_ros_driver2 rviz_MID360_launch.py
```

### 关键日志

正常启动应看到：

```
Init lds lidar success!
successfully set data type
successfully set pattern mode
successfully change work mode, handle: xxx
successfully enable Livox Lidar imu
livox/imu publish use imu format
livox/lidar publish use PointCloud2 format
```

### RViz 显示设置

启动后如果 RViz 黑屏，做两步：
1. **Fixed Frame** → 改为 `livox_frame`
2. **Add → /livox/lidar → PointCloud2** 添加点云话题

### 终端验证

```bash
ros2 topic echo /livox/lidar --matrix
ros2 topic hz /livox/lidar
```

应看到 10Hz/20Hz 的数据输出。

## 七、pcl_data_type 说明

| 值 | 格式 | 适用场景 |
|----|------|---------|
| 0 | ROS2 PointCloud2 标准格式 | 通用可视化、常规 ROS2 应用 |
| 1 | Livox 自定义格式 | FAST-LIO 等 SLAM 算法 |
| 2 | PCL 标准格式 | PCL 处理流程 |

## 八、Quick Start Checklist

- [ ] 电脑静态 IP 已配置（`192.168.123.x`）
- [ ] `ping 雷达IP` 能通
- [ ] `MID360_config.json` 中 `host_net_info` 的 IP 已改为电脑实际 IP
- [ ] `sudo ldconfig` 已执行
- [ ] `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` 已设置
- [ ] UDP 接收缓冲区已调大
- [ ] RViz Fixed Frame 设为 `livox_frame`

## 相关笔记

- [[多机器狗巡检]] — 项目总览
