"""
Character Rig Builder
=====================
This module builds a complete rigged character from your sprite assets,
using the hierarchical bone system.
"""

import pygame
import os
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
        
        # Load eye variants
        # --- Load eye variants from folder ---
        eye_variants = self._load_asset_variants("eyes")

        if eye_variants:
            # Pick the first one as default
            default_key = list(eye_variants.keys())[0]
            self.eye_variants = SpriteVariant(eye_variants, default=default_key)
            print(f"  ✅ Loaded {len(eye_variants)} eye variants from 'eyes/' folder:")
            for name in eye_variants.keys():
                print(f"     - {name}")
        else:
            # Fallback placeholder
            print("  ⚠️  No eye variants found in 'eyes/' folder, creating placeholder")
            placeholder = pygame.Surface((50, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(placeholder, (0, 0, 0), (0, 0, 50, 20))
            self.eye_variants = SpriteVariant({'default': placeholder})

        
        if eye_variants:
            self.eye_variants = SpriteVariant(eye_variants, default=list(eye_variants.keys())[0])
            print(f"  Loaded {len(eye_variants)} eye variants")
        else:
            # Fallback: create a simple eye sprite
            print("  Warning: No eye variants found, creating placeholder")
            placeholder = pygame.Surface((50, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(placeholder, (0, 0, 0), (0, 0, 50, 20))
            self.eye_variants = SpriteVariant({'default': placeholder})
        
        # TODO: Load mouth/eyebrow/hand variants from folders
        # For now, we'll use the face sprite itself
        
        print("Assets loaded successfully!")
    
    def _build_skeleton(self):
        """
        Build the complete bone hierarchy.
        
        Hierarchy:
        Root (screen position)
        └── Body
            ├── Legs (below body)
            ├── Collar (on body)
            ├── Head
            │   ├── Hat
            │   ├── Face
            │   ├── Eyes
            │   ├── Eyebrows
            │   └── Mouth
            ├── LeftArm
            │   └── LeftHand
            └── RightArm
                └── RightHand
        """
        print("Building skeleton...")
        
        # --- ROOT (screen anchor point) ---
        self.root = Bone(
            name="Root",
            local_transform=Transform(position=(400, 400))  # Default screen center
        )
        
        # --- BODY (main torso, 无 sprite)
        body_bone = Bone(
            name="Body",
            local_transform=Transform(position=(0, 0)),
            sprite=None,  # ← Body 本身不画图
            anchor_point=(0.5, 0.5)
        )
        self.root.add_child(body_bone)

        # ⭐ 先添加 LEGS（子节点，先画 = 底层）
        legs_bone = Bone(
            name="Legs",
            local_transform=Transform(position=(0, self.body_sprite.get_height() // 2 - 35)),
            sprite=self.legs_sprite,
            anchor_point=(0.5, 0.0)
        )
        body_bone.add_child(legs_bone)  # ← 先添加

        # ⭐ 再添加 BODY SPRITE（子节点，后画 = 盖住腿）
        body_sprite_bone = Bone(
            name="BodySprite",
            local_transform=Transform(position=(0, 0)),
            sprite=self.body_sprite,  # ← 真正的 body 图片在这里
            anchor_point=(0.5, 0.5)
        )
        body_bone.add_child(body_sprite_bone)  # ← 后添加

        # --- COLLAR
        collar_bone = Bone(
            name="Collar",
            local_transform=Transform(position=(0, -50)),
            sprite=self.collar_sprite,
            anchor_point=(0.5, 0.5)
        )
        body_bone.add_child(collar_bone)

        # --- HEAD
        head_bone = Bone(
            name="Head",
            local_transform=Transform(position=(0, -self.body_sprite.get_height() // 2 - 100)),
            sprite=None,
            anchor_point=(0.5, 0.5)
        )
        body_bone.add_child(head_bone)
        
        # --- FACE (base of head) ---
        face_bone = Bone(
            name="Face",
            local_transform=Transform(position=(0, 0)),
            sprite=self.face_sprite,
            anchor_point=(0.5, 0.5)
        )
        head_bone.add_child(face_bone)
        
        # --- HAT (on head) ---
        hat_bone = Bone(
            name="Hat",
            local_transform=Transform(position=(0, -self.face_sprite.get_height() // 2 + 200)),
            sprite=self.hat_sprite,
            anchor_point=(0.5, 1.0)  # Bottom-center of hat
        )
        head_bone.add_child(hat_bone)
        # --- EYES (on face) ---
        eyes_bone = Bone(
            name="Eyes",
            local_transform=Transform(position=(0, 18)),
            sprite=self.eye_variants.get_sprite(),
            anchor_point=(0.5, 0.5)
        )
        face_bone.add_child(eyes_bone)
        
        # --- EYEBROWS (above eyes) ---
        # TODO: Load actual eyebrow sprites
        eyebrows_bone = Bone(
            name="Eyebrows",
            local_transform=Transform(position=(0, -50)),
            sprite=None,  # Will be set when you add eyebrow assets
            anchor_point=(0.5, 0.5)
        )
        face_bone.add_child(eyebrows_bone)
        
        # --- MOUTH (below eyes) ---
        # TODO: Load actual mouth sprites
        mouth_bone = Bone(
            name="Mouth",
            local_transform=Transform(position=(0, 40)),
            sprite=None,  # Will be set when you add mouth assets
            anchor_point=(0.5, 0.5)
        )
        face_bone.add_child(mouth_bone)
        
        # --- LEFT ARM ---
        left_arm_bone = Bone(
            name="LeftArm",
            local_transform=Transform(position=(-self.body_sprite.get_width() // 2, 0)),
            sprite=None,  # TODO: Add arm sprite
            anchor_point=(0.5, 0.0)  # Shoulder pivot
        )
        body_bone.add_child(left_arm_bone)
        
        # --- LEFT HAND ---
        left_hand_bone = Bone(
            name="LeftHand",
            local_transform=Transform(position=(0, 80)),  # Below arm
            sprite=None,  # TODO: Add hand pose variants
            anchor_point=(0.5, 0.0)
        )
        left_arm_bone.add_child(left_hand_bone)
        
        # --- RIGHT ARM ---
        right_arm_bone = Bone(
            name="RightArm",
            local_transform=Transform(position=(self.body_sprite.get_width() // 2, 0)),
            sprite=None,  # TODO: Add arm sprite
            anchor_point=(0.5, 0.0)
        )
        body_bone.add_child(right_arm_bone)
        
        # --- RIGHT HAND ---
        right_hand_bone = Bone(
            name="RightHand",
            local_transform=Transform(position=(0, 80)),
            sprite=None,  # TODO: Add hand pose variants
            anchor_point=(0.5, 0.0)
        )
        right_arm_bone.add_child(right_hand_bone)
        
        # --- Cache bone references for easy access ---
        self._cache_bones()
        
        print(f"Skeleton built with {len(self.bones)} bones")
    
    def _cache_bones(self):
        """Build a dictionary of all bones for easy access"""
        def add_to_cache(bone):
            self.bones[bone.name] = bone
            for child in bone.children:
                add_to_cache(child)
        
        add_to_cache(self.root)
    
    def get_bone(self, name: str) -> Bone:
        """Get a bone by name"""
        return self.bones.get(name)
    
    # --- Animation Control Methods ---
    
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
        base_y = -self.body_sprite.get_height() // 2 - 130
        head.set_position(x, base_y + y)
    
    def set_eye_variant(self, variant_name: str):
        """Change eye sprite (for different directions, open/closed)"""
        if self.eye_variants.set_variant(variant_name):
            self.get_bone("Eyes").sprite = self.eye_variants.get_sprite()
    
    def set_eyebrow_height(self, offset: float):
        """Move eyebrows up/down (for expressions)"""
        eyebrow = self.get_bone("Eyebrows")
        eyebrow.set_position(0, -50 + offset)
    
    def set_arm_rotation(self, side: str, angle: float):
        """Rotate arm ('left' or 'right')"""
        bone_name = f"{side.capitalize()}Arm"
        self.get_bone(bone_name).set_rotation(angle)
    
    # --- Core Methods ---
    
    def update(self):
        """Update all bone transforms (call once per frame)"""
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
    pygame.display.set_caption("Character Rig Test")
    clock = pygame.time.Clock()
    
    # Build character (adjust path to your assets)
    current_dir = os.path.dirname(os.path.abspath(__file__))       # src/character
    project_root = os.path.abspath(os.path.join(current_dir, "../.."))  # 回到项目根目录
    assets_dir = os.path.join(project_root, "assets", "character")

    character = CharacterRig(assets_dir)
    character.print_hierarchy()
    
    # Main loop
    running = True
    debug_mode = True
    time = 0
    
    print("\nControls:")
    print("  D - Toggle debug visualization")
    print("  Arrow keys - Move character")
    print("  Q/E - Rotate head")
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
        time += 0.05
        # Head bob
        bob = 10 * (1 + 0.5 * (1 + pygame.math.Vector2(0, 1).rotate(time * 50).y))
        character.set_head_position_offset(0, bob)
        
        # Update and draw
        character.update()
        
        screen.fill((50, 50, 50))
        character.draw(screen, debug=debug_mode)
        
        # FPS counter
        fps = clock.get_fps()
        font = pygame.font.Font(None, 24)
        fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\nTest complete!")
