"""
Signal Sources
==============
Reads normalized data arrays and provides values synchronized to playback time.
"""

class ContinuousSignal:
    def __init__(self, data_array, fps):
        """
        Args:
            data_array (list): List of floats (0.0 - 1.0)
            fps (float): Analysis frames per second (from info.fps)
        """
        self.data = data_array
        self.fps = fps
        self.length = len(data_array)
        self.last_value = 0.0

    def get_value(self, current_time):
        """Get the value at the specific time (in seconds)."""
        if self.length == 0: 
            return 0.0
            
        # Calculate index
        idx = int(current_time * self.fps)
        
        # Clamp to boundaries
        if idx < 0: idx = 0
        if idx >= self.length: idx = self.length - 1
        
        self.last_value = self.data[idx]
        return self.data[idx]

class TriggerSignal:
    def __init__(self, timestamp_list):
        """
        Args:
            timestamp_list (list): List of float timestamps (seconds)
        """
        self.timestamps = sorted(timestamp_list)
        self.index = 0
        self.count = len(self.timestamps)
        self.tolerance = 0.05 # Time window to accept a beat

    def check(self, current_time):
        """
        Returns True if a trigger (beat) just happened.
        Optimized to scan forward linearly.
        """
        if self.index >= self.count:
            return False
        
        # Check if we passed the next timestamp
        # We use a small window to ensure we don't miss it between frames
        next_time = self.timestamps[self.index]
        
        if current_time >= next_time:
            # Trigger found! Advance index.
            self.index += 1
            return True
            
        return False

    def reset(self):
        self.index = 0