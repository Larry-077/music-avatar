# 🎭 2D Avatar Animation from Non-Lyrical Music
## HCI Research Project - Technical Documentation

---

## 📋 Project Overview

This project implements a **music-driven 2D character animation system** for HCI research. The system analyzes non-lyrical music and maps musical features to character animations in real-time.

### Research Goal
Investigate how different musical features (rhythm, volume, pitch, texture, emotion) can be mapped to visual character animations, and evaluate user perception of these mappings.

---

## 🏗️ System Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────┐
│     MUSIC ANALYSIS LAYER                │
│  (Extract Features from Audio)          │
│                                          │
│  • Beat/Rhythm Detection                │
│  • Volume Analysis (RMS)                │
│  • Pitch Extraction                     │
│  • Spectral Analysis (Texture)          │
│  • Emotion Classification               │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     MAPPING LAYER                       │
│  (Connect Music → Animation)            │
│                                          │
│  Configurable Mappings:                 │
│  • Rhythm    → Head Bob                 │
│  • Volume    → Body Scale               │
│  • Pitch     → Eyebrow Height           │
│  • Texture   → Eye Direction            │
│  • Emotion   → Facial Expression        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     ANIMATION LAYER                     │
│  (Bone System + Rendering)              │
│                                          │
│  Character Hierarchy:                   │
│  Root → Body → Head → Face Parts        │
│              → Arms → Hands             │
└─────────────────────────────────────────┘
```

---

## 📁 Current Project Structure

```
music-avatar-project/
│
├── assets/
│   ├── audio/                    # Music files
│   │   ├── test1.wav
│   │   └── test2.wav
│   │
│   └── character/                # Character sprites
│       ├── body.png
│       ├── face.png
│       ├── hat.png
│       ├── collar.png
│       ├── legs.png
│       ├── Stan_Eyes0001.png     # Eye variants
│       ├── Stan_Eyes0002.png
│       └── ...
│
├── src/
│   ├── core/
│   │   ├── bone.py              ✅ COMPLETE
│   │   ├── transform.py          ✅ (in bone.py)
│   │   └── asset_loader.py       ⏳ TODO
│   │
│   ├── character/
│   │   ├── rig.py               ✅ COMPLETE (character_rig.py)
│   │   └── renderer.py           ✅ (in bone.py)
│   │
│   ├── music/
│   │   ├── analyzer.py          ✅ COMPLETE (music-analyze.py)
│   │   └── feature_extractor.py  ⏳ TODO (expand analyzer)
│   │
│   ├── animation/
│   │   ├── engine.py             ⏳ TODO
│   │   ├── timeline.py           ⏳ TODO
│   │   └── easing.py             ⏳ TODO
│   │
│   ├── mappers/                  # Feature → Animation Mappers
│   │   ├── base_mapper.py        ⏳ TODO
│   │   ├── beat_mapper.py        ⏳ TODO
│   │   ├── volume_mapper.py      ⏳ TODO
│   │   ├── pitch_mapper.py       ⏳ TODO
│   │   └── emotion_mapper.py     ⏳ TODO
│   │
│   └── ui/
│       ├── mapper_config_ui.py   ⏳ TODO (Research interface)
│       └── export_ui.py          ⏳ TODO
│
├── bone_system.py               ✅ NEW! Core bone implementation
├── character_rig.py             ✅ NEW! Character setup
├── test_bone_system.py          ✅ NEW! Testing script
│
└── output/
    └── videos/                   # Exported animations
```

---

## 🦴 Bone System (COMPLETED TODAY!)

### Hierarchical Structure

```
Root (Screen Position)
└── Body (Torso)
    ├── Legs
    ├── Collar
    ├── Head
    │   ├── Hat
    │   ├── Face
    │   ├── Eyes (with variants: Stan_Eyes0001-XXXX)
    │   ├── Eyebrows (TODO: add sprite variants)
    │   └── Mouth (TODO: add phoneme shapes)
    ├── LeftArm
    │   └── LeftHand (TODO: add pose variants)
    └── RightArm
        └── RightHand (TODO: add pose variants)
