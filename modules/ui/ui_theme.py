# ui/ui_theme.py
import dearpygui.dearpygui as dpg

def create_theme():
    """Orange + Steel racing theme."""

    ORANGE = (255, 130, 30)
    DARK_BG = (26, 26, 28)
    MID_BG = (35, 35, 40)

    with dpg.font_registry():
        font_default = dpg.add_font("resources/fonts/segoeui.ttf", 16)

    with dpg.theme(tag="racing_theme"):
        with dpg.theme_component(dpg.mvAll):
            # --- Fonts ---
            dpg.bind_font(font_default)

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

    # ------------------------------------------------------------------
    # HELPER: Create a header theme
    # ------------------------------------------------------------------
    def make_header_theme(tag, bg, hover, active, text):
        with dpg.theme(tag=tag):
            with dpg.theme_component(dpg.mvCollapsingHeader):
                dpg.add_theme_color(dpg.mvThemeCol_Header, bg)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, hover)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, active)
                dpg.add_theme_color(dpg.mvThemeCol_Text, text)

    # ------------------------------------------------------------------
    # HEADER THEMES (Race / Basic / Advanced)
    # ------------------------------------------------------------------

    # Race Strategy Header — blue tone
    make_header_theme(
        "race_header_theme",
        bg=(40, 80, 160),
        hover=(60, 110, 200),
        active=(30, 60, 130),
        text=(255, 255, 255),
    )

    # Basic Strategy Header — green tone
    make_header_theme(
        "basic_header_theme",
        bg=(40, 140, 60),
        hover=(65, 170, 85),
        active=(35, 110, 45),
        text=(255, 255, 255),
    )

    # Advanced Strategy Header — orange/red tone
    make_header_theme(
        "advanced_header_theme",
        bg=(180, 90, 40),
        hover=(210, 120, 55),
        active=(160, 75, 30),
        text=(255, 255, 255),
    )

    # USER INPUT: pale yellow background + stronger yellow border
    with dpg.theme(tag="theme_user_input"):
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (255, 250, 180))  # pale yellow
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (255, 245, 150))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (255, 240, 120))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (230, 200, 40))  # strong yellow
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.5)

    # CALCULATED: light orange + stronger orange border
    with dpg.theme(tag="theme_calculated"):
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (255, 220, 170))  # light orange
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (255, 205, 140))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (255, 190, 120))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (210, 120, 40))  # strong orange
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.5)

    # OUTPUT: light grey + dark grey border
    with dpg.theme(tag="theme_output"):
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (210, 210, 210))  # light grey
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (200, 200, 200))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (190, 190, 190))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (90, 90, 90))  # dark grey
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.5)
