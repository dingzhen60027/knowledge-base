#!/usr/bin/env python3
"""Reproduce the diary figures from the bundled, read-only evidence snapshot.

python3 render_figures.py              # No ROS, bag, or robot required
python3 render_figures.py --collect    # Refresh from the original local files
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "evidence"
WS = Path("/home/dndx/d1max_nav_ws")
ROBOT = Path("/home/dndx/智元四足机器人D1 Max二次开发文档资料包v0.1.0/d1max_ros2")
RUN = WS / "maps/runs/20260917_190115_bag_faster_lio_sc_pgo_loop_fix_zenoh"
BASELINE = WS / "maps/runs/20260917_182845_bag_faster_lio_sc_pgo_dual_zenoh"
SYNTHETIC = Path("/tmp/d1max-large-loop-regression-0deo2mjh")
ORANGE, BLUE, INK, MUTED = "#C25A1B", "#2563A6", "#1D2939", "#667085"


def load_poses(path):
    rows = np.loadtxt(path).reshape(-1, 3, 4)
    result = np.tile(np.eye(4), (len(rows), 1, 1))
    result[:, :3, :] = rows
    return result


def transform(points, matrix):
    return points @ matrix[:3, :3].T + matrix[:3, 3]


def collect():
    """Copy only bounded evidence, never the raw bag or complete maps."""
    import open3d as o3d
    import yaml
    DATA.mkdir(exist_ok=True)
    sources = {
        "raw_poses.txt": RUN / "sc_pgo/odom_poses.txt",
        "optimized_poses.txt": RUN / "sc_pgo_final/optimized_poses.txt",
        "times.txt": RUN / "sc_pgo/times.txt",
        "loop_events.csv": RUN / "sc_pgo_final/loop_events.csv",
        "geometry_validation_final.json": RUN / "geometry_validation_final.json",
        "geometry_validation_initial.json": RUN / "geometry_validation_initial.json",
        "baseline_result.json": BASELINE / "result.json",
        "replay_result.json": RUN / "result.json",
        "repair_result.json": RUN / "repair_result.json",
        "pgo_manifest.json": RUN / "sc_pgo_final/manifest.json",
        "pgo_effective_config.yaml": RUN / "sc_pgo_final/effective_config.yaml",
        "faster_lio_config.yaml": RUN / "config/faster_lio_airy96.yaml",
        "synthetic_result.json": SYNTHETIC / "test_result.json",
        "synthetic_raw_poses.txt": SYNTHETIC / "odom_poses.txt",
        "synthetic_optimized_poses.txt": SYNTHETIC / "optimized_poses.txt",
    }
    provenance = []
    for target, source in sources.items():
        shutil.copyfile(source, DATA / target)
        provenance.append({"file": target, "source": str(source),
                           "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    audit = ROBOT / "diagnostics/EXTRINSICS_AUDIT_20260917.md"
    provenance.append({"file": None, "source": str(audit),
                       "sha256": hashlib.sha256(audit.read_bytes()).hexdigest(),
                       "note": "Read for the diary; not copied, device identifiers omitted."})
    metadata = WS / "bags/slam_raw_20260917_171716_fe8f38/metadata.yaml"
    bag = yaml.safe_load(metadata.read_text())["rosbag2_bagfile_information"]
    summary = {"duration_sec": bag["duration"]["nanoseconds"] / 1e9,
               "messages": bag["message_count"],
               "topics": [{"name": t["topic_metadata"]["name"], "count": t["message_count"]}
                          for t in bag["topics_with_message_count"]]}
    (DATA / "bag_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    raw, opt = load_poses(DATA / "raw_poses.txt"), load_poses(DATA / "optimized_poses.txt")
    target = o3d.geometry.PointCloud()
    scan_sources = []
    last = None
    for i in [*range(9), len(raw)-1]:
        source = RUN / f"sc_pgo/Scans/{i:06d}.pcd"
        scan_sources.append({"source": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
        value = o3d.io.read_point_cloud(str(source))
        xyz = np.asarray(value.points)
        keep = np.isfinite(xyz).all(axis=1) & (np.linalg.norm(xyz, axis=1) < 10.)
        value = value.select_by_index(np.flatnonzero(keep)).voxel_down_sample(.10)
        if i < 9:
            value.transform(raw[i])
            target += value
        else:
            last = np.asarray(value.points).copy()
    target = target.voxel_down_sample(.10)
    # Shared source points and shared first-world-frame axes; never level a
    # cloud separately, estimate another correction, or fabricate a surface.
    np.savez_compressed(DATA / "closure_clouds.npz", target=np.asarray(target.points),
                        before=transform(last, raw[-1]), after=transform(last, opt[-1]))
    (DATA / "source_manifest.json").write_text(json.dumps({
        "date": "2026-09-17", "timezone": "Asia/Shanghai", "sources": provenance,
        "cloud_sources": scan_sources,
        "cloud_visualization": "First 9 raw scans + final raw body scan; radius 10 m, voxel 0.10 m. XYZ only; no intensity or device identifiers.",
        "original_data_modified": False,
        "note": "Static evidence snapshot, not a new SLAM replay. No map or bag uploaded."
    }, ensure_ascii=False, indent=2) + "\n")


def style():
    font = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    if font.exists():
        font_manager.fontManager.addfont(str(font))
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=str(font)).get_name()
    plt.rcParams.update({"font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.labelcolor": INK, "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#CBD2DA",
        "axes.unicode_minus": False, "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "grid.color": "#E5E9EF", "grid.linewidth": .7})


def header(fig, title, subtitle):
    fig.text(.075, .96, title, size=19, weight="bold", va="top")
    fig.text(.075, .905, subtitle, size=10.5, color=MUTED, va="top")


def finish(fig, name, note):
    fig.text(.075, .035, note, fontsize=9, color=MUTED, va="bottom")
    fig.savefig(ROOT / name, dpi=180)
    plt.close(fig)


def render():
    style()
    raw, opt = load_poses(DATA / "raw_poses.txt"), load_poses(DATA / "optimized_poses.txt")
    times = np.loadtxt(DATA / "times.txt")
    relative = times - times[0]
    report = json.loads((DATA / "geometry_validation_final.json").read_text())
    assert len(raw) == len(opt) == len(times) == report["keyframes"] == 647
    assert np.all(np.diff(times) > 0) and np.isfinite(raw).all() and np.isfinite(opt).all()
    truth = np.array(report["first_last_submap_match"]["relative_transform"])
    for label, array in [("frontend", raw), ("optimized", opt)]:
        estimate = np.linalg.inv(array[0]) @ array[-1]
        measured = np.linalg.norm((np.linalg.inv(truth) @ estimate)[:3, 3])
        assert abs(measured-report[label]["closure_translation_error_m"]) < 1e-8
    with (DATA / "loop_events.csv").open() as stream:
        accepted = [r for r in csv.DictReader(stream) if r["event"] == "accepted"]
    assert len(accepted) == 6 and any(r["history_keyframe"] == "0" and r["current_keyframe"] == "642" for r in accepted)

    fig, ax = plt.subplots(figsize=(12, 6.5))
    fig.subplots_adjust(left=.09, right=.94, bottom=.19, top=.79)
    header(fig, "01  同一批关键帧的高度轨迹", "647 帧 · 979.0 秒传感器时间跨度 · 原始 Faster-LIO 与最终 SC-PGO 位姿")
    for array, color, label, line in [(raw, ORANGE, "Faster-LIO 前端", "--"), (opt, BLUE, "SC-PGO 优化后", "-")]:
        z = array[:, 2, 3]-array[0, 2, 3]
        ax.plot(relative, z, color=color, label=label, lw=2, ls=line)
        ax.plot(relative[-1], z[-1], "o", color=color, ms=6)
        ax.annotate(f"末端 {z[-1]:+.3f} m", (relative[-1], z[-1]), xytext=(-115, 14 if color==BLUE else -20), textcoords="offset points", color=color, weight="bold")
    ax.axhline(0, color="#98A2B3", lw=1)
    ax.set(xlabel="距首个关键帧的时间 / s", ylabel="相对首帧高度 / m", xlim=(0, relative[-1]+18), ylim=(-4.8, 1.8))
    ax.set_xticks([0,200,400,600,800,979]); ax.grid(axis="y")
    ax.legend(loc="lower left", frameon=False)
    finish(fig, "01-height-profile.png", "优化曲线是回环后的整条历史轨迹，不是在线修正延迟曲线。高度不是误差真值，也不假定沿途完全水平。")

    clouds = np.load(DATA / "closure_clouds.npz")
    fig, axes = plt.subplots(1, 2, figsize=(12, 7), sharex=True, sharey=True)
    fig.subplots_adjust(left=.08, right=.97, bottom=.21, top=.78, wspace=.12)
    header(fig, "02  起点子图与最后一帧点云", "相同原始点集、相同坐标轴、相同尺度；只替换最后一帧使用的位姿")
    for ax, key, title in zip(axes, ["before", "after"], ["前端位姿：两组点云高度错开", "优化位姿：回到同一高度区域"]):
        for points, color, marker, label in [(clouds["target"], BLUE, ".", "起点前 9 帧子图"), (clouds[key], ORANGE, "+", "最后一帧扫描")]:
            # A fixed world-X slab suppresses unrelated side rooms. The same
            # world ROI and display scale are used in both views.
            mask = (np.abs(points[:,0]) < 3) & (np.abs(points[:,1]) < 8) & (points[:,2]>-6.5) & (points[:,2]<3.5)
            p = points[mask]
            ax.scatter(p[:,1], p[:,2], s=1.8, color=color, marker=marker, alpha=.38, linewidths=.3, rasterized=True, label=label)
        ax.set(title=title, xlabel="世界坐标 Y / m", xlim=(-8,8), ylim=(-6.5,3.5))
        ax.set_aspect("equal", adjustable="box")
        ax.grid(alpha=.5)
    axes[0].set_ylabel("世界坐标 Z / m")
    handles, labels=axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(.5,.085), ncol=2, frameon=False, markerscale=5)
    finish(fig, "02-loop-clouds.png", "局部 Y–Z 投影，裁剪 |X| < 3 m；展示前后真实几何，不是 RViz 截图或整张地图精度证明。")

    floors = report["sampled_floor_tilt"]
    fig, ax = plt.subplots(figsize=(12, 6.4))
    fig.subplots_adjust(left=.09,right=.97,bottom=.21,top=.79)
    header(fig, "03  地面法向的抽样倾角", "10 个关键帧样本 · 同一局部点云法向分别使用两组位姿变换到世界坐标")
    x = np.arange(len(floors)); width=.34
    a=np.array([r["frontend_floor_tilt_deg"] for r in floors]); b=np.array([r["optimized_floor_tilt_deg"] for r in floors])
    ax.bar(x-width/2,a,width,color=ORANGE,label="Faster-LIO 前端",hatch="//",edgecolor="white",linewidth=.5)
    ax.bar(x+width/2,b,width,color=BLUE,label="SC-PGO 优化后")
    for positions, values, color in [(x-width/2,a,ORANGE),(x+width/2,b,BLUE)]:
        for pos,val in zip(positions,values): ax.text(pos,val+.06,f"{val:.2f}",ha="center",fontsize=8.5,color=color)
    ax.set_xticks(x, [str(r["keyframe"]) for r in floors]); ax.set(xlabel="关键帧编号",ylabel="相对世界 Z 轴的倾角 / °",ylim=(0,3.5))
    ax.set_axisbelow(True); ax.grid(axis="y"); ax.legend(frameon=False,loc="upper left",ncol=2)
    finish(fig, "03-floor-tilt.png", "这是局部平面抽样，不是全地图地面或测量基准。改善并不处处单调，仍有约 1–2° 的局部残余倾角。")

    a=load_poses(DATA/"synthetic_raw_poses.txt"); b=load_poses(DATA/"synthetic_optimized_poses.txt")
    sample=np.arange(len(a)); height=1.2*np.sin(np.pi*sample/(len(a)-1))
    test=json.loads((DATA/"synthetic_result.json").read_text())
    assert len(a)==len(b)==97 and test["passed"]
    fig, ax = plt.subplots(figsize=(12,6.4))
    fig.subplots_adjust(left=.09,right=.96,bottom=.19,top=.79)
    header(fig,"04  合成测试：真实高度变化是否被保留", "含地面的室内几何 · 注入 4.6 m 下沉与水平/航向漂移；本图不是实机测量")
    ax.plot(sample,height,color=INK,lw=1.8,ls=":",label="设定真实高度（峰值 1.20 m）")
    ax.plot(sample,a[:,2,3],color=ORANGE,lw=2,ls="--",label="注入漂移后的里程计")
    ax.plot(sample,b[:,2,3],color=BLUE,lw=2,label=f"优化后（峰值 {test['retained_height_peak_m']:.2f} m）")
    ax.set(xlabel="合成关键帧编号",ylabel="高度 / m",xlim=(0,96),ylim=(-5,1.8))
    ax.set_xticks([0,24,48,72,96]); ax.grid(axis="y"); ax.legend(frameon=False,loc="lower left")
    finish(fig,"04-synthetic-height.png", "三维首尾位置误差 0.263 m；只证明该合成场景未被压平，不等于多楼层或退化场景已验收。")
    print(json.dumps({"figures":4,"keyframes":len(raw),"accepted_constraints":len(accepted),
                      "closure_error_m":report["optimized"]["closure_translation_error_m"],
                      "source_checks":"passed"},indent=2))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect", action="store_true")
    args=parser.parse_args()
    if args.collect: collect()
    render()
