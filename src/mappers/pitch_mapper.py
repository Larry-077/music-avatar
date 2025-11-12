"""
PitchMapper - Pitch Mapping System
==================================
Maps musical pitch (frequency) to the character’s vertical floating motion.

Mapping logic:
- High pitch → character floats upward
- Low pitch → character sinks downward
- Smooth interpolation is applied to avoid jitter.
"""

import numpy as np


class PitchMapper:
    """
    Maps music pitch to the character's vertical position (floating effect).
    """
    
    def __init__(self,
                 float_range=50,        # Floating range in pixels; ±50 means total 100px motion
                 smoothing=0.15,        # Smoothing factor (0–1). Smaller = smoother, slower motion
                 pitch_min=50,          # Minimum pitch frequency (Hz)
                 pitch_max=500,         # Maximum pitch frequency (Hz)
                 base_y=400):           # Character’s base Y position
        """
        Initialize the PitchMapper.
        
        Args:
            float_range: Max vertical displacement range in pixels.
            smoothing: Smoothing coefficient. 0 = very smooth (slow), 1 = no smoothing (instant).
            pitch_min: Minimum pitch value to map.
            pitch_max: Maximum pitch value to map.
            base_y: The base vertical Y-coordinate of the character.
        """
        self.float_range = float_range
        self.smoothing = smoothing
        self.pitch_min = pitch_min
        self.pitch_max = pitch_max
        self.base_y = base_y
        
        # State tracking
        self.current_offset = 0.0   # Current smoothed offset (pixels)
        self.target_offset = 0.0    # Target offset based on pitch (pixels)
        
        # Will be computed from the pitch array length and duration
        self.sample_rate = None     
        
        # Debug
        self.debug = False
    
    def _normalize_pitch(self, pitch):
        """
        Normalize pitch to a 0.0–1.0 range.
        
        Args:
            pitch: Raw pitch value (Hz)
            
        Returns:
            Normalized pitch (0.0 = low, 1.0 = high)
        """
        if pitch == 0:
            # Silence or pitch not detected
            return 0.5  # Neutral midpoint
        
        # Clamp to [pitch_min, pitch_max]
        pitch = max(self.pitch_min, min(self.pitch_max, pitch))
        
        # Normalize to [0, 1]
        normalized = (pitch - self.pitch_min) / (self.pitch_max - self.pitch_min)
        return normalized
    
    def _get_pitch_at_time(self, pitch_data, current_time, duration):
        """
        Get the pitch value corresponding to the current playback time.
        
        Args:
            pitch_data: Array of pitch values
            current_time: Current playback time (seconds)
            duration: Total audio duration (seconds)
            
        Returns:
            Pitch value at that time (Hz)
        """
        if not pitch_data or len(pitch_data) == 0:
            return 0
        
        # Compute sampling rate once
        if self.sample_rate is None:
            self.sample_rate = len(pitch_data) / duration
            if self.debug:
                print(f"📊 Pitch sample rate: {self.sample_rate:.2f} Hz")
        
        frame_index = int(current_time * self.sample_rate)
        frame_index = max(0, min(len(pitch_data) - 1, frame_index))
        
        return pitch_data[frame_index]
    
    def _calculate_target_offset(self, normalized_pitch):
        """
        Convert normalized pitch to a vertical offset value.
        
        Args:
            normalized_pitch: Pitch normalized to 0.0–1.0
            
        Returns:
            Target offset (pixels)
        """
        # Map 0.0–1.0 → -float_range to +float_range
        # 0.5 = neutral, 0.0 = lowest, 1.0 = highest
        offset = (normalized_pitch - 0.5) * 2 * self.float_range
        
        # In Pygame, +Y is downward, so high pitch should move upward (negative offset)
        return -offset
    
    def _smooth_offset(self, dt):
        """
        Smoothly interpolate current offset toward target offset.
        
        Args:
            dt: Time delta (seconds)
        """
        # Linear interpolation (lerp)
        # Higher smoothing = faster response
        t = min(1.0, self.smoothing * dt * 60)  # Normalize to ~60 FPS
        self.current_offset += (self.target_offset - self.current_offset) * t
    
    def map(self, music_features, character_rig, current_time, dt=0.016):
        """
        Map pitch data to the character’s vertical floating motion.
        
        Args:
            music_features: Music analysis data containing 'pitch' array and total 'duration_seconds'
            character_rig: CharacterRig instance to move
            current_time: Current playback time (seconds)
            dt: Frame time step (default 1/60 sec)
        """
        pitch_data = music_features.get('pitch', [])
        duration = music_features.get('duration_seconds', 0)
        
        if not pitch_data or duration == 0:
            if self.debug:
                print("⚠️  No pitch data found")
            return
        
        # 1️⃣ Get the pitch value at the current playback time
        current_pitch = self._get_pitch_at_time(pitch_data, current_time, duration)
        
        # 2️⃣ Normalize pitch (convert Hz → [0,1])
        normalized_pitch = self._normalize_pitch(current_pitch)
        
        # 3️⃣ Compute desired target offset based on normalized pitch
        self.target_offset = self._calculate_target_offset(normalized_pitch)
        
        # 4️⃣ Smoothly interpolate current offset toward target
        self._smooth_offset(dt)
        
        # 5️⃣ Apply offset to character position
        new_y = self.base_y + self.current_offset
        root_pos = character_rig.root.local_transform.position
        character_rig.set_screen_position(root_pos[0], new_y)
        
        if self.debug:
            print(f"🎵 Pitch: {current_pitch:.1f}Hz | "
                  f"Normalized: {normalized_pitch:.2f} | "
                  f"Offset: {self.current_offset:.1f}px | "
                  f"Y: {new_y:.1f}")
    
    def reset(self):
        """Reset the mapper’s internal state."""
        self.current_offset = 0.0
        self.target_offset = 0.0
        self.sample_rate = None
    
    def set_parameters(self, float_range=None, smoothing=None, 
                       pitch_min=None, pitch_max=None, base_y=None):
        """
        Dynamically update mapper parameters.
        
        Args:
            float_range: New floating range
            smoothing: New smoothing factor
            pitch_min: New minimum pitch
            pitch_max: New maximum pitch
            base_y: New base Y position
        """
        if float_range is not None:
            self.float_range = float_range
        
        if smoothing is not None:
            self.smoothing = max(0.01, min(1.0, smoothing))
        
        if pitch_min is not None:
            self.pitch_min = pitch_min
        
        if pitch_max is not None:
            self.pitch_max = pitch_max
        
        if base_y is not None:
            self.base_y = base_y
        
        if self.debug:
            print(f"🔧 PitchMapper parameters updated:")
            print(f"   Float range: ±{self.float_range}px")
            print(f"   Smoothing: {self.smoothing:.2f}")
            print(f"   Pitch range: {self.pitch_min}-{self.pitch_max}Hz")
            print(f"   Base Y: {self.base_y}")


