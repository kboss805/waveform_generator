# Waveform Analyzer

**Version:** 1.1.0
**Target Users:** Engineers visualizing up to 5 independent waveforms with envelope analysis  
**Tech Stack:** Python 3.11+, NumPy 1.24+, SciPy 1.11+, CustomTkinter 5.2+, matplotlib 3.8+

---

## Quick Start
```bash
python -m venv venv && venv\Scripts\activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Architecture (Stable - Don't Change Without Review)

### Module Responsibilities
| Module | Purpose | What It Does | What It Doesn't Do |
|--------|---------|--------------|-------------------|
| `main.py` | Entry point | CustomTkinter context, main loop | No UI creation, no business logic |
| `app_state.py` | State manager | Global state, waveform state | No UI, no calculations |
| `waveform_generator.py` | Pure functions | Wave/envelope generation | No state, no UI |
| `ui_components.py` | UI layer | CustomTkinter widgets, matplotlib plots, callbacks | No calculations |
| `data_export.py` | Export logic | CSV generation | No UI |
| `config.py` | Configuration | Load/save `default.cfg` (INI), fallback defaults | No UI, no state mutation |

### Data Flow (Core Pattern)
```
User Input → Callback → Update State → Regenerate Waveforms → Update UI → Render
                                    ↓
                            Compute Envelopes (if enabled)
