"""
Export functionality for waveform data.

This module handles exporting waveform data to CSV, MATLAB .mat,
and JSON formats without UI logic.
"""

import json
import os
import re
from datetime import datetime
from typing import Any, List, Tuple, Optional

import numpy as np
from scipy.io import savemat


SUPPORTED_EXTENSIONS = ('.csv', '.mat', '.json')


def sanitize_fname(filepath: str, default_ext: str = '.csv') -> str:
    """
    Sanitize filepath by removing invalid characters from the filename
    portion and ensuring a supported extension.

    Args:
        filepath: Original filepath (can be full path or just filename)
        default_ext: Extension to use if none is present (.csv, .mat, .json)

    Returns:
        Sanitized filepath with a valid extension
    """
    # Split into directory and filename
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    # Remove invalid characters from filename only (not path separators)
    # These are invalid in Windows filenames: < > : " | ? *
    filename = re.sub(r'[<>:"|?*]', '', filename)

    # Check for supported extension
    lower = filename.lower()
    has_ext = any(lower.endswith(ext) for ext in SUPPORTED_EXTENSIONS)
    if not has_ext:
        filename += default_ext

    # Default name if empty
    name_without_ext = os.path.splitext(filename)[0]
    if not name_without_ext:
        filename = 'wfs' + default_ext

    # Reconstruct full path if directory was provided
    if directory:
        return os.path.join(directory, filename)
    return filename


