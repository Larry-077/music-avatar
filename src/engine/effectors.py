"""
Animation Effectors
===================
Classes that take a 0.0-1.0 input and drive CharacterRig properties.
"""
import math

# --- Base Class ---
class Effector:
    def update(self, value, character):
        pass

# --- 1. Continuous Effectors (Input: 0.0 - 1.0) ---

class ArmDancer(Effector):
    """Controls arm elevation and hand sprites based on intensity."""
    def __init__(self, smoothing=0.1):
        self.current_shoulder = 0.0
        self.current_elbow = 0.0
        self.smoothing = smoothing

    def update(self, value, character):
        # 1. Define target poses based on input value (0.0 to 1.0)
        # Mapping logic:
        # 0.0 - 0.2: Rest
        # 0.2 - 0.5: Curl (Low Energy)
        # 0.5 - 0.8: Open (Medium Energy)
        # 0.8 - 1.0: High (High Energy)
        
        target_shoulder = value * 90  # 0 to 90 degrees
        target_elbow = value * 120    # 0 to 120 degrees
        
        # Hand Sprite Logic (Discrete switching)
        hand_variant = "rest"
        if value > 0.8: hand_variant = "high"
        elif value > 0.5: hand_variant = "open"
        elif value > 0.2: hand_variant = "curl"
        
        # 2. Smoothing (Lerp)
        self.current_shoulder += (target_shoulder - self.current_shoulder) * self.smoothing
        self.current_elbow += (target_elbow - self.current_elbow) * self.smoothing
        
        # 3. Apply to Rig
        # Left arm
        character.set_arm_joint_rotation("left", self.current_shoulder, self.current_elbow)
        character.set_hand_variant("left", f"L_hand_{hand_variant}")
        
        # Right arm (mirrored)
        character.set_arm_joint_rotation("right", -self.current_shoulder, -self.current_elbow)
        character.set_hand_variant("right", f"R_hand_{hand_variant}")

class BodyPumper(Effector):
    """Scales the body size based on intensity."""
    def __init__(self, min_scale=0.9, max_scale=1.15):
        self.min_s = min_scale
        self.max_s = max_scale
        
    def update(self, value, character):
        # Linear map: 0->min, 1->max
        scale = self.min_s + (self.max_s - self.min_s) * value
        character.set_body_scale(scale)

class Floater(Effector):
    """Levitates the character vertically."""
    def __init__(self, max_offset=50):
        self.max_offset = max_offset
        self.base_y = 450 # Default screen Y
        
    def update(self, value, character):
        # Map 0.0->0, 1.0->-max_offset (Upward)
        offset = -1 * (value * self.max_offset)
        # Note: You might need to get the current X from the rig if it moves horizontally
        character.set_screen_position(400, self.base_y + offset)

class FaceExpression(Effector):
    """Controls mouth and eyebrows."""
    def update(self, value, character):
        # Eyebrows go up with intensity
        brow_offset = -15 * value # Up 15 pixels
        character.set_eyebrow_height(brow_offset)
        
        # Mouth could open slightly (if you have an 'open' variant that isn't viseme)
        # For now, we just assume the timeline handles mouth, or we map scale?
        # character.set_mouth_scale(1.0 + value * 0.5) # Hypothetical method

# --- 2. Trigger Effectors (Input: Boolean/Pulse) ---

class HeadBanger(Effector):
    """Nods head on trigger."""
    def __init__(self):
        self.timer = 0.0
        self.duration = 0.15
        self.active = False
        self.bob_amount = 20
        
    def trigger(self):
        self.active = True
        self.timer = self.duration
        
    def update(self, dt, character):
        # Special update signature for triggers: needs dt (delta time)
        offset = 0
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False
            else:
                # Simple linear bob
                progress = self.timer / self.duration
                offset = self.bob_amount * math.sin(progress * 3.14)
        
        character.set_head_position_offset(0, offset)

class Jump(Effector):
    """Whole body jump on trigger."""
    def __init__(self):
        self.timer = 0
        self.active = False
        self.jump_height = 40
        
    def trigger(self):
        self.active = True
        self.timer = 0.2
        
    def update(self, dt, character):
        if not self.active: return
        
        self.timer -= dt
        if self.timer <= 0:
            self.active = False
            # Reset position handled by continuous floaters usually, 
            # but force reset here if needed:
            # character.root.local_transform.position = (400, 450) 
        else:
            # Parabolic jump curve
            y_off = -self.jump_height * math.sin((self.timer/0.2) * 3.14)
            # Apply to ROOT or BODY offset
            # Ideally apply as offset, not absolute position
            pass