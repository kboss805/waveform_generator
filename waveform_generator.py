"""
Pure waveform generation functions.

This module contains stateless functions for generating waveforms and envelopes.
No UI or state management logic.
"""

import numpy as np
from scipy import signal
from typing import Tuple, List


def gen_sine_wf(
    freq: float,
    amp: float,
    offset: float = 0.0,
    dur: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a sine waveform with configurable y-axis offset.

    Args:
        freq: Frequency in Hz (0.1-100.0)
        amp: Amplitude (0.0-10.0), waveform ranges from offset to offset+amp
        offset: Y-axis offset (0.0-10.0)
        dur: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    time = np.linspace(0, dur, int(sample_rate * dur))
    half_amp = amp / 2
    wf = offset + half_amp * np.sin(2 * np.pi * freq * time)
    return time, wf


def gen_square_wf(
    freq: float,
    amp: float,
    duty_cycle: float,
    offset: float = 0.0,
    dur: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a square waveform with configurable y-axis offset.

    Args:
        freq: Frequency in Hz (0.1-100.0)
        amp: Amplitude (0.0-10.0), waveform ranges from offset to offset+amp
        duty_cycle: Duty cycle percentage (1.0-100.0)
        offset: Y-axis offset (0.0-10.0)
        dur: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    time = np.linspace(0, dur, int(sample_rate * dur))
    half_amp = amp / 2
    wf = offset + half_amp * signal.square(
        2 * np.pi * freq * time,
        duty=duty_cycle / 100
    )
    return time, wf


def gen_sawtooth_wf(
    freq: float,
    amp: float,
    offset: float = 0.0,
    dur: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a sawtooth waveform with configurable y-axis offset.

    Args:
        freq: Frequency in Hz (0.1-100.0)
        amp: Amplitude (0.0-10.0), waveform ranges from offset to offset+amp
        offset: Y-axis offset (0.0-10.0)
        dur: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    time = np.linspace(0, dur, int(sample_rate * dur))
    half_amp = amp / 2
    wf = offset + half_amp * signal.sawtooth(2 * np.pi * freq * time)
    return time, wf


def gen_triangle_wf(
    freq: float,
    amp: float,
    offset: float = 0.0,
    dur: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a triangle waveform with configurable y-axis offset.

    Args:
        freq: Frequency in Hz (0.1-100.0)
        amp: Amplitude (0.0-10.0), waveform ranges from offset to offset+amp
        offset: Y-axis offset (0.0-10.0)
        dur: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    time = np.linspace(0, dur, int(sample_rate * dur))
    half_amp = amp / 2
    wf = offset + half_amp * signal.sawtooth(
        2 * np.pi * freq * time,
        width=0.5
    )
    return time, wf


def compute_max_env(
    wfs: List[Tuple[np.ndarray, np.ndarray]]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute maximum envelope from multiple waveforms.

    Args:
        wfs: List of (time, amplitude) tuples

    Returns:
        Tuple of (time array, max envelope array)
    """
    if not wfs:
        return np.array([]), np.array([])

    time = wfs[0][0]  # Shared time base
    amps = np.array([w[1] for w in wfs])
    max_env = np.max(amps, axis=0)

    return time, max_env


def compute_min_env(
    wfs: List[Tuple[np.ndarray, np.ndarray]]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute minimum envelope from multiple waveforms.

    Args:
        wfs: List of (time, amplitude) tuples

    Returns:
        Tuple of (time array, min envelope array)
    """
    if not wfs:
        return np.array([]), np.array([])

    time = wfs[0][0]  # Shared time base
    amps = np.array([w[1] for w in wfs])
    min_env = np.min(amps, axis=0)

    return time, min_env


def compute_rms_env(
    wfs: List[Tuple[np.ndarray, np.ndarray]]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute RMS envelope from multiple waveforms.

    Args:
        wfs: List of (time, amplitude) tuples

    Returns:
        Tuple of (time array, RMS envelope array)
    """
    if not wfs:
        return np.array([]), np.array([])

    time = wfs[0][0]  # Shared time base
    amps = np.array([w[1] for w in wfs])
    rms_env = np.sqrt(np.mean(amps ** 2, axis=0))

    return time, rms_env


def gen_wf(
    wf_type: str,
    freq: float,
    amp: float,
    offset: float = 0.0,
    duty_cycle: float = 50.0,
    dur: float = 1.0,
    sample_rate: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a waveform based on type.

    Args:
        wf_type: Type of waveform (sine, square, sawtooth, triangle)
        freq: Frequency in Hz (0.1-100.0)
        amp: Amplitude (0.0-10.0)
        offset: Y-axis offset (0.0-10.0)
        duty_cycle: Duty cycle percentage (1.0-100.0, for square only)
        dur: Duration in seconds
        sample_rate: Samples per second

    Returns:
        Tuple of (time array, amplitude array)
    """
    wf_type = wf_type.lower()

    if wf_type == "sine":
        return gen_sine_wf(freq, amp, offset, dur, sample_rate)
    elif wf_type == "square":
        return gen_square_wf(freq, amp, duty_cycle, offset, dur, sample_rate)
    elif wf_type == "sawtooth":
        return gen_sawtooth_wf(freq, amp, offset, dur, sample_rate)
    elif wf_type == "triangle":
        return gen_triangle_wf(freq, amp, offset, dur, sample_rate)
    else:
        # Default to sine waveform
        return gen_sine_wf(freq, amp, offset, dur, sample_rate)
