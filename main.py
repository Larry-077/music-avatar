"""
主程序 - 图形化 UI 版本（扩展版）
=================================
使用按钮和滑块替代键盘控制
新增：眼睛动画和嘴巴动画控制
"""

import pygame
import os
import json
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.character.character_rig import CharacterRig
from src.mappers.beat_mapper import BeatMapper
from src.mappers.pitch_mapper import PitchMapper
from src.mappers.volume_mapper import VolumeMapper
from ui_components import Panel, Button, ToggleButton, Slider, Label


def main():
    """主循环 - 图形化 UI"""
    
    print("=" * 60)
    print("🎭 Music-Driven Avatar - Enhanced UI with Animations")
    print("=" * 60)
    
    # 初始化 Pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 700))
    pygame.display.set_caption("🎭 Music Avatar - UI Control Panel + Animations")
    clock = pygame.time.Clock()
    
    # 加载角色
    project_root = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(project_root, "assets", "character")
    
    print("\n📦 Loading character...")
    character = CharacterRig(assets_dir)
    
    # 加载音乐分析数据
    analysis_path = os.path.join(project_root, "src", "analysis_cache", "test2.json")
    
    print(f"\n🎵 Loading music analysis...")
    
    if not os.path.exists(analysis_path):
        print(f"❌ ERROR: Music analysis file not found!")
        return
    
    with open(analysis_path, 'r') as f:
        music_features = json.load(f)
    
    print(f"   ✅ Analysis loaded: {len(music_features['beats'])} beats detected")
    
    # 加载音频
    audio_path = os.path.join(project_root, "assets", "audio", "test2.wav")
    audio_loaded = False
    
    if os.path.exists(audio_path):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.music.load(audio_path)
            audio_loaded = True
            print("   ✅ Audio loaded")
        except Exception as e:
            print(f"   ⚠️  Audio error: {e}")
    
    # 创建 Mappers
    beat_mapper = BeatMapper(bob_amount=-25, bob_duration=0.2, easing='ease_out')
    pitch_mapper = PitchMapper(float_range=40, smoothing=0.15, pitch_min=80, pitch_max=400, base_y=450)
    volume_mapper = VolumeMapper(scale_min=0.9, scale_max=1.15, smoothing=0.2)
    
    # 音乐播放状态
    music_time = 0.0
    is_playing = False
    
    # Mapper 状态
    beat_enabled = True
    pitch_enabled = True
    volume_enabled = True
    
    # ===== 新增：生成眼睛时间线 =====
    eye_timeline = character.generate_simple_eye_timeline(duration_seconds=30)
    
    # ===== 新增：尝试加载嘴巴时间线 =====
    mouth_timeline_path = os.path.join(project_root, "src/viseme_timeline_30s.json")
    if os.path.exists(mouth_timeline_path):
        try:
            with open(mouth_timeline_path, 'r') as f:
                mouth_timeline = json.load(f)
            character.load_mouth_timeline(mouth_timeline, auto_start=True)
            print("   ✅ Mouth timeline loaded")
        except Exception as e:
            print(f"   ⚠️  Could not load mouth timeline: {e}")
    
    # ============================
    # 创建 UI 面板
    # ============================
    
    # 1. 播放控制面板
    playback_panel = Panel(820, 20, 360, 150, "🎵 Playback Control")
    
    play_button = Button(840, 70, 100, 40, "▶ Play", color=(50, 180, 100))
    pause_button = Button(950, 70, 100, 40, "⏸ Pause", color=(180, 100, 50))
    restart_button = Button(1060, 70, 100, 40, "🔄 Restart", color=(70, 130, 180))
    
    time_label = Label(840, 125, "Time: 0.00s / 0.00s", (200, 200, 200), 18)
    
    playback_panel.add_component(play_button)
    playback_panel.add_component(pause_button)
    playback_panel.add_component(restart_button)
    playback_panel.add_component(time_label)
    
    # 2. Mapper 控制面板
    mapper_panel = Panel(820, 190, 360, 250, "🎛️ Mapper Controls")
    
    beat_toggle = ToggleButton(840, 240, 320, 35, "🥁 Beat Mapper (Head Bob)", initial_state=True)
    pitch_toggle = ToggleButton(840, 285, 320, 35, "🎵 Pitch Mapper (Floating)", initial_state=True)
    volume_toggle = ToggleButton(840, 330, 320, 35, "🔊 Volume Mapper (Scale)", initial_state=True)
    
    debug_toggle = ToggleButton(840, 375, 150, 30, "🐛 Debug", initial_state=False,
                                 on_color=(100, 100, 180), off_color=(100, 100, 100))
    
    mapper_panel.add_component(beat_toggle)
    mapper_panel.add_component(pitch_toggle)
    mapper_panel.add_component(volume_toggle)
    mapper_panel.add_component(debug_toggle)
    
    # ===== 新增：动画控制按钮 =====
    blink_toggle = ToggleButton(840, 415, 150, 30, "👁️ Blink", initial_state=True,
                                 on_color=(50, 180, 100), off_color=(180, 50, 50))
    eye_anim_toggle = ToggleButton(1000, 415, 160, 30, "👀 Eye Anim", initial_state=False,
                                    on_color=(50, 180, 100), off_color=(100, 100, 100))
    
    mapper_panel.add_component(blink_toggle)
    mapper_panel.add_component(eye_anim_toggle)
    
    # 3. Beat Mapper 参数面板
    beat_param_panel = Panel(820, 460, 360, 150, "🥁 Beat Parameters")
    
    beat_amount_slider = Slider(840, 505, 320, -60, 0, -25, "Bob Amount")
    beat_duration_slider = Slider(840, 550, 320, 0.05, 0.5, 0.2, "Duration (s)")
    
    beat_param_panel.add_component(beat_amount_slider)
    beat_param_panel.add_component(beat_duration_slider)
    
    # 4. Pitch Mapper 参数面板
    pitch_param_panel = Panel(820, 460, 360, 150, "🎵 Pitch Parameters")
    pitch_param_panel.visible = False  # 默认隐藏
    
    pitch_range_slider = Slider(840, 505, 320, 0, 100, 40, "Float Range")
    pitch_smooth_slider = Slider(840, 550, 320, 0.01, 1.0, 0.15, "Smoothing")
    
    pitch_param_panel.add_component(pitch_range_slider)
    pitch_param_panel.add_component(pitch_smooth_slider)
    
    # 5. Volume Mapper 参数面板
    volume_param_panel = Panel(820, 460, 360, 150, "🔊 Volume Parameters")
    volume_param_panel.visible = False  # 默认隐藏
    
    volume_min_slider = Slider(840, 505, 320, 0.5, 1.0, 0.9, "Scale Min")
    volume_max_slider = Slider(840, 550, 320, 1.0, 1.5, 1.15, "Scale Max")
    
    volume_param_panel.add_component(volume_min_slider)
    volume_param_panel.add_component(volume_max_slider)
    
    # 6. 参数切换按钮
    param_beat_btn = Button(1000, 375, 50, 30, "Beat", color=(180, 100, 50))
    param_pitch_btn = Button(1055, 375, 50, 30, "Pitch", color=(100, 100, 100))
    param_volume_btn = Button(1110, 375, 55, 30, "Vol", color=(100, 100, 100))
    
    mapper_panel.add_component(param_beat_btn)
    mapper_panel.add_component(param_pitch_btn)
    mapper_panel.add_component(param_volume_btn)
    
    # 当前显示的参数面板
    current_param_panel = "beat"
    
    # 7. 统计信息面板
    stats_panel = Panel(820, 630, 360, 50, "📊 Statistics")
    
    stats_label = Label(840, 655, "Beats: 0 | Scale: 1.00 | Eye: 1_center", (200, 200, 200), 16)
    
    stats_panel.add_component(stats_label)
    
    # 开始播放
    if audio_loaded:
        pygame.mixer.music.play()
        is_playing = True
    
    print("\n✅ UI initialized!")
    print("=" * 60)
    
    # 主循环
    running = True
    debug_mode = False
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # ===== 新增：快捷键 =====
                elif event.key == pygame.K_e:
                    character.start_manual_blink()
                    print("👁️  Manual blink")
                elif event.key == pygame.K_t:
                    character.eye_timeline_enabled = not character.eye_timeline_enabled
                    print(f"Eye timeline: {'ON' if character.eye_timeline_enabled else 'OFF'}")
            
            # 处理所有 UI 面板事件
            playback_panel.handle_event(event)
            mapper_panel.handle_event(event)
            beat_param_panel.handle_event(event)
            pitch_param_panel.handle_event(event)
            volume_param_panel.handle_event(event)
            stats_panel.handle_event(event)
            
            # 播放控制按钮
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Play 按钮
                if play_button.is_hovered and not is_playing:
                    if audio_loaded:
                        pygame.mixer.music.unpause()
                    is_playing = True
                    print("▶️ Playing")
                
                # Pause 按钮
                elif pause_button.is_hovered and is_playing:
                    if audio_loaded:
                        pygame.mixer.music.pause()
                    is_playing = False
                    print("⏸️ Paused")
                
                # Restart 按钮
                elif restart_button.is_hovered:
                    music_time = 0.0
                    beat_mapper.reset()
                    pitch_mapper.reset()
                    volume_mapper.reset()
                    # 重置动画时间线
                    if character.eye_timeline_enabled:
                        character.eye_timeline_start_time = pygame.time.get_ticks() / 1000.0
                    if character.mouth_timeline_enabled:
                        character.mouth_timeline_start_time = pygame.time.get_ticks() / 1000.0
                    if audio_loaded:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.play()
                        if not is_playing:
                            pygame.mixer.music.pause()
                    print("🔄 Restarted")
                
                # Mapper 开关
                elif beat_toggle.is_hovered:
                    beat_enabled = beat_toggle.is_on
                    print(f"Beat Mapper: {'ON' if beat_enabled else 'OFF'}")
                
                elif pitch_toggle.is_hovered:
                    pitch_enabled = pitch_toggle.is_on
                    print(f"Pitch Mapper: {'ON' if pitch_enabled else 'OFF'}")
                
                elif volume_toggle.is_hovered:
                    volume_enabled = volume_toggle.is_on
                    print(f"Volume Mapper: {'ON' if volume_enabled else 'OFF'}")
                
                elif debug_toggle.is_hovered:
                    debug_mode = debug_toggle.is_on
                
                # ===== 新增：动画开关 =====
                elif blink_toggle.is_hovered:
                    character.blink_enabled = blink_toggle.is_on
                    print(f"Auto Blink: {'ON' if character.blink_enabled else 'OFF'}")
                
                elif eye_anim_toggle.is_hovered:
                    character.eye_timeline_enabled = eye_anim_toggle.is_on
                    if character.eye_timeline_enabled:
                        import time
                        character.eye_timeline_start_time = time.time() - music_time
                    print(f"Eye Animation: {'ON' if character.eye_timeline_enabled else 'OFF'}")
                
                # 参数面板切换
                elif param_beat_btn.is_hovered:
                    current_param_panel = "beat"
                    beat_param_panel.visible = True
                    pitch_param_panel.visible = False
                    volume_param_panel.visible = False
                    param_beat_btn.color = (180, 100, 50)
                    param_pitch_btn.color = (100, 100, 100)
                    param_volume_btn.color = (100, 100, 100)
                
                elif param_pitch_btn.is_hovered:
                    current_param_panel = "pitch"
                    beat_param_panel.visible = False
                    pitch_param_panel.visible = True
                    volume_param_panel.visible = False
                    param_beat_btn.color = (100, 100, 100)
                    param_pitch_btn.color = (180, 100, 50)
                    param_volume_btn.color = (100, 100, 100)
                
                elif param_volume_btn.is_hovered:
                    current_param_panel = "volume"
                    beat_param_panel.visible = False
                    pitch_param_panel.visible = False
                    volume_param_panel.visible = True
                    param_beat_btn.color = (100, 100, 100)
                    param_pitch_btn.color = (100, 100, 100)
                    param_volume_btn.color = (180, 100, 50)
            
            # 参数滑块更新
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                # Beat 参数
                if beat_amount_slider.dragging or (event.type == pygame.MOUSEBUTTONUP and beat_amount_slider.rect.collidepoint(event.pos)):
                    beat_mapper.bob_amount = beat_amount_slider.value
                
                if beat_duration_slider.dragging or (event.type == pygame.MOUSEBUTTONUP and beat_duration_slider.rect.collidepoint(event.pos)):
                    beat_mapper.bob_duration = beat_duration_slider.value
                
                # Pitch 参数
                if pitch_range_slider.dragging or (event.type == pygame.MOUSEBUTTONUP and pitch_range_slider.rect.collidepoint(event.pos)):
                    pitch_mapper.float_range = pitch_range_slider.value
                
                if pitch_smooth_slider.dragging or (event.type == pygame.MOUSEBUTTONUP and pitch_smooth_slider.rect.collidepoint(event.pos)):
                    pitch_mapper.smoothing = pitch_smooth_slider.value
                
                # Volume 参数
                if volume_min_slider.dragging or (event.type == pygame.MOUSEBUTTONUP and volume_min_slider.rect.collidepoint(event.pos)):
                    volume_mapper.scale_min = volume_min_slider.value
                
                if volume_max_slider.dragging or (event.type == pygame.MOUSEBUTTONUP and volume_max_slider.rect.collidepoint(event.pos)):
                    volume_mapper.scale_max = volume_max_slider.value
        
        # 更新音乐时间
        if is_playing:
            music_time += dt
            if music_time >= music_features['duration_seconds']:
                music_time = 0.0
                beat_mapper.reset()
                pitch_mapper.reset()
                volume_mapper.reset()
        
        # ===== 新增：更新嘴巴动画（如果启用）=====
        if character.mouth_timeline_enabled:
            character.update_mouth_timeline(music_time)
        
        # 应用 Mappers
        if volume_enabled:
            volume_mapper.map(music_features, character, music_time, dt)
        
        if pitch_enabled:
            pitch_mapper.map(music_features, character, music_time, dt)
        
        if beat_enabled:
            beat_mapper.map(music_features, character, music_time)
        
        # 更新角色（包括眨眼动画）
        character.update()
        
        # 更新 UI 文本
        time_label.set_text(f"Time: {music_time:.2f}s / {music_features['duration_seconds']:.2f}s")
        
        # 获取当前眼睛状态
        current_eye = character.eye_variants.current_variant if hasattr(character.eye_variants, 'current_variant') else "N/A"
        stats_label.set_text(
            f"Beats: {beat_mapper.beat_count} | "
            f"Scale: {volume_mapper.current_scale:.2f} | "
            f"Eye: {current_eye}"
        )
        
        # 渲染
        screen.fill((30, 35, 40))
        
        # 绘制角色
        character.draw(screen, debug=debug_mode)
        
        # 绘制 UI 面板
        playback_panel.draw(screen)
        mapper_panel.draw(screen)
        beat_param_panel.draw(screen)
        pitch_param_panel.draw(screen)
        volume_param_panel.draw(screen)
        stats_panel.draw(screen)
        
        # FPS 和状态
        font = pygame.font.Font(None, 20)
        fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, (100, 255, 100))
        screen.blit(fps_text, (10, 10))
        
        # 动画状态指示
        anim_status = font.render(
            f"Blink: {'ON' if character.blink_enabled else 'OFF'} | "
            f"Eye Anim: {'ON' if character.eye_timeline_enabled else 'OFF'}",
            True, (150, 150, 255)
        )
        screen.blit(anim_status, (10, 35))
        
        pygame.display.flip()
    
    # 清理
    if audio_loaded:
        pygame.mixer.music.stop()
    
    pygame.quit()
    
    print("\n" + "=" * 60)
    print("👋 Thanks for using Music Avatar!")
    print("=" * 60)


if __name__ == "__main__":
    main()