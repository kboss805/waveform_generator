# Real-Time Waveform Visualizer

A Python application for visualizing and analyzing multiple waveforms in real-time with envelope analysis capabilities.

## Installation

1. **Activate the virtual environment:**
   ```bash
   # Windows
   env\Scripts\activate
   ```

2. **Install dependencies (if not already done):**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python main.py
```

Or with the virtual environment:
```bash
env\Scripts\python.exe main.py
```

## Quick Start Guide

### Basic Usage

1. **Launch the application** - The app starts with one default sine wave (5 Hz, amplitude 5.0)

2. **Adjust waveform parameters:**
   - Use the **Frequency** slider to change the wave frequency (1-100 Hz)
   - Use the **Amplitude** slider to adjust the wave amplitude (0-10)
   - For Square/Pulse waves, use the **Duty Cycle** slider (1-100%)

3. **Change waveform type:**
   - Use the **Type** dropdown to select: Sine, Square, Pulse, Sawtooth, or Triangle

4. **Add more waveforms:**
   - Click **+ Add Waveform** button (max 5 waveforms)
   - Each waveform gets a unique color automatically

5. **Manage waveforms:**
   - Click on a waveform in the list to select and edit it
   - Click the **eye icon (👁)** to show/hide a waveform
   - Click the **X button** to remove a waveform (minimum 1 required)

### Envelope Analysis

When you have 2 or more **enabled** waveforms:

- **Show Max Envelope** - Displays the maximum amplitude at each time point (red dashed line)
- **Show Min Envelope** - Displays the minimum amplitude at each time point (blue dashed line)

Both envelopes can be enabled simultaneously.

### Global Controls

- **Time Span** - Adjusts the time window for visualization (0.1-10 seconds)
- **Auto-scale Y-axis** - Automatically adjusts the plot's vertical scale
- **Show Grid** - Toggles grid display on the plot

### Exporting Data

1. Enter a filename in the **Filename** field (e.g., `my_data.csv`)
2. Click **Export to CSV**
3. The file will be saved in the application directory
4. Exported data includes:
   - All enabled waveforms
   - Active envelopes (if enabled)
   - Metadata (waveform type, frequency, amplitude, etc.)

## Features

- **5 Waveform Types:** Sine, Square, Pulse, Sawtooth, Triangle
- **Up to 5 simultaneous waveforms**
- **Real-time visualization** with >30 FPS performance
- **Envelope analysis** (Max/Min envelopes)
- **CSV export** with full metadata
- **Independent waveform control**
- **Auto-scaling and grid display**

## File Structure

```
waveform_generator/
├── main.py                  # Application entry point
├── app_state.py            # State management
├── waveform_generator.py   # Waveform generation functions
├── ui_components.py        # UI and callbacks
├── data_export.py          # CSV export functionality
├── requirements.txt        # Python dependencies
├── CLAUDE.md              # Full specification document
└── README.md              # This file
```

## System Requirements

- Python 3.11 or higher
- Windows/Linux/macOS
- Minimum resolution: 1000x600 (recommended: 1200x800)

## Dependencies

- **DearPyGui** >= 1.10.0 - GUI framework
- **NumPy** >= 1.24.0 - Numerical computing
- **SciPy** >= 1.11.0 - Signal processing

## Performance

- **Target frame rate:** >30 FPS
- **Plot update latency:** <100ms
- **Memory usage:** <200MB
- **Startup time:** <2 seconds

## Keyboard Shortcuts

- Use sliders with arrow keys for fine control
- Click and drag on the plot to pan
- Scroll to zoom in/out on the plot

## Troubleshooting

**Application won't start:**
- Ensure Python 3.11+ is installed: `python --version`
- Verify dependencies are installed: `pip list`
- Activate virtual environment first

**Performance issues:**
- Reduce the number of visible waveforms
- Decrease the time span
- Disable envelopes if not needed

**Export fails:**
- Check file path permissions
- Ensure filename doesn't contain invalid characters
- The app will auto-correct the filename and add `.csv` if needed

## Version

Current version: **1.0**

See [CLAUDE.md](CLAUDE.md) for the complete specification and future roadmap.
