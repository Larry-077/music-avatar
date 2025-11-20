"""
Character Rig Builder
=====================
This module builds a complete rigged character from your sprite assets,
using the hierarchical bone system.
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
        """
        self.assets_dir = assets_dir
        self.root = None  
        
        self.bones = {}
        self._load_assets()
        self._build_skeleton()
        self._init_animation_systems()
    
    def _load_image(self, relative_path: str) -> pygame.Surface:
        """Helper to load an image"""
        path = os.path.join(self.assets_dir, relative_path)
        if not os.path.exists(path):
            print(f"Warning: Image not found: {path}")
            surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            surf.fill((255, 0, 255, 128)) 
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

        hand_variants = self._load_asset_variants("hands")
        
        l_hand_dict = {k: v for k, v in hand_variants.items() if k.startswith('L_')}
        r_hand_dict = {k: v for k, v in hand_variants.items() if k.startswith('R_')}
        
        if l_hand_dict:
            self.l_hand_variants = SpriteVariant(l_hand_dict, default=list(l_hand_dict.keys())[0])
            print(f"  ✅ Loaded {len(l_hand_dict)} left hand variants.")
        else:
            print("  ⚠️  No left hand variants found.")
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

        # 1. Shoulder_L 
        shoulder_L = Bone(
            name="Shoulder_L",
            local_transform=Transform(position=(-body_half_width + 14+5, -44), rotation=30), 
            sprite=self.l_arm_upper_sprite, 
            anchor_point=(0.6, 0.2)
        )
        body_bone.add_child(shoulder_L)

        # 2. Elbow_L 
        forearm_L = Bone(
            name="Elbow_L",
            local_transform=Transform(position=(4, self.l_arm_upper_sprite.get_height()-25), rotation=10),
            sprite=self.l_arm_forearm_sprite, 
            anchor_point=(0.6, 0.15) 
        )
        shoulder_L.add_child(forearm_L)

        # 3. Hand_L 
        hand_L = Bone(
            name="Hand_L",
            local_transform=Transform(position=(11, self.l_arm_forearm_sprite.get_height()-16)),
            sprite=self.l_hand_variants.get_sprite(),
            anchor_point=(0.5, 0.5)
        )
        forearm_L.add_child(hand_L)
        
        # =========================================================
        # --- RIGHT ARM (Shoulder -> Elbow -> Hand) ---
        # =========================================================
        
        # 1. Shoulder_R 
        shoulder_R = Bone(
            name="Shoulder_R",
            local_transform=Transform(position=(body_half_width-18-5, -40), rotation=-30), 
            sprite=self.r_arm_upper_sprite, 
            anchor_point=(0.4, 0.2) 
        )
        body_bone.add_child(shoulder_R)

        # 2. Elbow_R 
        forearm_R = Bone(
            name="Elbow_R",
            local_transform=Transform(position=(-4, self.r_arm_upper_sprite.get_height()-24), rotation=-10),
            sprite=self.r_arm_forearm_sprite, 
            anchor_point=(0.4, 0.15) 
        )
        shoulder_R.add_child(forearm_R)

        # 3. Hand_R 
        hand_R = Bone(
            name="Hand_R",
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
            anchor_point=(0.5, 1) 
        )
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
            local_transform=Transform(position=(0, -30)), 
            sprite=self.eyebrows_sprite, 
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
    
    def _init_animation_systems(self):
        """初始化眨眼和时间线动画系统"""
        self.blink_enabled = True
        self.last_blink_time = time.time()
        self.next_blink_interval = random.uniform(2.0, 5.0)
        self.is_blinking = False
        self.blink_start_time = 0.0
        self.blink_duration = 0.15
        
        all_eye_variants = list(self.eye_variants.variants.keys())
        self.blink_eyes = [e for e in ["close", "close2", "close3"] if e in all_eye_variants]
        if not self.blink_eyes and all_eye_variants:
            self.blink_eyes = [e for e in all_eye_variants if "close" in e.lower()]
        if not self.blink_eyes:
            self.blink_eyes = ["1_center"]
        
        self.normal_eye = "1_center"
        
        self.eye_timeline_enabled = False
        self.eye_timeline = []
        self.eye_timeline_start_time = 0.0
        
        self.mouth_timeline_enabled = False
        self.mouth_timeline = []
        self.mouth_timeline_start_time = 0.0
        
        print("  ✅ Animation systems initialized")
    
    def update_blink_animation(self):
        
        if not self.blink_enabled:
            return
        
        current_time = time.time()
        
        if not self.is_blinking:
            if current_time - self.last_blink_time >= self.next_blink_interval:
                self.is_blinking = True
                self.blink_start_time = current_time
                if self.blink_eyes:
                    self.set_eye_variant(random.choice(self.blink_eyes))
        else:
            if current_time - self.blink_start_time >= self.blink_duration:
                self.is_blinking = False
                self.last_blink_time = current_time
                self.next_blink_interval = random.uniform(2.0, 5.0)
                self.set_eye_variant(self.normal_eye)
    
    def update_eye_timeline(self, current_time=None):
        if not self.eye_timeline_enabled or not self.eye_timeline:
            return
        
        if current_time is None:
            current_time = time.time() - self.eye_timeline_start_time
        
        for seg in self.eye_timeline:
            if seg["start"] <= current_time < seg["start"] + seg["duration"]:
                if not self.is_blinking:
                    self.normal_eye = seg["variant"]
                    self.set_eye_variant(seg["variant"])
                break
    
    def update_mouth_timeline(self, current_time):
        if not self.mouth_timeline_enabled or not self.mouth_timeline:
            return
        
        for seg in self.mouth_timeline:
            if seg["start"] <= current_time < seg["end"]:
                self.set_mouth_variant(seg["viseme"])
                break

    def start_manual_blink(self):
        self.is_blinking = True
        self.blink_start_time = time.time()
        if self.blink_eyes:
            self.set_eye_variant(random.choice(self.blink_eyes))
    
    def toggle_auto_blink(self):
        self.blink_enabled = not self.blink_enabled
        return self.blink_enabled
    
    def set_blink_interval(self, min_interval, max_interval):
        self.next_blink_interval = random.uniform(min_interval, max_interval)
    
    def load_eye_timeline(self, timeline_data, auto_start=True):
        self.eye_timeline = timeline_data
        self.eye_timeline_enabled = auto_start
        if auto_start:
            self.eye_timeline_start_time = time.time()
        print(f"  ✅ Loaded eye timeline with {len(timeline_data)} segments")
    
    def load_mouth_timeline(self, timeline_data, auto_start=True):
        self.mouth_timeline = timeline_data
        self.mouth_timeline_enabled = auto_start
        if auto_start:
            self.mouth_timeline_start_time = time.time()
        print(f"  ✅ Loaded mouth timeline with {len(timeline_data)} segments")
    
    def generate_simple_eye_timeline(self, duration_seconds=30):
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
                if state in all_variants:
                    timeline.append({
                        "variant": state,
                        "start": current_time,
                        "duration": duration
                    })
                    current_time += duration
        
        return timeline
    
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
    


    def set_arm_joint_rotation(self, side: str, shoulder_angle: float, elbow_angle: float):
        
        side_char = side[0].upper() 
        
        shoulder_bone = self.get_bone(f"Shoulder_{side_char}")
        elbow_bone = self.get_bone(f"Elbow_{side_char}")
        
        if shoulder_bone:
            shoulder_bone.set_rotation(shoulder_angle)
        if elbow_bone:
            elbow_bone.set_rotation(elbow_angle)

    def set_hand_variant(self, side: str, variant_name: str):
        if side.lower() == 'left':
            hand_variants = self.l_hand_variants
            hand_bone_name = "Hand_L"
        elif side.lower() == 'right':
            hand_variants = self.r_hand_variants
            hand_bone_name = "Hand_R"
        else:
            return

  
        if hand_variants.set_variant(variant_name):
            self.get_bone(hand_bone_name).sprite = hand_variants.get_sprite()
        
    def update(self):
        """Update all bone transforms and animations (call once per frame)"""
   
        self.update_blink_animation()
        
        if self.eye_timeline_enabled:
            self.update_eye_timeline()
        
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
        base_y = -30 
        
        eyebrow = self.get_bone("Eyebrows")
        if eyebrow:
            current_x = eyebrow.local_transform.position[0]
            eyebrow.set_position(current_x, base_y + offset_y)
            
    def set_face_scale(self, scale: float):
        mouth = self.get_bone("Mouth")
        if mouth:
            mouth.set_scale(scale, scale)


