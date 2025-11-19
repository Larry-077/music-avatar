"""
Animation Effectors
===================
Classes that take a 0.0-1.0 input and drive CharacterRig properties.
"""
import math
import time
import random

# --- Base Class ---
class Effector:
    def update(self, value, character):
        pass

# --- 1. Continuous Effectors (Input: 0.0 - 1.0) ---

# src/engine/effectors.py

class ArmDancer(Effector):
    """Controls arm elevation and hand sprites based on intensity."""
    def __init__(self, smoothing=0.1):
        self.current_shoulder = 0.0
        self.current_elbow = 0.0
        self.smoothing = smoothing # 建议设为 0.1 - 0.15，太大会导致动作迟缓
        
        # ==========================================
        # 1. 同步你的默认位置 (Base Offsets)
        # 这里必须填你在 CharacterRig 里调好的 rotation 数值
        # ==========================================
        self.base_shoulder = 30.0   # 对应你代码里的 rotation=30
        self.base_elbow = 10.0      # 对应你代码里的 rotation=10
        
        # ==========================================
        # 2. 增大运动幅度 (Range)
        # 这些值决定了音乐最强(1.0)时，胳膊会转动多少度
        # ==========================================
        # 肩膀：从 30度 再往上抬 100度 -> 达到 130度 (高举)
        self.range_shoulder = 100.0  
        
        # 肘部：从 10度 再弯曲 80度 -> 达到 90度 (大臂带动小臂弯曲)
        # 如果你觉得小臂动得太僵硬，可以增加这个值
        self.range_elbow = 80.0    

    def update(self, value, character):
        # value 是 0.0 到 1.0 的输入信号
        
        # ==========================================
        # 3. 优化联动逻辑 (Non-linear Mapping)
        # 让小臂的反应比大臂稍微“滞后”或“非线性”一点，看起来更自然
        # ==========================================
        
        # 目标角度计算
        target_shoulder = self.base_shoulder + (value * self.range_shoulder)
        
        # 小技巧：让肘部弯曲得更明显一点，可以使用 value 的平方或开方，或者直接线性
        # 这里我们用线性，但是给一个基础倍率
        target_elbow = self.base_elbow + (value * self.range_elbow)
        
        # 4. 手部 Sprite 切换逻辑 (阈值微调)
        hand_variant = "rest"
        if value > 0.85: hand_variant = "high" # 只有非常强时才用 high
        elif value > 0.4: hand_variant = "open"
        elif value > 0.1: hand_variant = "curl"
        
        # 5. 平滑插值 (Lerp)
        # 这种写法保证了动作不会瞬移，而是平滑过渡
        self.current_shoulder += (target_shoulder - self.current_shoulder) * self.smoothing
        self.current_elbow += (target_elbow - self.current_elbow) * self.smoothing
        
        # 6. 应用到角色 (注意正负号)
        
        # 左臂 (Left Arm)
        # 你的Rig里左臂是正数 (rotation=30)，所以这里用正数
        character.set_arm_joint_rotation("left", self.current_shoulder, self.current_elbow)
        character.set_hand_variant("left", f"L_hand_{hand_variant}")
        
        # 右臂 (Right Arm)
        # 你的Rig里右臂是负数 (rotation=-30)，所以这里取反 (-self.current_shoulder)
        # 这样就能保证完全对称
        character.set_arm_joint_rotation("right", -self.current_shoulder, -self.current_elbow)
        character.set_hand_variant("right", f"R_hand_{hand_variant}")

class BodyPumper(Effector):
    """Scales the body size based on intensity."""
    def __init__(self, min_scale=0.95, max_scale=1.55):
        self.min_s = min_scale
        self.max_s = max_scale
        self.smoothing = 0.03 
        self.current_val = 0.0
        
    def update(self, value, character):
        if value < 0.1: value = 0.0
        self.current_val += (value - self.current_val) * self.smoothing
        scale = self.min_s + (self.max_s - self.min_s) * self.current_val
        character.set_body_scale(scale)

class Floater(Effector):
    """Levitates the character vertically."""
    def __init__(self, max_offset=200):
        self.max_offset = max_offset
        self.smoothing = 0.02
        self.current_val = 0.0
        self.base_y = None 
        self.idle_time = 0.0
        
    def update(self, value, character):
        current_x, current_y = character.root.local_transform.position
        if self.base_y is None:
            self.base_y = current_y
            
        self.current_val += (value - self.current_val) * self.smoothing
        music_offset = self.current_val * self.max_offset
        self.idle_time += 0.02 # 速度
        idle_offset = math.sin(self.idle_time) * 5
        target_y = self.base_y - music_offset + idle_offset
        
        character.set_screen_position(current_x, target_y)

class FaceExpression(Effector):
    """
    Controls facial features: Eyebrows height, Mouth scale.
    (Smoother & More Exaggerated Version)
    """
    def __init__(self):
        self.current_brow_offset = 0.0
        self.current_scale = 1.0
        
        # 🔧 [调整 1] 极慢的平滑度 (0.05)，过滤掉高频抖动
        self.smoothing = 0.05
        
        # 🔧 [调整 2] 更大的幅度
        self.max_brow_raise = -60.0  # 眉毛最高飞起 45px (非常夸张)
        self.max_mouth_scale = 3  # 嘴巴最大放大 1.6倍

    def update(self, value, character):
        if value < 0.05: 
            value = 0.0
        else:
            # 让 value 从 0.05 起步重新归一化
            value = (value - 0.05) / 0.95
            
        # 2. 🔧 [核心修改] 信号放大 (Pre-Gain)
        # 因为古典乐通常 value 只有 0.2 左右，我们先把它乘大
        # 乘以 2.5 倍，意味着只要 value 达到 0.4，表情就达到 100% 了
        boosted_value = value * 2.5
        
        # 3. 限制最大值 (Clamp)
        boosted_value = min(1.0, boosted_value)
        
        # 4. 施加一点点非线性 (可选)
        # 这样动作会有一种“弹射”的感觉，而不是死板的线性
        exaggerated_value = math.pow(boosted_value, 2.0) 
        
        # 目标值计算
        target_brow = exaggerated_value * self.max_brow_raise
        target_scale = 1.0 + (exaggerated_value * (self.max_mouth_scale - 1.0))
        
        # 平滑插值
        self.current_brow_offset += (target_brow - self.current_brow_offset) * self.smoothing
        self.current_scale += (target_scale - self.current_scale) * self.smoothing
        
        # 应用
        character.set_eyebrow_height(self.current_brow_offset)
        character.set_face_scale(self.current_scale)
