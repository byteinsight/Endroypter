from dataclasses import dataclass
import json
import logging
from pathlib import Path
import sys

# ============================================================
# APPLICATION NAME
# ============================================================
APP_NAME = "iRaceInsight2"

# ============================================================
# Detect PyInstaller bundle (frozen mode)
# ============================================================
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    INSTALL_ROOT = Path(sys.executable).parent
    RESOURCE_ROOT = Path(sys._MEIPASS) / "resources"
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    RESOURCE_ROOT = PROJECT_ROOT / "resources"

# ============================================================
# USER-WRITABLE ROOT — always safe to write to
# ============================================================
HOME_PATH = Path.home() / APP_NAME
HOME_PATH.mkdir(parents=True, exist_ok=True)

# Subfolders
LOG_FOLDER = HOME_PATH / "logs"
REPLAY_FOLDER = HOME_PATH / "replays"
CONFIG_FOLDER = HOME_PATH / "config"

for f in (LOG_FOLDER, REPLAY_FOLDER, CONFIG_FOLDER):
    f.mkdir(parents=True, exist_ok=True)

# ============================================================
# UIStyle Configuration (fixed, NOT user editable)
# ============================================================
class UIStyle:
    HEADER = (220, 220, 255, 255)
    WARNING = (255, 120, 120, 255)
    WARNING_LABEL = (255, 200, 180, 255)
    INFO = (255, 255, 180, 255)
    SUGGESTION = (255, 170, 100, 255)
    SECTION_LABEL = (230, 230, 230, 255)

# ============================================================
# System Configuration (fixed, NOT user editable)
# ============================================================
@dataclass(frozen=True)
class SystemConfig:
    """Protected values — fixed; never overridden by settings.json"""

    APP_NAME: str = APP_NAME
    VERSION: str = "1.0.0"
    DEFAULT_REFRESH_INTERVAL: int = 16

    # OPENAI CONFIG
    OPENAI_ENABLE: bool = True
    OPENAI_GPT_MODEL: str = "gpt-4o"
    OPENAI_RATE_LIMIT_PER_MINUTE: int = 500
    OPENAI_MAX_THREAD_COUNT: int = 6
    OPENAI_MAX_WORKERS: int = 2
    OPENAI_MAX_TOKENS: int = 1500
    OPENAI_DEFAULT_TEMPERATURE: float = 0.3
    OPENAI_DEFAULT_TOPP: float = 0.9

    # MQTT CONFIG
    DEFAULT_MQTT_ENABLE: bool = True
    MQTT_BROKER_ADDRESS: str = "194.164.95.88"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = "jim_clark"
    MQTT_PASSWORD: str = "karmic6"
    MQTT_REMOTE_CLIENT: str = "remote_666"
    MQTT_PRIME_TOPIC: str = "core_topic"
    MQTT_ALLOW_REPLAY_POSTING: bool = True


# ============================================================
# App Context (Settings + Paths + Logging + Runtime State)
# ============================================================
class AppContext:
    _instance = None

    @staticmethod
    def instance():
        if AppContext._instance is None:
            AppContext()
        return AppContext._instance

    def __init__(self):
        if AppContext._instance is not None:
            return  # Singleton

        self.system = SystemConfig()

        # Paths
        self.home = HOME_PATH
        self.log_folder = LOG_FOLDER
        self.replay_folder = REPLAY_FOLDER
        self.config_folder = CONFIG_FOLDER
        self.settings_file = self.config_folder / "settings.json"

        # Settings and runtime
        self.settings = self.load_settings()
        self.internal_state = {}  # runtime-only
        self.cache = {}

        # Logging
        self.logger = self._init_logging()

        self.ui = UIStyle()

        AppContext._instance = self

    # ============================================================
    # SETTINGS
    # ============================================================
    def load_settings(self):
        if not self.settings_file.exists():
            return {}

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠ Error loading settings.json: {e}")
            return {}

    def save_settings(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            self.logger.info("Settings saved successfully.")
        except Exception as e:
            self.logger.error(f"Error saving settings.json: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value

    # ============================================================
    # LOGGING
    # ============================================================
    def _init_logging(self):
        # Get the app-level logger
        logger = logging.getLogger(APP_NAME)

        # Avoid adding handlers more than once
        if logger.handlers:
            return logger

        # Logger captures all levels (handlers decide what to output)
        logger.setLevel(logging.DEBUG)

        # --- File Handler (always DEBUG+) ---
        log_file = self.log_folder / "app.log"
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)  # log everything to file

        # --- Console Handler (respects settings.debug) ---
        ch = logging.StreamHandler()
        # DEBUG to terminal only if enabled in settings, otherwise INFO+
        ch.setLevel(logging.DEBUG if self.settings.get("debug") else logging.INFO)

        # Log message format
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

        # Apply formatting to both handlers
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)

        # Attach handlers to logger
        logger.addHandler(fh)
        logger.addHandler(ch)

        # Confirm initialization
        logger.info(
            "Logger initialized (debug to terminal: %s).",
            "ON" if self.settings.get("debug") else "OFF"
        )

        return logger

