"""
UI components and callbacks for the Real-Time Waveform Visualizer.

This module contains all DearPyGui UI creation and callback logic.
"""

import dearpygui.dearpygui as dpg
from typing import Optional
from app_state import app_state, WaveformState
from waveform_generator import generate_waveform, compute_max_envelope, compute_min_envelope
from data_export import export_to_csv, prepare_waveform_for_export


# UI element tags
MAIN_WINDOW = "main_window"
PLOT_TAG = "main_plot"
Y_AXIS_TAG = "y_axis"
STATUS_BAR = "status_bar"
TIME_SPAN_SLIDER = "time_span_slider"
FREQ_SLIDER = "freq_slider"
AMP_SLIDER = "amp_slider"
DUTY_SLIDER = "duty_slider"
DUTY_LABEL = "duty_label"
WAVE_TYPE_COMBO = "wave_type_combo"
ADD_WAVE_BTN = "add_wave_btn"
EXPORT_FILENAME = "export_filename"
EXPORT_STATUS = "export_status"
EXPORT_BTN = "export_btn"
WAVEFORM_LIST_GROUP = "waveform_list_group"
AUTO_SCALE_CHECKBOX = "auto_scale_checkbox"
SHOW_GRID_CHECKBOX = "show_grid_checkbox"
MAX_ENV_CHECKBOX = "max_env_checkbox"
MIN_ENV_CHECKBOX = "min_env_checkbox"


def update_all_plots() -> None:
    """Regenerate and update all waveform plots and envelopes."""
    # Clear existing series
    if dpg.does_item_exist(Y_AXIS_TAG):
        children = dpg.get_item_children(Y_AXIS_TAG, slot=1)
        if children:
            for child in children:
                dpg.delete_item(child)

    # Generate and plot enabled waveforms
    waveform_data = []
    for waveform in app_state.waveforms:
        if waveform.enabled:
            time, amplitude = generate_waveform(
                waveform.wave_type,
                waveform.frequency,
                waveform.amplitude,
                waveform.duty_cycle,
                app_state.time_span,
                app_state.sample_rate
            )
            waveform_data.append((time, amplitude))

            # Create series
            series_tag = f"wave_{waveform.id}_series"
            label = f"{waveform.wave_type.capitalize()} {waveform.frequency:.1f} Hz"

            # Convert color to normalized values (0-1)
            color_normalized = tuple(c / 255.0 for c in waveform.color) + (1.0,)
            color_int = tuple(int(c) for c in waveform.color) + (255,)

            dpg.add_line_series(
                time.tolist(),
                amplitude.tolist(),
                label=label,
                parent=Y_AXIS_TAG,
                tag=series_tag
            )
            dpg.bind_item_theme(series_tag, create_line_theme(color_int))

    # Update envelopes
    if app_state.can_show_envelopes():
        if app_state.show_max_envelope and waveform_data:
            time, max_env = compute_max_envelope(waveform_data)
            dpg.add_line_series(
                time.tolist(),
                max_env.tolist(),
                label="Max Envelope",
                parent=Y_AXIS_TAG,
                tag="max_env_series"
            )
            dpg.bind_item_theme("max_env_series", create_line_theme((255, 0, 0, 255), thickness=2))

        if app_state.show_min_envelope and waveform_data:
            time, min_env = compute_min_envelope(waveform_data)
            dpg.add_line_series(
                time.tolist(),
                min_env.tolist(),
                label="Min Envelope",
                parent=Y_AXIS_TAG,
                tag="min_env_series"
            )
            dpg.bind_item_theme("min_env_series", create_line_theme((0, 0, 255, 255), thickness=2))

    # Auto-scale if enabled
    if app_state.auto_scale:
        dpg.set_axis_limits_auto(Y_AXIS_TAG)

    update_status_bar()


def create_line_theme(color: tuple, thickness: float = 2.0) -> str:
    """
    Create a theme for line series.

    Args:
        color: RGBA color tuple (0-255)
        thickness: Line thickness

    Returns:
        Theme tag
    """
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvLineSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, color, category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, thickness, category=dpg.mvThemeCat_Plots)
    return theme