# --- 2. Trigger Effectors (Input: Boolean/Pulse) ---

class HeadBanger(Effector):
    """Nods head on trigger. (Softer Decay)"""
    def __init__(self):
        self.timer = 0.0
        self.duration = 0.2 
        self.active = False
        self.bob_amount = 15
        self.current_offset = 0.0
        
    def trigger(self):
        self.active = True
        self.timer = self.duration
        
    def update(self, dt, character):
        target_offset = 0.0
        
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False
            else:
                # 🔧 [优化 2] 使用 Ease-Out 曲线
                # progress: 1.0 (刚开始) -> 0.0 (结束)
                progress = self.timer / self.duration
                
                # 这是一个类似弹簧的曲线：快速压下去，慢回弹
                # math.pow(progress, 2) 会让回弹初段慢，后段快？
                # 不，我们用简单的 sin 曲线模拟点头
                # 0 -> PI (0 -> 1 -> 0)
                
                # 改进：只做下压部分，然后靠平滑回弹
                # 让 target 瞬间变大
                target_offset = self.bob_amount * math.sin(progress * 3.14)

        # 🔧 [优化 3] 对 offset 本身也做一次平滑，防止跳变
        self.current_offset += (target_offset - self.current_offset) * 0.2
        
        character.set_head_position_offset(0, self.current_offset)

class Jump(Effector):
    """Whole body jump on trigger."""
    def __init__(self):
        self.timer = 0
        self.active = False
        self.jump_height = 40
        
    def trigger(self):
        self.active = True
        self.timer = 0.2
        
    def update(self, dt, character):
        if not self.active: return
        
        self.timer -= dt
        if self.timer <= 0:
            self.active = False
            # Reset position handled by continuous floaters usually, 
            # but force reset here if needed:
            # character.root.local_transform.position = (400, 450) 
        else:
            # Parabolic jump curve
            y_off = -self.jump_height * math.sin((self.timer/0.2) * 3.14)
            # Apply to ROOT or BODY offset
            # Ideally apply as offset, not absolute position
            pass


# src/engine/effectors.py (新增类)

class FootTapper(Effector):
    """
    Scales the legs/feet on beat trigger.
    """
    def __init__(self):
        self.scale_timer = 0.0
        self.duration = 0.25      
        self.max_scale = 1.2     
        self.current_scale = 1.0
        self.triggered = False

    def trigger(self):
        # 每次 Beat 触发时重置计时器
        self.triggered = True
        self.scale_timer = self.duration

    def update(self, dt, character):
        target_scale = 1.0
        
        if self.triggered:
            self.scale_timer -= dt
            if self.scale_timer <= 0:
                self.triggered = False
            else:
                # 简单的弹跳曲线：先快大，后慢缩
                progress = self.scale_timer / self.duration
                # sin(0..PI) 会产生 1.0 -> 1.4 -> 1.0 的弧线
                # 但我们想要更有打击感：瞬间变大，慢慢变小
                # 所以用 progress 本身作为衰减系数
                target_scale = 1.0 + (self.max_scale - 1.0) * math.sin(progress * 3.14)

        # 简单的平滑，让变大变小不那么生硬
        self.current_scale += (target_scale - self.current_scale) * 0.3
        
        feet_bone = character.get_bone("Feet")
        
        if feet_bone:
            feet_bone.set_scale(self.current_scale, self.current_scale)
            

class SimpleLipSync(Effector):
    """
    Simulates lip sync by switching random mouth shapes when volume is detected.
    """
    def __init__(self):
        self.last_switch_time = 0
        self.switch_interval = 0.3  # 每 0.08秒 切换一次嘴型 (约 12 FPS)
        
        # 你的张嘴素材文件名 (不带 .png)
        self.open_mouths = ["1", "2", "3", "4"]
        
        # 你的闭嘴素材文件名 (根据你之前的设置，可能是 "Sil", "M", "neutral" 等)
        # 这里的名字必须和 CharacterRig 加载时打印的名字一致
        self.closed_mouth = "Sil" 
        
        # 当前显示的嘴型
        self.current_mouth = self.closed_mouth

    def update(self, value, character):
        # value 通常是 Volume (0.0 - 1.0)
        
        # 1. 阈值判断：声音太小就闭嘴
        if value < 0.1:
            if self.current_mouth != self.closed_mouth:
                self.current_mouth = self.closed_mouth
                character.set_mouth_variant(self.closed_mouth)
            return

        # 2. 声音够大：开始动嘴
        now = time.time()
        if now - self.last_switch_time > self.switch_interval:
            # 随机选一张张嘴的图
            # 进阶技巧：声音越大，越倾向于选张得大的图 (假设 4 是最大)
            # 但简单的随机选择对于 South Park 风格已经足够好了
            new_mouth = random.choice(self.open_mouths)
            
            character.set_mouth_variant(new_mouth)
            self.current_mouth = new_mouth
            self.last_switch_time = now