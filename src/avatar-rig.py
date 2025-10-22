# src/avatar_rig.py
import pygame
import json
import os
import time

class AvatarRig:
    def __init__(self, assets_dir, rig_config_path):
        """
        Initializes the entire avatar rig by loading assets based on the config.
        """
        self.assets_dir = assets_dir
        self.config_path = rig_config_path
        
        # --- 1. Load Core Assets ---
        self.face = self._load_image('avatar/face.png')
        self.body = self._load_image('avatar/body/torso.png')
        
        # --- 2. Load Configurable Anchors and Scales ---
        self._load_rig_config() # Loads anchors for head, mouth, etc.

        # --- 3. Load Emotional Asset Sets (Mouths, Eyebrows) ---
        self.mouth_images = self._load_asset_dict('avatar/mouth')
        self.eyebrow_images = self._load_asset_dict('avatar/eyebrows')

        # --- 4. Initialize State Variables (The "Strings" of the Puppet) ---
        # These are the variables that the main loop will control.
        self.body_scale = 1.0
        self.position = (350, 350) # Default screen position
        self.head_angle = 0.0
        self.eyebrow_shape = "neutral"
        self.eyebrow_y_offset = 0
        self.mouth_shape = "Sil"
        self.body_color = (255, 255, 255) # Default white (no tint)
        
        # --- 5. Animation-specific State ---
        self.is_bouncing = False
        self.bounce_start_time = 0
        self.bounce_duration = 0.2 # Bounce takes 0.2 seconds

    # --- Helper Methods for Loading ---
    def _load_image(self, relative_path):
        path = os.path.join(self.assets_dir, relative_path)
        return pygame.image.load(path).convert_alpha()

    def _load_asset_dict(self, relative_dir):
        asset_dict = {}
        full_dir = os.path.join(self.assets_dir, relative_dir)
        if os.path.isdir(full_dir):
            for filename in os.listdir(full_dir):
                if filename.endswith('.png'):
                    name = os.path.splitext(filename)[0]
                    asset_dict[name] = self._load_image(os.path.join(relative_dir, filename))
        return asset_dict
        
    def _load_rig_config(self):
        # Default values
        self.head_anchor = (self.body.get_width() // 2, 50) # Anchor on body
        self.mouth_anchor = (self.face.get_width() // 2, 300) # Anchor on face
        self.eyebrow_anchor = (self.face.get_width() // 2, 150) # Anchor on face
        # You can expand this to load from your rig.json, similar to your old code

    # --- Packaged Animation Functions (The Public API) ---
    
    def set_body_scale(self, scale):
        self.body_scale = max(0.1, scale) # Prevent scaling to zero

    def set_position(self, x, y):
        self.position = (x, y)

    def set_head_nod(self, angle):
        self.head_angle = angle

    def set_eyebrow_shape(self, shape_name):
        if shape_name in self.eyebrow_images:
            self.eyebrow_shape = shape_name
    
    def set_eyebrow_height(self, y_offset):
        self.eyebrow_y_offset = y_offset

    def set_mouth_shape(self, shape_name):
        if shape_name in self.mouth_images:
            self.mouth_shape = shape_name
    
    def set_emotion(self, emotion):
        if emotion == "happy":
            self.set_eyebrow_shape("happy")
            # Maybe a smile mouth shape if you have one
        elif emotion == "sad":
            self.set_eyebrow_shape("sad")
        # Add more emotions as needed

    def trigger_body_bounce(self):
        """ This is how you implement a timed animation for the beat. """
        if not self.is_bouncing:
            self.is_bouncing = True
            self.bounce_start_time = time.perf_counter()

    # --- The Main Draw Method ---
    def draw(self, screen):
        # --- Update any ongoing animations ---
        current_time = time.perf_counter()
        bounce_offset_y = 0
        if self.is_bouncing:
            elapsed = current_time - self.bounce_start_time
            if elapsed < self.bounce_duration:
                # Simple parabola for bounce: goes up then down
                progress = elapsed / self.bounce_duration
                bounce_offset_y = -50 * (progress - progress**2) * 4 # A little math for a nice arc
            else:
                self.is_bouncing = False
        
        # --- Calculate positions based on hierarchy and state ---
        
        # 1. Body
        body_scaled = pygame.transform.rotozoom(self.body, 0, self.body_scale)
        body_pos = (self.position[0] - body_scaled.get_width() // 2,
                    self.position[1] - body_scaled.get_height() // 2 + bounce_offset_y)

        # 2. Head (relative to body)
        head_scaled = pygame.transform.rotozoom(self.face, self.head_angle, self.body_scale)
        head_pos_relative = (self.head_anchor[0] * self.body_scale, self.head_anchor[1] * self.body_scale)
        head_pos = (body_pos[0] + head_pos_relative[0] - head_scaled.get_width() // 2,
                    body_pos[1] + head_pos_relative[1] - head_scaled.get_height() // 2)

        # 3. Eyebrows (relative to head)
        eyebrow_img = self.eyebrow_images.get(self.eyebrow_shape)
        if eyebrow_img:
            eyebrow_scaled = pygame.transform.rotozoom(eyebrow_img, 0, self.body_scale)
            eyebrow_pos_relative = (self.eyebrow_anchor[0] * self.body_scale,
                                   (self.eyebrow_anchor[1] + self.eyebrow_y_offset) * self.body_scale)
            eyebrow_pos = (head_pos[0] + eyebrow_pos_relative[0] - eyebrow_scaled.get_width() // 2,
                           head_pos[1] + eyebrow_pos_relative[1] - eyebrow_scaled.get_height() // 2)

        # 4. Mouth (relative to head) - your existing logic is great here
        mouth_img = self.mouth_images.get(self.mouth_shape)
        if mouth_img:
            mouth_scaled = pygame.transform.rotozoom(mouth_img, 0, self.body_scale)
            mouth_pos_relative = (self.mouth_anchor[0] * self.body_scale, self.mouth_anchor[1] * self.body_scale)
            mouth_pos = (head_pos[0] + mouth_pos_relative[0] - mouth_scaled.get_width() // 2,
                         head_pos[1] + mouth_pos_relative[1] - mouth_scaled.get_height() // 2)

        # --- Blit everything to the screen in order ---
        screen.blit(body_scaled, body_pos)
        screen.blit(head_scaled, head_pos)
        if eyebrow_img: screen.blit(eyebrow_scaled, eyebrow_pos)
        if mouth_img: screen.blit(mouth_scaled, mouth_pos)