def on_time_span_changed(sender, value):
    """Callback for time span slider."""
    app_state.set_time_span(value)
    update_all_plots()


def on_frequency_changed(sender, value):
    """Callback for frequency slider."""
    waveform = app_state.get_active_waveform()
    if waveform:
        waveform.frequency = max(1.0, min(100.0, value))
        update_all_plots()
        update_waveform_list()


def on_amplitude_changed(sender, value):
    """Callback for amplitude slider."""
    waveform = app_state.get_active_waveform()
    if waveform:
        waveform.amplitude = max(0.0, min(10.0, value))
        update_all_plots()


def on_duty_cycle_changed(sender, value):
    """Callback for duty cycle slider."""
    waveform = app_state.get_active_waveform()
    if waveform:
        waveform.duty_cycle = max(1.0, min(100.0, value))
        update_all_plots()


def on_wave_type_changed(sender, value):
    """Callback for wave type combo box."""
    waveform = app_state.get_active_waveform()
    if waveform:
        waveform.wave_type = value.lower()
        update_waveform_controls()
        update_all_plots()
        update_waveform_list()


def on_auto_scale_changed(sender, value):
    """Callback for auto-scale checkbox."""
    app_state.auto_scale = value
    update_all_plots()


def on_show_grid_changed(sender, value):
    """Callback for show grid checkbox."""
    app_state.show_grid = value
    # Grid visibility is controlled by plot theme


def on_max_envelope_changed(sender, value):
    """Callback for max envelope checkbox."""
    app_state.show_max_envelope = value
    update_all_plots()


def on_min_envelope_changed(sender, value):
    """Callback for min envelope checkbox."""
    app_state.show_min_envelope = value
    update_all_plots()


def on_add_waveform():
    """Callback for add waveform button."""
    new_waveform = app_state.add_waveform()
    if new_waveform:
        update_waveform_list()
        update_waveform_controls()
        update_envelope_controls()
        update_all_plots()
        update_add_button()


def on_remove_waveform(waveform_id: int):
    """
    Callback for remove waveform button.

    Args:
        waveform_id: ID of waveform to remove
    """
    if app_state.remove_waveform(waveform_id):
        update_waveform_list()
        update_waveform_controls()
        update_envelope_controls()
        update_all_plots()
        update_add_button()


def on_toggle_waveform(waveform_id: int):
    """
    Callback for toggle waveform visibility.

    Args:
        waveform_id: ID of waveform to toggle
    """
    waveform = app_state.get_waveform(waveform_id)
    if waveform:
        waveform.enabled = not waveform.enabled
        update_envelope_controls()
        update_all_plots()
        update_waveform_list()


def on_select_waveform(waveform_id: int):
    """
    Callback for selecting a waveform.

    Args:
        waveform_id: ID of waveform to select
    """
    app_state.active_waveform_index = waveform_id
    update_waveform_controls()
    update_waveform_list()


def on_export():
    """Callback for export button."""
    filename = dpg.get_value(EXPORT_FILENAME)

    # Collect enabled waveform data
    waveforms_to_export = []
    for waveform in app_state.get_enabled_waveforms():
        time, amplitude = generate_waveform(
            waveform.wave_type,
            waveform.frequency,
            waveform.amplitude,
            waveform.duty_cycle,
            app_state.time_span,
            app_state.sample_rate
        )

        name = f"Waveform_{waveform.id + 1}_{waveform.wave_type.capitalize()}"
        waveform_data = prepare_waveform_for_export(
            name, time, amplitude,
            waveform.wave_type,
            waveform.frequency,
            waveform.amplitude,
            waveform.duty_cycle
        )
        waveforms_to_export.append(waveform_data)

    # Collect envelope data if enabled
    envelopes_to_export = []
    if app_state.can_show_envelopes():
        waveform_data = []
        for waveform in app_state.get_enabled_waveforms():
            time, amplitude = generate_waveform(
                waveform.wave_type,
                waveform.frequency,
                waveform.amplitude,
                waveform.duty_cycle,
                app_state.time_span,
                app_state.sample_rate
            )
            waveform_data.append((time, amplitude))

        if app_state.show_max_envelope:
            time, max_env = compute_max_envelope(waveform_data)
            envelopes_to_export.append(("Max_Envelope", time, max_env))

        if app_state.show_min_envelope:
            time, min_env = compute_min_envelope(waveform_data)
            envelopes_to_export.append(("Min_Envelope", time, min_env))

    # Export
    success, message = export_to_csv(
        filename,
        waveforms_to_export,
        envelopes_to_export if envelopes_to_export else None,
        app_state.sample_rate,
        app_state.time_span
    )

    # Update status
    dpg.set_value(EXPORT_STATUS, message)


