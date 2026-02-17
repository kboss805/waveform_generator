# Changelog

All notable changes to the Waveform Analyzer project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-16

### Added
- **Detachable Plot Window** - Move the matplotlib plot to a separate resizable window
  - Accessible via File → Detach Plot menu option
  - 800×600 default window size (fully resizable)
  - Includes pan/zoom navigation toolbar in detached window
  - Live parameter updates from main window to detached plot
  - All interactive features work in detached mode (cursors, envelopes, pan/zoom)
  - Placeholder in main window with "Re-attach Plot" button
  - Multiple re-attachment options: close window, click button, or File → Attach Plot
  - Multi-monitor support - window can be moved to any display
  - Implemented as `PlotWindow` CTkToplevel class with shared Figure reference

### Changed
- Updated APP_VERSION to 2.0.0
- Refactored plot area creation to support detachment via `_create_embedded_plot_widgets()` helper method
- Canvas and toolbar references now dynamically update to point to active window (main or detached)

### Technical Details
- New `PlotWindow` class (ui_components.py:153-197) for detached window management
- Added state tracking: `self.plot_window` and `self.is_detached` flags
- New methods: `_detach_plot()`, `_attach_plot()`, `_toggle_plot_detachment()`
- Menu bar dynamically updates to show "Detach Plot" or "Attach Plot" based on state
- All existing methods work without modification due to reference update pattern

## [1.3.0] - 2025-01-XX

### Added
- Configuration dialog (File → Configure...) for setting defaults
- Theme toggle (File → Toggle Theme) for dark/light mode switching
- Theme persistence in `default.cfg`

### Changed
- Y-axis settings now configurable and apply immediately

## [1.2.0] - 2025-01-XX

### Added
- Export formats: CSV, MATLAB .mat, JSON
- Color customization via right-click context menu
- Waveform renaming via right-click context menu

### Changed
- Export button now supports multiple formats via file dialog

## [1.1.0] - 2025-01-XX

### Added
- Peak-to-Peak envelope (cyan fill between max/min)
- RMS Envelope (orange glowing line)
- Live measurement cursors with proximity highlight
- Pinned reference cursor (left-click to pin)

### Changed
- Improved cursor tracking and visual feedback

## [1.0.0] - 2024-12-XX

### Added
- Initial release
- 4 waveform types: Sine, Square, Sawtooth, Triangle
- Up to 5 simultaneous waveforms
- Real-time visualization with matplotlib
- Max/Min envelope analysis
- CSV export functionality
- Configurable parameters (frequency, amplitude, offset, duty cycle)
- CustomTkinter modern UI
- Dark theme (Windows 11 style)

[2.0.0]: https://github.com/yourusername/waveform_analyzer/compare/v1.3.0...v2.0.0
[1.3.0]: https://github.com/yourusername/waveform_analyzer/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/yourusername/waveform_analyzer/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/yourusername/waveform_analyzer/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yourusername/waveform_analyzer/releases/tag/v1.0.0
