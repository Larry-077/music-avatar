# 🚀 Quick Start Guide

## What We Accomplished Today ✅

1. **Built a complete hierarchical bone system** (`bone_system.py`)
   - Parent-child transformations
   - Matrix-based calculations
   - Sprite variant support

2. **Created character rig** (`character_rig.py`)
   - Integrates all your body parts
   - Loads eye variants automatically
   - Provides clean animation API

3. **Made interactive test** (`test_bone_system.py`)
   - Real-time control
   - Debug visualization
   - Example animations

---

## 🎯 Your Next 3 Steps

### Step 1: Test the System (5 minutes)

```bash
# Navigate to your project folder
cd /path/to/music-avatar-project

# Copy the new files to your project
cp bone_system.py src/core/
cp character_rig.py src/character/
cp test_bone_system.py .

# Run the test
python test_bone_system.py
```

**Expected Result:** You should see your character on screen with interactive controls!

---

### Step 2: Organize Your Assets (30 minutes)

Create this folder structure in `assets/character/`:

```
assets/character/
├── eyes/
│   ├── open_neutral.png
│   ├── half_closed.png
│   ├── closed_blink.png
│   ├── look_left.png
│   ├── look_right.png
│   ├── look_up.png
│   └── look_down.png
│
├── eyebrows/
│   ├── neutral.png
│   ├── happy_raised.png
│   ├── sad_lowered.png
│   ├── angry_furrowed.png
│   └── surprised.png
│
├── mouth/
│   ├── Sil.png      # Silent (closed)
│   ├── A.png        # Open wide
│   ├── E.png        # Smile shape
│   ├── O.png        # Round
│   ├── U.png        # Pursed
│   └── M.png        # Closed lips
│
├── arms/
│   ├── left_arm.png
│   └── right_arm.png
│
└── hands/
    ├── left_open.png
    ├── left_fist.png
    ├── left_point.png
    ├── right_open.png
    ├── right_fist.png
    └── right_point.png
```

**Tips:**
- Move your existing `Stan_Eyes0001.png` files into `eyes/` folder
- Rename them to descriptive names (e.g., `Stan_Eyes0001.png` → `open_neutral.png`)
- Create simple placeholder images for missing parts (you can refine later)

---

### Step 3: Create Your First Mapper (2-3 hours)

Create `src/mappers/beat_mapper.py`:

```python
"""
Beat Mapper - Maps musical beats to head bobbing animation
"""

import time
from src.character.rig import CharacterRig

class BeatMapper:
    def __init__(self):
        self.last_beat_time = 0
        self.bob_duration = 0.2  # seconds
        
    def is_on_beat(self, current_time, beats):
        """Check if we're on a beat"""
        for beat_time in beats:
            if abs(current_time - beat_time) < 0.05:  # 50ms tolerance
                return True
        return False
    
    def map(self, music_features, character_rig, current_time):
        """Apply beat-driven head bob animation"""
        beats = music_features['beats']
        
        # Check if we're on a beat
        if self.is_on_beat(current_time, beats):
            # Trigger head bob
            if current_time - self.last_beat_time > 0.3:  # Prevent double-trigger
                self.last_beat_time = current_time
                character_rig.set_head_position_offset(0, -15)
        
        # Smooth return to neutral position
        time_since_beat = current_time - self.last_beat_time
        if time_since_beat < self.bob_duration:
            # Ease out
            progress = time_since_beat / self.bob_duration
            offset = -15 * (1 - progress)
            character_rig.set_head_position_offset(0, offset)
        else:
            character_rig.set_head_position_offset(0, 0)


# Test script
if __name__ == "__main__":
    import pygame
    import json
    from src.character.rig import CharacterRig
    
    # Initialize
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    character = CharacterRig("assets/character")
    mapper = BeatMapper()
    
    # Load music analysis
    with open("src/analysis_cache/test2.json", 'r') as f:
        music_features = json.load(f)
    
    # Play music and animate
    clock = pygame.time.Clock()
    start_time = time.time()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        current_time = time.time() - start_time
        
        # Apply mapper
        mapper.map(music_features, character, current_time)
        
        # Update and draw
        character.update()
        screen.fill((50, 50, 50))
        character.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
```

**Test it:**
```bash
python src/mappers/beat_mapper.py
```

You should see the character's head bob on each beat! 🎉

---

## 📊 Implementation Timeline

### This Week
- [x] Day 1: Bone system ✅ (DONE!)
- [ ] Day 2-3: Organize assets and update rig
- [ ] Day 4-5: First mapper (BeatMapper)
- [ ] Day 6-7: Test with real music

### Next Week
- [ ] VolumeMapper (body scale with loudness)
- [ ] PitchMapper (eyebrow height with pitch)
- [ ] Basic UI for mapper selection
- [ ] Video export function

### Week 3
- [ ] TextureMapper (eye direction)
- [ ] EmotionMapper (facial expressions)
- [ ] Polish and optimize
- [ ] User study preparation

---

## 🎨 Design Tips

### For Natural Motion

1. **Use Easing**: Don't jump between positions instantly
   ```python
   # Bad: Instant jump
   character.set_position(x, y)
   
   # Good: Smooth interpolation
   current_pos = character.get_position()
   new_pos = lerp(current_pos, target_pos, 0.1)  # 10% per frame
   character.set_position(new_pos)
   ```

2. **Add Anticipation**: Small movement before main action
   ```python
   # Head bob: slight up before down
   # 1. Move up 5px
   # 2. Move down 20px
   # 3. Return to 0
   ```

3. **Vary Timing**: Not all beats need same intensity
   ```python
   # Strong beats = big movement
   # Weak beats = small movement
   if beat_strength > 0.8:
       bob_amount = -20
   else:
       bob_amount = -10
   ```

---

## 🐛 Common Issues

### Character doesn't appear
- Check assets path: `assets/character/body.png` exists?
- Try absolute path in test script
- Enable debug mode to see bone structure

### Animation is choppy
- Target 60 FPS: `clock.tick(60)`
- Use delta time for smooth motion
- Reduce sprite sizes if needed

### Music sync is off
- Check audio file sample rate (librosa default: 22050 Hz)
- Adjust beat detection sensitivity
- Add manual offset parameter

---

## 🎯 Today's Deliverables

✅ **Files Ready:**
1. `bone_system.py` - Core bone implementation
2. `character_rig.py` - Character setup
3. `test_bone_system.py` - Interactive test
4. `PROJECT_DOCUMENTATION.md` - Full documentation
5. `QUICK_START.md` - This file!

✅ **System Capabilities:**
- Hierarchical bone transforms ✓
- Sprite variant switching ✓
- Debug visualization ✓
- Interactive controls ✓

⏳ **Next Phase:**
- Asset organization (your action)
- First mapper implementation (guided)
- Music synchronization test

---

## 📞 Need Help?

### If the test doesn't run:
1. Check Python version: `python --version` (need 3.7+)
2. Install dependencies: `pip install pygame numpy`
3. Verify file paths in test script

### If character looks wrong:
1. Check sprite sizes (should be ~200-400px)
2. Adjust anchor points in character_rig.py
3. Try debug mode (`D` key) to see bones

### If you want to modify:
1. Read `PROJECT_DOCUMENTATION.md` for architecture
2. Check `bone_system.py` docstrings
3. Look at test script for usage examples

---

## 🎉 You're Ready!

You have:
- ✅ A working bone system
- ✅ A complete character rig
- ✅ A test environment
- ✅ Clear next steps

**Focus on these 3 things:**
1. Get the test running
2. Organize your assets
3. Build the BeatMapper

Good luck! 🚀
