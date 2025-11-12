"""
BeatMapper - Rhythm Mapper
===========================
Maps musical beats to character head-bobbing animation.

Mapping logic:
- Each beat triggers one downward head bob.
- Uses easing functions for smooth animation.
- Adjustable parameters: bob amount, duration, easing type.
"""

import math


class BeatMapper:
    """
    Maps musical beats to head-bobbing animation.
    """
    
    def __init__(self, 
                 bob_amount=-20,      # Bob amplitude (negative = upward, positive = downward)
                 bob_duration=0.25,   # Duration of each bob (seconds)
                 easing='ease_out'):  # Easing function type
        """
        Initialize the BeatMapper.
        
        Args:
            bob_amount: Maximum head displacement (in pixels)
            bob_duration: Duration of the bob animation (seconds)
            easing: Type of easing function ('linear', 'ease_in', 'ease_out', 'ease_in_out')
        """
        self.bob_amount = bob_amount
        self.bob_duration = bob_duration
        self.easing_type = easing
        
        # State tracking
        self.last_beat_time = -999   # Last beat timestamp
        self.beat_tolerance = 0.05   # Time tolerance for beat detection (seconds)
        self.min_beat_interval = 0.2 # Minimum time between beats to prevent double-triggering
        
        # Debug info
        self.debug = False
        self.beat_count = 0
    
    def _ease(self, t):
        """
        Easing function.
        
        Args:
            t: Progress value (0.0 to 1.0)
            
        Returns:
            Eased progress (0.0 to 1.0)
        """
        if self.easing_type == 'linear':
            return t
        
        elif self.easing_type == 'ease_in':
            # Slow start
            return t * t
        
        elif self.easing_type == 'ease_out':
            # Slow end
            return 1 - (1 - t) * (1 - t)
        
        elif self.easing_type == 'ease_in_out':
            # Slow at both start and end
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        
        elif self.easing_type == 'bounce':
            # Bouncy effect
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 0.5 * (2 - 2 * t) * (2 - 2 * t)
        
        else:
            return t
    
    def _calculate_offset(self, time_since_beat):
        """
        Compute the current head offset based on time since last beat.
        
        Args:
            time_since_beat: Time elapsed since the last beat (seconds)
            
        Returns:
            Current head offset (pixels)
        """
        if time_since_beat >= self.bob_duration:
            # Animation finished — return to neutral position
            return 0.0
        
        # Compute progress (0.0 → 1.0)
        progress = time_since_beat / self.bob_duration
        
        # Apply easing
        eased_progress = self._ease(progress)
        
        # Compute offset: from maximum displacement back to 0
        offset = self.bob_amount * (1 - eased_progress)
        
        return offset
    
    def _find_nearest_beat(self, beats, current_time):
        """
        Find the beat closest to the current playback time.
        
        Args:
            beats: List of beat timestamps
            current_time: Current playback time (seconds)
            
        Returns:
            Nearest beat timestamp, or None if no beat is near
        """
        nearest_beat = None
        min_distance = float('inf')
        
        for beat_time in beats:
            distance = abs(current_time - beat_time)
            
            # Only consider beats close to the current time
            if distance < self.beat_tolerance and distance < min_distance:
                min_distance = distance
                nearest_beat = beat_time
        
        return nearest_beat
    
    def map(self, music_features, character_rig, current_time):
        """
        Map musical beats to character animation.
        
        Args:
            music_features: Music analysis data containing a 'beats' list
            character_rig: CharacterRig instance
            current_time: Current playback time (seconds)
        """
        # Extract beat list
        beats = music_features.get('beats', [])
        
        if not beats:
            if self.debug:
                print("⚠️  No beats found in music_features")
            return
        
        # Find the beat closest to the current time
        nearest_beat = self._find_nearest_beat(beats, current_time)
        
        # Check if a new beat should trigger
        if nearest_beat is not None:
            time_since_last = current_time - self.last_beat_time
            
            if time_since_last >= self.min_beat_interval:
                # New beat detected!
                self.last_beat_time = nearest_beat
                self.beat_count += 1
                
                if self.debug:
                    print(f"🥁 Beat #{self.beat_count} at {nearest_beat:.2f}s")
        
        # Compute current head offset
        time_since_beat = current_time - self.last_beat_time
        offset = self._calculate_offset(time_since_beat)
        
        # Apply to character rig
        character_rig.set_head_position_offset(0, offset)
        
        if self.debug and offset != 0:
            print(f"  Head offset: {offset:.1f}px (progress: {time_since_beat/self.bob_duration*100:.0f}%)")
    
    def reset(self):
        """Reset the mapper state."""
        self.last_beat_time = -999
        self.beat_count = 0
    
    def set_parameters(self, bob_amount=None, bob_duration=None, easing=None):
        """
        Dynamically update parameters.
        
        Args:
            bob_amount: New bob amplitude
            bob_duration: New duration
            easing: New easing type
        """
        if bob_amount is not None:
            self.bob_amount = bob_amount
        
        if bob_duration is not None:
            self.bob_duration = bob_duration
        
        if easing is not None:
            self.easing_type = easing
        
        if self.debug:
            print(f"🔧 Parameters updated: amount={self.bob_amount}, duration={self.bob_duration}, easing={self.easing_type}")


# --- Test code ---
if __name__ == "__main__":
    """
    Test BeatMapper’s beat detection and animation calculation.
    """
    print("=" * 60)
    print("BeatMapper Test")
    print("=" * 60)
    
    # Create mapper
    mapper = BeatMapper(bob_amount=-20, bob_duration=0.25, easing='ease_out')
    mapper.debug = True
    
    # Simulated music feature data
    fake_music = {
        'beats': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]  # One beat every 0.5 seconds
    }
    
    # Simulated character rig
    class FakeRig:
        def __init__(self):
            self.head_offset = 0
        
        def set_head_position_offset(self, x, y):
            self.head_offset = y
            print(f"    → Character head offset set to: {y:.1f}px")
    
    fake_rig = FakeRig()
    
    # Simulate playback over time
    print("\n🎵 Simulating music playback...\n")
    
    dt = 0.016  # 60 FPS
    current_time = 0.0
    max_time = 3.5
    
    while current_time < max_time:
        # Call mapper once per frame
        mapper.map(fake_music, fake_rig, current_time)
        
        current_time += dt
    
    print("\n✅ Test complete!")
    print(f"   Total beats detected: {mapper.beat_count}")
