"""
Character Rig Builder
=====================
This module builds a complete rigged character from your sprite assets,
using the hierarchical bone system.

扩展功能：
- 自动眨眼系统
- 眼睛方向动画
- 嘴巴动画时间线支持
"""
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pygame
import random
import time
from src.core.bone_system import Bone, Transform, SpriteVariant


class CharacterRig:
    """
    Complete character rig with all body parts properly connected.
    This is the main interface for animating your character.
    """
    
    def __init__(self, assets_dir: str):
        """
        Initialize character rig and load all assets.
        
        Args:
            assets_dir: Path to assets/character/ folder
        """
        self.assets_dir = assets_dir
        self.root = None  # Will be the root bone
        
        # Cache for bone references (for easy animation control)
        self.bones = {}
        
        # Build the rig
        self._load_assets()
        self._build_skeleton()
        
        # ===== 新增：初始化动画系统 =====
        self._init_animation_systems()
    
    def _load_image(self, relative_path: str) -> pygame.Surface:
        """Helper to load an image"""
        path = os.path.join(self.assets_dir, relative_path)
        if not os.path.exists(path):
            print(f"Warning: Image not found: {path}")
            # Return a placeholder
            surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            surf.fill((255, 0, 255, 128))  # Pink placeholder
            return surf
        return pygame.image.load(path).convert_alpha()
    
    def _load_asset_variants(self, folder: str, prefix: str = "") -> dict:
        """
        Load all PNG files from a folder as variants.
        Returns dict mapping filename (without extension) to sprite.
        """
        variants = {}
        full_path = os.path.join(self.assets_dir, folder)
        
        if not os.path.exists(full_path):
            print(f"Warning: Folder not found: {full_path}")
            return variants
        
        for filename in os.listdir(full_path):
            if filename.endswith('.png') and filename.startswith(prefix):
                name = os.path.splitext(filename)[0]
                variants[name] = self._load_image(os.path.join(folder, filename))
        
        return variants
    
    def _load_assets(self):
        """Load all character sprites"""
        print("Loading character assets...")
        
        # Core body parts
        self.body_sprite = self._load_image('body.png')
        self.face_sprite = self._load_image('face.png')
        self.hat_sprite = self._load_image('hat.png')
        self.collar_sprite = self._load_image('collar.png')
        self.legs_sprite = self._load_image('legs.png')
        self.feet_sprite = self._load_image('feet.png') 
        
        # --- Load eye variants from folder ---
        eye_variants = self._load_asset_variants("eyes")
        if eye_variants:
            default_key = list(eye_variants.keys())[0]
            self.eye_variants = SpriteVariant(eye_variants, default=default_key)
            print(f"  ✅ Loaded {len(eye_variants)} eye variants from 'eyes/' folder:")
            for name in eye_variants.keys():
                print(f"     - {name}")
        else:
            print("  ⚠️  No eye variants found in 'eyes/' folder, creating placeholder")
            placeholder = pygame.Surface((50, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(placeholder, (0, 0, 0), (0, 0, 50, 20))
            self.eye_variants = SpriteVariant({'default': placeholder})
        
        # --- Load mouth variants from folder ---
        mouth_variants = self._load_asset_variants("mouth")
        if mouth_variants:
            target_default = "D_L_mid" 
            
            if target_default in mouth_variants:
                default_key = target_default
            else:
                # 找不到就默认取第一个
                default_key = list(mouth_variants.keys())[0]
            
            self.mouth_variants = SpriteVariant(mouth_variants, default=default_key)
        else:
            print("  ⚠️  No mouth variants found in 'mouth/' folder, creating placeholder")
            placeholder = pygame.Surface((30, 15), pygame.SRCALPHA)
            pygame.draw.line(placeholder, (0, 0, 0), (0, 7), (30, 7), 2)
            self.mouth_variants = SpriteVariant({'default': placeholder})


        self.l_arm_upper_sprite = self._load_image('arms/left_upperarm.png') 
        self.r_arm_upper_sprite = self._load_image('arms/right_upperarm.png') 
        self.l_arm_forearm_sprite = self._load_image('arms/left_forearm.png') 
        self.r_arm_forearm_sprite = self._load_image('arms/right_forearm.png') 

        # --- Load Hand variants from folder (assuming L_ and R_ prefixes) ---
        hand_variants = self._load_asset_variants("hands")
        
        # 筛选左右手
        l_hand_dict = {k: v for k, v in hand_variants.items() if k.startswith('L_')}
        r_hand_dict = {k: v for k, v in hand_variants.items() if k.startswith('R_')}
        
        if l_hand_dict:
            self.l_hand_variants = SpriteVariant(l_hand_dict, default=list(l_hand_dict.keys())[0])
            print(f"  ✅ Loaded {len(l_hand_dict)} left hand variants.")
        else:
            print("  ⚠️  No left hand variants found.")
            # 使用一个小的占位符作为回退
            self.l_hand_variants = SpriteVariant({'default': pygame.Surface((20, 20), pygame.SRCALPHA)})
            
        if r_hand_dict:
            self.r_hand_variants = SpriteVariant(r_hand_dict, default=list(r_hand_dict.keys())[0])
            print(f"  ✅ Loaded {len(r_hand_dict)} right hand variants.")
        else:
            print("  ⚠️  No right hand variants found.")
            self.r_hand_variants = SpriteVariant({'default': pygame.Surface((20, 20), pygame.SRCALPHA)})
        
        self.eyebrows_sprite = self._load_image('eyebrows/Stan_Eyebrows0003.png')

        print("Assets loaded successfully!")
    
    def _build_skeleton(self):
        """
        Build the complete bone hierarchy.
        """
        print("Building skeleton...")
        
        # --- ROOT (screen anchor point) ---
        self.root = Bone(
            name="Root",
            local_transform=Transform(position=(400, 450))
        )
        
        # --- BODY (main torso) ---
        body_bone = Bone(
            name="Body",
            local_transform=Transform(position=(0, 0)),
            sprite=None,
            anchor_point=(0.5, 0.5)
        )
        self.root.add_child(body_bone)
        
        body_half_width = self.body_sprite.get_width() // 2

        # =========================================================
        # --- LEFT ARM (Shoulder -> Elbow -> Hand) ---
        # =========================================================

        # 1. Shoulder_L (上臂)
        shoulder_L = Bone(
            name="Shoulder_L",
            # 初始位置：位于身体左侧，略微向下偏移
            local_transform=Transform(position=(-body_half_width + 14+5, -44), rotation=30), 
            sprite=self.l_arm_upper_sprite,  # <-- 使用左上臂贴图
            anchor_point=(0.6, 0.2) # 旋转中心在肩部（上臂顶端）
        )
        body_bone.add_child(shoulder_L)

        # 2. Elbow_L (下臂/前臂)
        forearm_L = Bone(
            name="Elbow_L",
            # 位置：位于上臂 sprite 的底端
            local_transform=Transform(position=(4, self.l_arm_upper_sprite.get_height()-25), rotation=10),
            sprite=self.l_arm_forearm_sprite, # <-- 使用左下臂贴图
            anchor_point=(0.6, 0.15) # 旋转中心在肘部（下臂顶端）
        )
        shoulder_L.add_child(forearm_L)

        # 3. Hand_L (手部)
        hand_L = Bone(
            name="Hand_L",
            # 位置：位于下臂 sprite 的底端
            local_transform=Transform(position=(11, self.l_arm_forearm_sprite.get_height()-16)),
            sprite=self.l_hand_variants.get_sprite(),
            anchor_point=(0.5, 0.5) # 旋转中心在手腕
        )
        forearm_L.add_child(hand_L)
        
        # =========================================================
        # --- RIGHT ARM (Shoulder -> Elbow -> Hand) ---
        # =========================================================
        
        # 1. Shoulder_R (上臂)
        shoulder_R = Bone(
            name="Shoulder_R",
            # 初始位置：位于身体右侧
            local_transform=Transform(position=(body_half_width-18-5, -40), rotation=-30), 
            sprite=self.r_arm_upper_sprite, # <-- 使用右上臂贴图
            anchor_point=(0.4, 0.2) 
        )
        body_bone.add_child(shoulder_R)

        # 2. Elbow_R (下臂/前臂)
        forearm_R = Bone(
            name="Elbow_R",
            # 使用右上臂的高度来定位肘部关节
            local_transform=Transform(position=(-4, self.r_arm_upper_sprite.get_height()-24), rotation=-10),
            sprite=self.r_arm_forearm_sprite, # <-- 使用右下臂贴图
            anchor_point=(0.4, 0.15) 
        )
        shoulder_R.add_child(forearm_R)

        # 3. Hand_R (手部)
        hand_R = Bone(
            name="Hand_R",
            # 使用右下臂的高度来定位手腕关节
            local_transform=Transform(position=(-11, self.r_arm_forearm_sprite.get_height()-16)),
            sprite=self.r_hand_variants.get_sprite(),
            anchor_point=(0.5, 0.5) 
        )
        forearm_R.add_child(hand_R)

        # --- LEGS ---
        legs_bone = Bone(
            name="Legs",
            local_transform=Transform(position=(0, self.body_sprite.get_height() // 2 - 35)),
            sprite=self.legs_sprite,
            anchor_point=(0.5, 0.0)
        )
        body_bone.add_child(legs_bone)

        feet_bone = Bone(
            name="Feet",
            local_transform=Transform(position=(0, self.legs_sprite.get_height() - 8)), # 假设脚在腿的底部
            sprite=self.feet_sprite,
            anchor_point=(0.5, 1) # 中心缩放，产生"变大"效果
        )
        # 将脚挂载在腿上
        legs_bone.add_child(feet_bone)
        
        # --- BODY SPRITE ---
        body_sprite_bone = Bone(
            name="BodySprite",
            local_transform=Transform(position=(0, 0)),
            sprite=self.body_sprite,
            anchor_point=(0.5, 0.5)
        )
        body_bone.add_child(body_sprite_bone)
        
        # --- COLLAR ---
        collar_bone = Bone(
            name="Collar",
            local_transform=Transform(position=(0, -50)),
            sprite=self.collar_sprite,
            anchor_point=(0.5, 0.5)
        )
        body_bone.add_child(collar_bone)
        
        # --- HEAD ---
        head_bone = Bone(
            name="Head",
            local_transform=Transform(position=(0, -self.body_sprite.get_height() // 2 - 100)),
            sprite=None,
            anchor_point=(0.5, 0.5)
        )
        body_bone.add_child(head_bone)
        
        # --- FACE ---
        face_bone = Bone(
            name="Face",
            local_transform=Transform(position=(0, 0)),
            sprite=self.face_sprite,
            anchor_point=(0.5, 0.5)
        )
        head_bone.add_child(face_bone)
        
        # --- HAT ---
        hat_bone = Bone(
            name="Hat",
            local_transform=Transform(position=(0, -self.face_sprite.get_height() // 2 + 200)),
            sprite=self.hat_sprite,
            anchor_point=(0.5, 1.0)
        )
        head_bone.add_child(hat_bone)
        
        # --- EYES ---
        eyes_bone = Bone(
            name="Eyes",
            local_transform=Transform(position=(0, 18)),
            sprite=self.eye_variants.get_sprite(),
            anchor_point=(0.5, 0.5)
        )
        face_bone.add_child(eyes_bone)
        
        # --- EYEBROWS ---
        eyebrows_bone = Bone(
            name="Eyebrows",
            local_transform=Transform(position=(0, -30)), # 默认位置在眼睛上方
            sprite=self.eyebrows_sprite, # <--- 这里填入素材
            anchor_point=(0.5, 0.5)
        )
        head_bone.add_child(eyebrows_bone)
        
        # --- MOUTH ---
        mouth_bone = Bone(
            name="Mouth",
            local_transform=Transform(position=(0, 100)),
            sprite=self.mouth_variants.get_sprite(),
            anchor_point=(0.5, 0.5)
        )
        face_bone.add_child(mouth_bone)
        
        
        
        # Cache bone references
        self._cache_bones()
        print(f"Skeleton built with {len(self.bones)} bones")
    
    def _cache_bones(self):
        """Build a dictionary of all bones for easy access"""
        def add_to_cache(bone):
            self.bones[bone.name] = bone
            for child in bone.children:
                add_to_cache(child)
        
        add_to_cache(self.root)
    
    # ===== 新增：动画系统初始化 =====
    def _init_animation_systems(self):
        """初始化眨眼和时间线动画系统"""
        # 眨眼系统
        self.blink_enabled = True
        self.last_blink_time = time.time()
        self.next_blink_interval = random.uniform(2.0, 5.0)
        self.is_blinking = False
        self.blink_start_time = 0.0
        self.blink_duration = 0.15
        
        # 获取可用的闭眼状态
        all_eye_variants = list(self.eye_variants.variants.keys())
        self.blink_eyes = [e for e in ["close", "close2", "close3"] if e in all_eye_variants]
        if not self.blink_eyes and all_eye_variants:
            # 如果没有 close，尝试找任何包含 "close" 的
            self.blink_eyes = [e for e in all_eye_variants if "close" in e.lower()]
        if not self.blink_eyes:
            self.blink_eyes = ["1_center"]  # 最后的回退方案
        
        self.normal_eye = "1_center"
        
        # 眼睛时间线
        self.eye_timeline_enabled = False
        self.eye_timeline = []
        self.eye_timeline_start_time = 0.0
        
        # 嘴巴时间线
        self.mouth_timeline_enabled = False
        self.mouth_timeline = []
        self.mouth_timeline_start_time = 0.0
        
        print("  ✅ Animation systems initialized")
    
    # ===== 新增：眨眼动画方法 =====
    def update_blink_animation(self):
        """更新眨眼动画（在 update() 中调用）"""
        if not self.blink_enabled:
            return
        
        current_time = time.time()
        
        # 检查是否该眨眼了
        if not self.is_blinking:
            if current_time - self.last_blink_time >= self.next_blink_interval:
                # 开始眨眼
                self.is_blinking = True
                self.blink_start_time = current_time
                if self.blink_eyes:
                    self.set_eye_variant(random.choice(self.blink_eyes))
        else:
            # 正在眨眼，检查是否该睁眼
            if current_time - self.blink_start_time >= self.blink_duration:
                self.is_blinking = False
                self.last_blink_time = current_time
                self.next_blink_interval = random.uniform(2.0, 5.0)
                self.set_eye_variant(self.normal_eye)
    
    def update_eye_timeline(self, current_time=None):
        """更新眼睛时间线动画"""
        if not self.eye_timeline_enabled or not self.eye_timeline:
            return
        
        if current_time is None:
            current_time = time.time() - self.eye_timeline_start_time
        
        # 查找当前时间对应的眼睛状态
        for seg in self.eye_timeline:
            if seg["start"] <= current_time < seg["start"] + seg["duration"]:
                if not self.is_blinking:
                    self.normal_eye = seg["variant"]
                    self.set_eye_variant(seg["variant"])
                break
    
    def update_mouth_timeline(self, current_time):
        """更新嘴巴时间线动画"""
        if not self.mouth_timeline_enabled or not self.mouth_timeline:
            return
        
        for seg in self.mouth_timeline:
            if seg["start"] <= current_time < seg["end"]:
                self.set_mouth_variant(seg["viseme"])
                break
    
    # ===== 新增：控制方法 =====
    def start_manual_blink(self):
        """手动触发眨眼"""
        self.is_blinking = True
        self.blink_start_time = time.time()
        if self.blink_eyes:
            self.set_eye_variant(random.choice(self.blink_eyes))
    
    def toggle_auto_blink(self):
        """切换自动眨眼开关"""
        self.blink_enabled = not self.blink_enabled
        return self.blink_enabled
    
    def set_blink_interval(self, min_interval, max_interval):
        """设置眨眼间隔范围"""
        self.next_blink_interval = random.uniform(min_interval, max_interval)
    
    def load_eye_timeline(self, timeline_data, auto_start=True):
        """加载眼睛动画时间线"""
        self.eye_timeline = timeline_data
        self.eye_timeline_enabled = auto_start
        if auto_start:
            self.eye_timeline_start_time = time.time()
        print(f"  ✅ Loaded eye timeline with {len(timeline_data)} segments")
    
    def load_mouth_timeline(self, timeline_data, auto_start=True):
        """加载嘴巴动画时间线"""
        self.mouth_timeline = timeline_data
        self.mouth_timeline_enabled = auto_start
        if auto_start:
            self.mouth_timeline_start_time = time.time()
        print(f"  ✅ Loaded mouth timeline with {len(timeline_data)} segments")
    
    def generate_simple_eye_timeline(self, duration_seconds=30):
        """生成简单的眼睛时间线"""
        timeline = []
        current_time = 0.0
        
        states = [
            ("1_center", 3.0), ("1_left", 1.5), ("1_center", 2.0),
            ("1_right", 1.5), ("1_center", 2.5), ("1_up", 1.0),
            ("1_center", 3.0), ("1_down", 1.0),
        ]
        
        all_variants = list(self.eye_variants.variants.keys())
        
        while current_time < duration_seconds:
            for state, duration in states:
                if current_time >= duration_seconds:
                    break
                # 只使用存在的眼睛状态
                if state in all_variants:
                    timeline.append({
                        "variant": state,
                        "start": current_time,
                        "duration": duration
                    })
                    current_time += duration
        
        return timeline
    
    # ===== 原有方法保持不变 =====
    def get_bone(self, name: str) -> Bone:
        """Get a bone by name"""
        return self.bones.get(name)
    
    def set_screen_position(self, x: float, y: float):
        """Move the entire character on screen"""
        self.root.set_position(x, y)
    
    def set_body_scale(self, scale: float):
        """Scale the entire body"""
        self.get_bone("Body").set_scale(scale)
    
    def set_head_rotation(self, angle: float):
        """Rotate the head (and all facial features with it)"""
        self.get_bone("Head").set_rotation(angle)
    
    def set_head_position_offset(self, x: float, y: float):
        """Move head relative to body (for bobbing, etc.)"""
        head = self.get_bone("Head")
        base_y = -self.body_sprite.get_height() // 2 - 100
        head.set_position(x, base_y + y)
    
    def set_eye_variant(self, variant_name: str):
        """Change eye sprite (for different directions, open/closed)"""
        if self.eye_variants.set_variant(variant_name):
            self.get_bone("Eyes").sprite = self.eye_variants.get_sprite()
    
    def set_mouth_variant(self, variant_name: str):
        """Change mouth sprite (for different expressions)"""
        if self.mouth_variants.set_variant(variant_name):
            self.get_bone("Mouth").sprite = self.mouth_variants.get_sprite()
    
    def set_eyebrow_height(self, offset: float):
        """Move eyebrows up/down (for expressions)"""
        eyebrow = self.get_bone("Eyebrows")
        eyebrow.set_position(0, -50 + offset)
    
    # CharacterRig.py, 在 set_eyebrow_height 之后

# ===== 新增：手臂控制方法 =====

    def set_arm_joint_rotation(self, side: str, shoulder_angle: float, elbow_angle: float):
        """
        设置手臂的肩部和肘部旋转角度。
        
        Args:
            side: 'left' or 'right'
            shoulder_angle: 上臂相对于身体的旋转角度 (全局)
            elbow_angle: 下臂相对于上臂的旋转角度 (局部)
        """
        
        side_char = side[0].upper() # L 或 R
        
        # 注意我们现在使用 Shoulder_L/R 和 Elbow_L/R 骨骼名称
        shoulder_bone = self.get_bone(f"Shoulder_{side_char}")
        elbow_bone = self.get_bone(f"Elbow_{side_char}")
        
        if shoulder_bone:
            shoulder_bone.set_rotation(shoulder_angle)
        if elbow_bone:
            elbow_bone.set_rotation(elbow_angle)

    def set_hand_variant(self, side: str, variant_name: str):
        """
        切换手部的 Sprite 贴图。
        """
        if side.lower() == 'left':
            hand_variants = self.l_hand_variants
            hand_bone_name = "Hand_L"
        elif side.lower() == 'right':
            hand_variants = self.r_hand_variants
            hand_bone_name = "Hand_R"
        else:
            return

        # 尝试切换变体
        if hand_variants.set_variant(variant_name):
            self.get_bone(hand_bone_name).sprite = hand_variants.get_sprite()
        
    # ===== 修改：update() 方法添加动画更新 =====
    def update(self):
        """Update all bone transforms and animations (call once per frame)"""
        # 更新眨眼动画
        self.update_blink_animation()
        
        # 可选：更新眼睛时间线
        if self.eye_timeline_enabled:
            self.update_eye_timeline()
        
        # 更新骨骼变换
        self.root.update()
    
    def draw(self, screen: pygame.Surface, debug: bool = False):
        """Draw the entire character"""
        self.root.draw(screen, debug)
    
    def print_hierarchy(self):
        """Print the bone structure for debugging"""
        def print_bone(bone, indent=0):
            print("  " * indent + f"└─ {bone.name}")
            for child in bone.children:
                print_bone(child, indent + 1)
        
        print("\n=== Character Bone Hierarchy ===")
        print_bone(self.root)
        print("================================\n")

    def set_eyebrow_height(self, offset_y: float):
        """
        设置眉毛的垂直偏移量。
        Args:
            offset_y: 负数表示向上移（惊讶），正数表示向下移（生气/严肃）
        """
        # 获取眉毛的默认基准位置 (比如 -30)
        base_y = -30 
        
        eyebrow = self.get_bone("Eyebrows")
        if eyebrow:
            # 保持 X 不变，只改 Y
            current_x = eyebrow.local_transform.position[0]
            eyebrow.set_position(current_x, base_y + offset_y)
            
    def set_face_scale(self, scale: float):
        """
        设置面部特征的整体缩放（可选，用于增强表现力）
        """
        # 可以让眼睛或嘴巴随强度稍微变大
        mouth = self.get_bone("Mouth")
        if mouth:
            mouth.set_scale(scale, scale)


# --- Arm Tuning Tool ---
if __name__ == "__main__":
    print("Character Arm Tuning Tool")
    print("=========================")
    
    # 初始化 Pygame
    pygame.init()
    screen_width, screen_height = 1024, 768
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Character Rig - Arm Tuning Mode")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    big_font = pygame.font.Font(None, 36)
    
    # 初始化角色
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 假设你的 assets 文件夹在向上两级的目录，请根据实际情况调整路径
    project_root = os.path.abspath(os.path.join(current_dir, "../.."))
    assets_dir = os.path.join(project_root, "assets", "character")
    
    # 检查路径是否存在，防止报错
    if not os.path.exists(assets_dir):
        print(f"Error: Assets directory not found at {assets_dir}")
        print("Please adjust the 'assets_dir' path in the code.")
        # 创建临时的伪造路径以允许程序运行（显示粉色方块）
        assets_dir = "dummy_path"

    character = CharacterRig(assets_dir)
    
    # 设置角色初始位置到屏幕中心
    character.set_screen_position(screen_width // 2, screen_height // 2)

    # === 调试配置 ===
    # 定义我们要调整的骨骼列表
    tune_targets = [
        "Shoulder_L", "Elbow_L", "Hand_L",
        "Shoulder_R", "Elbow_R", "Hand_R"
    ]
    current_target_index = 0
    
    # 移动速度
    move_speed = 1.0
    fast_multiplier = 5.0
    
    running = True
    show_bones = True

    print("\n=== 操作指南 ===")
    print("  [TAB]   : 切换要调整的关节 (左肩 -> 左肘 -> 左手 -> 右侧...)")
    print("  [方向键]: 移动当前选中的关节 (调整相对位置)")
    print("  [Shift] : 按住加速移动")
    print("  [P]     : 在控制台打印当前所有坐标 (用于复制到代码中)")
    print("  [D]     : 显示/隐藏骨骼线条")
    print("  [ESC]   : 退出")
    print("================\n")

    while running:
        # 1. 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    # 切换选中的骨骼
                    current_target_index = (current_target_index + 1) % len(tune_targets)
                elif event.key == pygame.K_d:
                    show_bones = not show_bones
                elif event.key == pygame.K_p:
                    # 打印当前配置
                    print("\n=== Current Configuration (Copy these values) ===")
                    for name in tune_targets:
                        bone = character.get_bone(name)
                        pos = bone.local_transform.position
                        print(f"{name}: Position = ({pos[0]:.1f}, {pos[1]:.1f})")
                    print("===============================================\n")

        # 2. 持续按键处理 (用于平滑移动)
        keys = pygame.key.get_pressed()
        
        # 获取当前选中的骨骼
        target_bone_name = tune_targets[current_target_index]
        target_bone = character.get_bone(target_bone_name)
        
        if target_bone:
            current_speed = move_speed * (fast_multiplier if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 1.0)
            
            # 获取当前局部坐标
            cx, cy = target_bone.local_transform.position
            
            # 修改坐标
            if keys[pygame.K_LEFT]:
                cx -= current_speed
            if keys[pygame.K_RIGHT]:
                cx += current_speed
            if keys[pygame.K_UP]:
                cy -= current_speed
            if keys[pygame.K_DOWN]:
                cy += current_speed
                
            # 应用回骨骼
            target_bone.local_transform.position = (cx, cy)

        # 3. 更新
        character.update()
        
        # 4. 渲染
        screen.fill((60, 60, 60)) # 深灰色背景
        
        # 绘制角色
        character.draw(screen, debug=show_bones)
        
        # --- 绘制UI和高亮 ---
        
        # 高亮当前选中的骨骼位置
        if target_bone:
            # 获取全局坐标用于绘制提示圆圈
            gx, gy = target_bone.get_world_position()
            pygame.draw.circle(screen, (0, 255, 255), (int(gx), int(gy)), 10, 2) # 青色圆圈
            
            # 显示当前骨骼名称和坐标
            info_text = f"Selected: {target_bone_name}"
            coord_text = f"Local Pos: ({target_bone.local_transform.position[0]:.1f}, {target_bone.local_transform.position[1]:.1f})"
            
            # 在骨骼旁显示文字
            text_surf = font.render(target_bone_name, True, (0, 255, 255))
            screen.blit(text_surf, (gx + 15, gy - 10))

        # 屏幕左上角的HUD
        y_offset = 10
        title = big_font.render("Arm Tuning Mode", True, (255, 255, 255))
        screen.blit(title, (10, y_offset))
        y_offset += 40
        
        controls = [
            "[TAB] Switch Bone",
            "[Arrows] Move Position",
            "[Shift] Hold to speed up",
            "[P] Print Values to Console",
            f"Current Target: {tune_targets[current_target_index]}"
        ]
        
        for line in controls:
            col = (255, 255, 0) if "Current" in line else (200, 200, 200)
            t = font.render(line, True, col)
            screen.blit(t, (10, y_offset))
            y_offset += 25

        if target_bone:
            val_text = font.render(f"Values: {target_bone.local_transform.position}", True, (0, 255, 255))
            screen.blit(val_text, (10, y_offset + 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()