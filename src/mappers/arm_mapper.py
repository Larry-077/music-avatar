"""
ArmMapper - 手臂运动映射系统
================================
将音调映射到手臂的抬起和弯曲动作。

映射逻辑:
- 高音调 → 手臂上扬，手肘伸直
- 低音调 → 手臂下垂,手肘弯曲
- 使用平滑插值实现自然过渡
"""

import numpy as np


class ArmMapper:
    """
    将音乐音调映射到手臂的旋转和弯曲动作。
    """
    
    def __init__(self,
                 arm_rotation_range=90,      # 手臂旋转范围(度)，从基准位置的±范围
                 elbow_bend_range=45,        # 手肘弯曲范围(度)
                 smoothing=0.12,             # 平滑系数 (0-1)
                 pitch_min=50,               # 最低音调频率 (Hz)
                 pitch_max=500,              # 最高音调频率 (Hz)
                 base_arm_angle=45,          # 手臂基准角度(度)
                 base_elbow_angle=-15):      # 手肘基准角度(度)
        """
        初始化 ArmMapper。
        
        Args:
            arm_rotation_range: 手臂从基准位置可旋转的最大角度范围
            elbow_bend_range: 手肘弯曲的角度范围
            smoothing: 平滑系数。0 = 非常平滑(慢), 1 = 无平滑(瞬时)
            pitch_min: 映射的最低音调值
            pitch_max: 映射的最高音调值
            base_arm_angle: 手臂的中性/基准角度
            base_elbow_angle: 手肘的基准角度
        """
        self.arm_rotation_range = arm_rotation_range
        self.elbow_bend_range = elbow_bend_range
        self.smoothing = smoothing
        self.pitch_min = pitch_min
        self.pitch_max = pitch_max
        self.base_arm_angle = base_arm_angle
        self.base_elbow_angle = base_elbow_angle
        
        # 状态跟踪 - 左臂
        self.current_left_arm_angle = base_arm_angle
        self.target_left_arm_angle = base_arm_angle
        self.current_left_elbow_angle = base_elbow_angle
        self.target_left_elbow_angle = base_elbow_angle
        
        # 状态跟踪 - 右臂
        self.current_right_arm_angle = base_arm_angle
        self.target_right_arm_angle = base_arm_angle
        self.current_right_elbow_angle = base_elbow_angle
        self.target_right_elbow_angle = base_elbow_angle
        
        # 采样率(运行时计算)
        self.sample_rate = None
        
        # 调试模式
        self.debug = False
        
        # 左右手是否镜像(默认镜像,使动作对称)
        self.mirror_arms = True
    
    def _normalize_pitch(self, pitch):
        """
        将音调归一化到 0.0-1.0 范围。
        
        Args:
            pitch: 原始音调值 (Hz)
            
        Returns:
            归一化的音调 (0.0 = 低, 1.0 = 高)
        """
        if pitch == 0:
            # 静音或未检测到音调
            return 0.5  # 中性点
        
        # 限制到 [pitch_min, pitch_max]
        pitch = max(self.pitch_min, min(self.pitch_max, pitch))
        
        # 归一化到 [0, 1]
        normalized = (pitch - self.pitch_min) / (self.pitch_max - self.pitch_min)
        return normalized
    
    def _get_pitch_at_time(self, pitch_data, current_time, duration):
        """
        获取当前播放时间对应的音调值。
        
        Args:
            pitch_data: 音调数据数组
            current_time: 当前播放时间 (秒)
            duration: 音频总时长 (秒)
            
        Returns:
            该时刻的音调值 (Hz)
        """
        if not pitch_data or len(pitch_data) == 0:
            return 0
        
        # 计算采样率(仅一次)
        if self.sample_rate is None:
            self.sample_rate = len(pitch_data) / duration
            if self.debug:
                print(f"🎵 Arm mapper pitch sample rate: {self.sample_rate:.2f} Hz")
        
        frame_index = int(current_time * self.sample_rate)
        frame_index = max(0, min(len(pitch_data) - 1, frame_index))
        
        return pitch_data[frame_index]
    
    def _calculate_target_angles(self, normalized_pitch):
        """
        根据归一化的音调计算目标手臂和手肘角度。
        
        映射策略:
        - normalized_pitch = 0.0 (低音): 手臂下垂,手肘弯曲
        - normalized_pitch = 0.5 (中音): 基准姿势
        - normalized_pitch = 1.0 (高音): 手臂上扬,手肘伸直
        
        Args:
            normalized_pitch: 归一化的音调 (0.0-1.0)
            
        Returns:
            (target_arm_angle, target_elbow_angle) 元组
        """
        # 手臂旋转: 低音→下垂, 高音→上扬
        # 映射 [0, 1] → [base - range, base + range]
        arm_angle = self.base_arm_angle + (normalized_pitch - 0.5) * 2 * self.arm_rotation_range
        
        # 手肘弯曲: 使用更复杂的映射以实现自然效果
        # 低音时弯曲更多,高音时伸直
        # 使用二次曲线使中间区域更平缓
        elbow_factor = 1.0 - normalized_pitch  # 1.0=低音(弯曲), 0.0=高音(伸直)
        elbow_factor = elbow_factor ** 1.5  # 应用幂次使曲线更自然
        elbow_angle = self.base_elbow_angle - elbow_factor * self.elbow_bend_range
        
        return arm_angle, elbow_angle
    
    def _smooth_angles(self, dt):
        """
        平滑地将当前角度插值到目标角度。
        
        Args:
            dt: 时间增量 (秒)
        """
        # 归一化到 ~60 FPS
        t = min(1.0, self.smoothing * dt * 60)
        
        # 左臂平滑
        self.current_left_arm_angle += (self.target_left_arm_angle - self.current_left_arm_angle) * t
        self.current_left_elbow_angle += (self.target_left_elbow_angle - self.current_left_elbow_angle) * t
        
        # 右臂平滑
        self.current_right_arm_angle += (self.target_right_arm_angle - self.current_right_arm_angle) * t
        self.current_right_elbow_angle += (self.target_right_elbow_angle - self.current_right_elbow_angle) * t
    
    def map(self, music_features, character_rig, current_time, dt=0.016):
        """
        将音调数据映射到手臂动作。
        
        Args:
            music_features: 包含 'pitch' 数组和 'duration_seconds' 的音乐分析数据
            character_rig: CharacterRig 实例
            current_time: 当前播放时间 (秒)
            dt: 帧时间步长 (默认 1/60 秒)
        """
        pitch_data = music_features.get('pitch', [])
        duration = music_features.get('duration_seconds', 0)
        
        if not pitch_data or duration == 0:
            if self.debug:
                print("⚠️  No pitch data found for arm mapping")
            return
        
        # 1️⃣ 获取当前播放时间的音调值
        current_pitch = self._get_pitch_at_time(pitch_data, current_time, duration)
        
        # 2️⃣ 归一化音调 (Hz → [0,1])
        normalized_pitch = self._normalize_pitch(current_pitch)
        
        # 3️⃣ 计算目标角度
        target_arm_angle, target_elbow_angle = self._calculate_target_angles(normalized_pitch)
        
        # 4️⃣ 设置目标角度(考虑镜像)
        self.target_left_arm_angle = target_arm_angle
        self.target_left_elbow_angle = target_elbow_angle
        
        if self.mirror_arms:
            # 镜像: 右臂使用相同的角度
            self.target_right_arm_angle = target_arm_angle
            self.target_right_elbow_angle = target_elbow_angle
        else:
            # 非镜像: 可以设置不同的映射逻辑
            self.target_right_arm_angle = target_arm_angle
            self.target_right_elbow_angle = target_elbow_angle
        
        # 5️⃣ 平滑过渡
        self._smooth_angles(dt)
        
        # 6️⃣ 应用到角色骨骼
        self._apply_to_character(character_rig)
        
        if self.debug and int(current_time * 10) % 10 == 0:  # 每秒打印一次
            print(f"🎵 Pitch: {current_pitch:.1f}Hz | "
                  f"Normalized: {normalized_pitch:.2f} | "
                  f"Arm: {self.current_left_arm_angle:.1f}° | "
                  f"Elbow: {self.current_left_elbow_angle:.1f}°")
    
    def _apply_to_character(self, character_rig):
        """
        将计算的角度应用到角色的骨骼系统。
        
        Args:
            character_rig: CharacterRig 实例
        """
        # 查找骨骼(骨骼名称可能需要根据实际情况调整)
        # 假设骨骼结构: LeftUpperArm, LeftElbow, RightUpperArm, RightElbow
        
        # 左臂
        left_upper_arm = character_rig.root.find_bone("LeftUpperArm")
        if left_upper_arm:
            left_upper_arm.set_rotation(self.current_left_arm_angle)
        
        left_elbow = character_rig.root.find_bone("LeftElbow")
        if left_elbow:
            left_elbow.set_rotation(self.current_left_elbow_angle)
        
        # 右臂
        right_upper_arm = character_rig.root.find_bone("RightUpperArm")
        if right_upper_arm:
            # 右臂可能需要镜像旋转(取决于骨骼设置)
            right_upper_arm.set_rotation(-self.current_right_arm_angle)
        
        right_elbow = character_rig.root.find_bone("RightElbow")
        if right_elbow:
            right_elbow.set_rotation(self.current_right_elbow_angle)
    
    def reset(self):
        """重置映射器状态。"""
        self.current_left_arm_angle = self.base_arm_angle
        self.target_left_arm_angle = self.base_arm_angle
        self.current_left_elbow_angle = self.base_elbow_angle
        self.target_left_elbow_angle = self.base_elbow_angle
        
        self.current_right_arm_angle = self.base_arm_angle
        self.target_right_arm_angle = self.base_arm_angle
        self.current_right_elbow_angle = self.base_elbow_angle
        self.target_right_elbow_angle = self.base_elbow_angle
        
        self.sample_rate = None
    
    def set_parameters(self, arm_rotation_range=None, elbow_bend_range=None,
                       smoothing=None, pitch_min=None, pitch_max=None,
                       base_arm_angle=None, base_elbow_angle=None, mirror_arms=None):
        """
        动态更新映射器参数。
        
        Args:
            arm_rotation_range: 新的手臂旋转范围
            elbow_bend_range: 新的手肘弯曲范围
            smoothing: 新的平滑系数
            pitch_min: 新的最低音调
            pitch_max: 新的最高音调
            base_arm_angle: 新的基准手臂角度
            base_elbow_angle: 新的基准手肘角度
            mirror_arms: 是否镜像左右手
        """
        if arm_rotation_range is not None:
            self.arm_rotation_range = max(0, arm_rotation_range)
        
        if elbow_bend_range is not None:
            self.elbow_bend_range = max(0, elbow_bend_range)
        
        if smoothing is not None:
            self.smoothing = max(0.01, min(1.0, smoothing))
        
        if pitch_min is not None:
            self.pitch_min = pitch_min
        
        if pitch_max is not None:
            self.pitch_max = pitch_max
        
        if base_arm_angle is not None:
            self.base_arm_angle = base_arm_angle
        
        if base_elbow_angle is not None:
            self.base_elbow_angle = base_elbow_angle
        
        if mirror_arms is not None:
            self.mirror_arms = mirror_arms
        
        if self.debug:
            print(f"🔧 ArmMapper parameters updated:")
            print(f"   Arm rotation range: ±{self.arm_rotation_range}°")
            print(f"   Elbow bend range: {self.elbow_bend_range}°")
            print(f"   Smoothing: {self.smoothing:.2f}")
            print(f"   Pitch range: {self.pitch_min}-{self.pitch_max}Hz")
            print(f"   Base angles: arm={self.base_arm_angle}°, elbow={self.base_elbow_angle}°")
            print(f"   Mirror arms: {self.mirror_arms}")


