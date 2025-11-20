"""
Animation Effectors
===================
Classes that take a 0.0-1.0 input and drive CharacterRig properties.
"""
import math
import time
import random

# --- Base Class ---
class Effector:
    def update(self, value, character):
        pass


class ArmDancer(Effector):
    """Controls arm elevation and hand sprites based on intensity."""
    def __init__(self, smoothing=0.1):
        self.current_shoulder = 0.0
        self.current_elbow = 0.0
        self.smoothing = smoothing 
        
        self.base_shoulder = 30.0   
        self.base_elbow = 10.0      
        
        self.range_shoulder = 100.0  
        self.range_elbow = 80.0    

    def update(self, value, character):
    
        target_shoulder = self.base_shoulder + (value * self.range_shoulder)
        
        target_elbow = self.base_elbow + (value * self.range_elbow)
        
        hand_variant = "rest"
        if value > 0.85: hand_variant = "high" 
        elif value > 0.4: hand_variant = "open"
        elif value > 0.1: hand_variant = "curl"
        
    
        self.current_shoulder += (target_shoulder - self.current_shoulder) * self.smoothing
        self.current_elbow += (target_elbow - self.current_elbow) * self.smoothing
        
        character.set_arm_joint_rotation("left", self.current_shoulder, self.current_elbow)
        character.set_hand_variant("left", f"L_hand_{hand_variant}")
        
        character.set_arm_joint_rotation("right", -self.current_shoulder, -self.current_elbow)
        character.set_hand_variant("right", f"R_hand_{hand_variant}")

class BodyPumper(Effector):
    """Scales the body size based on intensity."""
    def __init__(self, min_scale=0.95, max_scale=1.55):
        self.min_s = min_scale
        self.max_s = max_scale
        self.smoothing = 0.03 
        self.current_val = 0.0
        
    def update(self, value, character):
        if value < 0.1: value = 0.0
        self.current_val += (value - self.current_val) * self.smoothing
        scale = self.min_s + (self.max_s - self.min_s) * self.current_val
        character.set_body_scale(scale)

class Floater(Effector):
    """Levitates the character vertically."""
    def __init__(self, max_offset=200):
        self.max_offset = max_offset
        self.smoothing = 0.02
        self.current_val = 0.0
        self.base_y = None 
        self.idle_time = 0.0
        
    def update(self, value, character):
        current_x, current_y = character.root.local_transform.position
        if self.base_y is None:
            self.base_y = current_y
            
        self.current_val += (value - self.current_val) * self.smoothing
        music_offset = self.current_val * self.max_offset
        self.idle_time += 0.02 
        idle_offset = math.sin(self.idle_time) * 5
        target_y = self.base_y - music_offset + idle_offset
        
        character.set_screen_position(current_x, target_y)

class FaceExpression(Effector):
    """
    Controls facial features: Eyebrows height, Mouth scale.
    (Smoother & More Exaggerated Version)
    """
    def __init__(self):
        self.current_brow_offset = 0.0
        self.current_scale = 1.0
        
        self.smoothing = 0.05
        
        self.max_brow_raise = -60.0  
        self.max_mouth_scale = 3  

    def update(self, value, character):
        if value < 0.05: 
            value = 0.0
        else:
            value = (value - 0.05) / 0.95
            
        boosted_value = value * 2.5
        
        boosted_value = min(1.0, boosted_value)
        
        exaggerated_value = math.pow(boosted_value, 2.0) 
        
        target_brow = exaggerated_value * self.max_brow_raise
        target_scale = 1.0 + (exaggerated_value * (self.max_mouth_scale - 1.0))
        
        self.current_brow_offset += (target_brow - self.current_brow_offset) * self.smoothing
        self.current_scale += (target_scale - self.current_scale) * self.smoothing
        
        character.set_eyebrow_height(self.current_brow_offset)
        character.set_face_scale(self.current_scale)
# --- 2. Trigger Effectors (Input: Boolean/Pulse) ---

class HeadBanger(Effector):
    """Nods head on trigger. (Softer Decay)"""
    def __init__(self):
        self.timer = 0.0
        self.duration = 0.2 
        self.active = False
        self.bob_amount = 15
        self.current_offset = 0.0
        
    def trigger(self):
        self.active = True
        self.timer = self.duration
        
    def update(self, dt, character):
        target_offset = 0.0
        
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False
            else:
                progress = self.timer / self.duration
                target_offset = self.bob_amount * math.sin(progress * 3.14)

        self.current_offset += (target_offset - self.current_offset) * 0.2
        
        character.set_head_position_offset(0, self.current_offset)



class FootTapper(Effector):
    """
    Scales the legs/feet on beat trigger.
    """
    def __init__(self):
        self.scale_timer = 0.0
        self.duration = 0.25      
        self.max_scale = 1.2     
        self.current_scale = 1.0
        self.triggered = False

    def trigger(self):
        self.triggered = True
        self.scale_timer = self.duration

    def update(self, dt, character):
        target_scale = 1.0
        
        if self.triggered:
            self.scale_timer -= dt
            if self.scale_timer <= 0:
                self.triggered = False
            else:
                progress = self.scale_timer / self.duration
                
                target_scale = 1.0 + (self.max_scale - 1.0) * math.sin(progress * 3.14)

    
        self.current_scale += (target_scale - self.current_scale) * 0.3
        
        feet_bone = character.get_bone("Feet")
        
        if feet_bone:
            feet_bone.set_scale(self.current_scale, self.current_scale)
            

class SimpleLipSync(Effector):
    """
    Simulates lip sync by switching random mouth shapes when volume is detected.
    """
    def __init__(self):
        self.last_switch_time = 0
        self.switch_interval = 0.6  
        self.silence_timer = 0.0 
        self.silence_threshold = 0.15 
        
        self.open_mouths = ["1", "2", "3", "4"]
        self.closed_mouth = "Sil" 
        self.current_mouth = self.closed_mouth

    def update(self, value, character):
        now = time.time()
        
        if value < 0.1:
            
            self.silence_timer += 0.016 
        else:
            
            self.silence_timer = 0.0

        if self.silence_timer > self.silence_threshold:
            if self.current_mouth != self.closed_mouth:
                character.set_mouth_variant(self.closed_mouth)
                self.current_mouth = self.closed_mouth
        else:
            
            if now - self.last_switch_time > self.switch_interval:
                new_mouth = random.choice(self.open_mouths)
                while new_mouth == self.current_mouth and len(self.open_mouths) > 1:
                    new_mouth = random.choice(self.open_mouths)
                
                character.set_mouth_variant(new_mouth)
                self.current_mouth = new_mouth
                self.last_switch_time = now