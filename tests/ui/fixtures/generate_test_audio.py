"""
Generate test audio files for VoiceStudio UI tests.

This script creates standardized WAV audio files used for testing:
- test_audio_short.wav (5s) - Clean sine wave tone
- test_audio_long.wav (30s) - Clean speech-like modulated tone
- test_audio_noisy.wav (5s) - Tone with background noise
- voice_reference_clean.wav (10s) - Clean reference for cloning tests
- voice_reference_multi_speaker.wav (15s) - Multi-segment reference

Run this script to regenerate fixtures if they don't exist or are corrupted.
"""

import math
import struct
import wave
from pathlib import Path


def generate_sine_wave(frequency: float, duration: float, sample_rate: int = 44100, amplitude: float = 0.5) -> bytes:
    """Generate a sine wave as raw bytes."""
    num_samples = int(sample_rate * duration)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        value = amplitude * math.sin(2 * math.pi * frequency * t)
        # Convert to 16-bit signed integer
        sample = int(value * 32767)
        samples.append(struct.pack('<h', sample))
    return b''.join(samples)


def generate_modulated_tone(duration: float, sample_rate: int = 44100) -> bytes:
    """Generate a speech-like modulated tone."""
    num_samples = int(sample_rate * duration)
    samples = []

    base_freq = 150  # Base frequency (typical speech fundamental)

    for i in range(num_samples):
        t = i / sample_rate

        # Modulate frequency to simulate speech patterns
        freq_mod = 1 + 0.2 * math.sin(2 * math.pi * 2 * t)  # Slow modulation
        freq = base_freq * freq_mod

        # Amplitude envelope with pauses
        envelope = 0.5
        # Add periodic "pauses" to simulate word gaps
        word_period = t % 0.8
        if word_period > 0.7:
            envelope *= (0.8 - word_period) / 0.1  # Fade out
        elif word_period < 0.1:
            envelope *= word_period / 0.1  # Fade in

        # Generate harmonics for richer sound
        value = 0.6 * math.sin(2 * math.pi * freq * t)  # Fundamental
        value += 0.25 * math.sin(2 * math.pi * freq * 2 * t)  # 1st harmonic
        value += 0.1 * math.sin(2 * math.pi * freq * 3 * t)  # 2nd harmonic

        value *= envelope * 0.5  # Scale down
        sample = int(max(-32767, min(32767, value * 32767)))
        samples.append(struct.pack('<h', sample))

    return b''.join(samples)


def generate_noise(duration: float, sample_rate: int = 44100, amplitude: float = 0.1) -> bytes:
    """Generate white noise."""
    import random
    num_samples = int(sample_rate * duration)
    samples = []
    for _ in range(num_samples):
        value = (random.random() * 2 - 1) * amplitude
        sample = int(value * 32767)
        samples.append(struct.pack('<h', sample))
    return b''.join(samples)


def add_noise_to_signal(signal: bytes, noise_level: float = 0.1) -> bytes:
    """Add noise to an existing signal."""
    import random
    samples = []
    for i in range(0, len(signal), 2):
        original = struct.unpack('<h', signal[i:i+2])[0]
        noise = (random.random() * 2 - 1) * noise_level * 32767
        combined = int(max(-32767, min(32767, original + noise)))
        samples.append(struct.pack('<h', combined))
    return b''.join(samples)


def write_wav(filepath: Path, audio_data: bytes, sample_rate: int = 44100, channels: int = 1, sample_width: int = 2):
    """Write audio data to a WAV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(filepath), 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)


def generate_all_fixtures():
    """Generate all test audio fixtures."""
    fixtures_dir = Path(__file__).parent
    sample_rate = 44100

    print("Generating test audio fixtures...")

    # 1. Short test audio (5 seconds) - 440Hz sine wave
    print("  Creating test_audio_short.wav (5s)...")
    short_audio = generate_sine_wave(440, 5.0, sample_rate)
    write_wav(fixtures_dir / "test_audio_short.wav", short_audio, sample_rate)

    # 2. Long test audio (30 seconds) - Modulated speech-like tone
    print("  Creating test_audio_long.wav (30s)...")
    long_audio = generate_modulated_tone(30.0, sample_rate)
    write_wav(fixtures_dir / "test_audio_long.wav", long_audio, sample_rate)

    # 3. Noisy test audio (5 seconds) - Tone with background noise
    print("  Creating test_audio_noisy.wav (5s)...")
    clean_signal = generate_sine_wave(440, 5.0, sample_rate, amplitude=0.4)
    noisy_audio = add_noise_to_signal(clean_signal, noise_level=0.15)
    write_wav(fixtures_dir / "test_audio_noisy.wav", noisy_audio, sample_rate)

    # 4. Voice reference clean (10 seconds) - Clean modulated tone for cloning
    print("  Creating voice_reference_clean.wav (10s)...")
    reference_clean = generate_modulated_tone(10.0, sample_rate)
    write_wav(fixtures_dir / "voice_reference_clean.wav", reference_clean, sample_rate)

    # 5. Multi-speaker reference (15 seconds) - Three distinct "speakers"
    print("  Creating voice_reference_multi_speaker.wav (15s)...")
    segments = []
    # Simulate different speakers with different base frequencies
    for _i, (freq, duration) in enumerate([(130, 5.0), (200, 5.0), (160, 5.0)]):
        segment = generate_sine_wave(freq, duration, sample_rate, amplitude=0.5)
        segments.append(segment)
    multi_audio = b''.join(segments)
    write_wav(fixtures_dir / "voice_reference_multi_speaker.wav", multi_audio, sample_rate)

    print("Done! Generated 5 audio fixture files.")

    # Verify files
    print("\nGenerated files:")
    for wav_file in fixtures_dir.glob("*.wav"):
        size_kb = wav_file.stat().st_size / 1024
        print(f"  - {wav_file.name}: {size_kb:.1f} KB")


if __name__ == "__main__":
    generate_all_fixtures()
