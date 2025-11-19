"""
Music Analyzer (Modular Version)
================================
Extracts normalized features from audio for 2D character animation.

Outputs two types of data:
1. Continuous Signals (0.0 - 1.0 arrays): Volume, Pitch, Centroid.
2. Trigger Signals (Timestamp lists): Beats.
"""

import librosa
import numpy as np
import json
import os

# --- Configuration ---
# HOP_LENGTH determines the "frame rate" of the analysis.
# 512 samples @ 22050Hz ~= 43 frames per second (FPS).
# This is high enough for smooth animation.
HOP_LENGTH = 512 
SAMPLE_RATE = 22050

def normalize_array(arr, min_val=None, max_val=None, use_percentile=False):
    """
    Helper to normalize an array to 0.0 - 1.0 range.
    
    Args:
        arr: Input numpy array.
        min_val: Hardcoded min (optional).
        max_val: Hardcoded max (optional).
        use_percentile: If True, uses 95th percentile as max to ignore outliers.
    """
    # Handle empty or NaN
    if len(arr) == 0: return arr
    arr = np.nan_to_num(arr)
    
    # Determine Range
    if min_val is None:
        min_val = np.min(arr)
    
    if max_val is None:
        if use_percentile:
            # Use 98% as max to avoid one loud "pop" flattening the rest of the song
            max_val = np.percentile(arr, 98)
        else:
            max_val = np.max(arr)
            
    # Avoid divide by zero
    if max_val - min_val == 0:
        return np.zeros_like(arr)
    
    # Linear Normalization formula
    norm = (arr - min_val) / (max_val - min_val)
    
    # Clip to ensure 0.0 - 1.0 limits
    return np.clip(norm, 0.0, 1.0)

def analyze_pitch_log(y, sr):
    """
    Extracts Pitch (F0) and converts to normalized Log scale (MIDI).
    Crucial for classical music to make low/high notes perceptually linear.
    """
    # 1. Extract F0 (Fundamental Frequency)
    # fmin=C2 (~65Hz), fmax=C7 (~2093Hz) covers most instruments
    f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), 
                               fmax=librosa.note_to_hz('C7'),
                               sr=sr, hop_length=HOP_LENGTH)
    
    f0 = np.nan_to_num(f0) # Replace NaNs with 0
    
    # 2. Convert to MIDI (Logarithmic Scale)
    # 0 Hz creates -inf, so we mask it
    midi_pitch = np.zeros_like(f0)
    non_zero_mask = f0 > 0
    midi_pitch[non_zero_mask] = librosa.hz_to_midi(f0[non_zero_mask])
    
    # 3. Normalize
    # Classical range: C2 (MIDI 36) to C7 (MIDI 96)
    # Any note outside this range is clamped
    normalized_pitch = normalize_array(midi_pitch, min_val=36, max_val=96)
    
    # 4. Silence Handling
    # Where f0 was 0, set normalized pitch to a neutral value (e.g., 0.0 or 0.5)
    # Here we set to 0.0 (Low) so arms drop when silent
    normalized_pitch[~non_zero_mask] = 0.0
    
    return normalized_pitch.tolist()

def analyze_volume_rms(y, sr):
    """
    Extracts Volume (RMS) and normalizes using percentile capping.
    """
    rms = librosa.feature.rms(y=y, hop_length=HOP_LENGTH)[0]
    
    # Use percentile to handle dynamic range of classical music
    return normalize_array(rms, use_percentile=True).tolist()

def analyze_centroid(y, sr):
    """
    Extracts Spectral Centroid (Brightness/Timbre).
    Low = Dark/Deep (Cello), High = Bright/Sharp (Violin/Brass).
    """
    cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=HOP_LENGTH)[0]
    
    # Log scale is often better for frequency-based features too, 
    # but linear is okay for simple brightness mapping.
    return normalize_array(cent, use_percentile=True).tolist()

def analyze_beats(y, sr):
    """
    Extracts Beat timestamps.
    """
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=HOP_LENGTH)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=HOP_LENGTH)
    return beat_times.tolist()

# --- Main Orchestrator ---

def analyze_song(audio_path, cache_dir="../analysis_cache"):
    """
    Main function to generate the standardized JSON.
    """
    filename = os.path.basename(audio_path)
    name_no_ext = os.path.splitext(filename)[0]
    cache_path = os.path.join(cache_dir, f"{name_no_ext}.json")
    
    # Check cache
    if os.path.exists(cache_path):
        print(f"📦 Loading cached analysis: {cache_path}")
        with open(cache_path, 'r') as f:
            return json.load(f)
    
    print(f"🎵 Analyzing new audio: {filename}...")
    
    # Load Audio
    try:
        y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
    except Exception as e:
        print(f"❌ Error loading audio: {e}")
        return None

    # Run Extraction
    duration = librosa.get_duration(y=y, sr=sr)
    
    data = {
        "info": {
            "filename": filename,
            "duration": duration,
            "sample_rate": sr,
            "hop_length": HOP_LENGTH,
            "fps": sr / HOP_LENGTH  # Analysis frames per second
        },
        "continuous": {
            "volume": analyze_volume_rms(y, sr),
            "pitch": analyze_pitch_log(y, sr),
            "timbre": analyze_centroid(y, sr) # renamed from articulation
        },
        "triggers": {
            "beats": analyze_beats(y, sr)
        }
    }
    
    # Save Cache
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_path, 'w') as f:
        json.dump(data, f)
    
    print(f"✅ Analysis saved to: {cache_path}")
    return data

# --- Test ---
if __name__ == "__main__":
    # Change this to your actual file path for testing
    test_path = "../../assets/audio/Hall of the Mountain King.wav" 
    
    if os.path.exists(test_path):
        result = analyze_song(test_path)
        if result:
            print(f"\n--- Analysis Summary ---")
            print(f"FPS: {result['info']['fps']:.2f}")
            print(f"Volume Frames: {len(result['continuous']['volume'])}")
            print(f"Pitch Frames: {len(result['continuous']['pitch'])}")
            print(f"Beats Detected: {len(result['triggers']['beats'])}")
    else:
        print(f"⚠️ File not found: {test_path}")