def export_to_csv(
    filename: str,
    wfs: List[Tuple[str, np.ndarray, np.ndarray, dict[str, Any]]],
    envs: Optional[List[Tuple[str, np.ndarray, np.ndarray]]] = None,
    sample_rate: int = 1000,
    dur: float = 1.0
) -> Tuple[bool, str]:
    """
    Export waveform data to CSV file.

    Args:
        filename: Destination filename
        wfs: List of (name, time, amplitude, params) tuples
        envs: Optional list of (name, time, amplitude) tuples for envelopes
        sample_rate: Sample rate in samples/second
        dur: Duration in seconds

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Sanitize filename
        filename = sanitize_fname(filename)

        # Prepare header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [f"# Exported: {timestamp}"]

        # Add waveform metadata
        for name, _, _, params in wfs:
            metadata_parts = [
                f"# {name}: {params['wf_type'].capitalize()}",
                f"{params['freq']} Hz",
                f"{params['amp']} amp",
                f"{params['offset']} offset"
            ]

            # Add duty cycle if applicable
            if params['wf_type'].lower() == 'square':
                metadata_parts.append(f"{params['duty_cycle']}% duty cycle")

            lines.append(", ".join(metadata_parts))

        # Add envelope metadata
        if envs:
            num_wfs = len(wfs)
            for env_name, _, _ in envs:
                lines.append(
                    f"# {env_name}: Computed from {num_wfs} waveforms"
                )

        # Add sample rate and duration
        lines.append(f"# Sample Rate: {sample_rate} S/s, Duration: {dur}s")

        # Create column headers
        headers = ["Time (s)"]
        for name, _, _, _ in wfs:
            headers.append(name)

        if envs:
            for env_name, _, _ in envs:
                headers.append(env_name)

        lines.append(",".join(headers))

        # Get time array (shared time base)
        if wfs:
            time = wfs[0][1]
        elif envs:
            time = envs[0][1]
        else:
            return False, "No data to export"

        # Build data rows
        num_samples = len(time)
        for i in range(num_samples):
            row = [f"{time[i]:.6f}"]

            # Add waveform amplitudes
            for _, _, amp, _ in wfs:
                row.append(f"{amp[i]:.6f}")

            # Add envelope amplitudes
            if envs:
                for _, _, amp in envs:
                    row.append(f"{amp[i]:.6f}")

            lines.append(",".join(row))

        # Write to file
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            f.write("\n".join(lines))

        return True, f"Successfully exported to {filename}"

    except PermissionError:
        return False, f"Permission denied: Cannot write to {filename}"
    except OSError as e:
        return False, f"File error: {str(e)}"
    except Exception as e:
        return False, f"Export failed: {str(e)}"


def export_to_mat(
    filename: str,
    wfs: List[Tuple[str, np.ndarray, np.ndarray, dict[str, Any]]],
    envs: Optional[List[Tuple[str, np.ndarray, np.ndarray]]] = None,
    sample_rate: int = 1000,
    dur: float = 1.0
) -> Tuple[bool, str]:
    """
    Export waveform data to MATLAB .mat file.

    Args:
        filename: Destination filename
        wfs: List of (name, time, amplitude, params) tuples
        envs: Optional list of (name, time, amplitude) tuples for envelopes
        sample_rate: Sample rate in samples/second
        dur: Duration in seconds

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        filename = sanitize_fname(filename, default_ext='.mat')

        if not wfs and not envs:
            return False, "No data to export"

        mdict: dict[str, Any] = {}

        # Time array (shared)
        if wfs:
            time = wfs[0][1]
        elif envs:
            time = envs[0][1]
        else:
            return False, "No data to export"
        mdict['time'] = time

        # Waveform data
        for name, _, amp, params in wfs:
            var_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
            if var_name[0:1].isdigit():
                var_name = 'wf_' + var_name
            mdict[var_name] = amp
            mdict[var_name + '_params'] = {
                'type': params['wf_type'],
                'frequency': params['freq'],
                'amplitude': params['amp'],
                'offset': params['offset'],
                'duty_cycle': params['duty_cycle'],
            }

        # Envelope data
        if envs:
            for env_name, _, amp in envs:
                var_name = re.sub(r'[^a-zA-Z0-9_]', '_', env_name)
                mdict[var_name] = amp

        # Metadata
        mdict['sample_rate'] = sample_rate
        mdict['duration'] = dur
        mdict['exported'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        savemat(filename, mdict)
        return True, f"Successfully exported to {filename}"

    except PermissionError:
        return False, f"Permission denied: Cannot write to {filename}"
    except OSError as e:
        return False, f"File error: {str(e)}"
    except Exception as e:
        return False, f"Export failed: {str(e)}"


def export_to_json(
    filename: str,
    wfs: List[Tuple[str, np.ndarray, np.ndarray, dict[str, Any]]],
    envs: Optional[List[Tuple[str, np.ndarray, np.ndarray]]] = None,
    sample_rate: int = 1000,
    dur: float = 1.0
) -> Tuple[bool, str]:
    """
    Export waveform data to JSON file.

    Args:
        filename: Destination filename
        wfs: List of (name, time, amplitude, params) tuples
        envs: Optional list of (name, time, amplitude) tuples for envelopes
        sample_rate: Sample rate in samples/second
        dur: Duration in seconds

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        filename = sanitize_fname(filename, default_ext='.json')

        # Time array (shared)
        if wfs:
            time = wfs[0][1]
        elif envs:
            time = envs[0][1]
        else:
            return False, "No data to export"

        data: dict[str, Any] = {
            'exported': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'sample_rate': sample_rate,
            'duration': dur,
            'time': time.tolist(),
            'waveforms': [],
            'envelopes': [],
        }

        for name, _, amp, params in wfs:
            data['waveforms'].append({
                'name': name,
                'type': params['wf_type'],
                'frequency': params['freq'],
                'amplitude': params['amp'],
                'offset': params['offset'],
                'duty_cycle': params['duty_cycle'],
                'amplitude_data': amp.tolist(),
            })

        if envs:
            for env_name, _, amp in envs:
                data['envelopes'].append({
                    'name': env_name,
                    'amplitude_data': amp.tolist(),
                })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return True, f"Successfully exported to {filename}"

    except PermissionError:
        return False, f"Permission denied: Cannot write to {filename}"
    except OSError as e:
        return False, f"File error: {str(e)}"
    except Exception as e:
        return False, f"Export failed: {str(e)}"


def prep_wf_for_export(
    name: str,
    time: np.ndarray,
    amp_array: np.ndarray,
    wf_type: str,
    freq: float,
    amp: float,
    offset: float = 0.0,
    duty_cycle: float = 50.0
) -> Tuple[str, np.ndarray, np.ndarray, dict]:
    """
    Prepare waveform data in format suitable for export.

    Args:
        name: Waveform name
        time: Time array
        amp_array: Amplitude array
        wf_type: Type of waveform
        freq: Frequency in Hz
        amp: Amplitude value
        offset: Y-axis offset
        duty_cycle: Duty cycle percentage (for square only)

    Returns:
        Tuple of (name, time, amplitude, params_dict)
    """
    params = {
        'wf_type': wf_type,
        'freq': freq,
        'amp': amp,
        'offset': offset,
        'duty_cycle': duty_cycle
    }

    return (name, time, amp_array, params)