```

### Design Constraints (Never Violate)
- ✅ CustomTkinter for the UI (modern Windows 11 look)
- ✅ matplotlib for plotting (dark theme)
- ✅ Native OS file dialogs for export
- ✅ NumPy only (no Pandas for CSV)
- ✅ All waveforms share same time base
- ✅ Separate UI from logic/calculations
- ✅ Windows compatible

### Performance SLAs
| Metric | Target | Critical? |
|--------|--------|-----------|
| Startup time | <2s | No |
| Plot update latency | <100ms | Yes |
| Frame rate | >30 FPS | Yes |
| Envelope calculation | <10ms | Yes |
| Memory usage | <200MB | No |

---

## User Stories (v1.0 Requirements)

### US1: Visualize Multiple Waveforms
**As an** engineer learning signal processing  
**I want to** see multiple waveforms in time domain plots simultaneously  
**So that** I can understand how waveforms behave and interact

**Acceptance Criteria:**
- ✅ Display all plots updating in real-time
- ✅ Include standard view controls like pan and zoom
- ✅ Smooth updates (>30 FPS)
- ✅ All plots update within 100ms of parameter change

### US2: Adjust Parameters Dynamically
**As an** engineer  
**I want to** adjust frequency, amplitude, and duty cycle of each waveform  
**So that** I can experiment and see immediate visual feedback

**Acceptance Criteria:**
- ✅ Frequency: 0.1-100 Hz, slider step 0.1 Hz
- ✅ Amplitude: 0-10, slider step 0.1
- ✅ Duty Cycle: 1-100%, slider step 1% (only for Square waves)
- ✅ Wave Duration: 0.5-120 seconds, step 0.5s
- ✅ All plots update immediately on parameter change (<100ms latency)
- ✅ Current values displayed clearly next to each slider

### US3: Generate Envelope Waveforms
**As an** engineer  
**I want to** optionally generate envelope waveforms from currently displayed waveforms  
**So that** I can view the maximum or minimum amplitude of all waveforms at any given sample

**Acceptance Criteria:**
- ✅ Checkbox control "Show Max Envelope" in Global Controls
- ✅ Checkbox control "Show Min Envelope" in Global Controls
- ✅ MaxEnvelope displays as green (#00FF00) glowing line when enabled
- ✅ MinEnvelope displays as red (#FF0000) glowing line when enabled
- ✅ Both can be enabled simultaneously
- ✅ Envelope waveforms update in real-time (<100ms) when:
  - Any waveform parameter changes
  - Waveforms are added/removed
  - Waveform visibility is toggled
- ✅ Envelope waveforms only calculate from enabled/visible waveforms
- ✅ Envelope checkboxes disabled when only 1 waveform exists
- ✅ Envelope waveforms appear in plot legend
- ✅ Envelope waveforms included in CSV export when enabled
- ✅ No performance degradation (maintain >30 FPS)

### US4: Export Data
**As a** researcher  
**I want to** export waveform data to CSV  
**So that** I can analyze it in other tools or share with colleagues

**Acceptance Criteria:**
- ✅ Export includes time and amplitude columns
- ✅ Metadata in CSV header (waveform type, frequency, amplitude)
- ✅ User can specify filename
- ✅ Success confirmation displayed
- ✅ CSV format compatible with Excel/MATLAB

---

## Current Feature Set (v1.1)

### Supported Waveforms
| Type | Required Parameters | Optional Parameters |
|------|-------------------|-------------------|
| Sine | frequency (0.1-100 Hz), amplitude (0-10) | - |
| Square | frequency, amplitude | duty_cycle (1-100%, default 50%) |
| Sawtooth | frequency, amplitude | - |
| Triangle | frequency, amplitude | - |

**Limits:** 5 waveforms max, 1 waveform minimum

### Envelope Analysis
- **Max Envelope:** Green (#00FF00) glowing line - highest amplitude at each time sample
- **Min Envelope:** Red (#FF0000) glowing line - lowest amplitude at each time sample
- **RMS Envelope:** Orange (#FFA500) glowing line - root-mean-square across all enabled waveforms
- **Peak-to-Peak Fill:** Cyan (#00FFFF) shaded region between max and min envelopes (appears automatically when both are enabled)
- **Glow Effect:** Layered lines (8px/6px/4px at 0.1/0.2/0.3 alpha + 2px core at full alpha)
- **Auto-hide:** Source waveforms are automatically hidden when any envelope is enabled
- **Behavior:** Disabled when ≤1 waveform, calculates from enabled waveforms only, real-time updates

### Measurement Cursors
- **Toggle:** "Cursors: ON/OFF" button in Measurement sidebar section
- **Live Tracking:** When enabled, a white cursor line follows the mouse and readout updates continuously
- **Pin Reference:** Left-click on plot to pin a dashed reference cursor for comparison
- **Readout:** Shows time and interpolated amplitude for each enabled waveform at cursor positions (Pin + Cur labels)
- **Delta:** When both pinned and live cursors present, shows ΔT between them
- **Clear Pin:** "Clear Pin" button removes the pinned reference cursor
- **Persistence:** Pinned cursor survives parameter changes (re-drawn after plot update)

### Waveform Renaming
- **Right-click** any waveform button to open context menu with "Rename..." option
- **Tooltip** on hover: "Right-click to change waveform name"
- Custom names propagate to plot legend and CSV export
- Duplicate names are rejected with a re-prompt
- Empty name reverts to default ("Waveform N")

### Configuration
- **File:** `default.cfg` (INI format) stored alongside the application or executable
- **Access:** File → Configure... opens a modal dialog (420×640)
- **Sections:**
  - **Global** — `duration` (wave duration in seconds)
  - **Waveform Defaults** — `type`, `frequency`, `amplitude`, `offset`, `duty_cycle` (applied on next launch)
  - **Display** — `y_axis_title`, `y_min`, `y_max` (applied immediately on save)
- **Behavior:** Display settings update the live plot instantly; waveform defaults are read at `app_state` import time
- **PyInstaller:** Config path resolves to the directory of the executable when frozen

### Export Capability
- **Format:** CSV with time column + amplitude columns
- **Metadata:** Timestamp, waveform parameters, sample rate, duration
- **Options:** Select which waveforms to export (including envelopes)

---

## State Model

### Per-Waveform State
```python
{
    "id": int,              # 0-4
    "wave_type": str,       # "sine" | "square" | "sawtooth" | "triangle"
    "frequency": float,     # 0.1-100.0 Hz
    "amplitude": float,     # 0.0-10.0
    "offset": float,        # 0.0-10.0
    "duty_cycle": float,    # 1.0-100.0% (Square only)
    "color": tuple,         # (R, G, B) auto-assigned
    "enabled": bool,        # Show/hide waveform
    "name": str             # Custom display name (empty = default)
}
```

### Global State
```python
{
    "duration": float,               # 0.5-120.0 seconds (wave duration)
    "sample_rate": int,              # 1000 (fixed)
    "active_waveform_index": int,    # Which waveform controls are shown
    "show_max_envelope": bool,       # MaxEnvelope visibility
    "show_min_envelope": bool,       # MinEnvelope visibility
    "show_rms_envelope": bool,       # RMS Envelope visibility
    "hide_src_wfs": bool             # Auto-set when envelopes enabled
}
```

### Initial State (Startup)
- Values loaded from `default.cfg`; built-in fallbacks used if file is missing
- Default fallback: 1 Sine waveform, 0.2 Hz, 2.0 amplitude, 8.0 offset, Yellow, enabled
- Default fallback: duration 10.0s, Envelopes: OFF

---

## UI Specification

### Layout (1200x900 default, 1000x800 minimum, Dark Theme #1a1a1a)

**Menu Bar:** File > Configure..., Help > About... (CTkMenuBar, fully dark-themed)

**Sidebar (330px, scrollable):**
```
┌─ Waveforms ──────────────────┐
│ [+ Add Waveform]             │  ← Max 5
│ [Waveform 1    ] [ON] [X]    │  ← Click=select, ON/OFF=toggle, X=remove
│ [Waveform 2    ] [OFF][X]    │     Right-click=rename, hover=tooltip
├─ Waveform Parameters ────────┤  ← Shows selected waveform
│ Type: [Sine ▼]               │
│ Wave Duration: [input][-][+] │  ← 0.5-120 seconds
│ Offset: [input] [-] [+]      │
│ Frequency: [input] [-] [+]   │
│ Amplitude: [input] [-] [+]   │
│ Duty Cycle: (hidden for Sine)│
├─ Advanced ───────────────────┤
│ ☐ Show Max Envelope          │  ← Disabled when ≤1 waveform
│ ☐ Show Min Envelope          │  ← Peak-to-Peak fill when both on
│ ☐ Show RMS Envelope          │  ← Orange glow line
├─ Measurement ────────────────┤
│ [Cursors: OFF] [Clear Pin]   │  ← Toggle + clear pinned cursor
│ Cursor readout text          │  ← Live T/Y values, pin, ΔT
├─ Export ─────────────────────┤
│ [Export to CSV]              │  ← Opens native OS file dialog
│ Status: Ready                │
└──────────────────────────────┘
```

**Main Area:** Single plot, all waveforms overlaid, shared time axis

**Status Bar:** `Waveforms: X/5`

**About Dialog:** App name, version (APP_VERSION constant), description, author info

### Color Palette (Auto-assigned)
| Waveform | Color | RGB |
|----------|-------|-----|
| 1 | Yellow | (255, 255, 0) |
| 2 | Cyan | (0, 255, 255) |
| 3 | Magenta | (255, 0, 255) |
| 4 | Green | (0, 255, 0) |
| 5 | Orange | (255, 165, 0) |
| MaxEnvelope | Green (glow) | #00FF00 |
| MinEnvelope | Red (glow) | #FF0000 |
| RMSEnvelope | Orange (glow) | #FFA500 |
| Peak-to-Peak | Cyan (fill) | #00FFFF @ 12% alpha |
| Cursors | Gray (dashed) | #AAAAAA @ 70% alpha |

### Plot Styling
- Background: #1a1a1a, Axes: #666666, Grid: #666666 @ 20% opacity
- Line width: 2px, Anti-aliasing: enabled

---

## Implementation Reference

### Wave Generation Functions
```python
import numpy as np
from scipy import signal

