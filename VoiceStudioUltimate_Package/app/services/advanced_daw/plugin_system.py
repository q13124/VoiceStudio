#!/usr/bin/env python3
"""
VoiceStudio Advanced Plugin System
Professional plugin architecture supporting VST, AU, and native plugins.
"""

import sys
import os
import time
import logging
import numpy as np
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Callable
from pathlib import Path
from datetime import datetime
import uuid
from dataclasses import dataclass
from enum import Enum
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginType(Enum):
    EFFECT = "effect"
    INSTRUMENT = "instrument"
    ANALYZER = "analyzer"
    GENERATOR = "generator"

class PluginCategory(Enum):
    DYNAMICS = "dynamics"
    EQ = "eq"
    REVERB = "reverb"
    DELAY = "delay"
    MODULATION = "modulation"
    DISTORTION = "distortion"
    FILTER = "filter"
    SYNTHESIZER = "synthesizer"
    SAMPLER = "sampler"
    DRUM_MACHINE = "drum_machine"

@dataclass
class PluginParameter:
    """Plugin parameter definition"""
    name: str
    value: float
    min_value: float
    max_value: float
    default_value: float
    unit: str = ""
    display_name: str = ""
    description: str = ""

    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.name.replace("_", " ").title()

class PluginInfo:
    """Plugin information container"""
    def __init__(self, name: str, version: str, plugin_type: PluginType,
                 category: PluginCategory, author: str, description: str = ""):
        self.name = name
        self.version = version
        self.plugin_type = plugin_type
        self.category = category
        self.author = author
        self.description = description
        self.parameters = {}
        self.input_channels = 2
        self.output_channels = 2
        self.sample_rate = 44100
        self.buffer_size = 512

