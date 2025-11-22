# ui/ui_theme.py
import dearpygui.dearpygui as dpg
from modules.core.ui_style import UIStyle as STYLE

def _rgb(color_rgba):
    """Convert RGBA → RGB (DearPyGui ignores alpha)."""
    return color_rgba[:3]


def create_theme():
    """Create and bind the full application theme using the UIStyle palette."""

    # ------------------------------------------------------------
    # MAIN RACING THEME (GLOBAL)
    # ------------------------------------------------------------
    with dpg.theme(tag="racing_theme"):
        with dpg.theme_component(dpg.mvAll):

            # --- Global Backgrounds ---
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, _rgb(STYLE.BACKGROUND))
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, _rgb(STYLE.CALC_BG_ALT))

            # --- Text ---
            dpg.add_theme_color(dpg.mvThemeCol_Text, _rgb(STYLE.TEXT))
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, _rgb(STYLE.DISABLED_BG))

            # --- Inputs / Frames ---
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (45, 45, 50))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (65, 65, 70))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (85, 85, 90))

            # --- Buttons ---
            dpg.add_theme_color(dpg.mvThemeCol_Button, (55, 55, 55))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (85, 55, 25))
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonActive,
                _rgb(STYLE.PRIMARY_ORANGE_DEFAULT)
            )

            # --- Headers ---
            dpg.add_theme_color(dpg.mvThemeCol_Header, (50, 50, 55))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (90, 50, 20))
            dpg.add_theme_color(
                dpg.mvThemeCol_HeaderActive,
                _rgb(STYLE.PRIMARY_ORANGE_DEFAULT)
            )

            # --- Tables ---
            dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, (40, 40, 48))
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, (30, 30, 32))
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (33, 33, 36))

            # --- Borders ---
            dpg.add_theme_color(dpg.mvThemeCol_Border, _rgb(STYLE.BORDER_COLOR))

            # --- Spacing & Rounding ---
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8)

    # Bind immediately
    dpg.bind_theme("racing_theme")

    # ------------------------------------------------------------
    # HELPER: HEADER THEME BUILDER
    # ------------------------------------------------------------
    def make_header_theme(tag, bg, hover, active, text):
        with dpg.theme(tag=tag):
            with dpg.theme_component(dpg.mvCollapsingHeader):
                dpg.add_theme_color(dpg.mvThemeCol_Header, bg)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, hover)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, active)
                dpg.add_theme_color(dpg.mvThemeCol_Text, text)

    # ------------------------------------------------------------
    # HEADER THEMES (Race / Basic / Advanced)
    # ------------------------------------------------------------

    # Race Strategy Header (deep steel blue)
    make_header_theme(
        "race_header_theme",
        bg=STYLE.SECONDARY_BLUE_DEFAULT,
        hover=STYLE.SECONDARY_BLUE_LIGHT,
        active=STYLE.SECONDARY_BLUE_DARK,
        text=STYLE.TEXT_ON_SECONDARY_BLUE,
    )

    # Basic Strategy Header (racing green)
    make_header_theme(
        "basic_header_theme",
        bg=STYLE.SECONDARY_GREEN_DEFAULT,
        hover=STYLE.SECONDARY_GREEN_LIGHT,
        active=STYLE.SECONDARY_GREEN_DARK,
        text=STYLE.TEXT_ON_SECONDARY_GREEN,
    )

    # Advanced Strategy Header (brand orange)
    make_header_theme(
        "advanced_header_theme",
        bg=STYLE.PRIMARY_ORANGE_DEFAULT,
        hover=STYLE.PRIMARY_ORANGE_LIGHT,
        active=STYLE.PRIMARY_ORANGE_DARK,
        text=STYLE.TEXT_ON_PRIMARY_ORANGE,
    )

    # ------------------------------------------------------------
    # SEMANTIC INPUT / OUTPUT THEMES (Excel-style UI mapping)
    # ------------------------------------------------------------

    # USER INPUT
    with dpg.theme(tag="theme_user_input"):
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, _rgb(STYLE.INPUT_BG))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (255, 245, 150))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (255, 240, 120))
            dpg.add_theme_color(dpg.mvThemeCol_Border, _rgb(STYLE.NOTE_TEXT))
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.5)
        with dpg.theme_component(dpg.mvInputInt):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, _rgb(STYLE.INPUT_BG))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (255, 245, 150))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (255, 240, 120))
            dpg.add_theme_color(dpg.mvThemeCol_Border, _rgb(STYLE.NOTE_TEXT))
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.5)
        with dpg.theme_component(dpg.mvInputFloat):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, _rgb(STYLE.INPUT_BG))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (255, 245, 150))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (255, 240, 120))
            dpg.add_theme_color(dpg.mvThemeCol_Border, _rgb(STYLE.NOTE_TEXT))
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.5)

    # CALCULATED
    with dpg.theme(tag="theme_calculated"):
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, _rgb(STYLE.CALC_BG_ALT))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (255, 205, 140))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (255, 190, 120))
            dpg.add_theme_color(dpg.mvThemeCol_Border, _rgb(STYLE.BORDER_COLOR))
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.5)

    # OUTPUT
    with dpg.theme(tag="output_cell_theme"):
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, _rgb(STYLE.OUTPUT_BG))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (200, 200, 200))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (190, 190, 190))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (90, 90, 90))
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.5)

    # LABEL
    with dpg.theme(tag="input_label_theme"):
        with dpg.theme_component(dpg.mvText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, STYLE.TEXT_LIGHT)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, STYLE.SPACING_X, STYLE.SPACING_Y)

    # SECTION THEME
    with dpg.theme(tag="section_label_theme"):
        with dpg.theme_component(dpg.mvText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, STYLE.PRIMARY_ORANGE_DEFAULT)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, STYLE.SPACING_X, STYLE.SPACING_Y)
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, STYLE.SESSION_BACKGROUND_COLOR)
            dpg.add_theme_color(dpg.mvThemeCol_Border, STYLE.SESSION_BORDER_COLOR)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, STYLE.TABLE_BORDER)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, STYLE.TABLE_CORNER_RADIUS)

    # TABLE THEME
    with dpg.theme(tag="default_table_theme"):
        with dpg.theme_component(dpg.mvTable):
            dpg.add_theme_color(
                dpg.mvThemeCol_Border,
                STYLE.SESSION_BORDER_COLOR
            )
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, STYLE.TABLE_BORDER)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,STYLE.TABLE_CORNER_RADIUS)
