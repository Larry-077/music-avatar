"""
主程序 - Modern Cream & Navy UI (Final Layout)
=============================================
"""
import pygame
import os
import json
import sys

# 1. 路径设置
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.character.character_rig import CharacterRig
from src.engine.binder import BindingEngine
from ui_components import (Button, SourceButton, EffectorButton, ConnectionLine, 
                           Label, Panel, COLOR_BG, COLOR_TEXT_MAIN)

def main():
    # 2. 初始化
    pygame.init()
    W, H = 1200, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Music Avatar Studio - Cream Edition")
    clock = pygame.time.Clock()
    
    # --- 3. 资源加载 ---
    project_root = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(project_root, "assets", "character")
    
    # 角色设置
    character = CharacterRig(assets_dir)
    character.set_screen_position(W * 0.2, H * 0.6) 
    character.set_body_scale(1.0)
    
    # 数据加载
    json_path = os.path.join(project_root, "src", "analysis_cache", "test3.json") 
    audio_path = os.path.join(project_root, "assets", "audio", "test3.wav")
    
    if not os.path.exists(json_path):
        print("❌ Error: Analysis JSON not found. Run analysis.py first.")
        return
        
    with open(json_path, 'r') as f: music_features = json.load(f)
    
    # 音频引擎
    audio_loaded = False
    if os.path.exists(audio_path):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.set_volume(1.0)
            audio_loaded = True
            # 预热
            pygame.mixer.music.play()
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"Audio Error: {e}")

    # 绑定引擎
    engine = BindingEngine(music_features)
    engine.clear_bindings() 

    # ==========================================
    # UI 布局构建 (Layout)
    # ==========================================
    
    # 基础坐标定义
    UI_X = 500 
    PANEL_W = 650
    PANEL_H = 580
    
    # 🔧 [布局核心]
    CONTROL_Y = 50    # 播放按钮悬浮在顶部
    PANEL_Y   = 110   # 面板主体下移，留出呼吸空间
    
    # 1. 控制面板背景
    main_panel = Panel(UI_X, PANEL_Y, PANEL_W, PANEL_H, "PATCH BAY")
    
    # 2. 播放控制 (使用 CONTROL_Y)
    btn_play  = Button(UI_X + PANEL_W - 250, CONTROL_Y, 70, 36, "PLAY", 14)
    btn_pause = Button(UI_X + PANEL_W - 170, CONTROL_Y, 70, 36, "PAUSE", 14)
    btn_reset = Button(UI_X + PANEL_W - 90,  CONTROL_Y, 70, 36, "RESET", 14)
    
    # 时间显示 (放在面板底部)
    lbl_time = Label(UI_X + 30, PANEL_Y + PANEL_H - 40, "00:00.00", size=20, color=(100, 100, 100), bold=True)

    # 3. 内部按钮坐标计算
    COL_IN_X = UI_X + 40
    COL_OUT_X = UI_X + PANEL_W - 180
    
    # 🔧 [布局核心] 内部元素随面板下移
    START_Y = PANEL_Y + 80 
    GAP = 60
    
    # --- 左侧 Inputs ---
    lbl_sig = Label(COL_IN_X, START_Y - 30, "INPUTS", size=14, bold=True)
    
    src_btns = []
    inputs_def = [
        ("Volume", "volume", False),
        ("Pitch", "pitch", False),
        ("Timbre", "timbre", False),
        ("Beat", "beat", True) # Beat 放在列表最后
    ]
    
    # 为了视觉分隔，我们手动处理 Beat 按钮的位置
    # 前三个是连续信号
    for i in range(3):
        text, sid, is_trig = inputs_def[i]
        btn = SourceButton(COL_IN_X, START_Y + i*GAP, 140, 40, text)
        btn.signal_id = sid
        btn.is_trigger = is_trig
        src_btns.append(btn)
        
    # Beat 按钮 (Trigger) 单独往下放一点
    TRIG_START_Y = START_Y + 3*GAP + 30
    lbl_trig = Label(COL_IN_X, TRIG_START_Y - 30, "TRIGGERS", size=14, bold=True)
    
    text, sid, is_trig = inputs_def[3] # Beat
    btn_beat = SourceButton(COL_IN_X, TRIG_START_Y, 140, 40, text)
    btn_beat.signal_id = sid
    btn_beat.is_trigger = is_trig
    src_btns.append(btn_beat)
        
    # --- 右侧 Outputs ---
    lbl_eff = Label(COL_OUT_X, START_Y - 30, "OUTPUTS", size=14, bold=True)
    
    eff_btns = []
    # 连续动作列表
    outputs_cont = [
        ("Arm Dance", "arm_dance", False),
        ("Body Pump", "body_pump", False),
        ("Levitate", "float", False),
        ("Face Expr", "face", False),
        ("Lip Sync",  "lip_sync", False),
    ]
    
    for i, (text, eid, is_trig) in enumerate(outputs_cont):
        btn = EffectorButton(COL_OUT_X, START_Y + i*GAP, 140, 40, text)
        btn.effector_id = eid
        btn.is_trigger = is_trig
        eff_btns.append(btn)
        
    # 触发动作列表 (Actions)
    ACT_START_Y = START_Y + len(outputs_cont)*GAP + 30
    lbl_act = Label(COL_OUT_X, ACT_START_Y - 30, "ACTIONS", size=14, bold=True)
    
    outputs_trig = [
        ("Head Bob", "head_bob", True),
        ("Foot Tap", "foot_tap", True)
    ]
    
    for i, (text, eid, is_trig) in enumerate(outputs_trig):
        btn = EffectorButton(COL_OUT_X, ACT_START_Y + i*GAP, 140, 40, text)
        btn.effector_id = eid
        btn.is_trigger = is_trig
        eff_btns.append(btn)

    # --- 状态管理 ---
    selected_source = None
    connections = [] 
    music_time = 0.0
    is_playing = False
    
    # 辅助：同步引擎
    def sync_bindings_to_engine():
        engine.clear_bindings()
        for conn in connections:
            s_id = conn.start_btn.signal_id
            e_id = conn.end_btn.effector_id
            engine.set_binding(s_id, e_id)
    
    # ==========================================
    # 主循环
    # ==========================================
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # 1. 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            # 播放控制
            if btn_play.handle_event(event):
                if audio_loaded and not is_playing:
                    pygame.mixer.music.unpause()
                    is_playing = True
            if btn_pause.handle_event(event):
                if audio_loaded and is_playing:
                    pygame.mixer.music.pause()
                    is_playing = False
            if btn_reset.handle_event(event):
                music_time = 0.0
                engine.signals['beat'].reset()
                if audio_loaded:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play()
                    if not is_playing: pygame.mixer.music.pause()

            # --- 连线交互 ---
            
            # A. 点击 Source
            for btn in src_btns:
                if btn.handle_event(event):
                    if selected_source == btn:
                        btn.selected = False
                        selected_source = None
                    else:
                        if selected_source: selected_source.selected = False
                        btn.selected = True
                        selected_source = btn
            
            # B. 点击 Effector
            for btn in eff_btns:
                if btn.handle_event(event):
                    if selected_source:
                        # 检查类型兼容
                        if selected_source.is_trigger != btn.is_trigger:
                            print("❌ 类型不匹配")
                        else:
                            # 检查是否已有连接 (用于Toggle)
                            existing = next((c for c in connections if c.start_btn == selected_source and c.end_btn == btn), None)
                            
                            if existing:
                                connections.remove(existing) # 断开
                            else:
                                # 移除该 Effector 的其他连接 (单驱动原则)
                                connections = [c for c in connections if c.end_btn != btn]
                                connections.append(ConnectionLine(selected_source, btn))
                            
                            sync_bindings_to_engine()
                    else:
                        print("⚠️ 请先选择左侧的一个 Source")

        # 2. 更新逻辑
        if is_playing:
            music_time += dt
            if music_time >= music_features['info']['duration']:
                music_time = 0.0
                engine.signals['beat'].reset()
                if audio_loaded: pygame.mixer.music.play()
        
        # 🔧 [视觉反馈] 更新右侧按钮的激活状态
        for btn in eff_btns: btn.active = False
        for conn in connections: conn.end_btn.active = True
        
        engine.update(music_time, dt, character)
        character.update()
        
        # 3. 绘制
        screen.fill(COLOR_BG)
        
        # 角色
        character.draw(screen)
        
        # UI 面板
        main_panel.draw(screen)
        
        # 连线
        for line in connections:
            line.draw(screen)
            
        # 按钮与标签
        btn_play.draw(screen)
        btn_pause.draw(screen)
        btn_reset.draw(screen)
        
        lbl_time.set_text(f"{int(music_time//60):02}:{music_time%60:05.2f}")
        lbl_time.draw(screen)

        lbl_sig.draw(screen)
        lbl_trig.draw(screen)
        lbl_eff.draw(screen)
        lbl_act.draw(screen)
        
        for btn in src_btns: btn.draw(screen)
        for btn in eff_btns: btn.draw(screen)
        
        pygame.display.flip()
        
    if audio_loaded: pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()