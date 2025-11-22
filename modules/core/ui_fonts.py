import os
import logging

import dearpygui.dearpygui as dpg

class FontManager:

    """
    Loads and stores all application fonts.
    Provides simple, direct attribute-style access (e.g. fonts.ui_bold).
    """

    def __init__(self, root_path: str, logger: logging.Logger):
        self.fonts_path = f"{root_path}/resources/fonts"
        self.logger = logger
        self._fonts = {}

    # Helper to load a single font safely
    def safe_add_font(self, name: str, filename: str, size: int):
        full_path = f"{self.fonts_path}/{filename}"

        # Check file exists before DearPyGui touches it
        if not os.path.isfile(full_path):
            self.logger.error(f"Font '{name}' missing: {full_path}")
            return None

        try:
            font = dpg.add_font(full_path, size)
            self.logger.info(f"Font loaded: {name} ({filename}, {size}px)")
            return font

        except Exception as e:
            # DearPyGui may throw Python-side exceptions only for some cases.
            self.logger.error(f"Failed to load font '{name}' from {full_path}: {e}")
            return None

    def load(self):

        with dpg.font_registry():

            # Default UI font (must succeed or DPG uses its built-in one)
            default_font = self.safe_add_font("default_font", "segoeui.ttf", 16)

            # Default fallback bind
            if default_font:
                dpg.bind_font(default_font)
                self._fonts["default_font"] = default_font
            else:
                self.logger.warning("Using built-in DPG font as fallback.")
                self._fonts["default_font"] = None

            # Secondary fonts (safe but optional)
            self._fonts["ui_bold"] = self.safe_add_font("ui_bold", "segoeuib.ttf", 16)
            self._fonts["mono"] = self.safe_add_font("mono", "consola.ttf", 16)
            self._fonts["mono_bold"] = self.safe_add_font("mono_bold", "consolab.ttf", 18)
            self._fonts["title"] = self.safe_add_font("title", "Audiowide-Regular.ttf", 22)
            self._fonts["input_label"] = self.safe_add_font("title", "Audiowide-Regular.ttf", 16)

        self.logger.info("FontManager: Font load complete.")

    def __getattr__(self, name: str):
        """
        Allow attribute access like font_manager.title or font_manager.ui_bold.
        Raises AttributeError if the font does not exist.
        """
        if name in self._fonts:
            return self._fonts[name]

        raise AttributeError(f"Font '{name}' not found in FontManager.")