def update_waveform_list():
    """Update the waveform list UI."""
    if dpg.does_item_exist(WAVEFORM_LIST_GROUP):
        dpg.delete_item(WAVEFORM_LIST_GROUP, children_only=True)

        for waveform in app_state.waveforms:
            with dpg.group(horizontal=True, parent=WAVEFORM_LIST_GROUP):
                # Selection indicator
                is_active = waveform.id == app_state.active_waveform_index
                symbol = "●" if is_active else "○"

                # Waveform info button
                label = f"{symbol} {waveform.wave_type.capitalize()} {waveform.frequency:.1f} Hz"
                if not waveform.enabled:
                    label = f"[Disabled] {label}"

                dpg.add_button(
                    label=label,
                    width=180,
                    callback=lambda s, a, u: on_select_waveform(u),
                    user_data=waveform.id
                )

                # Toggle visibility button
                eye_symbol = "👁" if waveform.enabled else "⊗"
                dpg.add_button(
                    label=eye_symbol,
                    width=30,
                    callback=lambda s, a, u: on_toggle_waveform(u),
                    user_data=waveform.id
                )

                # Remove button (disabled if at min waveforms)
                can_remove = len(app_state.waveforms) > app_state.MIN_WAVEFORMS
                dpg.add_button(
                    label="X",
                    width=30,
                    callback=lambda s, a, u: on_remove_waveform(u),
                    user_data=waveform.id,
                    enabled=can_remove
                )


def update_waveform_controls():
    """Update waveform control sliders based on active waveform."""
    waveform = app_state.get_active_waveform()
    if not waveform:
        return

    # Update sliders
    dpg.set_value(FREQ_SLIDER, waveform.frequency)
    dpg.set_value(AMP_SLIDER, waveform.amplitude)
    dpg.set_value(DUTY_SLIDER, waveform.duty_cycle)
    dpg.set_value(WAVE_TYPE_COMBO, waveform.wave_type.capitalize())

    # Show/hide duty cycle for square and pulse waves
    needs_duty = waveform.wave_type.lower() in ['square', 'pulse']
    dpg.configure_item(DUTY_SLIDER, show=needs_duty)
    dpg.configure_item(DUTY_LABEL, show=needs_duty)


def update_envelope_controls():
    """Enable/disable envelope checkboxes based on number of enabled waveforms."""
    can_show = app_state.can_show_envelopes()
    dpg.configure_item(MAX_ENV_CHECKBOX, enabled=can_show)
    dpg.configure_item(MIN_ENV_CHECKBOX, enabled=can_show)

    if not can_show:
        app_state.show_max_envelope = False
        app_state.show_min_envelope = False
        dpg.set_value(MAX_ENV_CHECKBOX, False)
        dpg.set_value(MIN_ENV_CHECKBOX, False)


def update_add_button():
    """Enable/disable add waveform button based on max limit."""
    can_add = len(app_state.waveforms) < app_state.MAX_WAVEFORMS
    dpg.configure_item(ADD_WAVE_BTN, enabled=can_add)


def update_status_bar():
    """Update status bar with current info."""
    num_waveforms = len(app_state.waveforms)
    fps = dpg.get_frame_rate()
    status_text = f"Sample Rate: {app_state.sample_rate} S/s | FPS: {fps:.0f} | Waveforms: {num_waveforms}/{app_state.MAX_WAVEFORMS}"
    dpg.set_value(STATUS_BAR, status_text)


