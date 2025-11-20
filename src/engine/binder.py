"""
Binder / Engine Core
====================
Manages the mapping between Signals and Effectors.
"""
from src.engine.signals import ContinuousSignal, TriggerSignal
from src.engine.effectors import *

class BindingEngine:
    def __init__(self, analysis_data):
        self.analysis = analysis_data
        fps = analysis_data['info']['fps']
        
        # 1. Create Signals Sources
        self.signals = {
            'volume': ContinuousSignal(analysis_data['continuous']['volume'], fps),
            'pitch':  ContinuousSignal(analysis_data['continuous']['pitch'], fps),
            'timbre': ContinuousSignal(analysis_data['continuous']['timbre'], fps),
            'beat':   TriggerSignal(analysis_data['triggers']['beats'])
        }
        
        # 2. Create Available Effectors
        self.effectors = {
            'arm_dance': ArmDancer(),
            'body_pump': BodyPumper(),
            'float':     Floater(),
            'face':      FaceExpression(),
            'head_bob':  HeadBanger(),
            'foot_tap':  FootTapper(),
            'lip_sync':  SimpleLipSync()
        }
        
        # 3. Bindings (The "Wiring")
        # Format: list of tuples (signal_name, effector_name)
        # Default bindings:
        self.continuous_bindings = [
            ('pitch', 'arm_dance'),  # Pitch drives Arms
            ('volume', 'body_pump'), # Volume drives Scale
            ('pitch', 'float')       # Pitch drives Levitation
        ]
        
        self.trigger_bindings = [
            ('beat', 'head_bob')     # Beat drives Head Bob
        ]

    def set_binding(self, signal_name, effector_name):
        """API to change bindings at runtime (for UI)."""
        # Remove any existing binding for this effector to avoid conflict?
        # Or allow multi-drive? For simplicity, let's append.
        # You might want logic to clear old bindings first.
        if signal_name == 'beat':
            self.trigger_bindings.append((signal_name, effector_name))
        else:
            self.continuous_bindings.append((signal_name, effector_name))
            
    def clear_bindings(self):
        self.continuous_bindings = []
        self.trigger_bindings = []

    def update(self, current_time, dt, character_rig):
        """
        Main loop call.
        """
        # A. Process Continuous Bindings
        for sig_name, eff_name in self.continuous_bindings:
            if sig_name in self.signals and eff_name in self.effectors:
                val = self.signals[sig_name].get_value(current_time)
                self.effectors[eff_name].update(val, character_rig)
                
        # B. Process Trigger Bindings
        # 1. Check trigger
        if self.signals['beat'].check(current_time):
            for sig_name, eff_name in self.trigger_bindings:
                if sig_name == 'beat':
                    self.effectors[eff_name].trigger()
        
        # 2. Update Trigger Animations (Decay logic)
        for _, eff_name in self.trigger_bindings:
            effector = self.effectors[eff_name]
            
            if hasattr(effector, 'update'):
                try:
                    # Trigger effectors need 'dt'
                    effector.update(dt, character_rig)
                except TypeError:
                    pass

    def remove_binding_by_effector(self, effector_id):
        """Remove any binding that targets this effector."""
        # Filter out tuples where the second element matches effector_id
        self.continuous_bindings = [
            (s, e) for s, e in self.continuous_bindings if e != effector_id
        ]
        self.trigger_bindings = [
            (s, e) for s, e in self.trigger_bindings if e != effector_id
        ]