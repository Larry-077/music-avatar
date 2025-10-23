"""
Simple Bone System Test
========================
This script tests the basic bone system and character rig.
"""

import pygame
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.bone_system import Bone, Transform
from src.character.character_rig import CharacterRig


def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("🎭 2D Avatar Bone System Test")
    clock = pygame.time.Clock()
    
    # Path to your character assets
    assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'character')
    
    print("=" * 60)
    print("🎭 2D Avatar Animation - Bone System Test")
    print("=" * 60)
    print(f"\nLooking for assets in: {assets_path}")
    
    # Check if assets directory exists
    if not os.path.exists(assets_path):
        print(f"\n❌ Assets directory not found!")
        print(f"   Please create: {assets_path}")
        print(f"   And add your character images there.")
        return
    
    # Build character rig
    try:
        character = CharacterRig(assets_path)
        character.print_hierarchy()
        print("\n✅ Character rig built successfully!")
    except Exception as e:
        print(f"\n❌ Error building character: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test controls info
    print("\n" + "=" * 60)
    print("🎮 CONTROLS:")
    print("=" * 60)
    print("  [D]          - Toggle debug visualization")
    print("  [SPACE]      - Trigger bounce animation")
    print("  [Arrow Keys] - Move character")
    print("  [Q / E]      - Rotate head left/right")
    print("  [W / S]      - Move head up/down")
    print("  [1-5]        - Test eye variants")
    print("  [A]          - Rotate left arm")
    print("  [F]          - Rotate right arm")
    print("  [R]          - Reset all")
    print("  [ESC]        - Quit")
    print("=" * 60)
    
    # Animation state
    debug_mode = True
    time = 0
    bounce_time = 0
    is_bouncing = False
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        time += dt
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_d:
                    debug_mode = not debug_mode
                    print(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
                
                elif event.key == pygame.K_SPACE:
                    # Trigger bounce
                    is_bouncing = True
                    bounce_time = 0
                    print("🎾 Bounce!")
                
                elif event.key == pygame.K_r:
                    # Reset everything
                    character.set_screen_position(400, 400)
                    character.set_body_scale(1.0)
                    character.set_head_rotation(0)
                    character.set_head_position_offset(0, 0)
                    character.set_arm_rotation('left', 0)
                    character.set_arm_rotation('right', 0)
                    print("🔄 Reset")
                
                # Test eye variants
                elif event.key == pygame.K_1:
                    character.set_eye_variant('eyes_0001')
                    print("👀 Eye variant 1")
                elif event.key == pygame.K_2:
                    character.set_eye_variant('eyes_0002')
                    print("👀 Eye variant 2")
                elif event.key == pygame.K_3:
                    character.set_eye_variant('eyes_0003')
                    print("👀 Eye variant 3")
        
        # Continuous key presses
        keys = pygame.key.get_pressed()
        
        # Movement
        root_pos = character.root.local_transform.position
        move_speed = 200 * dt  # pixels per second
        
        new_x, new_y = root_pos
        if keys[pygame.K_LEFT]:
            new_x -= move_speed
        if keys[pygame.K_RIGHT]:
            new_x += move_speed
        if keys[pygame.K_UP]:
            new_y -= move_speed
        if keys[pygame.K_DOWN]:
            new_y += move_speed
        
        if (new_x, new_y) != root_pos:
            character.set_screen_position(new_x, new_y)
        
        # Head rotation
        head_rot = character.get_bone("Head").local_transform.rotation
        rot_speed = 90 * dt  # degrees per second
        
        if keys[pygame.K_q]:
            character.set_head_rotation(head_rot - rot_speed)
        if keys[pygame.K_e]:
            character.set_head_rotation(head_rot + rot_speed)
        
        # Head vertical movement
        head_pos = character.get_bone("Head").local_transform.position
        if keys[pygame.K_w]:
            character.set_head_position_offset(head_pos[0], head_pos[1] - move_speed)
        if keys[pygame.K_s]:
            character.set_head_position_offset(head_pos[0], head_pos[1] + move_speed)
        
        # Arm rotation
        left_arm_rot = character.get_bone("LeftArm").local_transform.rotation
        right_arm_rot = character.get_bone("RightArm").local_transform.rotation
        
        if keys[pygame.K_a]:
            character.set_arm_rotation('left', left_arm_rot + rot_speed)
        if keys[pygame.K_f]:
            character.set_arm_rotation('right', right_arm_rot - rot_speed)
        
        # --- ANIMATIONS ---
        
        # Bounce animation
        if is_bouncing:
            bounce_time += dt
            bounce_duration = 0.3
            
            if bounce_time < bounce_duration:
                # Parabolic bounce
                progress = bounce_time / bounce_duration
                bounce_offset = -30 * (progress - progress**2) * 4
                
                # Apply to body scale (squash and stretch)
                scale = 1.0 + 0.1 * (1 - abs(2 * progress - 1))
                character.set_body_scale(scale)
                
                # Apply vertical offset
                base_y = 400
                character.set_screen_position(root_pos[0], base_y + bounce_offset)
            else:
                is_bouncing = False
                character.set_body_scale(1.0)
        
        # Idle breathing animation (subtle)
        if not is_bouncing:
            breath_scale = 1.0 + 0.02 * pygame.math.Vector2(1, 0).rotate(time * 60).x
            character.set_body_scale(breath_scale)
        
        # --- UPDATE & RENDER ---
        
        character.update()
        
        # Clear screen
        screen.fill((30, 30, 40))
        
        # Draw grid (for reference)
        if debug_mode:
            grid_color = (50, 50, 60)
            for x in range(0, 800, 50):
                pygame.draw.line(screen, grid_color, (x, 0), (x, 600))
            for y in range(0, 600, 50):
                pygame.draw.line(screen, grid_color, (0, y), (800, y))
        
        # Draw character
        character.draw(screen, debug=debug_mode)
        
        # UI overlay
        font = pygame.font.Font(None, 24)
        
        # FPS
        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.0f}", True, (0, 255, 0))
        screen.blit(fps_text, (10, 10))
        
        # Debug mode indicator
        if debug_mode:
            debug_text = font.render("DEBUG MODE", True, (255, 255, 0))
            screen.blit(debug_text, (10, 35))
        
        # Position info
        pos_text = font.render(
            f"Pos: ({root_pos[0]:.0f}, {root_pos[1]:.0f})", 
            True, (200, 200, 200)
        )
        screen.blit(pos_text, (10, 60))
        
        # Rotation info
        rot_text = font.render(
            f"Head Rot: {head_rot:.1f}°", 
            True, (200, 200, 200)
        )
        screen.blit(rot_text, (10, 85))
        
        pygame.display.flip()
    
    pygame.quit()
    print("\n👋 Test complete!")


if __name__ == "__main__":
    main()