# All functions return (time: np.ndarray, amplitude: np.ndarray)

def generate_sine_wave(frequency: float, amplitude: float, duration: float = 1.0, sample_rate: int = 1000):
    time = np.linspace(0, duration, int(sample_rate * duration))
    return time, amplitude * np.sin(2 * np.pi * frequency * time)

def generate_square_wave(frequency: float, amplitude: float, duty_cycle: float, duration: float = 1.0, sample_rate: int = 1000):
    time = np.linspace(0, duration, int(sample_rate * duration))
    return time, amplitude * signal.square(2 * np.pi * frequency * time, duty=duty_cycle/100)

def generate_sawtooth_wave(frequency: float, amplitude: float, duration: float = 1.0, sample_rate: int = 1000):
    time = np.linspace(0, duration, int(sample_rate * duration))
    return time, amplitude * signal.sawtooth(2 * np.pi * frequency * time)

def generate_triangle_wave(frequency: float, amplitude: float, duration: float = 1.0, sample_rate: int = 1000):
    time = np.linspace(0, duration, int(sample_rate * duration))
    return time, amplitude * signal.sawtooth(2 * np.pi * frequency * time, width=0.5)

# Envelope calculations
def compute_max_envelope(waveforms: list[tuple[np.ndarray, np.ndarray]]):
    if not waveforms: return np.array([]), np.array([])
    time = waveforms[0][0]  # Shared time base
    return time, np.max(np.array([w[1] for w in waveforms]), axis=0)