# --- Test Code ---
if __name__ == "__main__":
    """
    Test PitchMapper’s pitch-to-motion mapping.
    """
    print("=" * 60)
    print("PitchMapper Test")
    print("=" * 60)
    
    mapper = PitchMapper(
        float_range=50,
        smoothing=0.15,
        pitch_min=100,
        pitch_max=400,
        base_y=400
    )
    mapper.debug = True
    
    fake_music = {
        'pitch': [100, 120, 150, 180, 220, 260, 300, 350, 400] * 10,  # repeating pattern
        'duration_seconds': 3.0
    }
    
    class FakeRig:
        def __init__(self):
            self.root = type('obj', (object,), {
                'local_transform': type('obj', (object,), {
                    'position': (400, 400)
                })()
            })()
            self.y = 400
        
        def set_screen_position(self, x, y):
            self.y = y
            print(f"    → Character position: ({x:.0f}, {y:.0f})")
    
    fake_rig = FakeRig()
    
    print("\n🎵 Simulating music playback with pitch changes...\n")
    
    dt = 0.016  # 60 FPS
    current_time = 0.0
    max_time = 3.0
    
    frame = 0
    while current_time < max_time:
        if frame % 30 == 0:
            print(f"\n--- Time: {current_time:.2f}s ---")
        mapper.map(fake_music, fake_rig, current_time, dt)
        
        current_time += dt
        frame += 1
    
    print("\n✅ Test complete!")
    print(f"   Final offset: {mapper.current_offset:.1f}px")
    print(f"   Final Y position: {fake_rig.y:.1f}")
