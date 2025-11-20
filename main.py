"""
 Modern UI 
=============================================
"""
import pygame
import os
import json
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.character.character_rig import CharacterRig
from src.engine.binder import BindingEngine
from ui_components import (Button, SourceButton, EffectorButton, ConnectionLine, 
                           Label, Panel, COLOR_BG, COLOR_TEXT_MAIN)

def main():
    
    pygame.init()
    W, H = 1200, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Music Avatar Studio - Cream Edition")
    clock = pygame.time.Clock()
    
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(project_root, "assets", "character")
    
    character = CharacterRig(assets_dir)
    character.set_screen_position(W * 0.2, H * 0.6) 
    character.set_body_scale(1.0)
    
    json_path = os.path.join(project_root, "src", "analysis_cache", "test3.json") 
    audio_path = os.path.join(project_root, "assets", "audio", "test3.wav")
    
    if not os.path.exists(json_path):
        print("❌ Error: Analysis JSON not found. Run analysis.py first.")
        return
        
    with open(json_path, 'r') as f: music_features = json.load(f)
    
    audio_loaded = False
    if os.path.exists(audio_path):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.set_volume(1.0)
            audio_loaded = True
            pygame.mixer.music.play()
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"Audio Error: {e}")

    engine = BindingEngine(music_features)
    engine.clear_bindings() 

   
    UI_X = 500 
    PANEL_W = 650
    PANEL_H = 580
    
    CONTROL_Y = 50    
    PANEL_Y   = 110   
    
    main_panel = Panel(UI_X, PANEL_Y, PANEL_W, PANEL_H, "PATCH BAY")
    
    btn_play  = Button(UI_X + PANEL_W - 250, CONTROL_Y, 70, 36, "PLAY", 14)
    btn_pause = Button(UI_X + PANEL_W - 170, CONTROL_Y, 70, 36, "PAUSE", 14)
    btn_reset = Button(UI_X + PANEL_W - 90,  CONTROL_Y, 70, 36, "RESET", 14)
    
    lbl_time = Label(UI_X + 30, PANEL_Y + PANEL_H - 40, "00:00.00", size=20, color=(100, 100, 100), bold=True)

    COL_IN_X = UI_X + 40
    COL_OUT_X = UI_X + PANEL_W - 180
    
    START_Y = PANEL_Y + 80 
    GAP = 60
    
    lbl_sig = Label(COL_IN_X, START_Y - 30, "MUSIC ELEMENTS", size=14, bold=True)
    
    src_btns = []
    inputs_def = [
        ("Volume", "volume", False),
        ("Pitch", "pitch", False),
        ("Timbre", "timbre", False),
        ("Beat", "beat", True) 
    ]
    
    for i in range(3):
        text, sid, is_trig = inputs_def[i]
        btn = SourceButton(COL_IN_X, START_Y + i*GAP, 140, 40, text)
        btn.signal_id = sid
        btn.is_trigger = is_trig
        src_btns.append(btn)
        
    TRIG_START_Y = START_Y + 3*GAP + 152
    lbl_trig = Label(COL_IN_X, TRIG_START_Y - 30, "TRIGGERS", size=14, bold=True)
    
    text, sid, is_trig = inputs_def[3] # Beat
    btn_beat = SourceButton(COL_IN_X, TRIG_START_Y, 140, 40, text)
    btn_beat.signal_id = sid
    btn_beat.is_trigger = is_trig
    src_btns.append(btn_beat)
        
    lbl_eff = Label(COL_OUT_X, START_Y - 30, "OUTPUTS", size=14, bold=True)
    
    eff_btns = []
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

    selected_source = None
    connections = [] 
    music_time = 0.0
    is_playing = False
    
    def sync_bindings_to_engine():
        engine.clear_bindings()
        for conn in connections:
            s_id = conn.start_btn.signal_id
            e_id = conn.end_btn.effector_id
            engine.set_binding(s_id, e_id)
    

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
     
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

            for btn in src_btns:
                if btn.handle_event(event):
                    if selected_source == btn:
                        btn.selected = False
                        selected_source = None
                    else:
                        if selected_source: selected_source.selected = False
                        btn.selected = True
                        selected_source = btn
            
            for btn in eff_btns:
                if btn.handle_event(event):
                    if selected_source:
                        if selected_source.is_trigger != btn.is_trigger:
                            print("❌")
                        else:
                            existing = next((c for c in connections if c.start_btn == selected_source and c.end_btn == btn), None)
                            
                            if existing:
                                connections.remove(existing)
                            else:
                                connections = [c for c in connections if c.end_btn != btn]
                                connections.append(ConnectionLine(selected_source, btn))
                            
                            sync_bindings_to_engine()
                    

        if is_playing:
            music_time += dt
            if music_time >= music_features['info']['duration']:
                music_time = 0.0
                engine.signals['beat'].reset()
                if audio_loaded: pygame.mixer.music.play()
        
        for btn in eff_btns: btn.active = False
        for conn in connections: conn.end_btn.active = True
        
        engine.update(music_time, dt, character)
        character.update()
        
        screen.fill(COLOR_BG)
        
        character.draw(screen)
        
        main_panel.draw(screen)
        
        for line in connections:
            line.draw(screen)
            
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