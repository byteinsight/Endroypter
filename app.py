# app.py
import dearpygui.dearpygui as dpg

from helpers.app_context import AppContext
from ui.ui_theme import create_theme
from ui.ui_main import UIMain

def main():

    # Create the single global settings & logging context
    ctx = AppContext.instance()

    # Optional: log something early
    ctx.logger.info("Application starting...")

    # Create the DearPyGui context
    dpg.create_context()

    # Create the OS-level viewport/window
    dpg.create_viewport(title="iRaceInsight V2.0", width=1200, height=1000)

    # Apply custom theme before building UI
    create_theme()

    # Build all panels and UI layout
    ui = UIMain()
    ui.build()

    # Finalize DearPyGui internal setup
    dpg.setup_dearpygui()

    # Display the viewport on screen
    dpg.show_viewport()

    # Set the main app window to fill the viewport
    dpg.set_primary_window("main_window", True)

    # Start DPG event/render loop
    dpg.start_dearpygui()

    # Clean up when the window closes
    dpg.destroy_context()


if __name__ == "__main__":
    # Entry point for the application
    main()
