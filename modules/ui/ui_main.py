# ui/ui_main.py
import dearpygui.dearpygui as dpg

from modules.ui.help_panel import HelpPanel
from modules.ui.settings_panel import SettingsPanel
from modules.ui.timing_panel import TimingPanel
from modules.ui.crewchief_panel import CrewChiefPanel
from modules.ui.dashboard_panel import DashPanel

class UIMain:
    """
    Main DearPyGUI UI controller.

    Responsibilities:
    - Owns and builds all top-level panels (Timing, Crew Chief, Settings, Help).
    - Creates the tab bar that hosts each panel.
    - Tracks which tab is currently visible.
    - Notifies panels when they become visible (on_show) or hidden (on_hide),
      enabling visibility-aware UI updates where only visible tabs redraw their data.

    This structure ensures:
      • No GPU/CPU waste from updating hidden tabs.
      • Clean lifecycle events for each panel.
      • A single central place for tab management and update control.
    """

    def __init__(self, ctx):
        self.ctx = ctx

        # Store panels keyed by a stable tab tag.
        # Each panel receives the shared context.
        self.panels = {
            "dashboard": DashPanel(ctx),
            "timing": TimingPanel(ctx),
            "crew_chief": CrewChiefPanel(ctx),
            "settings": SettingsPanel(ctx),
            "help": HelpPanel(ctx),
        }

        # Track which tab is active so update loops know where to route UI updates.
        self.active_tab = None

    def build(self):
        """Build the main application window and the tab structure."""

        with dpg.window(
            tag="main_window",
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            no_collapse=True,
            no_close=True
        ):
            # Create the tab bar for panel switching.
            # The callback fires whenever a new tab becomes active.
            with dpg.tab_bar(callback=self.on_tab_changed, tag="main_tab_bar"):

                # Build each panel inside its own tab item.
                for tag, panel in self.panels.items():
                    with dpg.tab(label=panel.LABEL, tag=tag):
                        panel.build()

            # The first panel is activated by default after build.
            first_tag = next(iter(self.panels.keys()))
            self.active_tab = first_tag
            self.panels[first_tag].on_show()

    def on_tab_changed(self, sender, app_data):
        """
        Fired automatically by DearPyGUI when the user selects a different tab.

        Parameters:
            sender: The tab bar.
            app_data: The tag of the newly selected tab item.
        """
        # Resolve the actual tag (your string like "timing", "dashboard")
        tab_alias = dpg.get_item_alias(app_data)
        self.ctx.logger.debug(f"Tab Changed: {tab_alias}")

        # Update active tab tracking.
        self.active_tab = tab_alias

        # Notify each panel whether it is now visible or hidden.
        for tag, panel in self.panels.items():
            if tag == tab_alias:
                # self.ctx.logger.debug(f"Tag: {tag}; Panel: {panel.LABEL} - SHOW")
                panel.on_show()   # Panel becomes eligible for live updates
            else:
                # self.ctx.logger.debug(f"Tag: {tag}; Panel: {panel.LABEL} - HIDE")
                panel.on_hide()   # Panel stops receiving live updates
