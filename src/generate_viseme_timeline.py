"""
Generate 30-second Viseme Timeline
生成 30 秒的音素时间线（用于口型动画测试）
"""

import json
import random

# 可用的音素列表（对应你的 mouth 图片）
VISEME_SET = ["Sil", "A", "D", "E", "F", "L", "M", "O", "R", "S", "U", "W"]

# 音素出现的频率权重（模拟自然说话）
VISEME_WEIGHTS = {
    "Sil": 0.15,  # 安静/停顿
    "A": 0.12,    # 啊
    "E": 0.10,    # 诶
    "O": 0.10,    # 哦
    "M": 0.08,    # 嗯（闭嘴）
    "L": 0.08,    # L 音
    "D": 0.07,    # D 音
    "S": 0.07,    # S 音
    "R": 0.06,    # R 音
    "W": 0.06,    # W 音（撅嘴）
    "U": 0.06,    # U 音
    "F": 0.05,    # F 音
}

def generate_viseme_timeline(duration_seconds=30, fps=24):
    """
    生成模拟说话的 viseme timeline
    
    Args:
        duration_seconds: 总时长（秒）
        fps: 帧率
        
    Returns:
        list of segments: [{"viseme": "A", "start": 0.0, "end": 0.2, "scale": 1.0}, ...]
    """
    timeline = []
    current_time = 0.0
    frame_duration = 1.0 / fps
    
    # 创建不同的说话模式
    patterns = [
        # 1. 快速说话（0-10秒）
        {"min_duration": 0.08, "max_duration": 0.25, "scale_range": (0.95, 1.1)},
        # 2. 正常说话（10-20秒）
        {"min_duration": 0.12, "max_duration": 0.35, "scale_range": (0.9, 1.15)},
        # 3. 慢速/强调（20-30秒）
        {"min_duration": 0.15, "max_duration": 0.5, "scale_range": (0.85, 1.25)},
    ]
    
    while current_time < duration_seconds:
        # 选择当前的说话模式
        if current_time < 10:
            pattern = patterns[0]
        elif current_time < 20:
            pattern = patterns[1]
        else:
            pattern = patterns[2]
        
        # 随机选择音素（基于权重）
        viseme = random.choices(
            list(VISEME_WEIGHTS.keys()),
            weights=list(VISEME_WEIGHTS.values()),
            k=1
        )[0]
        
        # 随机持续时间
        duration = random.uniform(pattern["min_duration"], pattern["max_duration"])
        
        # 随机缩放（用于音量/强度变化）
        scale = random.uniform(*pattern["scale_range"])
        
        # 对齐到帧边界
        duration = round(duration / frame_duration) * frame_duration
        end_time = current_time + duration
        
        # 确保不超过总时长
        if end_time > duration_seconds:
            end_time = duration_seconds
            duration = end_time - current_time
        
        # 添加片段
        segment = {
            "viseme": viseme,
            "start": round(current_time, 3),
            "end": round(end_time, 3),
            "scale": round(scale, 2)
        }
        timeline.append(segment)
        
        current_time = end_time
    
    return timeline


def add_emphasis_moments(timeline):
    """
    在时间线中添加强调时刻（大嘴型、长持续时间）
    """
    # 在特定时刻添加强调
    emphasis_times = [5.0, 12.0, 18.0, 25.0]  # 强调的时间点
    emphasis_visemes = ["A", "O", "E"]  # 强调用的大嘴型
    
    for emph_time in emphasis_times:
        # 找到最接近的片段
        for i, seg in enumerate(timeline):
            if seg["start"] <= emph_time < seg["end"]:
                # 替换为强调音素
                viseme = random.choice(emphasis_visemes)
                timeline[i]["viseme"] = viseme
                timeline[i]["scale"] = random.uniform(1.2, 1.4)  # 更大的缩放
                break
    
    return timeline


def save_timeline(timeline, filename):
    """保存 timeline 到 JSON 文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved timeline to: {filename}")
    print(f"   Total segments: {len(timeline)}")
    print(f"   Duration: {timeline[-1]['end']:.2f} seconds")
    
    # 统计音素分布
    viseme_counts = {}
    for seg in timeline:
        v = seg["viseme"]
        viseme_counts[v] = viseme_counts.get(v, 0) + 1
    
    print(f"\n📊 Viseme distribution:")
    for v, count in sorted(viseme_counts.items(), key=lambda x: -x[1]):
        print(f"   {v:3s}: {count:3d} times")


if __name__ == "__main__":
    print("=" * 60)
    print("Generating 30-second Viseme Timeline")
    print("=" * 60)
    
    # 设置随机种子以获得可重复的结果（可选）
    random.seed(42)
    
    # 生成 30 秒的时间线
    timeline = generate_viseme_timeline(duration_seconds=30, fps=24)
    
    # 添加强调时刻
    timeline = add_emphasis_moments(timeline)
    
    # 保存到文件
    output_file = "viseme_timeline_30s.json"
    save_timeline(timeline, output_file)
    
    print("\n" + "=" * 60)
    print("✅ Generation complete!")
    print("=" * 60)
    
    # 显示前几个片段作为示例
    print("\n📋 First 10 segments:")
    for i, seg in enumerate(timeline[:10]):
        print(f"   {i+1:2d}. {seg['start']:5.2f}s - {seg['end']:5.2f}s: "
              f"{seg['viseme']:3s} (scale={seg['scale']:.2f})")