"""
Main Entry Point for 2D Avatar Animation System
================================================
This is the primary script to run your animation system.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import pygame
import json
from src.character.character_rig import CharacterRig
from src.music.analyzer import analyze_song


def main():
    """Main application loop"""
    
    print("=" * 60)
    print("🎭 2D Avatar Animation System")
    print("=" * 60)
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("🎭 Music-Driven Avatar Animation")
    clock = pygame.time.Clock()
    
    # Setup paths
    assets_path = os.path.join(project_root, "assets", "character")
    audio_path = os.path.join(project_root, "assets", "audio", "test2.wav")
    
    # Check if assets exist
    if not os.path.exists(assets_path):
        print(f"\n❌ ERROR: Assets folder not found at: {assets_path}")
        print("Please make sure assets/character/ exists with your sprite files.")
        return
    
    # Build character
    print("\n📦 Loading character...")
    try:
        character = CharacterRig(assets_path)
        print("✅ Character loaded successfully!")
        character.print_hierarchy()
    except Exception as e:
        print(f"\n❌ ERROR loading character: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Analyze music (if file exists)
    music_features = None
    if os.path.exists(audio_path):
        print(f"\n🎵 Analyzing music: {os.path.basename(audio_path)}")
        music_features = analyze_song(audio_path)
        if music_features:
            print(f"✅ Found {len(music_features['beats'])} beats")
    else:
        print(f"\n⚠️  No audio file found at: {audio_path}")
        print("Running without music sync.")
    
    # Display controls
    print("\n" + "=" * 60)
    print("🎮 CONTROLS:")
    print("=" * 60)
    print("  [D]          - Toggle debug visualization")
    print("  [SPACE]      - Bounce animation")
    print("  [Arrow Keys] - Move character")
    print("  [Q / E]      - Rotate head")
    print("  [1-5]        - Change eye variant")
    print("  [R]          - Reset")
    print("  [ESC]        - Quit")
    print("=" * 60)
    
    # Animation state
    debug_mode = False
    time = 0
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        time += dt
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_d:
                    debug_mode = not debug_mode
                    print(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
                
                elif event.key == pygame.K_r:
                    character.set_screen_position(400, 400)
                    character.set_body_scale(1.0)
                    character.set_head_rotation(0)
                    print("🔄 Reset")
                
                # Eye variants
                elif event.key == pygame.K_1:
                    character.set_eye_variant('eyes_0001')
                elif event.key == pygame.K_2:
                    character.set_eye_variant('eyes_0002')
                elif event.key == pygame.K_3:
                    character.set_eye_variant('eyes_0003')
        
        # Handle continuous input
        keys = pygame.key.get_pressed()
        
        # Movement
        pos = character.root.local_transform.position
        speed = 200 * dt
        
        new_x, new_y = pos
        if keys[pygame.K_LEFT]:
            new_x -= speed
        if keys[pygame.K_RIGHT]:
            new_x += speed
        if keys[pygame.K_UP]:
            new_y -= speed
        if keys[pygame.K_DOWN]:
            new_y += speed
        
        if (new_x, new_y) != pos:
            character.set_screen_position(new_x, new_y)
        
        # Head rotation
        head_rot = character.get_bone("Head").local_transform.rotation
        if keys[pygame.K_q]:
            character.set_head_rotation(head_rot - 90 * dt)
        if keys[pygame.K_e]:
            character.set_head_rotation(head_rot + 90 * dt)
        
        # Simple idle animation
        breath = 1.0 + 0.02 * pygame.math.Vector2(1, 0).rotate(time * 60).x
        character.set_body_scale(breath)
        
        # TODO: Add music-driven animation here
        # if music_features:
        #     # Apply beat mapper, volume mapper, etc.
        #     pass
        
        # Update and render
        character.update()
        
        screen.fill((40, 40, 50))
        character.draw(screen, debug=debug_mode)
        
        # UI
        font = pygame.font.Font(None, 24)
        fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, (0, 255, 0))
        screen.blit(fps_text, (10, 10))
        
        if debug_mode:
            debug_text = font.render("DEBUG MODE", True, (255, 255, 0))
            screen.blit(debug_text, (10, 35))
        
        pygame.display.flip()
    
    pygame.quit()
    print("\n👋 Thank you for using the animation system!")


if __name__ == "__main__":
    main()
