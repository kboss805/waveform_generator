"""
Real-Time Waveform Visualizer - Main Entry Point

This module initializes DearPyGui context and runs the main loop.
"""

import dearpygui.dearpygui as dpg
from ui_components import create_ui, MAIN_WINDOW


def main():
    """Initialize and run the application."""
    # Create DearPyGui context
    dpg.create_context()

    # Configure viewport
    dpg.create_viewport(
        title="Real-Time Waveform Visualizer",
        width=1200,
        height=800,
        min_width=1000,
        min_height=600
    )

    # Setup DearPyGui
    dpg.setup_dearpygui()

    # Create UI
    create_ui()

    # Set primary window
    dpg.set_primary_window(MAIN_WINDOW, True)

    # Show viewport
    dpg.show_viewport()

    # Main render loop
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    # Cleanup
    dpg.destroy_context()


if __name__ == "__main__":
    main()
