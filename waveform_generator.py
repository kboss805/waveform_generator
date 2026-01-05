"""
Pure waveform generation functions.

This module contains stateless functions for generating waveforms and envelopes.
No UI or state management logic.
"""

import numpy as np
from scipy import signal
from typing import Tuple, List


def generate_sine_wave(
    frequency: float,
    amplitude: float,
    duration: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a sine wave.

    Args:
        frequency: Frequency in Hz (1.0-100.0)
        amplitude: Amplitude (0.0-10.0)
        duration: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    time = np.linspace(0, duration, int(sample_rate * duration))
    wave = amplitude * np.sin(2 * np.pi * frequency * time)
    return time, wave


def generate_square_wave(
    frequency: float,
    amplitude: float,
    duty_cycle: float,
    duration: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a square wave.

    Args:
        frequency: Frequency in Hz (1.0-100.0)
        amplitude: Amplitude (0.0-10.0)
        duty_cycle: Duty cycle percentage (1.0-100.0)
        duration: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    time = np.linspace(0, duration, int(sample_rate * duration))
    wave = amplitude * signal.square(
        2 * np.pi * frequency * time,
        duty=duty_cycle / 100
    )
    return time, wave


def generate_sawtooth_wave(
    frequency: float,
    amplitude: float,
    duration: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a sawtooth wave.

    Args:
        frequency: Frequency in Hz (1.0-100.0)
        amplitude: Amplitude (0.0-10.0)
        duration: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    time = np.linspace(0, duration, int(sample_rate * duration))
    wave = amplitude * signal.sawtooth(2 * np.pi * frequency * time)
    return time, wave


def generate_triangle_wave(
    frequency: float,
    amplitude: float,
    duration: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a triangle wave.

    Args:
        frequency: Frequency in Hz (1.0-100.0)
        amplitude: Amplitude (0.0-10.0)
        duration: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    time = np.linspace(0, duration, int(sample_rate * duration))
    wave = amplitude * signal.sawtooth(
        2 * np.pi * frequency * time,
        width=0.5
    )
    return time, wave


def generate_pulse_wave(
    frequency: float,
    amplitude: float,
    duty_cycle: float,
    duration: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a pulse wave (same as square wave).

    Args:
        frequency: Frequency in Hz (1.0-100.0)
        amplitude: Amplitude (0.0-10.0)
        duty_cycle: Duty cycle percentage (1.0-100.0)
        duration: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    return generate_square_wave(frequency, amplitude, duty_cycle, duration, sample_rate)


def compute_max_envelope(
    waveforms: List[Tuple[np.ndarray, np.ndarray]]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute maximum envelope from multiple waveforms.

    Args:
        waveforms: List of (time, amplitude) tuples

    Returns:
        Tuple of (time array, max envelope array)
    """
    if not waveforms:
        return np.array([]), np.array([])

    time = waveforms[0][0]  # Shared time base
    amplitudes = np.array([w[1] for w in waveforms])
    max_env = np.max(amplitudes, axis=0)

    return time, max_env


def compute_min_envelope(
    waveforms: List[Tuple[np.ndarray, np.ndarray]]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute minimum envelope from multiple waveforms.

    Args:
        waveforms: List of (time, amplitude) tuples

    Returns:
        Tuple of (time array, min envelope array)
    """
    if not waveforms:
        return np.array([]), np.array([])

    time = waveforms[0][0]  # Shared time base
    amplitudes = np.array([w[1] for w in waveforms])
    min_env = np.min(amplitudes, axis=0)

    return time, min_env


def generate_waveform(
    wave_type: str,
    frequency: float,
    amplitude: float,
    duty_cycle: float = 50.0,
    duration: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a waveform based on type.

    Args:
        wave_type: Type of waveform (sine, square, pulse, sawtooth, triangle)
        frequency: Frequency in Hz (1.0-100.0)
        amplitude: Amplitude (0.0-10.0)
        duty_cycle: Duty cycle percentage (1.0-100.0, for square/pulse only)
        duration: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    wave_type = wave_type.lower()

    if wave_type == "sine":
        return generate_sine_wave(frequency, amplitude, duration, sample_rate)
    elif wave_type == "square":
        return generate_square_wave(frequency, amplitude, duty_cycle, duration, sample_rate)
    elif wave_type == "pulse":
        return generate_pulse_wave(frequency, amplitude, duty_cycle, duration, sample_rate)
    elif wave_type == "sawtooth":
        return generate_sawtooth_wave(frequency, amplitude, duration, sample_rate)
    elif wave_type == "triangle":
        return generate_triangle_wave(frequency, amplitude, duration, sample_rate)
    else:
        # Default to sine wave
        return generate_sine_wave(frequency, amplitude, duration, sample_rate)