def compute_min_envelope(waveforms: list[tuple[np.ndarray, np.ndarray]]):
    if not waveforms: return np.array([]), np.array([])
    time = waveforms[0][0]  # Shared time base
    return time, np.min(np.array([w[1] for w in waveforms]), axis=0)
```

### CustomTkinter + matplotlib Patterns
```python
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Configure appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create matplotlib figure with dark theme
plt.style.use('dark_background')
fig = Figure(figsize=(8, 6), facecolor='#1a1a1a')
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

# Plot waveforms
ax.clear()
ax.plot(time, amplitude, color=color, label=label, linewidth=2)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")
ax.legend()
canvas.draw()

# Entry with +/- buttons
freq_entry = ctk.CTkEntry(frame, width=120)
freq_dec_btn = ctk.CTkButton(frame, text="-", width=30, command=on_decrement)
freq_inc_btn = ctk.CTkButton(frame, text="+", width=30, command=on_increment)

# Native file dialog for export
from tkinter import filedialog
filename = filedialog.asksaveasfilename(
    defaultextension=".csv",
    filetypes=[("CSV files", "*.csv")],
    initialfile="waveforms.csv"
)
```

### CSV Export Format
```csv
# Exported: 2025-01-03 14:30:00
# MySignal: Sine, 0.2 Hz, 10.0 amp
# Waveform_2: Square, 0.2 Hz, 10.0 amp, 50.0% duty cycle
# Max_Envelope: Computed from 2 waveforms
# Sample Rate: 1000 S/s, Duration: 10.0s
Time (s),MySignal,Waveform_2,Max_Envelope
0.000000,8.000000,10.000000,10.000000
0.001000,8.001257,10.000000,10.000000
```
Note: Custom waveform names (via rename) are used for column headers. Spaces replaced with underscores.

---

## Development Standards

### Code Style
- **PEP 8** compliance, max 88 chars/line
- **Type hints** on all function signatures
- **Google-style docstrings** for public functions
- Functions <30 lines (split if longer)
- Descriptive variable names (no `a`, `b`, `x` unless math context)

### Error Handling
| Error Type | Strategy |
|------------|----------|
| Invalid parameter range | Silently clamp to valid range |
| File export failure | Show error in UI status area |
| Invalid filename | Auto-correct (remove invalid chars, add .csv) |
| Division by zero | Handle gracefully in calculations |
| No enabled waveforms | Hide envelope plots |

---

## Testing Protocol

### Pre-Commit Checklist
- [ ] All 5 wave types render correctly
- [ ] Edge cases: min/max frequency (0.1 Hz, 100 Hz), min/max amplitude (0, 10)
- [ ] Duty cycle: 1%, 50%, 100% for Square
- [ ] Wave duration: 0.5s, 10s, 120s
- [ ] Envelopes: Test with 2, 3, 5 waveforms (same phase, opposite phase)
- [ ] Mixed enabled/disabled waveforms
- [ ] Toggle max/min independently and together
- [ ] CSV export with/without envelopes
- [ ] Add/remove waveforms (test min/max limits)
- [ ] No console errors or warnings
- [ ] FPS >30 during parameter changes

### Manual Test Scenarios
1. **Startup:** Should show waveform with values from `default.cfg` (or fallback defaults)
2. **Add to max:** Add 4 more waveforms, verify limit enforcement
3. **Remove to min:** Remove to 1 waveform, verify limit enforcement
4. **Envelope edge:** Enable max/min with only 1 wave (should be disabled)
5. **Performance:** Change frequency rapidly, verify smooth updates
6. **Rename:** Right-click waveform, enter custom name, verify in list/legend/CSV
7. **Duplicate name:** Try renaming to an existing name, verify rejection
8. **Auto-hide:** Enable envelope, verify source waveforms hidden automatically
9. **Configure dialog:** Open File → Configure..., change display settings, verify plot updates immediately
10. **Config persistence:** Modify waveform defaults in Configure, restart app, verify new defaults load

---

## Future Feature Roadmap

### v1.1 - Enhanced Analysis
- ✅ **Peak-to-Peak Envelope:** Cyan shaded area between max/min (auto when both enabled)
- ✅ **RMS Envelope:** Orange glowing line, RMS across enabled waveforms
- ✅ **Measurement Cursors:** Live tracking cursor with pinned reference and ΔT

### v1.2 - Composite Operations
- [ ] **Arithmetic Operations:** Add, subtract, multiply, divide waveforms

### v1.3 - Export & Usability
- [ ] **Export Formats:** MATLAB .mat, JSON
- [ ] **Keyboard Shortcuts:** Space, A, 1-5 for quick actions
- [ ] **Color Customization:** User-selectable waveform colors
- [ ] **Theme Toggle:** Dark/light mode

### v2.0 - Advanced Features
- [ ] **Statistics Panel:** Mean, RMS, peak-to-peak per waveform
- [ ] **Multiple Plots:** Separate plots option
- [ ] **Detachable Windows:** Resizable, multi-monitor support
- ✅ **Custom User Settings:** Configurable defaults via `default.cfg` and File → Configure... dialog

---

## Adding New Features (Guide for Future Development)

### Step 1: Update This Document
1. Add feature to appropriate version section in Roadmap
2. Update State Model if new state required
3. Update UI Specification if new controls needed
4. Document any new constraints

### Step 2: Plan Architecture Impact
- Does it need new module? Update Project Structure
- Does it change data flow? Update Architecture section
- Does it affect performance SLAs? Update metrics
- Does it violate design constraints? Discuss alternatives

### Step 3: Implement
- Create functions in appropriate modules per Module Responsibilities
- Follow Code Style and Error Handling standards
- Update Testing Protocol with new test cases

### Step 4: Validate
- Run full Testing Protocol checklist
- Verify performance SLAs still met
- Update version number if releasing

---

## Common Pitfall Avoidance

### Don't:
- ❌ Use Pandas for CSV (NumPy only)
- ❌ Create separate time bases per waveform
- ❌ Put business logic in UI layer
- ❌ Use global variables excessively
- ❌ Skip type hints or docstrings
- ❌ Add new config keys without updating the Configure dialog and `save_config()`

### Do:
- ✅ Keep modules focused on single responsibility
- ✅ Separate UI creation from callbacks/logic
- ✅ Use tags for all updatable UI elements
- ✅ Test edge cases and error conditions
- ✅ Monitor FPS during development
- ✅ Clamp invalid inputs instead of crashing
- ✅ Write descriptive commit messages

---

## Questions for Claude When Starting Work

Before implementing ANY task, ask:
1. **What user story does this relate to?**
2. **What modules will I modify?**
3. **Does this change the state model?**
4. **Will this affect performance SLAs?**
5. **What edge cases should I test?**
6. **Does this violate any design constraints?**

If uncertain, **ask for clarification before coding**.
