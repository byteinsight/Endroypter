# ui/pit_panel.py
import json

import dearpygui.dearpygui as dpg

from modules.helpers.pit_strategist import PitStrategist
from modules.ui.base_panel import BasePanel

# --------------------------------------------
# THE PIT CALC PANEL CLASS
# --------------------------------------------
class CrewChiefPanel(BasePanel):
    LABEL = "Crew Chief"

    RACE_SETUP_GRID = [
        [
            {"label": "Race Type", "tag": "race_mode", "type": "combo", "width": 200, "items": ["Time", "Laps", "Distance"]},
            {"label": "Race Length (mins)", "tag": "race_length_mins", "default": 45, "style": "user_input"},
            {"label": "Race Length (laps)", "tag": "race_length_laps", "default": 20},
            {"label": "Race Dist (km)", "tag": "race_distance", "default": 1000},
            {"label": "Lap Length (km)", "tag": "lap_length", "default": 5.807},
            {"label": "Total Laps", "tag": "total_laps", "default": 0, "readonly": True},
        ]
    ]

    RACE_DELTAS_GRID = [
        [
            {"section": "PIT DELTAS"}, {}, {},
            {"section": "LAP TIMES & FUEL USAGE"}, {}, {}
        ],
        [
            # Pit Inputs - Left Top
            {"label": "Tank Capacity (l)", "tag": "tank_capacity", "default": 103.00},
            {"label": "Service Time (s)", "tag": "service_time", "default": 42.00},
            {"label": "Fuel Rate (l/s)", "tag": "refuelling_rate", "readonly": True},

            # Lap Time Inputs - Right Top
            {"label": "Fast Lap (s)", "tag": "target_fast_lap", "default": 119.5},
            {"label": "Target Lap (s)", "tag": "target_lap", "default": 121.5},
            {"label": "Fuel Saving Lap (s)", "tag": "target_fuel_lap", "default": 123.0},
        ],
        [
            # Pit Deltas - Left Middle
            {"label": "Delta Time (s)", "tag": "total_pit_time", "default": 62.00},
            {"label": "Tyre Change (s)", "tag": "tyre_change_time", "default": 21.00},
            {"label": "PL Loss (s)", "tag": "pit_lane_loss", "readonly": True},

            # Fuel Usage - Right Middle
            {"label": "Fuel Min", "tag": "fuel_min", "default": 3.46},
            {"label": "Fuel Avg", "tag": "fuel_avg", "default": 3.57},
            {"label": "Fuel Max", "tag": "fuel_max", "default": 3.67},
        ],
        [
            # Free Stop - Left Bottom
            {"label": "Free Tyres (~litres)", "tag": "tyre_change_litres", "readonly": True},
            {"label": "Free Tyres (~laps)", "tag": "tyre_change_laps", "readonly": True},
            {"label": "Lap Margin", "tag": "lap_margin", "default": 1.00},
            # Lap/Stint - Right Bottom
            {"label": "Laps per Stint (Min)", "tag": "basic_lps_min", "readonly": True},
            {"label": "Laps per Stint (Avg)", "tag": "basic_lps_avg", "readonly": True},
            {"label": "Laps per Stint (Max)", "tag": "basic_lps_max", "readonly": True},

        ]
    ]

    BASIC_STRATEGY_RESULT_GRID = [
        [
            # Stops - Right Top
            {"label": "Stops (Min)", "tag": "basic_stops_min", "readonly": True},
            {"label": "Stops (Avg)", "tag": "basic_stops_avg", "readonly": True},
            {"label": "Stops (Max)", "tag": "basic_stops_max", "readonly": True},
            # Last Stint - Right Bottom
            {"label": "Last Stint (Min)", "tag": "basic_last_stint_min", "readonly": True},
            {"label": "Last Stint  (Avg)", "tag": "basic_last_stint_avg", "readonly": True},
            {"label": "Last Stint  (Max)", "tag": "basic_last_stint_max", "readonly": True},
        ],
    ]

    ADVANCED_STRATEGY_INPUT_GRID = [
        [
            {"label": "Target Fuel/Lap (l)", "tag": "target_fuel", "default": 0.00},
            {"label": "Target Pace (s)", "tag": "target_pace", "default": 0.00},
            {"label": "Include Lap Margin", "tag": "include_lap_margin", "default": True},
            {"label": "Leader Avg Lap (s)", "tag": "leader_pace", "default": 119.00},
            {"label": "Adjusted Laps", "tag": "adjusted_total_laps", "default": 0, "readonly": False},
            {"label": "Use Adjusted Laps", "tag": "use_adjusted_laps", "default": False},
        ]
    ]

    def __init__(self, ctx):
        super().__init__(ctx)
        self.ctx = ctx
        self.ps = PitStrategist(self.ctx)

    def build(self):
        """Main entry point for building this panel."""
        column_width = (dpg.get_viewport_client_width()+100) // 2

        # Race Config as full width top col.
        with dpg.collapsing_header(label="RACE CONFIGURATION", tag="race_configuration_header", default_open=True):
            self.build_input_grid(self.RACE_SETUP_GRID, columns=6)
            self.build_input_grid(self.RACE_DELTAS_GRID, columns=6)
            with dpg.collapsing_header(label="BASIC STRATEGY", tag="basic_strategy_header", default_open=True):
                self.build_input_grid(self.BASIC_STRATEGY_RESULT_GRID, columns=6)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Load Config", width=150, callback=self.on_load_config_action)
            dpg.add_button(label="Initialise", callback=self.initialise_action)
            dpg.add_button(label="Recalculate", callback=self.calculate_strategies_action)
            dpg.add_button(label="Save Config", width=150, callback=self.on_save_config_action)

        with dpg.collapsing_header(label="ADVANCED STRATEGY", tag="advanced_strategy_header", default_open=True):
            self.build_input_grid(self.ADVANCED_STRATEGY_INPUT_GRID, columns=6)

            with dpg.group(horizontal=True):
                # LEFT COLUMN
                with dpg.child_window(
                        tag="full_race_distance_equal_stint_strategy",
                        width=600,  # <<< set your width
                        autosize_y=True
                ):
                    pass  # initially empty

                # RIGHT COLUMN
                with dpg.child_window(
                        tag="full_race_distance_final_stint_strategy",
                        width=600,  # <<< set your width
                        autosize_y=True
                ):
                    pass  # initially empty

        dpg.bind_item_theme("race_configuration_header", "race_header_theme")
        dpg.bind_item_theme("basic_strategy_header", "basic_header_theme")
        dpg.bind_item_theme("advanced_strategy_header", "advanced_header_theme")

        # Create hidden popups once during UI build
        with dpg.window(label="Saved", modal=True, show=False, tag="save_success_popup"):
            dpg.add_text("Configuration saved successfully.")
            dpg.add_button(label="OK", callback=lambda: dpg.hide_item("save_success_popup"))

        with dpg.window(label="Error", modal=True, show=False, tag="save_error_popup"):
            dpg.add_text("Failed to save configuration.")
            dpg.add_button(label="OK", callback=lambda: dpg.hide_item("save_error_popup"))

        with dpg.window(label="Loaded", modal=True, show=False, tag="load_success_popup"):
            dpg.add_text("Configuration loaded successfully.")
            dpg.add_button(label="OK", callback=lambda: dpg.hide_item("load_success_popup"))

        with dpg.window(label="Error", modal=True, show=False, tag="load_error_popup"):
            dpg.add_text("Failed to load configuration.")
            dpg.add_button(label="OK", callback=lambda: dpg.hide_item("load_error_popup"))

    def build_stint_plan_grid(self, name: str, prefix: str, plan: dict):
        """
        Given a stint plan dict such as:
        {
            'stints': 6,
            'stops': 5,
            'laps_for_free_tyres': 15,
            'stint_laps': [...],
            'fuel_requirements': [...]
        }
        return a grid definition list suitable for build_input_grid().
        """
        self.ctx.logger.info(f"Building stint plan grid: {plan}")
        grid = []

        # --- Section: Summary ---
        grid.append([
            {"section": f"{name}"},
            {f"section": f"{sum(plan['stint_laps'])} Total Laps"}
        ])

        grid.append([
            {"label": "Total Stints", "tag": f"{prefix}_total_stints", "default": str(plan['stints']), "readonly": True},
            {"label": "Total Stops", "tag": f"{prefix}_total_stops", "default": str(plan['stops']), "readonly": True},
            {"label": "Free Tyre Laps", "tag": f"{prefix}_free_tyre_laps", "default": str(plan['laps_for_free_tyres']), "readonly": True},
        ])

        # --- Section: Per-Stint Breakdown ---
        grid.append([{"section": "Per-Stint Breakdown"}, {"section": "Laps"}, {"section": "Fuel (l)"}])

        stint_count = plan.get("stints", 0)

        for i in range(stint_count):
            lap_val = str(plan["stint_laps"][i])
            fuel_val = str(plan["fuel_requirements"][i])

            grid.append([
                {"section": f"Stint {i + 1}"},
                {"tag": f"{prefix}_stint_{i + 1}_laps", "default": lap_val, "readonly": True},
                {"tag": f"{prefix}_stint_{i + 1}_fuel", "default": fuel_val, "readonly": True},
            ])

        return grid

    def render_fuel_limited(self, data: dict, parent: str):
        """
        Renders the fuel-limited warning UI (hybrid layout):
        - Simple labels for general info
        - A real DPG table for illegal stints
        """
        style = self.ctx.ui  # convenience alias

        # -----------------------------------------
        # Section Header
        # -----------------------------------------
        dpg.add_text("Fuel-Limited Stint Plan", parent=parent, color=style.WARNING_LABEL)
        dpg.add_separator(parent=parent)

        # -----------------------------------------
        # Message (label)
        # -----------------------------------------
        if msg := data.get("message"):
            message = f"Message: {msg}"
            dpg.add_text(message, parent=parent)  # Wrap for readability
            dpg.add_spacer(height=4, parent=parent)

        # -----------------------------------------
        # Max legal laps
        # -----------------------------------------
        if "max_legal_laps" in data:
            dpg.add_text(f"Maximum Allowed per Stint: {data['max_legal_laps']} laps", parent=parent)
            dpg.add_spacer(height=4, parent=parent)

        # -----------------------------------------
        # Illegal stints table
        # -----------------------------------------
        illegal = data.get("illegal_stints", [])
        if illegal:
            dpg.add_text("Illegal Stints:", parent=parent)
            with dpg.table(
                    parent=parent,
                    borders_innerH=True,
                    borders_innerV=True,
                    borders_outerH=True,
                    borders_outerV=True,
                    header_row=True
            ):

                # Columns
                dpg.add_table_column(label="Stint")
                dpg.add_table_column(label="Planned Laps")
                dpg.add_table_column(label="Fuel Save Needed")

                # Rows
                for entry in illegal:
                    with dpg.table_row():
                        dpg.add_text(f"Stint {entry['stint']}")
                        dpg.add_text(str(entry["laps"]))
                        dpg.add_text(f"-{entry['fuel_saving_required']} laps")

            dpg.add_spacer(height=4, parent=parent)

        # -----------------------------------------
        # Suggestion
        # -----------------------------------------
        if suggestion := data.get("suggestion"):
            suggestion = f"Suggestion: {suggestion}"
            dpg.add_text(suggestion, parent=parent, wrap=600, color=style.SECTION_LABEL)
            dpg.add_spacer(height=4, parent=parent)

    def render_tyre_limited(self, data: dict, parent: str):
        """
        Renders the tyre-limited warning UI (hybrid layout):
        - Simple labels for general info
        - No table is required for this result type
        """
        style = self.ctx.ui  # convenience alias

        # -----------------------------------------
        # Section Header
        # -----------------------------------------
        dpg.add_text("Tyre-Limited Stint Plan", parent=parent, color=style.WARNING_LABEL)
        dpg.add_separator(parent=parent)

        # -----------------------------------------
        # Message
        # -----------------------------------------
        if msg := data.get("message"):
            dpg.add_text(f"Message: {msg}", parent=parent, wrap=600)
            dpg.add_spacer(height=4, parent=parent)

        # -----------------------------------------
        # Max legal laps (max allowed tyre stint length)
        # -----------------------------------------
        if "max_stint_laps" in data:
            dpg.add_text(
                f"Maximum Stint Length on Tyres: {data['max_stint_laps']} laps",
                parent=parent
            )
            dpg.add_spacer(height=4, parent=parent)

        # -----------------------------------------
        # Required laps
        # -----------------------------------------
        if "laps_required" in data:
            dpg.add_text(
                f"Laps Required for Free Stop Window: {data['laps_required']} laps",
                parent=parent
            )
            dpg.add_spacer(height=4, parent=parent)

        # -----------------------------------------
        # Penultimate + Final Stint Lengths
        # -----------------------------------------
        if "penultimate" in data or "final" in data:
            dpg.add_text("Critical Stint Lengths:", parent=parent)
            with dpg.group(parent=parent, indent=8):
                if "penultimate" in data:
                    dpg.add_text(f"Penultimate Stint: {data['penultimate']} laps")
                if "final" in data:
                    dpg.add_text(f"Final Stint: {data['final']} laps")
            dpg.add_spacer(height=4, parent=parent)

        # -----------------------------------------
        # Total laps + remainder
        # -----------------------------------------
        if "total_laps" in data:
            dpg.add_text(f"Total Laps: {data['total_laps']}", parent=parent)
        if "remainder" in data:
            dpg.add_text(f"Remainder After Splitting: {data['remainder']}", parent=parent)
            dpg.add_spacer(height=4, parent=parent)

        # -----------------------------------------
        # Suggestion
        # -----------------------------------------
        if suggestion := data.get("suggestion"):
            dpg.add_text(
                f"Suggestion: {suggestion}",
                parent=parent,
                wrap=600,
                color=style.SECTION_LABEL
            )
            dpg.add_spacer(height=4, parent=parent)

    # --------------------------------------------
    # TAB ACTIONS
    # --------------------------------------------
    def initialise_action(self):
        """
        This action initialises the UI elements based on user inputs.
        :return:
        """

        self.ctx.logger.info(f"Crew Chief Reporting for Duty!")

        self.get_race_distance_in_laps()

        self.do_pit_stop_analysis()

        self.calculate_basic_stint_lengths()

        self.calculate_full_race_distance_basic_strategy()

        dpg.set_value("target_fuel", dpg.get_value("fuel_avg"))
        dpg.set_value("target_pace", dpg.get_value("target_lap"))

    def calculate_strategies_action(self):
        # Calculate the adjusted total laps based on leaders pace
        total_laps = dpg.get_value("total_laps")
        leader_pace = dpg.get_value("leader_pace")
        target_pace = dpg.get_value("target_pace")
        self.ctx.logger.info(f"Total laps: {total_laps}; leader_pace: {leader_pace}; target_pace: {target_pace}")
        adj_total_laps = self.ps.calculate_adjusted_total_laps(total_laps, target_pace, leader_pace)
        dpg.set_value("adjusted_total_laps", adj_total_laps)

        # Clear existing dynamic content from the group.
        dpg.delete_item("full_race_distance_equal_stint_strategy", children_only=True)
        dpg.delete_item("full_race_distance_final_stint_strategy", children_only=True)

        self.calculate_full_race_distance_equal_stint_strategy()
        self.calculate_full_race_distance_final_stint_strategy()

    def on_save_config_action(self):
        """
        Opens the save dialog.
        When user chooses a file, on_save_config_selected is triggered.
        """
        with dpg.file_dialog(
                directory_selector=False,
                show=True,
                callback=self.on_save_config_selected,
                modal=True,
                height=400,
                width=600,
                default_path=self.ctx.replay_folder,
                default_filename="race_config.json"
        ):
            dpg.add_file_extension(".json", color=(255, 0, 255, 255), custom_text="[json]")

    def on_load_config_action(self):
        """
        Opens a file dialog to select a config file.
        """
        with dpg.file_dialog(
                directory_selector=False,
                show=True,
                callback=self.on_load_config_selected,
                modal=True,
                height=400,
                width=600,
                default_path=self.ctx.replay_folder,
        ):
            dpg.add_file_extension(".json", color=(255, 0, 255, 255), custom_text="[json]")

    # --------------------------------------------
    # STRATEGY CALLS
    # --------------------------------------------
    @staticmethod
    def get_total_laps():
        if dpg.get_value("use_adjusted_laps"):
            total_laps = dpg.get_value("adjusted_total_laps")
        else:
            total_laps = dpg.get_value("total_laps")
        if dpg.get_value("include_lap_margin"):
            total_laps += dpg.get_value("lap_margin")
        return total_laps

    def get_race_distance_in_laps(self):
        race_mode = dpg.get_value("race_mode").lower()

        if race_mode == "time":
            race_length_mins = dpg.get_value("race_length_mins")
            target_lap = dpg.get_value("target_lap")
            no_of_laps = self.ps.calculate_total_laps_on_time(race_length_mins, target_lap)

        # Set the no of laps we expect to complete based on race distance
        elif race_mode == "distance":
            race_distance = dpg.get_value("race_distance")
            lap_length = dpg.get_value("lap_length")
            no_of_laps = self.ps.calculate_total_laps_on_distance(race_distance, lap_length)

        else:
            no_of_laps = dpg.get_value("race_length_laps")

        dpg.set_value("total_laps", no_of_laps)
        self.ctx.logger.info(f"Total Race Laps = {no_of_laps} based on Race Mode = {race_mode}")

    def do_pit_stop_analysis(self):
        # Get the Pit Lane report based on manual observations
        tpt = dpg.get_value("total_pit_time")
        st = dpg.get_value("service_time")
        tc = dpg.get_value("tank_capacity")
        tct = dpg.get_value("tyre_change_time")
        af = dpg.get_value("fuel_avg")
        pll, rr, tcli, tcla = self.ps.get_pit_stop_report(tpt, st, tc, tct, af)
        dpg.set_value("pit_lane_loss", pll)
        dpg.set_value("refuelling_rate", f"{rr:.3f}")
        dpg.set_value("tyre_change_litres", f"{tcli:.3f}")
        dpg.set_value("tyre_change_laps", f"{tcla:.3f}")

    def calculate_basic_stint_lengths(self):
        # Calculate the no of laps per stint based on expected fuel usage
        total_fuel = dpg.get_value("tank_capacity")
        fuel_to_stila = {
            "fuel_min": "basic_lps_min",
            "fuel_avg": "basic_lps_avg",
            "fuel_max": "basic_lps_max",
        }

        for fuel_tag, stila_tag in fuel_to_stila.items():
            fuel_lap = dpg.get_value(fuel_tag)
            laps = self.ps.calculate_laps_in_tank(total_fuel, fuel_lap)
            dpg.set_value(stila_tag, f"{laps:.3f}")

    def calculate_full_race_distance_basic_strategy(self):
        """ Basic Strategy assumes that the team completes all 173 laps regardless of their finishing position.
            It maximises stint length based on fuel usage.

        :return:
        """
        total_laps = round(dpg.get_value("total_laps"),1) + round(dpg.get_value("lap_margin"),1)

        tank_capacity = round(dpg.get_value("tank_capacity"),3)

        fuel_usage_modes = [("min", "fuel_min"), ("avg", "fuel_avg"), ("max", "fuel_max"), ]

        self.ctx.logger.info(f"Basic Strategy based on {total_laps} laps with a {tank_capacity}l tank capacity.")

        # For each of the fuel/lap usage levels
        for label, fuel_tag in fuel_usage_modes:
            fuel_lap = round(dpg.get_value(fuel_tag),3)

            # Get the number of laps completed when fuel use is as specified
            stint_laps = self.ps.max_stint_laps(tank_capacity, fuel_lap)

            # Get the stint plan
            stint_plan = self.ps.basic_stint_plan(total_laps, fuel_lap, stint_laps)
            self.ctx.logger.info(f"Stint Plan: {stint_plan}")

            # Populate UI fields
            dpg.set_value(f"basic_stops_{label}", stint_plan["stops"])
            dpg.set_value(f"basic_last_stint_{label}", stint_plan["last_stint_laps"])

    def calculate_full_race_distance_equal_stint_strategy(self):
        """ Basic Equal Stint Strategy assumes that the team completes all 173 laps regardless of their finishing position.
            This strategy equalises the stints to avoid any 'splash and dash' at the end.
        :return:
        """

        total_laps = self.get_total_laps()
        tank_capacity = dpg.get_value("tank_capacity")
        tyre_change_litres = dpg.get_value("tyre_change_litres")
        target_fuel = dpg.get_value("target_fuel")

        stint_array = self.ps.calculate_equal_stint_plan(
            total_laps=int(total_laps),
            tank_capacity=float(tank_capacity),
            fuel_per_lap=float(target_fuel),
            tyre_change_litres=float(tyre_change_litres)
        )

        if stint_array.get("status") == "passed":
            # Build the stint grid plan and then build into the group.
            stint_grid_plan = self.build_stint_plan_grid("Uniform Stint Plan", "frdess", stint_array)
            with dpg.group(parent="full_race_distance_equal_stint_strategy"):
                self.build_input_grid(stint_grid_plan, columns=3)

        elif stint_array.get("status") == "fuel_limited":
            with dpg.group(parent="full_race_distance_equal_stint_strategy"):
                self.render_fuel_limited(stint_array, parent=dpg.last_item())
        else:
            self.ctx.logger.warning(f"Unknown stint calculation error: {stint_array.get('status')}")

    def calculate_full_race_distance_final_stint_strategy(self):
        """ Basic Final Stint strategy assumes that the team completes all 173 laps regardless of their finishing position.
            But equalises the final two stints to reduce the risk of a 'splash and dash' at the end.
            However, it maximises stint lengths during the bulk of the race."""

        total_laps = self.get_total_laps()
        tank_capacity = dpg.get_value("tank_capacity")
        tyre_change_litres = dpg.get_value("tyre_change_litres")
        target_fuel = dpg.get_value("target_fuel")

        # Build a stint array based on maximum stints except last two which are equalised
        stint_array = self.ps.calculate_final_stint_plan(
            total_laps=int(total_laps),
            tank_capacity=float(tank_capacity),
            fuel_per_lap=float(target_fuel),
            tyre_change_litres=float(tyre_change_litres)
        )

        if stint_array.get("status") == "passed":
            # Build the stint grid plan and then build into the group.
            stint_grid_plan = self.build_stint_plan_grid("Equal Final Plan", "frdfss", stint_array)
            with dpg.group(parent="full_race_distance_final_stint_strategy"):
                self.build_input_grid(stint_grid_plan, columns=3)

        elif stint_array.get("status") == "fuel_limited":
            with dpg.group(parent="full_race_distance_final_stint_strategy"):
                self.render_fuel_limited(stint_array, parent=dpg.last_item())

        elif stint_array.get("status") == "tyre_limited":
            with dpg.group(parent="full_race_distance_final_stint_strategy"):
                self.render_tyre_limited(stint_array, parent=dpg.last_item())
        else:
            self.ctx.logger.warning(f"Unknown stint calculation error: {stint_array.get('status')}")

    # --------------------------------------------
    # SAVE/LOAD ACTIONS
    # --------------------------------------------
    @staticmethod
    def extract_ui_values_from_grid(grid):
        """
        Given a grid definition (list of lists of cell dicts),
        extract all UI values by reading dpg.get_value(cell['tag']).

        Returns: dict { tag: value }
        """
        result = {}

        for row in grid:
            for cell in row:
                # Ignore blanks
                if not cell or not isinstance(cell, dict):
                    continue

                tag = cell.get("tag")
                if not tag:
                    continue

                try:
                    value = dpg.get_value(tag)
                except Exception:
                    # Widget might not exist or tag is not a value widget
                    continue

                result[tag] = value

        return result

    def extract_all_config(self, grids: dict):
        full_config = {}

        for section_name, grid in grids.items():
            full_config[section_name] = self.extract_ui_values_from_grid(grid)

        return full_config

    @staticmethod
    def apply_full_config(config: dict):
        for section_name, section_values in config.items():
            for tag, value in section_values.items():
                if dpg.does_item_exist(tag):
                    try:
                        dpg.set_value(tag, value)
                    except Exception:
                        pass  # Silently ignore invalid loads

    def on_save_config_selected(self, sender, app_data):
        """
        Called when user selects a save location.
        app_data contains file_path_name, file_name, current_path, etc.
        """
        file_path = app_data.get('file_path_name')
        if not file_path:
            return

        # Build your combined config
        grids = {
            "race_setup": self.RACE_SETUP_GRID,
            "race_deltas": self.RACE_DELTAS_GRID,
            "basic_strategy": self.BASIC_STRATEGY_RESULT_GRID,
            "advanced_strategy": self.ADVANCED_STRATEGY_INPUT_GRID,
        }

        config = self.extract_all_config(grids)

        # Write JSON
        try:
            with open(file_path, "w") as f:
                json.dump(config, f, indent=4)
            dpg.show_item("save_success_popup")
        except Exception as e:
            dpg.show_item("save_error_popup")

    def on_load_config_selected(self, sender, app_data):
        """
        Called when the user selects a config file from the file dialog.
        """
        file_path = app_data.get("file_path_name")
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                loaded_cfg = json.load(f)

            # Apply to UI
            self.apply_full_config(loaded_cfg)

            # Optionally remember the folder
            self.ctx.replay_folder = app_data.get("current_path", self.ctx.replay_folder)

            # Success popup
            dpg.show_item("load_success_popup")

        except Exception as e:
            print("Load error:", e)
            dpg.show_item("load_error_popup")


