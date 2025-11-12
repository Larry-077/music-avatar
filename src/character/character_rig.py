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
import pygame
import os
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
            default_key = list(mouth_variants.keys())[min(4, len(mouth_variants)-1)]
            self.mouth_variants = SpriteVariant(mouth_variants, default=default_key)
            print(f"  ✅ Loaded {len(mouth_variants)} mouth variants from 'mouth/' folder:")
            for name in mouth_variants.keys():
                print(f"     - {name}")
        else:
            print("  ⚠️  No mouth variants found in 'mouth/' folder, creating placeholder")
            placeholder = pygame.Surface((30, 15), pygame.SRCALPHA)
            pygame.draw.line(placeholder, (0, 0, 0), (0, 7), (30, 7), 2)
            self.mouth_variants = SpriteVariant({'default': placeholder})
        
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
        
        # --- LEGS ---
        legs_bone = Bone(
            name="Legs",
            local_transform=Transform(position=(0, self.body_sprite.get_height() // 2 - 35)),
            sprite=self.legs_sprite,
            anchor_point=(0.5, 0.0)
        )
        body_bone.add_child(legs_bone)
        
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
            local_transform=Transform(position=(0, -50)),
            sprite=None,
            anchor_point=(0.5, 0.5)
        )
        face_bone.add_child(eyebrows_bone)
        
        # --- MOUTH ---
        mouth_bone = Bone(
            name="Mouth",
            local_transform=Transform(position=(0, 100)),
            sprite=self.mouth_variants.get_sprite(),
            anchor_point=(0.5, 0.5)
        )
        face_bone.add_child(mouth_bone)
        
        # --- LEFT ARM ---
        left_arm_bone = Bone(
            name="LeftArm",
            local_transform=Transform(position=(-self.body_sprite.get_width() // 2, 0)),
            sprite=None,
            anchor_point=(0.5, 0.0)
        )
        body_bone.add_child(left_arm_bone)
        
        # --- LEFT HAND ---
        left_hand_bone = Bone(
            name="LeftHand",
            local_transform=Transform(position=(0, 80)),
            sprite=None,
            anchor_point=(0.5, 0.0)
        )
        left_arm_bone.add_child(left_hand_bone)
        
        # --- RIGHT ARM ---
        right_arm_bone = Bone(
            name="RightArm",
            local_transform=Transform(position=(self.body_sprite.get_width() // 2, 0)),
            sprite=None,
            anchor_point=(0.5, 0.0)
        )
        body_bone.add_child(right_arm_bone)
        
        # --- RIGHT HAND ---
        right_hand_bone = Bone(
            name="RightHand",
            local_transform=Transform(position=(0, 80)),
            sprite=None,
            anchor_point=(0.5, 0.0)
        )
        right_arm_bone.add_child(right_hand_bone)
        
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
    
    def set_arm_rotation(self, side: str, angle: float):
        """Rotate arm ('left' or 'right')"""
        bone_name = f"{side.capitalize()}Arm"
        self.get_bone(bone_name).set_rotation(angle)
    
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


# --- Test Script ---
if __name__ == "__main__":
    print("Character Rig Builder - Test Mode")
    print("=" * 50)
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Character Rig Test - With Blink Animation")
    clock = pygame.time.Clock()
    
    # Build character
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../.."))
    assets_dir = os.path.join(project_root, "assets", "character")
    
    character = CharacterRig(assets_dir)
    character.print_hierarchy()
    
    # Generate eye timeline (optional)
    character.generate_simple_eye_timeline(30)
    
    # Main loop
    running = True
    debug_mode = True
    anim_time = 0
    
    print("\nControls:")
    print("  D - Toggle debug visualization")
    print("  B - Toggle auto-blink")
    print("  E - Manual blink")
    print("  T - Toggle eye timeline")
    print("  Arrow keys - Move character")
    print("  Q/E - Rotate head")
    print("  1-5 - Test eye positions")
    print("  A/O/M - Test mouth shapes")
    print("  ESC - Quit")
    
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    debug_mode = not debug_mode
                elif event.key == pygame.K_b:
                    state = character.toggle_auto_blink()
                    print(f"Auto-blink: {'ON' if state else 'OFF'}")
                elif event.key == pygame.K_e:
                    character.start_manual_blink()
                    print("Manual blink triggered")
                elif event.key == pygame.K_t:
                    character.eye_timeline_enabled = not character.eye_timeline_enabled
                    if character.eye_timeline_enabled:
                        character.eye_timeline_start_time = time.time()
                    print(f"Eye timeline: {'ON' if character.eye_timeline_enabled else 'OFF'}")
                # Test eye positions
                elif event.key == pygame.K_1:
                    character.set_eye_variant("1_center")
                elif event.key == pygame.K_2:
                    character.set_eye_variant("1_left")
                elif event.key == pygame.K_3:
                    character.set_eye_variant("1_right")
                elif event.key == pygame.K_4:
                    character.set_eye_variant("1_up")
                elif event.key == pygame.K_5:
                    character.set_eye_variant("1_down")
                # Test mouth shapes
                elif event.key == pygame.K_a:
                    character.set_mouth_variant("A")
                elif event.key == pygame.K_o:
                    character.set_mouth_variant("O")
                elif event.key == pygame.K_m:
                    character.set_mouth_variant("M")
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        root_pos = character.root.local_transform.position
        if keys[pygame.K_LEFT]:
            character.set_screen_position(root_pos[0] - 2, root_pos[1])
        if keys[pygame.K_RIGHT]:
            character.set_screen_position(root_pos[0] + 2, root_pos[1])
        if keys[pygame.K_UP]:
            character.set_screen_position(root_pos[0], root_pos[1] - 2)
        if keys[pygame.K_DOWN]:
            character.set_screen_position(root_pos[0], root_pos[1] + 2)
        
        head_rot = character.get_bone("Head").local_transform.rotation
        if keys[pygame.K_q]:
            character.set_head_rotation(head_rot - 1)
        if keys[pygame.K_e]:
            character.set_head_rotation(head_rot + 1)
        
        # Simple animation
        anim_time += 0.05
        bob = 10 * (1 + 0.5 * (1 + pygame.math.Vector2(0, 1).rotate(anim_time * 50).y))
        character.set_head_position_offset(0, bob)
        
        # Update and draw
        character.update()
        
        screen.fill((50, 50, 50))
        character.draw(screen, debug=debug_mode)
        
        # Info text
        font = pygame.font.Font(None, 20)
        fps_text = font.render(f"FPS: {clock.get_fps():.1f}", True, (255, 255, 255))
        blink_text = font.render(
            f"Blink: {'ON' if character.blink_enabled else 'OFF'} | "
            f"Timeline: {'ON' if character.eye_timeline_enabled else 'OFF'}",
            True, (100, 255, 100)
        )
        screen.blit(fps_text, (10, 10))
        screen.blit(blink_text, (10, 35))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\nTest complete!")