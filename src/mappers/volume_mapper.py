"""
VolumeMapper - Volume-to-Scale Mapper
=====================================
Maps the music’s loudness (volume) to the character’s body scale.

Mapping logic:
- Higher volume → character body enlarges
- Lower volume → character body shrinks
- Uses smooth interpolation to avoid abrupt changes
"""


class VolumeMapper:
    """
    Maps music volume to the character’s body scaling.
    """
    
    def __init__(self,
                 scale_min=0.9,         # Minimum scale when quiet
                 scale_max=1.15,        # Maximum scale when loud
                 smoothing=0.2,         # Smoothing factor (0–1)
                 base_scale=1.0):       # Base scale multiplier
        """
        Initialize the VolumeMapper.
        
        Args:
            scale_min: Minimum scale factor when volume = 0.
            scale_max: Maximum scale factor when volume = 1.
            smoothing: Smoothing coefficient; 0 = very smooth (slow), 1 = no smoothing (instant response).
            base_scale: Base scale multiplier.
        """
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.smoothing = smoothing
        self.base_scale = base_scale
        
        # State tracking
        self.current_scale = base_scale     # Smoothed current scale
        self.target_scale = base_scale      # Target scale determined by volume
        
        # Sample rate info (computed once)
        self.sample_rate = None
        
        # Debug mode
        self.debug = False
    
    def _get_volume_at_time(self, volume_data, current_time, duration):
        """
        Retrieve the volume value corresponding to the current playback time.
        
        Args:
            volume_data: Array of volume values (0.0–1.0)
            current_time: Current playback time in seconds
            duration: Total duration of the audio in seconds
            
        Returns:
            Volume value (0.0–1.0) at that time.
        """
        if not volume_data or len(volume_data) == 0:
            return 0.0
        
        # Compute sample rate (samples per second)
        if self.sample_rate is None:
            self.sample_rate = len(volume_data) / duration
            if self.debug:
                print(f"📊 Volume sample rate: {self.sample_rate:.2f} Hz")
        
        # Compute frame index
        frame_index = int(current_time * self.sample_rate)
        
        # Boundary check
        frame_index = max(0, min(len(volume_data) - 1, frame_index))
        
        return volume_data[frame_index]
    
    def _calculate_target_scale(self, volume):
        """
        Compute the target body scale from the given volume value.
        
        Args:
            volume: Normalized volume (0.0–1.0)
            
        Returns:
            Target body scale factor.
        """
        # Linear mapping: volume 0.0 → scale_min, volume 1.0 → scale_max
        scale = self.scale_min + volume * (self.scale_max - self.scale_min)
        
        return scale * self.base_scale
    
    def _smooth_scale(self, dt):
        """
        Smoothly transition the current scale toward the target scale.
        
        Args:
            dt: Time delta (seconds)
        """
        # Linear interpolation (lerp)
        # Higher smoothing → faster response
        t = min(1.0, self.smoothing * dt * 60)  # Normalized to 60 FPS
        
        self.current_scale += (self.target_scale - self.current_scale) * t
    
    def map(self, music_features, character_rig, current_time, dt=0.016):
        """
        Map music volume to the character’s body scale.
        
        Args:
            music_features: Music analysis data containing 'volume' array and total 'duration_seconds'
            character_rig: CharacterRig instance
            current_time: Current playback time (seconds)
            dt: Frame time delta (seconds), defaults to 1/60 (60 FPS)
        """
        # Retrieve volume data
        volume_data = music_features.get('volume', [])
        duration = music_features.get('duration_seconds', 0)
        
        if not volume_data or duration == 0:
            if self.debug:
                print("⚠️  No volume data found")
            return
        
        # Get current volume value
        current_volume = self._get_volume_at_time(volume_data, current_time, duration)
        
        # Compute target scale
        self.target_scale = self._calculate_target_scale(current_volume)
        
        # Smooth transition
        self._smooth_scale(dt)
        
        # Apply to character
        character_rig.set_body_scale(self.current_scale)
        
        if self.debug:
            print(f"🔊 Volume: {current_volume:.2f} | "
                  f"Target Scale: {self.target_scale:.3f} | "
                  f"Current Scale: {self.current_scale:.3f}")
    
    def reset(self):
        """Reset the mapper’s state."""
        self.current_scale = self.base_scale
        self.target_scale = self.base_scale
        self.sample_rate = None
    
    def set_parameters(self, scale_min=None, scale_max=None, 
                       smoothing=None, base_scale=None):
        """
        Dynamically update mapper parameters.
        
        Args:
            scale_min: New minimum scale
            scale_max: New maximum scale
            smoothing: New smoothing coefficient
            base_scale: New base scale
        """
        if scale_min is not None:
            self.scale_min = max(0.1, scale_min)
        
        if scale_max is not None:
            self.scale_max = max(self.scale_min, scale_max)
        
        if smoothing is not None:
            self.smoothing = max(0.01, min(1.0, smoothing))
        
        if base_scale is not None:
            self.base_scale = max(0.1, base_scale)
        
        if self.debug:
            print(f"🔧 VolumeMapper parameters updated:")
            print(f"   Scale range: {self.scale_min:.2f} - {self.scale_max:.2f}")
            print(f"   Smoothing: {self.smoothing:.2f}")
            print(f"   Base scale: {self.base_scale:.2f}")


# --- Test Code ---
if __name__ == "__main__":
    """
    Test VolumeMapper’s volume-to-scale mapping.
    """
    print("=" * 60)
    print("VolumeMapper Test")
    print("=" * 60)
    
    # Create mapper
    mapper = VolumeMapper(
        scale_min=0.85,
        scale_max=1.2,
        smoothing=0.2,
        base_scale=1.0
    )
    mapper.debug = True
    
    # Simulated music data (volume oscillating up and down)
    import math
    fake_music = {
        'volume': [0.5 + 0.5 * math.sin(i * 0.1) for i in range(100)],  # sinusoidal volume pattern
        'duration_seconds': 3.0
    }
    
    # Simulated character rig
    class FakeRig:
        def __init__(self):
            self.body_scale = 1.0
        
        def set_body_scale(self, scale):
            self.body_scale = scale
            print(f"    → Body scale: {scale:.3f}")
    
    fake_rig = FakeRig()
    
    # Simulate playback over time
    print("\n🎵 Simulating music playback with volume changes...\n")
    
    dt = 0.016  # 60 FPS
    current_time = 0.0
    max_time = 3.0
    
    frame = 0
    while current_time < max_time:
        # Print every 30 frames (≈0.5s)
        if frame % 30 == 0:
            print(f"\n--- Time: {current_time:.2f}s ---")
            mapper.map(fake_music, fake_rig, current_time, dt)
        else:
            mapper.map(fake_music, fake_rig, current_time, dt)
        
        current_time += dt
        frame += 1
    
    print("\n✅ Test complete!")
    print(f"   Final scale: {mapper.current_scale:.3f}")