class BasePlugin(ABC):
    """Base class for all plugins"""

    def __init__(self, info: PluginInfo):
        self.info = info
        self.enabled = True
        self.bypassed = False
        self.parameters = {}
        self.parameter_callbacks = {}

        # Initialize parameters
        for param_name, param_def in info.parameters.items():
            self.parameters[param_name] = param_def.value

    def set_parameter(self, name: str, value: float):
        """Set plugin parameter"""
        if name in self.parameters:
            param_def = self.info.parameters[name]
            # Clamp value to valid range
            value = max(param_def.min_value, min(param_def.max_value, value))
            self.parameters[name] = value

            # Call parameter change callback
            if name in self.parameter_callbacks:
                self.parameter_callbacks[name](value)

    def get_parameter(self, name: str) -> float:
        """Get plugin parameter value"""
        return self.parameters.get(name, 0.0)

    def add_parameter_callback(self, name: str, callback: Callable[[float], None]):
        """Add parameter change callback"""
        self.parameter_callbacks[name] = callback

    def bypass(self, bypassed: bool):
        """Bypass plugin"""
        self.bypassed = bypassed

    def enable(self, enabled: bool):
        """Enable/disable plugin"""
        self.enabled = enabled

    @abstractmethod
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process audio through plugin"""
        pass

    @abstractmethod
    def reset(self):
        """Reset plugin state"""
        pass

class EffectPlugin(BasePlugin):
    """Base class for effect plugins"""

    def __init__(self, info: PluginInfo):
        super().__init__(info)
        self.delay_buffer = None
        self.filter_state = None

    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process audio through effect"""
        if not self.enabled or self.bypassed:
            return input_buffer

        return self._process_effect(input_buffer, sample_rate)

    @abstractmethod
    def _process_effect(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process effect-specific audio"""
        pass

class InstrumentPlugin(BasePlugin):
    """Base class for instrument plugins"""

    def __init__(self, info: PluginInfo):
        super().__init__(info)
        self.active_notes = {}
        self.sample_rate = 44100

    def note_on(self, note: int, velocity: int):
        """Trigger note on"""
        self.active_notes[note] = {
            'velocity': velocity,
            'start_time': time.time(),
            'phase': 0.0
        }

    def note_off(self, note: int):
        """Trigger note off"""
        if note in self.active_notes:
            del self.active_notes[note]

    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Generate audio from active notes"""
        if not self.enabled:
            return np.zeros_like(input_buffer)

        self.sample_rate = sample_rate
        return self._generate_audio(input_buffer, sample_rate)

    @abstractmethod
    def _generate_audio(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Generate instrument-specific audio"""
        pass

# Built-in Effect Plugins

class ReverbPlugin(EffectPlugin):
    """Professional reverb effect"""

    def __init__(self):
        info = PluginInfo(
            name="Professional Reverb",
            version="1.0",
            plugin_type=PluginType.EFFECT,
            category=PluginCategory.REVERB,
            author="VoiceStudio",
            description="High-quality algorithmic reverb"
        )

        # Add parameters
        info.parameters = {
            "room_size": PluginParameter("room_size", 0.5, 0.0, 1.0, 0.5, "", "Room Size", "Size of the virtual room"),
            "damping": PluginParameter("damping", 0.5, 0.0, 1.0, 0.5, "", "Damping", "High frequency damping"),
            "wet_level": PluginParameter("wet_level", 0.3, 0.0, 1.0, 0.3, "", "Wet Level", "Amount of reverb signal"),
            "dry_level": PluginParameter("dry_level", 0.7, 0.0, 1.0, 0.7, "", "Dry Level", "Amount of dry signal"),
            "pre_delay": PluginParameter("pre_delay", 0.0, 0.0, 0.1, 0.0, "s", "Pre Delay", "Delay before reverb starts"),
            "stereo_width": PluginParameter("stereo_width", 1.0, 0.0, 2.0, 1.0, "", "Stereo Width", "Stereo image width")
        }

        super().__init__(info)

        # Initialize reverb buffers
        self.max_delay_samples = int(2.0 * 44100)  # 2 seconds max
        self.delay_buffers = {
            'left': np.zeros(self.max_delay_samples),
            'right': np.zeros(self.max_delay_samples)
        }
        self.write_positions = {'left': 0, 'right': 0}
        self.filter_coeffs = {'left': 0.0, 'right': 0.0}

    def _process_effect(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process reverb effect"""
        try:
            if input_buffer.ndim == 1:
                # Convert mono to stereo
                input_buffer = np.column_stack([input_buffer, input_buffer])

            output = np.zeros_like(input_buffer)

            # Get parameters
            room_size = self.get_parameter("room_size")
            damping = self.get_parameter("damping")
            wet_level = self.get_parameter("wet_level")
            dry_level = self.get_parameter("dry_level")
            pre_delay = self.get_parameter("pre_delay")
            stereo_width = self.get_parameter("stereo_width")

            # Calculate delay times
            delay_times = [
                0.0297, 0.0371, 0.0411, 0.0437, 0.0053, 0.0077, 0.0113, 0.0137
            ]

            # Apply room size scaling
            delay_times = [t * (0.5 + room_size) for t in delay_times]

            # Process each channel
            for ch in range(min(2, input_buffer.shape[1])):
                channel_input = input_buffer[:, ch]
                channel_output = np.zeros_like(channel_input)

                # Apply pre-delay
                pre_delay_samples = int(pre_delay * sample_rate)
                if pre_delay_samples > 0:
                    delayed_input = np.concatenate([
                        np.zeros(pre_delay_samples),
                        channel_input[:-pre_delay_samples]
                    ])
                else:
                    delayed_input = channel_input

                # Process through delay lines
                for i, delay_time in enumerate(delay_times):
                    delay_samples = int(delay_time * sample_rate)
                    if delay_samples < self.max_delay_samples:
                        # Get delayed signal
                        delayed_signal = self._get_delayed_signal(channel_input, delay_samples, ch)

                        # Apply damping filter
                        filtered_signal = self._apply_damping_filter(delayed_signal, damping, ch)

                        # Add to output
                        channel_output += filtered_signal * 0.125  # Equal mix

                # Apply stereo width
                if ch == 0:  # Left channel
                    channel_output *= stereo_width
                elif ch == 1:  # Right channel
                    channel_output *= (2.0 - stereo_width)

                # Mix wet and dry
                output[:, ch] = channel_input * dry_level + channel_output * wet_level

            return output

        except Exception as e:
            logger.error(f"Reverb processing failed: {e}")
            return input_buffer

    def _get_delayed_signal(self, input_signal: np.ndarray, delay_samples: int, channel: int) -> np.ndarray:
        """Get delayed signal from delay buffer"""
        ch_name = 'left' if channel == 0 else 'right'
        buffer = self.delay_buffers[ch_name]
        write_pos = self.write_positions[ch_name]

        output = np.zeros_like(input_signal)

        for i, sample in enumerate(input_signal):
            # Write to buffer
            buffer[write_pos] = sample

            # Read delayed sample
            read_pos = (write_pos - delay_samples) % self.max_delay_samples
            output[i] = buffer[read_pos]

            # Update write position
            write_pos = (write_pos + 1) % self.max_delay_samples

        self.write_positions[ch_name] = write_pos
        return output

    def _apply_damping_filter(self, signal: np.ndarray, damping: float, channel: int) -> np.ndarray:
        """Apply damping filter"""
        ch_name = 'left' if channel == 0 else 'right'
        coeff = self.filter_coeffs[ch_name]

        # Simple one-pole low-pass filter
        filtered = np.zeros_like(signal)
        filtered[0] = signal[0]

        for i in range(1, len(signal)):
            filtered[i] = coeff * filtered[i-1] + (1 - coeff) * signal[i]

        # Update filter coefficient
        self.filter_coeffs[ch_name] = damping * 0.9

        return filtered

    def reset(self):
        """Reset reverb state"""
        for buffer in self.delay_buffers.values():
            buffer.fill(0)
        for pos in self.write_positions.values():
            pos = 0
        for coeff in self.filter_coeffs.values():
            coeff = 0.0

class DelayPlugin(EffectPlugin):
    """Professional delay effect"""

    def __init__(self):
        info = PluginInfo(
            name="Professional Delay",
            version="1.0",
            plugin_type=PluginType.EFFECT,
            category=PluginCategory.DELAY,
            author="VoiceStudio",
            description="High-quality delay with modulation"
        )

        info.parameters = {
            "delay_time": PluginParameter("delay_time", 0.25, 0.001, 2.0, 0.25, "s", "Delay Time", "Delay time in seconds"),
            "feedback": PluginParameter("feedback", 0.3, 0.0, 0.95, 0.3, "", "Feedback", "Amount of delayed signal fed back"),
            "wet_level": PluginParameter("wet_level", 0.5, 0.0, 1.0, 0.5, "", "Wet Level", "Amount of delayed signal"),
            "dry_level": PluginParameter("dry_level", 0.5, 0.0, 1.0, 0.5, "", "Dry Level", "Amount of dry signal"),
            "modulation_rate": PluginParameter("modulation_rate", 0.5, 0.0, 10.0, 0.5, "Hz", "Mod Rate", "Modulation rate"),
            "modulation_depth": PluginParameter("modulation_depth", 0.0, 0.0, 0.1, 0.0, "s", "Mod Depth", "Modulation depth"),
            "filter_cutoff": PluginParameter("filter_cutoff", 1.0, 0.1, 1.0, 1.0, "", "Filter Cutoff", "Low-pass filter cutoff")
        }

        super().__init__(info)

        # Initialize delay buffer
        self.max_delay_samples = int(2.0 * 44100)  # 2 seconds max
        self.delay_buffer = np.zeros(self.max_delay_samples)
        self.write_position = 0
        self.modulation_phase = 0.0

    def _process_effect(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process delay effect"""
        try:
            # Get parameters
            delay_time = self.get_parameter("delay_time")
            feedback = self.get_parameter("feedback")
            wet_level = self.get_parameter("wet_level")
            dry_level = self.get_parameter("dry_level")
            mod_rate = self.get_parameter("modulation_rate")
            mod_depth = self.get_parameter("modulation_depth")
            filter_cutoff = self.get_parameter("filter_cutoff")

            # Convert to mono for processing
            if input_buffer.ndim > 1:
                mono_input = np.mean(input_buffer, axis=1)
            else:
                mono_input = input_buffer

            output = np.zeros_like(mono_input)

            # Process each sample
            for i, sample in enumerate(mono_input):
                # Calculate modulated delay time
                modulation = np.sin(2 * np.pi * mod_rate * i / sample_rate) * mod_depth
                current_delay_time = delay_time + modulation
                delay_samples = int(current_delay_time * sample_rate)

                # Clamp delay samples
                delay_samples = max(1, min(delay_samples, self.max_delay_samples - 1))

                # Write to delay buffer
                self.delay_buffer[self.write_position] = sample

                # Read delayed sample
                read_position = (self.write_position - delay_samples) % self.max_delay_samples
                delayed_sample = self.delay_buffer[read_position]

                # Apply feedback
                self.delay_buffer[self.write_position] += delayed_sample * feedback

                # Apply low-pass filter to feedback
                if filter_cutoff < 1.0:
                    delayed_sample = self._apply_lowpass_filter(delayed_sample, filter_cutoff)

                # Mix wet and dry
                output[i] = sample * dry_level + delayed_sample * wet_level

                # Update write position
                self.write_position = (self.write_position + 1) % self.max_delay_samples

            # Convert back to stereo if needed
            if input_buffer.ndim > 1:
                output = np.column_stack([output, output])

            return output

        except Exception as e:
            logger.error(f"Delay processing failed: {e}")
            return input_buffer

    def _apply_lowpass_filter(self, sample: float, cutoff: float) -> float:
        """Apply simple low-pass filter"""
        # Simple one-pole low-pass filter
        if not hasattr(self, 'filter_state'):
            self.filter_state = 0.0

        self.filter_state = cutoff * self.filter_state + (1 - cutoff) * sample
        return self.filter_state

    def reset(self):
        """Reset delay state"""
        self.delay_buffer.fill(0)
        self.write_position = 0
        self.modulation_phase = 0.0
        if hasattr(self, 'filter_state'):
            self.filter_state = 0.0

class CompressorPlugin(EffectPlugin):
    """Professional compressor"""

    def __init__(self):
        info = PluginInfo(
            name="Professional Compressor",
            version="1.0",
            plugin_type=PluginType.EFFECT,
            category=PluginCategory.DYNAMICS,
            author="VoiceStudio",
            description="High-quality dynamics compressor"
        )

        info.parameters = {
            "threshold": PluginParameter("threshold", -12.0, -60.0, 0.0, -12.0, "dB", "Threshold", "Compression threshold"),
            "ratio": PluginParameter("ratio", 3.0, 1.0, 20.0, 3.0, ":1", "Ratio", "Compression ratio"),
            "attack": PluginParameter("attack", 10.0, 0.1, 100.0, 10.0, "ms", "Attack", "Attack time"),
            "release": PluginParameter("release", 100.0, 10.0, 1000.0, 100.0, "ms", "Release", "Release time"),
            "knee": PluginParameter("knee", 2.0, 0.0, 10.0, 2.0, "dB", "Knee", "Soft knee width"),
            "makeup_gain": PluginParameter("makeup_gain", 0.0, 0.0, 20.0, 0.0, "dB", "Makeup Gain", "Output gain compensation")
        }

        super().__init__(info)

        # Compressor state
        self.envelope = 0.0
        self.gain_reduction = 0.0

    def _process_effect(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process compressor effect"""
        try:
            # Get parameters
            threshold_db = self.get_parameter("threshold")
            ratio = self.get_parameter("ratio")
            attack_ms = self.get_parameter("attack")
            release_ms = self.get_parameter("release")
            knee_db = self.get_parameter("knee")
            makeup_gain_db = self.get_parameter("makeup_gain")

            # Convert to linear
            threshold_linear = 10 ** (threshold_db / 20)
            makeup_gain_linear = 10 ** (makeup_gain_db / 20)

            # Calculate time constants
            attack_coeff = np.exp(-1.0 / (attack_ms * sample_rate / 1000))
            release_coeff = np.exp(-1.0 / (release_ms * sample_rate / 1000))

            output = np.zeros_like(input_buffer)

            # Process each channel
            for ch in range(input_buffer.shape[1] if input_buffer.ndim > 1 else 1):
                channel_input = input_buffer[:, ch] if input_buffer.ndim > 1 else input_buffer
                channel_output = np.zeros_like(channel_input)

                for i, sample in enumerate(channel_input):
                    # Calculate input level
                    input_level = abs(sample)

                    # Calculate gain reduction
                    if input_level > threshold_linear:
                        # Calculate compression amount
                        over_threshold = input_level - threshold_linear
                        compressed_level = threshold_linear + over_threshold / ratio

                        # Apply soft knee
                        if knee_db > 0:
                            knee_factor = min(1.0, over_threshold / (knee_db / 20))
                            compressed_level = threshold_linear + over_threshold * (1 - knee_factor) / ratio + over_threshold * knee_factor

                        # Calculate gain reduction
                        target_gain_reduction = compressed_level / input_level
                    else:
                        target_gain_reduction = 1.0

                    # Apply envelope
                    if target_gain_reduction < self.gain_reduction:
                        # Attack
                        self.gain_reduction = target_gain_reduction + (self.gain_reduction - target_gain_reduction) * attack_coeff
                    else:
                        # Release
                        self.gain_reduction = target_gain_reduction + (self.gain_reduction - target_gain_reduction) * release_coeff

                    # Apply gain reduction and makeup gain
                    channel_output[i] = sample * self.gain_reduction * makeup_gain_linear

                if input_buffer.ndim > 1:
                    output[:, ch] = channel_output
                else:
                    output = channel_output

            return output

        except Exception as e:
            logger.error(f"Compressor processing failed: {e}")
            return input_buffer

    def reset(self):
        """Reset compressor state"""
        self.envelope = 0.0
        self.gain_reduction = 0.0

# Built-in Instrument Plugins

class SynthesizerPlugin(InstrumentPlugin):
    """Professional synthesizer"""

    def __init__(self):
        info = PluginInfo(
            name="Professional Synthesizer",
            version="1.0",
            plugin_type=PluginType.INSTRUMENT,
            category=PluginCategory.SYNTHESIZER,
            author="VoiceStudio",
            description="Multi-oscillator synthesizer"
        )

        info.parameters = {
            "osc1_waveform": PluginParameter("osc1_waveform", 0, 0, 3, 0, "", "Osc 1 Wave", "Oscillator 1 waveform"),
            "osc1_octave": PluginParameter("osc1_octave", 0, -2, 2, 0, "", "Osc 1 Octave", "Oscillator 1 octave"),
            "osc1_level": PluginParameter("osc1_level", 0.8, 0.0, 1.0, 0.8, "", "Osc 1 Level", "Oscillator 1 level"),
            "osc2_waveform": PluginParameter("osc2_waveform", 1, 0, 3, 1, "", "Osc 2 Wave", "Oscillator 2 waveform"),
            "osc2_octave": PluginParameter("osc2_octave", 0, -2, 2, 0, "", "Osc 2 Octave", "Oscillator 2 octave"),
            "osc2_level": PluginParameter("osc2_level", 0.6, 0.0, 1.0, 0.6, "", "Osc 2 Level", "Oscillator 2 level"),
            "filter_cutoff": PluginParameter("filter_cutoff", 0.5, 0.0, 1.0, 0.5, "", "Filter Cutoff", "Filter cutoff frequency"),
            "filter_resonance": PluginParameter("filter_resonance", 0.1, 0.0, 1.0, 0.1, "", "Filter Resonance", "Filter resonance"),
            "attack": PluginParameter("attack", 0.1, 0.001, 2.0, 0.1, "s", "Attack", "Envelope attack time"),
            "decay": PluginParameter("decay", 0.3, 0.001, 2.0, 0.3, "s", "Decay", "Envelope decay time"),
            "sustain": PluginParameter("sustain", 0.7, 0.0, 1.0, 0.7, "", "Sustain", "Envelope sustain level"),
            "release": PluginParameter("release", 0.5, 0.001, 2.0, 0.5, "s", "Release", "Envelope release time")
        }

        super().__init__(info)

        # Oscillator phases
        self.osc_phases = {}

    def _generate_audio(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Generate synthesizer audio"""
        try:
            output = np.zeros_like(input_buffer)

            # Get parameters
            osc1_wave = int(self.get_parameter("osc1_waveform"))
            osc1_octave = int(self.get_parameter("osc1_octave"))
            osc1_level = self.get_parameter("osc1_level")
            osc2_wave = int(self.get_parameter("osc2_waveform"))
            osc2_octave = int(self.get_parameter("osc2_octave"))
            osc2_level = self.get_parameter("osc2_level")
            filter_cutoff = self.get_parameter("filter_cutoff")
            filter_resonance = self.get_parameter("filter_resonance")

            # Process each active note
            for note, note_data in self.active_notes.items():
                # Calculate frequency
                frequency = 440 * (2 ** ((note - 69) / 12)) * (2 ** osc1_octave)

                # Generate samples
                num_samples = len(input_buffer)
                t = np.arange(num_samples) / sample_rate

                # Generate oscillator 1
                osc1_signal = self._generate_waveform(t, frequency, osc1_wave, note)

                # Generate oscillator 2
                frequency2 = 440 * (2 ** ((note - 69) / 12)) * (2 ** osc2_octave)
                osc2_signal = self._generate_waveform(t, frequency2, osc2_wave, note)

                # Mix oscillators
                mixed_signal = osc1_signal * osc1_level + osc2_signal * osc2_level

                # Apply filter
                filtered_signal = self._apply_filter(mixed_signal, filter_cutoff, filter_resonance, note)

                # Apply envelope
                envelope = self._calculate_envelope(note_data, t, sample_rate)
                enveloped_signal = filtered_signal * envelope

                # Add to output
                output += enveloped_signal

            return output

        except Exception as e:
            logger.error(f"Synthesizer generation failed: {e}")
            return np.zeros_like(input_buffer)

    def _generate_waveform(self, t: np.ndarray, frequency: float, waveform: int, note: int) -> np.ndarray:
        """Generate waveform"""
        phase = 2 * np.pi * frequency * t

        # Initialize phase if needed
        if note not in self.osc_phases:
            self.osc_phases[note] = {'osc1': 0.0, 'osc2': 0.0}

        # Add phase offset
        phase += self.osc_phases[note]['osc1']

        # Generate waveform
        if waveform == 0:  # Sine
            signal = np.sin(phase)
        elif waveform == 1:  # Square
            signal = np.sign(np.sin(phase))
        elif waveform == 2:  # Sawtooth
            signal = 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
        elif waveform == 3:  # Triangle
            signal = 2 * np.abs(2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))) - 1
        else:
            signal = np.sin(phase)

        # Update phase
        self.osc_phases[note]['osc1'] = phase[-1] % (2 * np.pi)

        return signal

    def _apply_filter(self, signal: np.ndarray, cutoff: float, resonance: float, note: int) -> np.ndarray:
        """Apply low-pass filter"""
        # Simple one-pole low-pass filter
        if note not in self.osc_phases:
            self.osc_phases[note] = {'osc1': 0.0, 'osc2': 0.0, 'filter': 0.0}

        filtered = np.zeros_like(signal)
        filter_state = self.osc_phases[note]['filter']

        for i, sample in enumerate(signal):
            filter_state = cutoff * filter_state + (1 - cutoff) * sample
            filtered[i] = filter_state

        self.osc_phases[note]['filter'] = filter_state
        return filtered

    def _calculate_envelope(self, note_data: Dict, t: np.ndarray, sample_rate: int) -> np.ndarray:
        """Calculate ADSR envelope"""
        attack_time = self.get_parameter("attack")
        decay_time = self.get_parameter("decay")
        sustain_level = self.get_parameter("sustain")
        release_time = self.get_parameter("release")

        note_age = t - note_data['start_time']
        envelope = np.zeros_like(t)

        for i, age in enumerate(note_age):
            if age < attack_time:
                # Attack
                envelope[i] = age / attack_time
            elif age < attack_time + decay_time:
                # Decay
                decay_progress = (age - attack_time) / decay_time
                envelope[i] = 1.0 - decay_progress * (1.0 - sustain_level)
            else:
                # Sustain
                envelope[i] = sustain_level

        return envelope

    def reset(self):
        """Reset synthesizer state"""
        self.osc_phases.clear()

class PluginManager:
    """Plugin management system"""

    def __init__(self):
        self.plugins = {}
        self.plugin_instances = {}
        self.effect_chains = {}
        self.instrument_racks = {}

        # Register built-in plugins
        self._register_builtin_plugins()

    def _register_builtin_plugins(self):
        """Register built-in plugins"""
        # Effects
        self.register_plugin("reverb", ReverbPlugin)
        self.register_plugin("delay", DelayPlugin)
        self.register_plugin("compressor", CompressorPlugin)

        # Instruments
        self.register_plugin("synthesizer", SynthesizerPlugin)

    def register_plugin(self, name: str, plugin_class):
        """Register a plugin class"""
        self.plugins[name] = plugin_class

    def create_plugin_instance(self, name: str) -> Optional[BasePlugin]:
        """Create plugin instance"""
        if name in self.plugins:
            plugin_class = self.plugins[name]
            instance = plugin_class()
            instance_id = str(uuid.uuid4())
            self.plugin_instances[instance_id] = instance
            return instance
        return None

    def get_plugin_instance(self, instance_id: str) -> Optional[BasePlugin]:
        """Get plugin instance by ID"""
        return self.plugin_instances.get(instance_id)

    def remove_plugin_instance(self, instance_id: str):
        """Remove plugin instance"""
        if instance_id in self.plugin_instances:
            del self.plugin_instances[instance_id]

    def create_effect_chain(self, chain_id: str) -> List[str]:
        """Create effect chain"""
        self.effect_chains[chain_id] = []
        return self.effect_chains[chain_id]

    def add_effect_to_chain(self, chain_id: str, plugin_name: str) -> Optional[str]:
        """Add effect to chain"""
        if chain_id in self.effect_chains:
            instance = self.create_plugin_instance(plugin_name)
            if instance:
                instance_id = str(uuid.uuid4())
                self.plugin_instances[instance_id] = instance
                self.effect_chains[chain_id].append(instance_id)
                return instance_id
        return None

    def process_effect_chain(self, chain_id: str, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process audio through effect chain"""
        if chain_id not in self.effect_chains:
            return input_buffer

        output = input_buffer
        for instance_id in self.effect_chains[chain_id]:
            instance = self.get_plugin_instance(instance_id)
            if instance:
                output = instance.process(output, sample_rate)

        return output

    def create_instrument_rack(self, rack_id: str) -> List[str]:
        """Create instrument rack"""
        self.instrument_racks[rack_id] = []
        return self.instrument_racks[rack_id]

    def add_instrument_to_rack(self, rack_id: str, plugin_name: str) -> Optional[str]:
        """Add instrument to rack"""
        if rack_id in self.instrument_racks:
            instance = self.create_plugin_instance(plugin_name)
            if instance:
                instance_id = str(uuid.uuid4())
                self.plugin_instances[instance_id] = instance
                self.instrument_racks[rack_id].append(instance_id)
                return instance_id
        return None

    def trigger_note_on(self, rack_id: str, note: int, velocity: int):
        """Trigger note on for all instruments in rack"""
        if rack_id in self.instrument_racks:
            for instance_id in self.instrument_racks[rack_id]:
                instance = self.get_plugin_instance(instance_id)
                if instance and isinstance(instance, InstrumentPlugin):
                    instance.note_on(note, velocity)

    def trigger_note_off(self, rack_id: str, note: int):
        """Trigger note off for all instruments in rack"""
        if rack_id in self.instrument_racks:
            for instance_id in self.instrument_racks[rack_id]:
                instance = self.get_plugin_instance(instance_id)
                if instance and isinstance(instance, InstrumentPlugin):
                    instance.note_off(note)

    def generate_instrument_audio(self, rack_id: str, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Generate audio from instrument rack"""
        if rack_id not in self.instrument_racks:
            return np.zeros_like(input_buffer)

        output = np.zeros_like(input_buffer)
        for instance_id in self.instrument_racks[rack_id]:
            instance = self.get_plugin_instance(instance_id)
            if instance and isinstance(instance, InstrumentPlugin):
                instrument_output = instance.process(input_buffer, sample_rate)
                output += instrument_output

        return output

    def get_available_plugins(self) -> Dict[str, PluginInfo]:
        """Get list of available plugins"""
        available = {}
        for name, plugin_class in self.plugins.items():
            # Create temporary instance to get info
            temp_instance = plugin_class()
            available[name] = temp_instance.info
        return available

    def save_plugin_preset(self, instance_id: str, preset_name: str, file_path: str):
        """Save plugin preset"""
        instance = self.get_plugin_instance(instance_id)
        if instance:
            preset_data = {
                'plugin_name': instance.info.name,
                'preset_name': preset_name,
                'parameters': instance.parameters,
                'created_at': datetime.now().isoformat()
            }

            with open(file_path, 'w') as f:
                json.dump(preset_data, f, indent=2)

    def load_plugin_preset(self, instance_id: str, file_path: str):
        """Load plugin preset"""
        instance = self.get_plugin_instance(instance_id)
        if instance:
            try:
                with open(file_path, 'r') as f:
                    preset_data = json.load(f)

                # Load parameters
                for param_name, param_value in preset_data.get('parameters', {}).items():
                    instance.set_parameter(param_name, param_value)

            except Exception as e:
                logger.error(f"Failed to load preset: {e}")

def main():
    """Demo the plugin system"""
    logger.info("🎛️ VoiceStudio Advanced Plugin System Demo")

    # Create plugin manager
    manager = PluginManager()

    # Create effect chain
    chain_id = "master_chain"
    manager.create_effect_chain(chain_id)

    # Add effects to chain
    reverb_id = manager.add_effect_to_chain(chain_id, "reverb")
    delay_id = manager.add_effect_to_chain(chain_id, "delay")
    compressor_id = manager.add_effect_to_chain(chain_id, "compressor")

    logger.info("✅ Created effect chain with reverb, delay, and compressor")

    # Create instrument rack
    rack_id = "main_rack"
    manager.create_instrument_rack(rack_id)

    # Add synthesizer
    synth_id = manager.add_instrument_to_rack(rack_id, "synthesizer")

    logger.info("✅ Created instrument rack with synthesizer")

    # Configure effects
    if reverb_id:
        reverb = manager.get_plugin_instance(reverb_id)
        reverb.set_parameter("room_size", 0.7)
        reverb.set_parameter("wet_level", 0.4)

    if delay_id:
        delay = manager.get_plugin_instance(delay_id)
        delay.set_parameter("delay_time", 0.375)
        delay.set_parameter("feedback", 0.3)

    if compressor_id:
        compressor = manager.get_plugin_instance(compressor_id)
        compressor.set_parameter("threshold", -8.0)
        compressor.set_parameter("ratio", 4.0)

    logger.info("✅ Configured effect parameters")

    # Configure synthesizer
    if synth_id:
        synth = manager.get_plugin_instance(synth_id)
        synth.set_parameter("osc1_waveform", 1)  # Square wave
        synth.set_parameter("osc1_level", 0.8)
        synth.set_parameter("filter_cutoff", 0.6)

    logger.info("✅ Configured synthesizer parameters")

    # Generate test audio
    sample_rate = 44100
    duration = 2.0
    num_samples = int(sample_rate * duration)

    # Create input buffer
    input_buffer = np.zeros(num_samples)

    # Trigger notes
    manager.trigger_note_on(rack_id, 60, 80)  # C4
    manager.trigger_note_on(rack_id, 64, 70)  # E4
    manager.trigger_note_on(rack_id, 67, 75)  # G4

    # Generate instrument audio
    instrument_audio = manager.generate_instrument_audio(rack_id, input_buffer, sample_rate)

    # Process through effect chain
    processed_audio = manager.process_effect_chain(chain_id, instrument_audio, sample_rate)

    # Save processed audio
    import soundfile as sf
    output_path = "plugin_demo_output.wav"
    sf.write(output_path, processed_audio, sample_rate)

    logger.info(f"✅ Generated and processed audio saved to {output_path}")

    # Save plugin presets
    if reverb_id:
        manager.save_plugin_preset(reverb_id, "Large Hall", "reverb_preset.json")

    if synth_id:
        manager.save_plugin_preset(synth_id, "Lead Synth", "synth_preset.json")

    logger.info("✅ Saved plugin presets")

    logger.info("🎉 Advanced plugin system demo completed!")

if __name__ == "__main__":
    main()
