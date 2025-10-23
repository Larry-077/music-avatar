import librosa
import numpy as np
import json
import os

# --- Core Analysis Functions ---

def analyze_beats(y, sr):
    """
    Analyzes the beat and tempo of the audio.
    Returns a list of timestamps for each detected beat.
    """
    try:
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        # 修复: tempo 可能是数组，需要提取第一个元素
        if isinstance(tempo, np.ndarray):
            tempo_value = float(tempo[0]) if len(tempo) > 0 else float(tempo)
        else:
            tempo_value = float(tempo)
            
        print(f"Detected Tempo: {tempo_value:.2f} BPM")
        return beat_times.tolist()
    except Exception as e:
        print(f"Error analyzing beats: {e}")
        return []

def analyze_volume(y, sr):
    """
    Analyzes the volume (RMS Energy) of the audio over time.
    Returns a list of volume values, normalized between 0.0 and 1.0.
    """
    try:
        # Calculate RMS with a smaller frame length for more temporal detail
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
        
        # Normalize the RMS values to a 0-1 range for easier mapping
        rms_normalized = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6) # Add epsilon to avoid division by zero
        return rms_normalized.tolist()
    except Exception as e:
        print(f"Error analyzing volume: {e}")
        return []

def analyze_pitch(y, sr):
    """
    Analyzes the dominant pitch of the audio over time.
    Returns a list of pitch frequencies (in Hz). Zero means no clear pitch was found.
    """
    try:
        # Estimate pitch using the pyin algorithm, which is often more robust
        pitches, magnitudes, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        
        # Where magnitude is low, we can assume it's unpitched
        pitches[magnitudes < 0.1] = 0
        
        # Replace NaN with 0
        pitches = np.nan_to_num(pitches)
        return pitches.tolist()
    except Exception as e:
        print(f"Error analyzing pitch: {e}")
        return []

def analyze_articulation_proxy(y, sr):
    """
    A simple proxy for musical articulation (e.g., sharp vs. smooth sounds).
    Analyzes the "spectral centroid," which is related to the brightness of a sound.
    Higher values mean a brighter/sharper sound (like a cymbal).
    Lower values mean a darker/smoother sound (like a cello).
    Returns a list of normalized brightness values (0-1).
    """
    try:
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        # Normalize for easier mapping
        sc_normalized = (spectral_centroids - np.min(spectral_centroids)) / (np.max(spectral_centroids) - np.min(spectral_centroids) + 1e-6)
        return sc_normalized.tolist()
    except Exception as e:
        print(f"Error analyzing articulation proxy: {e}")
        return []


# --- Main Orchestrator Function ---

def analyze_song(audio_path, cache_dir="src/analysis_cache"):
    """
    Analyzes a given audio file for various musical elements.
    Checks for a cached JSON file first to speed up subsequent loads.
    
    Args:
        audio_path (str): The path to the audio file (e.g., 'assets/audio/classical_demo.wav').
        cache_dir (str): The directory to store and load cached analysis files.
        
    Returns:
        dict: A dictionary containing all the analysis data.
    """
    # Create a unique filename for the cache
    audio_filename = os.path.basename(audio_path)
    cache_filename = f"{os.path.splitext(audio_filename)[0]}.json"
    cache_filepath = os.path.join(cache_dir, cache_filename)
    
    # --- Step 1: Check for Cached Analysis ---
    if os.path.exists(cache_filepath):
        print(f"Loading analysis from cache: {cache_filepath}")
        with open(cache_filepath, 'r') as f:
            return json.load(f)
    
    print(f"No cache found. Analyzing song: {audio_filename}")
    
    # --- Step 2: Load Audio if no cache exists ---
    try:
        y, sr = librosa.load(audio_path, sr=None) # Load with original sample rate
    except Exception as e:
        print(f"Error loading audio file {audio_path}: {e}")
        return None
        
    # --- Step 3: Run All Analysis Functions ---
    analysis_data = {
        "audio_filename": audio_filename,
        "duration_seconds": librosa.get_duration(y=y, sr=sr),
        "beats": analyze_beats(y, sr),
        "volume": analyze_volume(y, sr),
        "pitch": analyze_pitch(y, sr),
        "articulation_proxy": analyze_articulation_proxy(y, sr),
        # You can add emotion analysis here later
    }
    
    # --- Step 4: Save the Analysis to Cache for next time ---
    os.makedirs(cache_dir, exist_ok=True) # Ensure the cache directory exists
    print(f"Saving analysis to cache: {cache_filepath}")
    with open(cache_filepath, 'w') as f:
        json.dump(analysis_data, f, indent=2)
        
    return analysis_data


# --- Example Usage (for testing this file directly) ---
if __name__ == '__main__':
    # Make sure you have an audio file at this path to test!
    # Create the folder assets/audio/ and place a .wav file there.
    test_audio_path = 'assets/audio/test2.wav'
    
    if not os.path.exists(test_audio_path):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"TEST WARNING: Audio file not found at '{test_audio_path}'")
        print("Please create the folders and add a .wav file to test this script.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        # Run the full analysis
        song_data = analyze_song(test_audio_path)
        
        if song_data:
            print("\n--- Analysis Complete ---")
            print(f"Duration: {song_data['duration_seconds']:.2f} seconds")
            print(f"Number of beats detected: {len(song_data['beats'])}")
            print(f"Number of volume frames: {len(song_data['volume'])}")
            print(f"Number of pitch frames: {len(song_data['pitch'])}")
            print("\nFirst 5 beat timestamps:", song_data['beats'][:5])