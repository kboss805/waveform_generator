"""
UI components for the Real-Time Waveform Visualizer.

This module contains all CustomTkinter UI creation and callback logic.
"""

import os
import sys
import customtkinter as ctk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from app_state import (
    app_state, DEFAULT_DURATION,
    DURATION_MIN, DURATION_MAX, DURATION_STEP,
    FREQ_MIN, FREQ_MAX, FREQ_STEP,
    AMP_MIN, AMP_MAX, AMP_STEP,
    OFFSET_MIN, OFFSET_MAX, OFFSET_STEP,
    DUTY_MIN, DUTY_MAX, DUTY_STEP
)
from waveform_generator import gen_wf, compute_max_env, compute_min_env
from data_export import export_to_csv, prep_wf_for_export


# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color constants
SECTION_HEADER_COLOR = "#FFFF00"  # Yellow
ENABLED_TEXT_COLOR = "#FFFFFF"
DISABLED_TEXT_COLOR = "#808080"


class WaveformApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Waveform Generator/Analyzer")
        self.geometry("1200x900")
        self.minsize(1000, 800)

        # Set window icon
        self._set_icon()

        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Store widget references
        self.wf_buttons = []
        self.toggle_buttons = []
        self.remove_buttons = []

        # Create UI components
        self._create_sidebar()
        self._create_plot_area()
        self._create_status_bar()

        # Initialize UI state
        self._update_wf_list()
        self._update_wf_parameters()
        self._update_env_controls()
        self._update_add_button()
        self._update_all_plots()

    def _set_icon(self):
        """Set the window icon if available."""
        # Determine base path (handles PyInstaller bundled app)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(base_path, "icon.ico")

        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

    def _create_sidebar(self):
        """Create the sidebar with all controls."""
        # Sidebar frame with scrolling
        self.sidebar = ctk.CTkScrollableFrame(self, width=330)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=(10, 0))

        # === Waveforms ===
        self._add_section_header("Waveforms")

        # Add Waveform button
        self.add_wf_btn = ctk.CTkButton(
            self.sidebar, text="+ Add Waveform",
            command=self._on_add_wf
        )
        self.add_wf_btn.pack(fill="x", pady=(5, 5))

        # Waveform list container
        self.wf_list_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.wf_list_frame.pack(fill="x", pady=(0, 10))

        # === Waveform Parameters ===
        self._add_section_header("Waveform Parameters")

        # Waveform Type
        ctk.CTkLabel(self.sidebar, text="Type").pack(anchor="w", pady=(5, 2))
        self.wf_type_combo = ctk.CTkComboBox(
            self.sidebar,
            values=["Sine", "Square", "Sawtooth", "Triangle"],
            command=self._on_wf_type_changed,
            width=200
        )
        self.wf_type_combo.pack(anchor="w", pady=(0, 5))
        self.wf_type_combo.set("Sine")

        # Wave Duration
        ctk.CTkLabel(self.sidebar, text="Wave Duration (s)").pack(anchor="w", pady=(5, 2))
        self.duration_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.duration_frame.pack(fill="x", pady=(0, 5))

        self.duration_entry = ctk.CTkEntry(self.duration_frame, width=120)
        self.duration_entry.pack(side="left", padx=(0, 5))
        self.duration_entry.insert(0, str(DEFAULT_DURATION))
        self.duration_entry.bind("<Return>", self._on_duration_enter)
        self.duration_entry.bind("<FocusOut>", self._on_duration_enter)

        self.duration_dec_btn = ctk.CTkButton(
            self.duration_frame, text="-", width=30,
            command=self._on_duration_dec
        )
        self.duration_dec_btn.pack(side="left", padx=2)

        self.duration_inc_btn = ctk.CTkButton(
            self.duration_frame, text="+", width=30,
            command=self._on_duration_inc
        )
        self.duration_inc_btn.pack(side="left", padx=2)

        # Offset
        ctk.CTkLabel(self.sidebar, text="Offset").pack(anchor="w", pady=(5, 2))
        self.offset_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.offset_frame.pack(fill="x", pady=(0, 5))

        self.offset_entry = ctk.CTkEntry(self.offset_frame, width=120)
        self.offset_entry.pack(side="left", padx=(0, 5))
        self.offset_entry.insert(0, "5.0")
        self.offset_entry.bind("<Return>", self._on_offset_enter)
        self.offset_entry.bind("<FocusOut>", self._on_offset_enter)

        self.offset_dec_btn = ctk.CTkButton(
            self.offset_frame, text="-", width=30,
            command=self._on_offset_dec
        )
        self.offset_dec_btn.pack(side="left", padx=2)

        self.offset_inc_btn = ctk.CTkButton(
            self.offset_frame, text="+", width=30,
            command=self._on_offset_inc
        )
        self.offset_inc_btn.pack(side="left", padx=2)

        # Frequency
        ctk.CTkLabel(self.sidebar, text="Frequency (Hz)").pack(anchor="w", pady=(5, 2))
        self.freq_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.freq_frame.pack(fill="x", pady=(0, 5))

        self.freq_entry = ctk.CTkEntry(self.freq_frame, width=120)
        self.freq_entry.pack(side="left", padx=(0, 5))
        self.freq_entry.insert(0, str(FREQ_MIN))
        self.freq_entry.bind("<Return>", self._on_freq_enter)
        self.freq_entry.bind("<FocusOut>", self._on_freq_enter)

        self.freq_dec_btn = ctk.CTkButton(
            self.freq_frame, text="-", width=30,
            command=self._on_freq_dec
        )
        self.freq_dec_btn.pack(side="left", padx=2)

        self.freq_inc_btn = ctk.CTkButton(
            self.freq_frame, text="+", width=30,
            command=self._on_freq_inc
        )
        self.freq_inc_btn.pack(side="left", padx=2)

        # Amplitude
        ctk.CTkLabel(self.sidebar, text="Amplitude").pack(anchor="w", pady=(5, 2))
        self.amp_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.amp_frame.pack(fill="x", pady=(0, 5))

        self.amp_entry = ctk.CTkEntry(self.amp_frame, width=120)
        self.amp_entry.pack(side="left", padx=(0, 5))
        self.amp_entry.insert(0, "5.0")
        self.amp_entry.bind("<Return>", self._on_amp_enter)
        self.amp_entry.bind("<FocusOut>", self._on_amp_enter)

        self.amp_dec_btn = ctk.CTkButton(
            self.amp_frame, text="-", width=30,
            command=self._on_amp_dec
        )
        self.amp_dec_btn.pack(side="left", padx=2)

        self.amp_inc_btn = ctk.CTkButton(
            self.amp_frame, text="+", width=30,
            command=self._on_amp_inc
        )
        self.amp_inc_btn.pack(side="left", padx=2)

        # Duty Cycle (hidden by default, shown for Square waves)
        self.duty_label = ctk.CTkLabel(self.sidebar, text="Duty Cycle (%)")
        self.duty_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")

        self.duty_entry = ctk.CTkEntry(self.duty_frame, width=120)
        self.duty_entry.pack(side="left", padx=(0, 5))
        self.duty_entry.insert(0, "50.0")
        self.duty_entry.bind("<Return>", self._on_duty_enter)
        self.duty_entry.bind("<FocusOut>", self._on_duty_enter)

        self.duty_dec_btn = ctk.CTkButton(
            self.duty_frame, text="-", width=30,
            command=self._on_duty_dec
        )
        self.duty_dec_btn.pack(side="left", padx=2)

        self.duty_inc_btn = ctk.CTkButton(
            self.duty_frame, text="+", width=30,
            command=self._on_duty_inc
        )
        self.duty_inc_btn.pack(side="left", padx=2)

        # === Advanced ===
        self._add_section_header("Advanced")

        # Max Envelope checkbox
        max_env_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        max_env_frame.pack(fill="x", pady=2)
        self.show_max_env_var = ctk.BooleanVar(value=False)
        self.show_max_env_cb = ctk.CTkCheckBox(
            max_env_frame, text="",
            variable=self.show_max_env_var,
            command=self._on_max_env_changed,
            width=24
        )
        self.show_max_env_cb.pack(side="left")
        self.show_max_env_label = ctk.CTkLabel(max_env_frame, text="Show Max Envelope")
        self.show_max_env_label.pack(side="left")

        # Min Envelope checkbox
        min_env_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        min_env_frame.pack(fill="x", pady=2)
        self.show_min_env_var = ctk.BooleanVar(value=False)
        self.show_min_env_cb = ctk.CTkCheckBox(
            min_env_frame, text="",
            variable=self.show_min_env_var,
            command=self._on_min_env_changed,
            width=24
        )
        self.show_min_env_cb.pack(side="left")
        self.show_min_env_label = ctk.CTkLabel(min_env_frame, text="Show Min Envelope")
        self.show_min_env_label.pack(side="left")

        # Hide Source Waveforms checkbox
        hide_src_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        hide_src_frame.pack(fill="x", pady=(2, 10))
        self.hide_src_var = ctk.BooleanVar(value=False)
        self.hide_src_cb = ctk.CTkCheckBox(
            hide_src_frame, text="",
            variable=self.hide_src_var,
            command=self._on_hide_src_changed,
            width=24
        )
        self.hide_src_cb.pack(side="left")
        self.hide_src_label = ctk.CTkLabel(hide_src_frame, text="Hide Source Waveforms")
        self.hide_src_label.pack(side="left")

        # === Export ===
        self._add_section_header("Export")

        ctk.CTkButton(
            self.sidebar, text="Export to CSV",
            command=self._on_export_clicked
        ).pack(fill="x", pady=(5, 5))

        self.export_status = ctk.CTkLabel(
            self.sidebar, text="Status: Ready",
            text_color="#00FF00"
        )
        self.export_status.pack(anchor="w", pady=(5, 10))

    def _create_plot_area(self):
        """Create the matplotlib plot area."""
        # Plot container
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=(10, 0))
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)

        # Create matplotlib figure with dark theme
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(8, 6), facecolor='#1a1a1a')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1a1a1a')

        # Configure axes
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True, alpha=0.3, color='#666666')

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Add navigation toolbar for pan/zoom
        toolbar_frame = ctk.CTkFrame(self.plot_frame, fg_color="transparent")
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ctk.CTkLabel(
            self, text="Waveforms: 1/5",
            anchor="w"
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))

    def _add_section_header(self, text: str):
        """Add a section header with separator."""
        # Separator line
        separator = ctk.CTkFrame(self.sidebar, height=1, fg_color="#666666")
        separator.pack(fill="x", pady=(10, 5))

        # Header text
        header = ctk.CTkLabel(
            self.sidebar, text=text,
            text_color=SECTION_HEADER_COLOR,
            font=ctk.CTkFont(weight="bold")
        )
        header.pack(anchor="w")

    # === Callback Methods ===

    def _on_duration_enter(self, event=None):
        """Handle duration entry."""
        try:
            value = float(self.duration_entry.get())
            value = max(DURATION_MIN, min(DURATION_MAX, value))
            app_state.set_duration(value)
            self.duration_entry.delete(0, "end")
            self.duration_entry.insert(0, f"{value:.1f}")
            self._update_duration_btns()
            self._update_all_plots()
        except ValueError:
            self.duration_entry.delete(0, "end")
            self.duration_entry.insert(0, f"{app_state.duration:.1f}")

    def _on_duration_inc(self):
        """Increment duration."""
        new_value = min(DURATION_MAX, app_state.duration + DURATION_STEP)
        app_state.set_duration(new_value)
        self.duration_entry.delete(0, "end")
        self.duration_entry.insert(0, f"{new_value:.1f}")
        self._update_duration_btns()
        self._update_all_plots()

    def _on_duration_dec(self):
        """Decrement duration."""
        new_value = max(DURATION_MIN, app_state.duration - DURATION_STEP)
        app_state.set_duration(new_value)
        self.duration_entry.delete(0, "end")
        self.duration_entry.insert(0, f"{new_value:.1f}")
        self._update_duration_btns()
        self._update_all_plots()

    def _on_max_env_changed(self):
        """Handle max envelope toggle."""
        app_state.show_max_env = self.show_max_env_var.get()
        self._update_env_controls()
        self._update_all_plots()

    def _on_min_env_changed(self):
        """Handle min envelope toggle."""
        app_state.show_min_env = self.show_min_env_var.get()
        self._update_env_controls()
        self._update_all_plots()

    def _on_hide_src_changed(self):
        """Handle hide source waveforms toggle."""
        app_state.hide_src_wfs = self.hide_src_var.get()
        self._update_wf_management_controls()
        self._update_all_plots()

    def _on_add_wf(self):
        """Add a new waveform."""
        new_wf = app_state.add_wf()
        if new_wf:
            self._update_wf_list()
            self._update_wf_parameters()
            self._update_env_controls()
            self._update_all_plots()
            self._update_add_button()

    def _on_remove_wf(self, wf_id: int):
        """Remove a waveform."""
        if app_state.remove_wf(wf_id):
            self._update_wf_list()
            self._update_wf_parameters()
            self._update_env_controls()
            self._update_all_plots()
            self._update_add_button()

    def _on_toggle_wf(self, wf_id: int):
        """Toggle waveform visibility."""
        wf = app_state.get_wf(wf_id)
        if wf:
            wf.enabled = not wf.enabled
            self._update_env_controls()
            self._update_all_plots()
            self._update_wf_list()

    def _on_select_wf(self, wf_id: int):
        """Select a waveform for editing."""
        app_state.active_wf_index = wf_id
        self._update_wf_parameters()
        self._update_wf_list()

    def _on_wf_type_changed(self, value: str):
        """Handle waveform type change."""
        wf = app_state.get_active_wf()
        if wf:
            wf.wf_type = value.lower()
            self._update_wf_parameters()
            self._update_all_plots()

    def _on_freq_enter(self, event=None):
        """Handle frequency entry."""
        wf = app_state.get_active_wf()
        if wf:
            try:
                value = float(self.freq_entry.get())
                value = max(FREQ_MIN, min(FREQ_MAX, value))
                wf.freq = value
                self.freq_entry.delete(0, "end")
                self.freq_entry.insert(0, f"{value:.1f}")
                self._update_freq_btns()
                self._update_all_plots()
            except ValueError:
                self.freq_entry.delete(0, "end")
                self.freq_entry.insert(0, f"{wf.freq:.1f}")

    def _on_freq_inc(self):
        """Increment frequency."""
        wf = app_state.get_active_wf()
        if wf:
            new_value = min(FREQ_MAX, wf.freq + FREQ_STEP)
            wf.freq = new_value
            self.freq_entry.delete(0, "end")
            self.freq_entry.insert(0, f"{new_value:.1f}")
            self._update_freq_btns()
            self._update_all_plots()

    def _on_freq_dec(self):
        """Decrement frequency."""
        wf = app_state.get_active_wf()
        if wf:
            new_value = max(FREQ_MIN, wf.freq - FREQ_STEP)
            wf.freq = new_value
            self.freq_entry.delete(0, "end")
            self.freq_entry.insert(0, f"{new_value:.1f}")
            self._update_freq_btns()
            self._update_all_plots()

    def _on_amp_enter(self, event=None):
        """Handle amplitude entry."""
        wf = app_state.get_active_wf()
        if wf:
            try:
                value = float(self.amp_entry.get())
                value = max(AMP_MIN, min(AMP_MAX, value))
                wf.amp = value
                self.amp_entry.delete(0, "end")
                self.amp_entry.insert(0, f"{value:.1f}")
                self._update_amp_btns()
                self._update_all_plots()
            except ValueError:
                self.amp_entry.delete(0, "end")
                self.amp_entry.insert(0, f"{wf.amp:.1f}")

    def _on_amp_inc(self):
        """Increment amplitude."""
        wf = app_state.get_active_wf()
        if wf:
            new_value = min(AMP_MAX, wf.amp + AMP_STEP)
            wf.amp = new_value
            self.amp_entry.delete(0, "end")
            self.amp_entry.insert(0, f"{new_value:.1f}")
            self._update_amp_btns()
            self._update_all_plots()

    def _on_amp_dec(self):
        """Decrement amplitude."""
        wf = app_state.get_active_wf()
        if wf:
            new_value = max(AMP_MIN, wf.amp - AMP_STEP)
            wf.amp = new_value
            self.amp_entry.delete(0, "end")
            self.amp_entry.insert(0, f"{new_value:.1f}")
            self._update_amp_btns()
            self._update_all_plots()

    def _on_offset_enter(self, event=None):
        """Handle offset entry."""
        wf = app_state.get_active_wf()
        if wf:
            try:
                value = float(self.offset_entry.get())
                value = max(OFFSET_MIN, min(OFFSET_MAX, value))
                wf.offset = value
                self.offset_entry.delete(0, "end")
                self.offset_entry.insert(0, f"{value:.1f}")
                self._update_offset_btns()
                self._update_all_plots()
            except ValueError:
                self.offset_entry.delete(0, "end")
                self.offset_entry.insert(0, f"{wf.offset:.1f}")

    def _on_offset_inc(self):
        """Increment offset."""
        wf = app_state.get_active_wf()
        if wf:
            new_value = min(OFFSET_MAX, wf.offset + OFFSET_STEP)
            wf.offset = new_value
            self.offset_entry.delete(0, "end")
            self.offset_entry.insert(0, f"{new_value:.1f}")
            self._update_offset_btns()
            self._update_all_plots()

    def _on_offset_dec(self):
        """Decrement offset."""
        wf = app_state.get_active_wf()
        if wf:
            new_value = max(OFFSET_MIN, wf.offset - OFFSET_STEP)
            wf.offset = new_value
            self.offset_entry.delete(0, "end")
            self.offset_entry.insert(0, f"{new_value:.1f}")
            self._update_offset_btns()
            self._update_all_plots()

    def _on_duty_enter(self, event=None):
        """Handle duty cycle entry."""
        wf = app_state.get_active_wf()
        if wf:
            try:
                value = float(self.duty_entry.get())
                value = max(DUTY_MIN, min(DUTY_MAX, value))
                wf.duty_cycle = value
                self.duty_entry.delete(0, "end")
                self.duty_entry.insert(0, f"{value:.1f}")
                self._update_duty_btns()
                self._update_all_plots()
            except ValueError:
                self.duty_entry.delete(0, "end")
                self.duty_entry.insert(0, f"{wf.duty_cycle:.1f}")

    def _on_duty_inc(self):
        """Increment duty cycle."""
        wf = app_state.get_active_wf()
        if wf:
            new_value = min(DUTY_MAX, wf.duty_cycle + DUTY_STEP)
            wf.duty_cycle = new_value
            self.duty_entry.delete(0, "end")
            self.duty_entry.insert(0, f"{new_value:.1f}")
            self._update_duty_btns()
            self._update_all_plots()

    def _on_duty_dec(self):
        """Decrement duty cycle."""
        wf = app_state.get_active_wf()
        if wf:
            new_value = max(DUTY_MIN, wf.duty_cycle - DUTY_STEP)
            wf.duty_cycle = new_value
            self.duty_entry.delete(0, "end")
            self.duty_entry.insert(0, f"{new_value:.1f}")
            self._update_duty_btns()
            self._update_all_plots()

    def _on_export_clicked(self):
        """Handle export button click - shows native file dialog."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="waveforms.csv",
            title="Export Waveforms to CSV"
        )

        if not filename:
            return  # User cancelled

        # Collect enabled waveform data
        wfs_to_export = []
        wf_arrays = []
        for wf in app_state.get_enabled_wfs():
            time, amp = gen_wf(
                wf.wf_type,
                wf.freq,
                wf.amp,
                wf.offset,
                wf.duty_cycle,
                app_state.duration,
                app_state.sample_rate
            )
            wf_arrays.append((time, amp))

            name = f"Waveform_{wf.id + 1}_{wf.wf_type.capitalize()}"
            export_data = prep_wf_for_export(
                name, time, amp,
                wf.wf_type,
                wf.freq,
                wf.amp,
                wf.offset,
                wf.duty_cycle
            )
            wfs_to_export.append(export_data)

        # Collect envelope data if enabled
        envs_to_export = []
        if app_state.can_show_envelopes() and wf_arrays:
            if app_state.show_max_env:
                time, max_env = compute_max_env(wf_arrays)
                envs_to_export.append(("Max_Envelope", time, max_env))

            if app_state.show_min_env:
                time, min_env = compute_min_env(wf_arrays)
                envs_to_export.append(("Min_Envelope", time, min_env))

        # Export
        success, message = export_to_csv(
            filename,
            wfs_to_export,
            envs_to_export if envs_to_export else None,
            app_state.sample_rate,
            app_state.duration
        )

        # Update status
        if success:
            self.export_status.configure(text=message, text_color="#00FF00")
        else:
            self.export_status.configure(text=message, text_color="#FF0000")

    # === UI Update Methods ===

    def _update_all_plots(self):
        """Regenerate and update all waveform plots."""
        self.ax.clear()

        # Configure axes
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_xlim(0, app_state.duration)
        self.ax.set_ylim(0, 15)
        self.ax.grid(visible=True, alpha=0.3, color='#666666')

        # Generate and plot enabled waveforms
        wf_data = []
        for wf in app_state.wfs:
            if wf.enabled:
                time, amp = gen_wf(
                    wf.wf_type,
                    wf.freq,
                    wf.amp,
                    wf.offset,
                    wf.duty_cycle,
                    app_state.duration,
                    app_state.sample_rate
                )
                wf_data.append((time, amp))

                # Only plot if not hiding source waveforms
                if not app_state.hide_src_wfs:
                    # Convert RGB tuple to matplotlib color format
                    color = tuple(c / 255 for c in wf.color)
                    label = f"Waveform {wf.id + 1}"
                    self.ax.plot(time, amp, color=color, label=label, linewidth=2)

        # Plot envelopes
        if app_state.can_show_envelopes() and wf_data:
            if app_state.show_max_env:
                time, max_env = compute_max_env(wf_data)
                self.ax.plot(time, max_env, color='darkblue', label='Max Envelope',
                           linewidth=2, linestyle='--')

            if app_state.show_min_env:
                time, min_env = compute_min_env(wf_data)
                self.ax.plot(time, min_env, color='red', label='Min Envelope',
                           linewidth=2, linestyle='--')

        # Add legend if there are any lines
        if self.ax.get_lines():
            self.ax.legend(loc='upper right')

        # Redraw canvas
        self.canvas.draw()

        # Update status bar
        self._update_status_bar()

    def _update_wf_list(self):
        """Update the waveform list UI."""
        # Clear existing widgets safely
        children = list(self.wf_list_frame.winfo_children())
        for widget in children:
            try:
                widget.destroy()
            except Exception:
                pass

        self.wf_buttons = []
        self.toggle_buttons = []
        self.remove_buttons = []

        for wf in app_state.wfs:
            row_frame = ctk.CTkFrame(self.wf_list_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            # Selection button
            is_selected = wf.id == app_state.active_wf_index
            fg_color = "#3d3d6b" if is_selected else "#2b2b2b"
            border_color = "#6496ff" if is_selected else "#2b2b2b"
            border_width = 2 if is_selected else 0

            wf_btn = ctk.CTkButton(
                row_frame,
                text=f"Waveform {wf.id + 1}",
                width=180,
                fg_color=fg_color,
                border_color=border_color,
                border_width=border_width,
                command=lambda wid=wf.id: self._on_select_wf(wid)
            )
            wf_btn.pack(side="left", padx=(0, 5))
            self.wf_buttons.append(wf_btn)

            # Visibility toggle button
            vis_text = "ON" if wf.enabled else "OFF"
            vis_color = "#009600" if wf.enabled else "#646464"
            vis_btn = ctk.CTkButton(
                row_frame,
                text=vis_text,
                width=40,
                fg_color=vis_color,
                command=lambda wid=wf.id: self._on_toggle_wf(wid)
            )
            vis_btn.pack(side="left", padx=2)
            self.toggle_buttons.append(vis_btn)

            # Remove button (only show if more than 1 waveform)
            if len(app_state.wfs) > app_state.MIN_WFS:
                is_enabled = not app_state.hide_src_wfs
                remove_btn = ctk.CTkButton(
                    row_frame,
                    text="X",
                    width=30,
                    fg_color="#8B0000" if is_enabled else "#646464",
                    state="normal" if is_enabled else "disabled",
                    command=lambda wid=wf.id: self._on_remove_wf(wid)
                )
                remove_btn.pack(side="left", padx=2)
                self.remove_buttons.append(remove_btn)

    def _update_wf_parameters(self):
        """Update waveform parameter inputs based on active waveform."""
        wf = app_state.get_active_wf()
        if not wf:
            return

        # Update entry fields
        self.freq_entry.delete(0, "end")
        self.freq_entry.insert(0, f"{wf.freq:.1f}")

        self.amp_entry.delete(0, "end")
        self.amp_entry.insert(0, f"{wf.amp:.1f}")

        self.offset_entry.delete(0, "end")
        self.offset_entry.insert(0, f"{wf.offset:.1f}")

        self.duty_entry.delete(0, "end")
        self.duty_entry.insert(0, f"{wf.duty_cycle:.1f}")

        self.wf_type_combo.set(wf.wf_type.capitalize())

        # Update button states
        self._update_freq_btns()
        self._update_amp_btns()
        self._update_offset_btns()
        self._update_duty_btns()

        # Show/hide duty cycle for square waves
        needs_duty = wf.wf_type.lower() == 'square'
        if needs_duty:
            self.duty_label.pack(anchor="w", pady=(5, 2), after=self.amp_frame)
            self.duty_frame.pack(fill="x", pady=(0, 5), after=self.duty_label)
        else:
            self.duty_label.pack_forget()
            self.duty_frame.pack_forget()

    def _update_duration_btns(self):
        """Update duration button states."""
        at_min = app_state.duration <= DURATION_MIN
        at_max = app_state.duration >= DURATION_MAX
        self.duration_dec_btn.configure(state="disabled" if at_min else "normal")
        self.duration_inc_btn.configure(state="disabled" if at_max else "normal")

    def _update_freq_btns(self):
        """Update frequency button states."""
        wf = app_state.get_active_wf()
        if wf:
            at_min = wf.freq <= FREQ_MIN
            at_max = wf.freq >= FREQ_MAX
            self.freq_dec_btn.configure(state="disabled" if at_min else "normal")
            self.freq_inc_btn.configure(state="disabled" if at_max else "normal")

    def _update_amp_btns(self):
        """Update amplitude button states."""
        wf = app_state.get_active_wf()
        if wf:
            at_min = wf.amp <= AMP_MIN
            at_max = wf.amp >= AMP_MAX
            self.amp_dec_btn.configure(state="disabled" if at_min else "normal")
            self.amp_inc_btn.configure(state="disabled" if at_max else "normal")

    def _update_offset_btns(self):
        """Update offset button states."""
        wf = app_state.get_active_wf()
        if wf:
            at_min = wf.offset <= OFFSET_MIN
            at_max = wf.offset >= OFFSET_MAX
            self.offset_dec_btn.configure(state="disabled" if at_min else "normal")
            self.offset_inc_btn.configure(state="disabled" if at_max else "normal")

    def _update_duty_btns(self):
        """Update duty cycle button states."""
        wf = app_state.get_active_wf()
        if wf:
            at_min = wf.duty_cycle <= DUTY_MIN
            at_max = wf.duty_cycle >= DUTY_MAX
            self.duty_dec_btn.configure(state="disabled" if at_min else "normal")
            self.duty_inc_btn.configure(state="disabled" if at_max else "normal")

    def _update_env_controls(self):
        """Enable/disable envelope checkboxes based on number of enabled waveforms."""
        can_show = app_state.can_show_envelopes()

        # Update max envelope checkbox
        self.show_max_env_cb.configure(state="normal" if can_show else "disabled")
        self.show_max_env_label.configure(
            text_color=ENABLED_TEXT_COLOR if can_show else DISABLED_TEXT_COLOR
        )

        # Update min envelope checkbox
        self.show_min_env_cb.configure(state="normal" if can_show else "disabled")
        self.show_min_env_label.configure(
            text_color=ENABLED_TEXT_COLOR if can_show else DISABLED_TEXT_COLOR
        )

        # Hide source checkbox requires at least one envelope to be shown
        can_hide_src = can_show and (app_state.show_max_env or app_state.show_min_env)
        self.hide_src_cb.configure(state="normal" if can_hide_src else "disabled")
        self.hide_src_label.configure(
            text_color=ENABLED_TEXT_COLOR if can_hide_src else DISABLED_TEXT_COLOR
        )

        # If hide source becomes disabled, turn it off
        if not can_hide_src:
            if app_state.hide_src_wfs:
                app_state.hide_src_wfs = False
                self._update_wf_management_controls()
            self.hide_src_var.set(False)

        if not can_show:
            app_state.show_max_env = False
            app_state.show_min_env = False
            self.show_max_env_var.set(False)
            self.show_min_env_var.set(False)

    def _update_add_button(self):
        """Enable/disable add waveform button based on max limit and hide_src state."""
        can_add = len(app_state.wfs) < app_state.MAX_WFS and not app_state.hide_src_wfs
        self.add_wf_btn.configure(state="normal" if can_add else "disabled")

    def _update_wf_management_controls(self):
        """Enable/disable waveform management controls based on hide_src state."""
        self._update_add_button()
        self._update_wf_list()

    def _update_status_bar(self):
        """Update status bar with current info."""
        num_wfs = len(app_state.wfs)
        self.status_bar.configure(text=f"Waveforms: {num_wfs}/{app_state.MAX_WFS}")
