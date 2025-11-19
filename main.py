"""
主程序 - 模块化连线交互版本 (修复交互问题版)
=================================
修复了按钮无法点击和动画不播放的问题。
"""

import pygame
import os
import json
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.character.character_rig import CharacterRig
from src.engine.binder import BindingEngine
from ui_components import Panel, Button, ToggleButton, Label, SourceButton, EffectorButton, ConnectionLine


def main():
    print("=" * 60)
    print("🎛️  Music Avatar - Modular Patching Interface")
    print("=" * 60)
    
    # 1. 初始化 Pygame
    pygame.init()
    SCREEN_W, SCREEN_H = 1200, 700
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("🎭 Music Avatar - Interactive Patching System")
    clock = pygame.time.Clock()
    
    # 2. 加载资源
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 加载角色
    assets_dir = os.path.join(project_root, "assets", "character")
    print(f"📦 Loading character from: {assets_dir}")
    character = CharacterRig(assets_dir)
    
    # 加载音乐分析数据
    json_path = os.path.join(project_root, "src", "analysis_cache", "test3.json") 
    audio_path = os.path.join(project_root, "assets", "audio", "test3.wav")
    
    if not os.path.exists(json_path):
        print(f"❌ ERROR: Analysis file not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        music_features = json.load(f)
    
    # 初始化音频
    audio_loaded = False
    if os.path.exists(audio_path):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.music.load(audio_path)
            audio_loaded = True
            print("✅ Audio loaded")
        except Exception as e:
            print(f"⚠️ Audio error: {e}")
            
    # 3. 初始化核心引擎
    print("⚙️  Initializing Binding Engine...")
    engine = BindingEngine(music_features)
    engine.clear_bindings() 
    
    # 音乐状态
    music_time = 0.0
    is_playing = False
    
    # =========================================================
    # UI 构建
    # =========================================================
    
    # --- 播放控制 ---
    # 修正点1: 不要在 Panel 里 add_component 按钮，既然我们要手动控制它们
    playback_panel = Panel(400, 20, 400, 80, "Playback")
    
    btn_play = Button(420, 45, 80, 35, "Play", color=(50, 180, 100))
    btn_pause = Button(510, 45, 80, 35, "Pause", color=(180, 100, 50))
    btn_reset = Button(600, 45, 80, 35, "Reset", color=(70, 130, 180))
    lbl_time = Label(700, 52, "0.00s", font_size=24)
    
    # --- 左侧：信号源 (Sources) ---
    source_panel = Panel(30, 150, 200, 400, "📶 Signal Sources")
    
    src_btns = []
    y_start = 200
    
    btn_vol = SourceButton(50, y_start, 160, 40, "Volume", color=(60, 60, 80))
    btn_vol.signal_id = 'volume'
    btn_vol.is_trigger = False
    src_btns.append(btn_vol)
    
    btn_pitch = SourceButton(50, y_start + 60, 160, 40, "Pitch", color=(60, 60, 80))
    btn_pitch.signal_id = 'pitch'
    btn_pitch.is_trigger = False
    src_btns.append(btn_pitch)
    
    btn_timbre = SourceButton(50, y_start + 120, 160, 40, "Timbre", color=(60, 60, 80))
    btn_timbre.signal_id = 'timbre'
    btn_timbre.is_trigger = False
    src_btns.append(btn_timbre)
    
    lbl_trig = Label(50, y_start + 180, "--- Triggers ---", (150, 150, 150), 18)
    
    btn_beat = SourceButton(50, y_start + 210, 160, 40, "Beat", color=(100, 50, 50))
    btn_beat.signal_id = 'beat'
    btn_beat.is_trigger = True
    src_btns.append(btn_beat)

    # --- 右侧：执行器 (Effectors) ---
    effector_panel = Panel(970, 150, 200, 500, "🎬 Effectors")
    
    eff_btns = []
    y_start = 200
    
    btn_arm = EffectorButton(990, y_start, 160, 40, "Arm Dance", color=(60, 80, 60))
    btn_arm.effector_id = 'arm_dance'
    btn_arm.is_trigger = False
    eff_btns.append(btn_arm)
    
    btn_pump = EffectorButton(990, y_start + 60, 160, 40, "Body Pump", color=(60, 80, 60))
    btn_pump.effector_id = 'body_pump'
    btn_pump.is_trigger = False
    eff_btns.append(btn_pump)
    
    btn_float = EffectorButton(990, y_start + 120, 160, 40, "Levitate", color=(60, 80, 60))
    btn_float.effector_id = 'float'
    btn_float.is_trigger = False
    eff_btns.append(btn_float)
    
    btn_face = EffectorButton(990, y_start + 180, 160, 40, "Face Expr", color=(60, 80, 60))
    btn_face.effector_id = 'face'
    btn_face.is_trigger = False
    eff_btns.append(btn_face)
    
    lbl_act = Label(990, y_start + 240, "--- Actions ---", (150, 150, 150), 18)
    
    btn_bob = EffectorButton(990, y_start + 270, 160, 40, "Head Bob", color=(50, 100, 50))
    btn_bob.effector_id = 'head_bob'
    btn_bob.is_trigger = True
    eff_btns.append(btn_bob)
    
    # --- UI 状态 ---
    selected_source = None
    connections = [] 
    
    # =========================================================
    # 主循环
    # =========================================================
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # 1. 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # 修正点2: 播放面板只处理拖拽，按钮单独处理
            playback_panel.handle_event(event)
            
            # 播放控制逻辑
            if btn_play.handle_event(event) and not is_playing:
                if audio_loaded: pygame.mixer.music.unpause()
                is_playing = True
                print("▶ Playing")
            
            if btn_pause.handle_event(event) and is_playing:
                if audio_loaded: pygame.mixer.music.pause()
                is_playing = False
                print("⏸ Paused")
            
            if btn_reset.handle_event(event):
                music_time = 0.0
                engine.signals['beat'].reset()
                if audio_loaded:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play()
                    if not is_playing: pygame.mixer.music.pause()
                print("🔄 Reset")
            
            # -------------------------------------------------
            # 核心连线交互逻辑 (Patching Logic)
            # -------------------------------------------------
            
            # 修正点3: handle_event 必须在循环内对所有事件调用，而不仅仅是 MOUSEBUTTONUP
            
            # A. 检查 Source 点击
            for btn in src_btns:
                if btn.handle_event(event): # 如果发生了点击
                    if selected_source == btn:
                        btn.selected = False
                        selected_source = None
                    else:
                        if selected_source: selected_source.selected = False
                        btn.selected = True
                        selected_source = btn
                        print(f"Selected Source: {btn.signal_id}")

            # B. 检查 Effector 点击
            for btn in eff_btns:
                if btn.handle_event(event): # 如果发生了点击
                    if selected_source:
                        # 尝试连接
                        if selected_source.is_trigger != btn.is_trigger:
                            print(f"❌ Compatibility Error: Cannot connect {selected_source.text} to {btn.text}")
                        else:
                            # 建立连接
                            engine.remove_binding_by_effector(btn.effector_id)
                            engine.set_binding(selected_source.signal_id, btn.effector_id)
                            
                            # 更新连线视觉
                            connections = [c for c in connections if c.end_btn != btn]
                            new_line = ConnectionLine(selected_source, btn, color=(100, 200, 255))
                            connections.append(new_line)
                            print(f"🔗 Connected: {selected_source.signal_id} -> {btn.effector_id}")
                    else:
                        # 断开连接
                        engine.remove_binding_by_effector(btn.effector_id)
                        connections = [c for c in connections if c.end_btn != btn]
                        print(f"✂️ Disconnected: {btn.effector_id}")

        # 2. 更新逻辑
        if is_playing:
            music_time += dt
            # 循环播放检查
            duration = music_features['info']['duration']
            if music_time >= duration:
                music_time = 0.0
                engine.signals['beat'].reset()
                if audio_loaded: pygame.mixer.music.play()
        
        # 引擎更新
        engine.update(music_time, dt, character)
        
        # 角色动画更新
        character.update()
        
        # 更新文本
        lbl_time.set_text(f"{music_time:.2f}s")

        # 3. 渲染绘制
        screen.fill((30, 35, 40))
        
        # A. 绘制连线
        for line in connections:
            line.draw(screen)
        
        # B. 绘制角色
        character.draw(screen)
        
        # C. 绘制 UI
        playback_panel.draw(screen)
        btn_play.draw(screen)
        btn_pause.draw(screen)
        btn_reset.draw(screen)
        lbl_time.draw(screen)
        
        source_panel.draw(screen)
        for btn in src_btns:
            btn.draw(screen)
        screen.blit(lbl_trig.font.render(lbl_trig.text, True, lbl_trig.color), (lbl_trig.x, lbl_trig.y))
            
        effector_panel.draw(screen)
        for btn in eff_btns:
            btn.draw(screen)
        screen.blit(lbl_act.font.render(lbl_act.text, True, lbl_act.color), (lbl_act.x, lbl_act.y))

        font_small = pygame.font.Font(None, 24)
        hint = font_small.render("1. Click a Source (Left)  2. Click an Effector (Right) to connect", True, (150, 150, 150))
        screen.blit(hint, (350, 660))

        pygame.display.flip()
    
    if audio_loaded: pygame.mixer.music.stop()
    pygame.quit()
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()