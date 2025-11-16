import dearpygui.dearpygui as dpg
from math import ceil

INPUT_GRID = [
    {"section": "Race Info"},
    [
        {"label": "Target Lap (s)", "tag": "target_lap", "default": 121.5},
        {"label": "Race Dist (km)", "tag": "race_distance", "default": 1000},
        {"label": "Lap Length (km)", "tag": "lap_length", "default": 5.807},
    ],

    {"section": "Fuel Info"},
    [
        {"label": "Tank (L)", "tag": "tank_capacity", "default": 103.9},
        {"label": "Fuel Avg", "tag": "fuel_avg", "default": 3.57},
        {"label": "Fuel Max", "tag": "fuel_max", "default": 3.67},
    ],

    {"section": "Derived"},
    [
        {"label": "Fuel Min", "tag": "fuel_min", "default": 3.46},
        {"label": "Total Laps", "tag": "total_laps", "default": 0, "readonly": True},
        {"label": "Tyre Change (s)", "tag": "tyre_change_time", "default": 21.0},
    ],
]

def build_input_grid(grid_data, columns=3):

    with dpg.table(
        header_row=False,
        borders_innerH=True,
        borders_innerV=True,
        borders_outerH=True,
        borders_outerV=True,
        policy=dpg.mvTable_SizingStretchProp,
    ):
        # Create fixed number of columns
        for _ in range(columns):
            dpg.add_table_column()

        for row in grid_data:

            # ----------------------------------------
            # SECTION LABEL ROW
            # ----------------------------------------
            if "section" in row:
                with dpg.table_row():
                    with dpg.group(horizontal=False):
                        dpg.add_text(row["section"])
                    # pad remaining columns
                    for _ in range(columns - 1):
                        dpg.add_text("")
                continue

            # ----------------------------------------
            # NORMAL INPUT ROW
            # ----------------------------------------
            with dpg.table_row():

                for item in row:
                    with dpg.group(horizontal=False):
                        dpg.add_text(item["label"])
                        dpg.add_input_float(
                            tag=item["tag"],
                            default_value=item["default"],
                            width=130,
                            readonly=item.get("readonly", False)
                        )

                # Pad blank columns if the row is short
                missing = columns - len(row)
                for _ in range(missing):
                    dpg.add_text("")



# ------------ helper cells for Inputs tab ------------
def cell(label, tag, default):
    with dpg.group(horizontal=False):
        dpg.add_text(label)
        dpg.add_input_float(tag=tag, default_value=default, width=130)


def calculate_total_laps():
    race_distance = dpg.get_value("race_distance")
    lap_length = dpg.get_value("lap_length")
    total = ceil(race_distance / lap_length) if lap_length > 0 else 0
    dpg.set_value("total_laps", total)


# ------------ Theme (optional) ------------
def create_theme():
    with dpg.theme(tag="racing_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (26, 26, 28))
            dpg.add_theme_color(dpg.mvThemeCol_Text, (235, 235, 235))

            ORANGE = (255, 130, 30)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (55, 55, 55))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (90, 55, 20))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ORANGE)

            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4)

    dpg.bind_theme("racing_theme")


# ------------ Main App ------------
def main():
    dpg.create_context()
    dpg.create_viewport(title="Race Tool", width=850, height=600)

    create_theme()

    with dpg.window(
            tag="main_window",
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            no_collapse=True,
            no_close=True
    ):

        # =====================================================
        #                       TAB BAR
            # =====================================================
        with dpg.tab_bar():

            # ---------------- TAB 1: STANDINGS ----------------
            with dpg.tab(label="Standings"):
                dpg.add_text("Live race standings, driver gaps, delta, etc.")
                dpg.add_separator()
                # Add your live data widgets here

            # ---------------- TAB 2: STINTS -------------------
            with dpg.tab(label="Stints"):
                dpg.add_text("Stint planning, fuel per stint, tyre windows.")
                dpg.add_separator()
                # Add stint tables, graphs, calculations here

            # ---------------- TAB 3: STRATEGY ------------------
            with dpg.tab(label="Strategy"):
                dpg.add_text("Fuel strategy, pit windows, undercut/overcut models.")
                dpg.add_separator()
                # Add plots, strategy outputs, time deltas

            # ---------------- TAB 4: INPUTS --------------------
            with dpg.tab(label="Inputs"):
                build_input_grid(INPUT_GRID, columns=3)

                dpg.add_button(label="Calculate Total Laps", callback=calculate_total_laps)

    dpg.setup_dearpygui()
    dpg.set_primary_window("main_window", True)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
