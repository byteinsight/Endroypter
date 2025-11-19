import time
import threading

import dearpygui.dearpygui as dpg

from modules.core.app_context import AppContext
from modules.irace_sdk.irsdk_service import IRSDKService
from modules.ui.ui_main import UIMain
from modules.ui.ui_theme import create_theme


class App:
    """
    The main application wrapper for iRaceInsight V2.0.
    Encapsulates lifecycle:
        - Context & logging
        - DearPyGUI init/shutdown
        - UI construction
        - Viewport configuration
    """
    # Variables related to our polling of the irsdk
    sdk_polling_running = False
    sdk_polling_thread = None
    sdk_polling_interval = None

    # -------------------------------------------------------
    # APP INIT - called once by static main method
    # -------------------------------------------------------
    def __init__(self, width: int = 1200, height: int = 840):
        # Create or load global application context
        self.ctx = AppContext.instance()

        self.width = width
        self.height = height

        # DPG context must be created before any UI operations
        dpg.create_context()

        # Create OS-level viewport
        dpg.create_viewport(
            title=self.ctx.system.APP_NAME,
            width=self.width,
            height=self.height,
            small_icon="iRaceInsight.ico",
            large_icon="iRaceInsight.ico",
        )

        # Apply theme (fonts, colours, styles)
        create_theme()

        # Create the IRSDK Service helper
        self.ir = IRSDKService(self.ctx)
        self.sdk_polling_interval = 1/int(self.ctx.get("polling_rate", 60))    # seconds

        # Placeholder for main UI instance
        self.ui = None

        self.ctx.logger.info(f"Application initialization completed. Polling Interval set at: {self.sdk_polling_interval:.3f} secs")

    # -------------------------------------------------------
    # Build UI - Constructs the main dpg.window and its primary containers
    # -------------------------------------------------------
    def build_ui(self):
        """Build all UI components and panels."""
        self.ui = UIMain(self.ctx)
        self.ui.build()
        self.ctx.logger.info("UI build completed.")

    # -------------------------------------------------------
    # RUN - Step 3 after Init and Build
    # -------------------------------------------------------
    def run(self):
        """Setup DearPyGUI and enter the main render loop."""
        self.ctx.logger.info("Application Entering Run Loop")

        # Finalize DPG setup
        dpg.setup_dearpygui()

        # Start SDK polling thread AFTER setup, BEFORE event loop
        self.sdk_polling_running = True
        self.sdk_polling_thread = threading.Thread(target=self.sdk_polling_loop, daemon=True)
        self.sdk_polling_thread.start()

        # Show application window
        dpg.show_viewport()

        # Ensure our defined main window gets focus & sizing
        dpg.set_primary_window("main_window", True)

        # Get primary monitor resolution
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        self.ctx.logger.debug(f"Viewport width: {viewport_width}, height: {viewport_height}")

        # Enter the DPG event loop
        dpg.start_dearpygui()

        # After loop exits (window closed)
        self.shutdown()

    # -------------------------------------------------------
    # SDK POLLING LOOP - UI updates from the SDK are triggered here
    # -------------------------------------------------------
    def sdk_polling_loop(self):
        """Background thread for polling the iRacing SDK."""

        self.ctx.logger.info(f"iRSDK Polling thread started at {self.sdk_polling_interval:.3f} secs")

        while self.sdk_polling_running:
            try:
                # Get data from the background task
                # Potential updates include: timing, weather, session, track
                available_updates = self.ir.get_update()

                # If timing data changed, push to the TimingPanel (visible-only)
                if available_updates.get("timing"):
                    self.timer_panel_updates()

                if available_updates.get("session"):
                    dashboard_panel = self.ui.panels.get("dashboard")
                    combined_data = {"session_data": getattr(self.ir, "session_data", None)}
                    dashboard_panel.update(combined_data)

            except Exception as error:
                self.ctx.logger.error(f"Error in iRSDK Polling Loop: {error}")

            # 3. Wait for the next poll interval
            time.sleep(self.sdk_polling_interval)

        self.ctx.logger.info(f"iRSDK Polling thread ended...")

    # -------------------------------------------------------
    # Timing Panel Updates
    # -------------------------------------------------------
    def timer_panel_updates(self):
        timing_panel = self.ui.panels.get("timing")

        if timing_panel and timing_panel.requires_update:

            combined_data = {
                "timing_data": getattr(self.ir, "timing_data", None),
                "driver_data": getattr(self.ir, "driver_data", None),
                "PlayerCarIdx": self.ir.get_player_car_idx(),

            }
            timing_panel.update(combined_data)


    # -------------------------------------------------------
    # Clean Shutdown
    # -------------------------------------------------------
    def shutdown(self):
        """Clean shutdown of DearPyGUI and logging."""
        self.ctx.logger.info("Shutting down application...")
        dpg.destroy_context()
        self.ctx.logger.debug("DPG context destroyed.")
        self.ctx.logger.info("Application terminated cleanly.")

    # -------------------------------------------------------
    # Convenience entry point.
    # -------------------------------------------------------
    @staticmethod
    def main():
        """Convenience entry point."""
        app = App()
        app.build_ui()
        app.run()


# -------------------------------------------
# Standard entry point
# -------------------------------------------
if __name__ == "__main__":
    App.main()