```

### Key Features

- **Parent-Child Transformations**: Each bone's transform is relative to its parent
- **Automatic Propagation**: Rotating the head rotates all facial features automatically
- **Sprite Variants**: Easy switching between different eye directions, expressions, etc.
- **Debug Visualization**: Can visualize bone connections and pivot points

---

## 🎵 Music Features (PARTIALLY COMPLETE)

### Implemented (in `src/music-analyze.py`)

| Feature | Detection Method | Output |
|---------|------------------|--------|
| **Beats** | `librosa.beat.beat_track()` | List of beat timestamps |
| **Volume** | RMS energy analysis | Frame-by-frame volume (0-1) |
| **Pitch** | `librosa.pyin()` fundamental frequency | Pitch contour in Hz |
| **Articulation** | Spectral centroid | Brightness/texture (0-1) |

### To Implement

| Feature | Proposed Method | Purpose |
|---------|----------------|---------|
| **Emotion** | Valence/Arousal from spectral features | Happy/sad, calm/energetic |
| **Rhythm Pattern** | Beat strength + tempo changes | Strong vs weak beats |
| **Texture** | Spectral rolloff + ZCR | Smooth vs rough sound |

---

## 🔗 Mapping System (TODO)

### Concept

The **Mapper** is the core research component that connects music analysis to animation parameters.

### Example Mappings

```python
# Example: Beat Mapper
class BeatMapper:
    def map(self, music_features, character_rig, time):
        # On each beat, trigger head bob
        if self.is_on_beat(time, music_features['beats']):
            character_rig.set_head_position_offset(0, -10)
            # Smooth return to normal
            
# Example: Volume Mapper  
class VolumeMapper:
    def map(self, music_features, character_rig, time):
        volume = self.get_volume_at_time(time)
        # Scale body with volume (1.0 to 1.2)
        scale = 1.0 + 0.2 * volume
        character_rig.set_body_scale(scale)
