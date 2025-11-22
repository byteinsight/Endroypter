import dearpygui.dearpygui as dpg
from pathlib import Path

from modules.ui.base_panel import BasePanel



class SettingsPanel(BasePanel):
    LABEL = "Settings"

    INPUT_GRID = [
        [{"section": "Application Settings"}],
        [
            {"label": "Debug", "tag": "debug", "default": True},
            {"label": "Autosave (s)", "tag": "autosave_interval", "default": 30},
            {"label": "MQTT Enable", "tag": "mqtt_enable", "default": True},
        ],

        [{"section": "Access Credentials"}],
        [
            {"label": "iRacing CustID", "tag": "iracing_custid", "default": 123456},
            {"label": "iRaceInsight Access Key", "tag": "irace_insight_key", "default": 123456789},
        ],

        [{"section": "Telemetry Settings"}],
        [
            {"label": "Polling Rate (Hz)", "tag": "polling_rate", "default": 60},
            {"label": "Cache Size", "tag": "cache_size", "default": 5000},
        ],

        [{"section": "Data Paths"}],
        [
            {
                "label": "Log Folder",
                "tag": "log_folder",
                "default": "",       # will be replaced by ctx.log_folder
                "type": "string"
            },
            {
                "label": "Replay Folder",
                "tag": "replay_folder",
                "default": "",       # will be replaced by ctx.replay_folder
                "type": "string"
            },
        ],
    ]

    def __init__(self, ctx):
        super().__init__(ctx)
        self.ctx = ctx

    # -------------------------------------------------------
    # BUILD UI
    # -------------------------------------------------------
    def build(self):
        """Build the settings panel."""
        self.build_input_grid(self.INPUT_GRID, columns=2)
        self.populate_from_settings()

        dpg.add_separator()
        dpg.add_button(label="Save Settings", callback=self.save_settings_action)
        dpg.add_button(label="Reload Settings", callback=self.reload_settings_action)

    # -------------------------------------------------------
    # UI HELPERS
    # -------------------------------------------------------
    def collect_values(self):
        """Collect all widget values into a dict."""
        settings = {}
        for row in self.INPUT_GRID:
            if isinstance(row[0], dict) and "section" in row[0]:
                continue
            for item in row:
                tag = item["tag"]
                settings[tag] = dpg.get_value(tag)
        return settings

    def populate_from_settings(self):
        """Populate UI from context settings + defaults."""
        for row in self.INPUT_GRID:
            if isinstance(row[0], dict) and "section" in row[0]:
                continue

            for item in row:
                tag = item["tag"]

                # Context defaults for paths
                if tag == "log_folder":
                    default_val = str(self.ctx.log_folder)
                elif tag == "replay_folder":
                    default_val = str(self.ctx.replay_folder)
                else:
                    default_val = item.get("default")

                # Pull from context or apply default
                value = self.ctx.get(tag, default_val)

                # Persist default if missing
                self.ctx.set(tag, value)

                dpg.set_value(tag, value)

    # -------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------
    def save_settings_action(self):
        updated_values = self.collect_values()

        # Push all values into the AppContext settings
        for key, value in updated_values.items():
            self.ctx.set(key, value)

        # Ensure log/replay folders stay inside HOME_PATH
        log_path = Path(updated_values["log_folder"])
        replay_path = Path(updated_values["replay_folder"])

        if not log_path.is_relative_to(self.ctx.home):
            log_path = self.ctx.home / "logs"
            self.ctx.set("log_folder", str(log_path))

        if not replay_path.is_relative_to(self.ctx.home):
            replay_path = self.ctx.home / "replays"
            self.ctx.set("replay_folder", str(replay_path))

        # Update context paths & check folders exist
        self.ctx.log_folder = Path(self.ctx.get("log_folder"))
        self.ctx.replay_folder = Path(self.ctx.get("replay_folder"))
        self.ctx.log_folder.mkdir(parents=True, exist_ok=True)
        self.ctx.replay_folder.mkdir(parents=True, exist_ok=True)

        # Save to disk
        self.ctx.save_settings()
        self.ctx.logger.info("Settings saved from SettingsPanel.")

    def reload_settings_action(self):
        """
        Reload settings from disk and refresh the UI.

        This action discards the current in-memory user settings stored in
        ``AppContext.settings`` and replaces them with the contents of
        ``settings.json``. Only user-configurable settings are affected;
        internal runtime state, cached values, system configuration, and
        application paths remain intact.

        """
        # Reload settings.json into context
        self.ctx.settings = self.ctx.load_settings()
        self.populate_from_settings()
        self.ctx.logger.info("Settings reloaded from disk.")