def create_ui():
    """Create the main UI layout."""
    with dpg.window(label="Real-Time Waveform Visualizer", tag=MAIN_WINDOW, width=1200, height=800):
        with dpg.group(horizontal=True):
            # Sidebar
            with dpg.child_window(width=300, height=-25):
                # Global Controls
                dpg.add_text("Global Controls", color=(255, 255, 0))
                dpg.add_separator()

                dpg.add_slider_float(
                    label="Time Span (s)",
                    tag=TIME_SPAN_SLIDER,
                    default_value=1.0,
                    min_value=0.1,
                    max_value=10.0,
                    callback=on_time_span_changed,
                    width=200
                )

                dpg.add_checkbox(
                    label="Auto-scale Y-axis",
                    tag=AUTO_SCALE_CHECKBOX,
                    default_value=True,
                    callback=on_auto_scale_changed
                )

                dpg.add_checkbox(
                    label="Show Grid",
                    tag=SHOW_GRID_CHECKBOX,
                    default_value=True,
                    callback=on_show_grid_changed
                )

                dpg.add_checkbox(
                    label="Show Max Envelope",
                    tag=MAX_ENV_CHECKBOX,
                    default_value=False,
                    callback=on_max_envelope_changed,
                    enabled=False
                )

                dpg.add_checkbox(
                    label="Show Min Envelope",
                    tag=MIN_ENV_CHECKBOX,
                    default_value=False,
                    callback=on_min_envelope_changed,
                    enabled=False
                )

                dpg.add_separator()

                # Waveforms List
                dpg.add_text("Waveforms", color=(255, 255, 0))
                dpg.add_separator()

                dpg.add_button(
                    label="+ Add Waveform",
                    tag=ADD_WAVE_BTN,
                    callback=on_add_waveform,
                    width=-1
                )

                dpg.add_group(tag=WAVEFORM_LIST_GROUP)

                dpg.add_separator()

                # Waveform Controls
                dpg.add_text("Waveform Controls", color=(255, 255, 0))
                dpg.add_separator()

                dpg.add_combo(
                    label="Type",
                    tag=WAVE_TYPE_COMBO,
                    items=["Sine", "Square", "Pulse", "Sawtooth", "Triangle"],
                    default_value="Sine",
                    callback=on_wave_type_changed,
                    width=200
                )

                dpg.add_slider_float(
                    label="Frequency (Hz)",
                    tag=FREQ_SLIDER,
                    default_value=5.0,
                    min_value=1.0,
                    max_value=100.0,
                    callback=on_frequency_changed,
                    width=200
                )

                dpg.add_slider_float(
                    label="Amplitude",
                    tag=AMP_SLIDER,
                    default_value=5.0,
                    min_value=0.0,
                    max_value=10.0,
                    callback=on_amplitude_changed,
                    width=200
                )

                dpg.add_text("Duty Cycle (%)", tag=DUTY_LABEL, show=False)
                dpg.add_slider_float(
                    tag=DUTY_SLIDER,
                    default_value=50.0,
                    min_value=1.0,
                    max_value=100.0,
                    callback=on_duty_cycle_changed,
                    width=200,
                    show=False
                )

                dpg.add_separator()

                # Export
                dpg.add_text("Export", color=(255, 255, 0))
                dpg.add_separator()

                dpg.add_input_text(
                    label="Filename",
                    tag=EXPORT_FILENAME,
                    default_value="waveforms.csv",
                    width=200
                )

                dpg.add_button(
                    label="Export to CSV",
                    tag=EXPORT_BTN,
                    callback=on_export,
                    width=-1
                )

                dpg.add_text("Status: Ready", tag=EXPORT_STATUS, color=(0, 255, 0))

            # Main plot area
            with dpg.child_window(height=-25):
                with dpg.plot(label="Waveforms", height=-1, width=-1, tag=PLOT_TAG):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
                    dpg.add_plot_axis(dpg.mvYAxis, label="Amplitude", tag=Y_AXIS_TAG)

        # Status bar
        dpg.add_text("", tag=STATUS_BAR)

    # Initialize UI state
    update_waveform_list()
    update_waveform_controls()
    update_envelope_controls()
    update_add_button()
    update_all_plots()