# --- 测试代码 ---
if __name__ == "__main__":
    """
    测试 ArmMapper 的音调到手臂动作映射。
    """
    print("=" * 60)
    print("ArmMapper Test")
    print("=" * 60)
    
    mapper = ArmMapper(
        arm_rotation_range=90,
        elbow_bend_range=45,
        smoothing=0.12,
        pitch_min=100,
        pitch_max=400,
        base_arm_angle=45,
        base_elbow_angle=-15
    )
    mapper.debug = True
    
    # 模拟音乐数据: 音调从低到高再到低
    import math
    fake_music = {
        'pitch': [100 + 150 * (0.5 + 0.5 * math.sin(i * 0.05)) for i in range(200)],
        'duration_seconds': 6.0
    }
    
    # 模拟角色骨架
    class FakeBone:
        def __init__(self, name):
            self.name = name
            self.rotation = 0
        
        def set_rotation(self, angle):
            self.rotation = angle
        
        def find_bone(self, name):
            if self.name == name:
                return self
            return None
    
    class FakeRig:
        def __init__(self):
            self.root = FakeBone("Root")
            self.left_arm = FakeBone("LeftUpperArm")
            self.left_elbow = FakeBone("LeftElbow")
            self.right_arm = FakeBone("RightUpperArm")
            self.right_elbow = FakeBone("RightElbow")
            
            # 让 root 能找到所有骨骼
            self.root.find_bone = lambda name: {
                "LeftUpperArm": self.left_arm,
                "LeftElbow": self.left_elbow,
                "RightUpperArm": self.right_arm,
                "RightElbow": self.right_elbow
            }.get(name)
        
        def print_status(self):
            print(f"    → Left Arm: {self.left_arm.rotation:.1f}°, Elbow: {self.left_elbow.rotation:.1f}°")
            print(f"    → Right Arm: {self.right_arm.rotation:.1f}°, Elbow: {self.right_elbow.rotation:.1f}°")
    
    fake_rig = FakeRig()
    
    print("\n🎵 模拟音乐播放,音调变化驱动手臂运动...\n")
    
    dt = 0.016  # 60 FPS
    current_time = 0.0
    max_time = 6.0
    
    frame = 0
    while current_time < max_time:
        if frame % 60 == 0:  # 每秒打印一次
            print(f"\n--- Time: {current_time:.2f}s ---")
            mapper.map(fake_music, fake_rig, current_time, dt)
            fake_rig.print_status()
        else:
            mapper.map(fake_music, fake_rig, current_time, dt)
        
        current_time += dt
        frame += 1
    
    print("\n✅ Test complete!")
    print(f"   Final left arm angle: {mapper.current_left_arm_angle:.1f}°")
    print(f"   Final left elbow angle: {mapper.current_left_elbow_angle:.1f}°")