# --- Arm Tuning Tool ---
if __name__ == "__main__":
    print("Character Arm Tuning Tool")
    print("=========================")
    

    pygame.init()
    screen_width, screen_height = 1024, 768
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Character Rig - Arm Tuning Mode")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    big_font = pygame.font.Font(None, 36)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../.."))
    assets_dir = os.path.join(project_root, "assets", "character")
    if not os.path.exists(assets_dir):
        print(f"Error: Assets directory not found at {assets_dir}")
        print("Please adjust the 'assets_dir' path in the code.")
        assets_dir = "dummy_path"

    character = CharacterRig(assets_dir)
    

    character.set_screen_position(screen_width // 2, screen_height // 2)
    tune_targets = [
        "Shoulder_L", "Elbow_L", "Hand_L",
        "Shoulder_R", "Elbow_R", "Hand_R"
    ]
    current_target_index = 0
    
    move_speed = 1.0
    fast_multiplier = 5.0
    
    running = True
    show_bones = True

    print("\n=== Operation Guide ===")
    print("  [TAB]   : Switch/Cycle the joint to be adjusted (Left Shoulder -> Left Elbow -> Left Hand -> Right Side...)")
    print("  [Arrow Keys]: Move the currently selected joint (Adjust relative position)")
    print("  [Shift] : Hold down to accelerate movement")
    print("  [P]     : Print all current coordinates to the console (For copying into code)")
    print("  [D]     : Show/Hide skeleton lines")
    print("  [ESC]   : Exit")
    print("================\n")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:

                    current_target_index = (current_target_index + 1) % len(tune_targets)
                elif event.key == pygame.K_d:
                    show_bones = not show_bones
                elif event.key == pygame.K_p:
                    print("\n=== Current Configuration (Copy these values) ===")
                    for name in tune_targets:
                        bone = character.get_bone(name)
                        pos = bone.local_transform.position
                        print(f"{name}: Position = ({pos[0]:.1f}, {pos[1]:.1f})")
                    print("===============================================\n")

        keys = pygame.key.get_pressed()
        target_bone_name = tune_targets[current_target_index]
        target_bone = character.get_bone(target_bone_name)
        
        if target_bone:
            current_speed = move_speed * (fast_multiplier if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 1.0)
            
            cx, cy = target_bone.local_transform.position
            
            if keys[pygame.K_LEFT]:
                cx -= current_speed
            if keys[pygame.K_RIGHT]:
                cx += current_speed
            if keys[pygame.K_UP]:
                cy -= current_speed
            if keys[pygame.K_DOWN]:
                cy += current_speed
                
            target_bone.local_transform.position = (cx, cy)

        character.update()
        
        screen.fill((60, 60, 60)) 
        
        character.draw(screen, debug=show_bones)
        

        if target_bone:
            gx, gy = target_bone.get_world_position()
            pygame.draw.circle(screen, (0, 255, 255), (int(gx), int(gy)), 10, 2) 
            
  
            info_text = f"Selected: {target_bone_name}"
            coord_text = f"Local Pos: ({target_bone.local_transform.position[0]:.1f}, {target_bone.local_transform.position[1]:.1f})"
            
            text_surf = font.render(target_bone_name, True, (0, 255, 255))
            screen.blit(text_surf, (gx + 15, gy - 10))

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