```

### Configurable Interface (Research Tool)

For your HCI study, you need a UI where researchers can:

1. **Select musical feature** from dropdown (rhythm, volume, pitch, etc.)
2. **Select animation target** from dropdown (head bob, body scale, eye direction, etc.)
3. **Adjust mapping parameters** (sensitivity, range, easing)
4. **Preview in real-time**
5. **Export video** for user studies

---

## 🎯 Implementation Roadmap

### ✅ **Phase 1: Foundation (COMPLETED TODAY!)**

- [x] Bone system with parent-child hierarchy
- [x] Character rig with your sprite assets
- [x] Basic transform calculations
- [x] Debug visualization
- [x] Test script with interactive controls

### **Phase 2: Complete Character Assets (NEXT STEP)**

**Your Action Items:**
1. **Organize sprite folders:**
   ```
   assets/character/
   ├── body.png         ✅ Already have
   ├── face.png         ✅ Already have
   ├── hat.png          ✅ Already have
   ├── eyes/            📁 Create folder
   │   ├── open.png
   │   ├── half.png
   │   ├── closed.png
   │   ├── look_left.png
   │   ├── look_right.png
   │   └── ...
   ├── eyebrows/        📁 Create folder
   │   ├── neutral.png
   │   ├── happy.png
   │   ├── sad.png
   │   ├── raised.png
   │   └── ...
   ├── mouth/           📁 Create folder
   │   ├── Sil.png      (closed)
   │   ├── A.png        (open wide)
   │   ├── E.png
   │   ├── O.png
   │   └── ...          (phoneme shapes)
   ├── arms/            📁 Create folder
   │   ├── left_arm.png
   │   └── right_arm.png
   └── hands/           📁 Create folder
       ├── left_neutral.png
       ├── left_fist.png
       ├── right_point.png
       └── ...
   ```

2. **Update `character_rig.py`** to load these assets

### **Phase 3: Mapper System (1-2 weeks)**

- [ ] Create `BaseMapper` class
- [ ] Implement 5 core mappers:
  - [ ] `BeatMapper` (rhythm → head bob)
  - [ ] `VolumeMapper` (loudness → body scale)
  - [ ] `PitchMapper` (frequency → eyebrow height)
  - [ ] `TextureMapper` (brightness → eye direction)
  - [ ] `EmotionMapper` (valence/arousal → facial expression)
- [ ] Create timeline system for smooth animations
- [ ] Add easing functions (ease-in, ease-out, etc.)

### **Phase 4: Research Interface (1-2 weeks)**

- [ ] **Desktop App (PyQt5 or Pygame GUI)**
  - Dropdown menus for feature/animation selection
  - Real-time preview window
  - Parameter sliders
  - Video export button
  
- [ ] **OR Web App (Flask + p5.js)**
  - Better for remote user studies
  - Shareable links
  - Results collection

### **Phase 5: User Study Tools (1 week)**

- [ ] Batch video export
- [ ] Condition randomization
- [ ] Survey integration
- [ ] Data logging

---

## 🚀 How to Run (Current State)

### Prerequisites

```bash
pip install pygame numpy librosa
```

### Test the Bone System

```bash
python test_bone_system.py
```

**Controls:**
- `D` - Toggle debug mode
- Arrow keys - Move character
- `Q`/`E` - Rotate head
- `SPACE` - Trigger bounce animation
- `1`-`5` - Test eye variants

### Analyze Music

```bash
cd src
python music-analyze.py
```

Output saved to `src/analysis_cache/test2.json`

---

## 🤔 Design Decisions & Rationale

### Why Desktop App First?

1. **Performance**: Real-time rendering is smoother
2. **Control**: Full access to system resources
3. **Offline Use**: No server needed during development
4. **Video Export**: Direct file generation
5. **Can add web export later** if needed

### Why Bone System Instead of Simple Sprites?

1. **Hierarchical Control**: Moving the head automatically moves all facial features
2. **Realistic Motion**: Proper parent-child relationships
3. **Scalability**: Easy to add new body parts
4. **Research Flexibility**: Can test different rigging approaches

### Why Separate Mappers?

1. **Modularity**: Each mapper is independent
2. **A/B Testing**: Easy to swap mappers for comparison
3. **Research Focus**: Each mapper tests a specific hypothesis
4. **User Control**: Researchers can enable/disable mappers

---

## 📝 Next Steps for You

### Immediate (Today/Tomorrow):

1. **Test the bone system:**
   ```bash
   python test_bone_system.py
   ```

2. **Verify your assets load correctly**
   - Check that body.png, face.png, etc. appear
   - Test eye variants with number keys

3. **Organize remaining sprites** into folders (see Phase 2 above)

### This Week:

1. **Add mouth/eyebrow assets** to character rig
2. **Create first mapper** (I recommend starting with BeatMapper - easiest!)
3. **Test music sync** - load a song and trigger head bob on beats

### Next Week:

1. **Implement remaining mappers**
2. **Create configuration UI**
3. **Start collecting test videos**

---

## 🆘 Troubleshooting

### "Assets not found"
- Make sure `assets/character/` folder exists
- Check that image files are PNG format
- Verify file names match exactly

### "No eye variants loaded"
- Check that Stan_Eyes files are in `assets/character/`
- Files should be named `Stan_Eyes0001.png`, `Stan_Eyes0002.png`, etc.

### Performance issues
- Reduce screen resolution
- Disable debug mode (`D` key)
- Use smaller sprite images

---

## 📚 Technical References

### Libraries Used

- **Pygame**: 2D rendering and animation
- **NumPy**: Matrix transformations
- **Librosa**: Music analysis
- **PyQt5** (future): UI for mapper configuration

### Key Algorithms

- **Transform Hierarchy**: Matrix multiplication for nested transforms
- **Beat Detection**: Onset strength envelope + peak picking
- **Spectral Analysis**: Short-time Fourier transform (STFT)
- **Easing Functions**: Robert Penner's easing equations (to be added)

---

## 🎓 For Your HCI Paper

### What You Can Write About:

1. **Technical Contribution**: Novel mapping between music features and 2D animation
2. **System Design**: Modular, configurable mapper architecture
3. **User Study**: Perception of different music-to-motion mappings
4. **Evaluation Metrics**: 
   - Perceived naturalness
   - Emotional congruence
   - Feature identification accuracy

### Example Research Questions:

- "Which musical features are most salient in driving perceived character emotion?"
- "Do users prefer literal mappings (volume → size) or abstract mappings (texture → eye direction)?"
- "Can non-musicians identify which musical feature is controlling the animation?"

---

## 📞 Questions?

This is a solid foundation! The bone system is working, and you have a clear path forward. Focus on:

1. **Assets organization** (this week)
2. **First mapper** (BeatMapper - should take ~2-3 hours)
3. **Music sync test** (load song + trigger animations)

You're in great shape for an HCI project! 🎉

---

*Last Updated: 2025-10-22*
*Status: Phase 1 Complete ✅ | Phase 2 In Progress ⏳*
