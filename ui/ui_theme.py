# ui/ui_theme.py
import dearpygui.dearpygui as dpg

def create_theme():
    """Orange + Steel racing theme."""

    ORANGE = (255, 130, 30)
    DARK_BG = (26, 26, 28)
    MID_BG = (35, 35, 40)

    with dpg.theme(tag="racing_theme"):
        with dpg.theme_component(dpg.mvAll):

            # --- Backgrounds ---
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, DARK_BG)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, MID_BG)

            # --- Text ---
            dpg.add_theme_color(dpg.mvThemeCol_Text, (235, 235, 235))
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (120, 120, 120))

            # --- Inputs / Frames ---
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (45, 45, 50))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (65, 65, 70))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (85, 85, 90))

            # --- Buttons ---
            dpg.add_theme_color(dpg.mvThemeCol_Button, (55, 55, 55))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (85, 55, 25))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ORANGE)

            # --- Headers (table headers, tree headers) ---
            dpg.add_theme_color(dpg.mvThemeCol_Header, (50, 50, 55))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (90, 50, 20))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, ORANGE)

            # --- Tables ---
            dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, (40, 40, 48))
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, (30, 30, 32))
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (33, 33, 36))

            # --- Borders ---
            dpg.add_theme_color(dpg.mvThemeCol_Border, (70, 70, 75))

            # --- Rounding & Spacing ---
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8)

    dpg.bind_theme("racing_theme")
