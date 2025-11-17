# ui/pit_panel.py

import dearpygui.dearpygui as dpg

from helpers.pit_strategist import PitStrategist
from ui.base_panel import BasePanel

# --------------------------------------------
# THE PIT CALC PANEL CLASS
# --------------------------------------------
class CrewChiefPanel(BasePanel):
    label = "Crew Chief"

    INPUT_GRID = [
        [{"section": "RACE INFO (Distance Based)"}],
        [
            {"label": "Race Dist (km)", "tag": "race_distance", "default": 1000},
            {"label": "Lap Length (km)", "tag": "lap_length", "default": 5.807},
            {"label": "Total Laps", "tag": "total_laps", "default": 0, "readonly": True},
        ],

        [{"section": "PIT DELTAS"}],
        [
            {"label": "Service Time (s)", "tag": "service_time", "default": 42.00},
            {"label": "Tyre Change (s)", "tag": "tyre_change_time", "default": 21.00},
            {"label": "Dela Time (s)", "tag": "total_pit_time", "default": 62.00},
        ],
        [
            {"label": "PL Loss (s)", "tag": "pit_lane_loss", "default": 0.00},
            {"label": "Fuel Rate (l/s)", "tag": "refuelling_rate", "default": 0.00},
            {"label": "Free Tyres  (~laps)", "tag": "tyre_change_laps", "default": 0.00},
        ],

        [{"section": "FUEL INFO"}],
        [
            {"label": "Tank (L)", "tag": "tank_capacity", "default": 103.9},
            {"label": "Lap Margin", "tag": "lap_margin", "default": 1.00},
            {"label": "Free Tyres (litres)", "tag": "tyre_change_litres", "default": 0.00},
        ],
        [
            {"label": "Fuel Min", "tag": "fuel_min", "default": 3.46},
            {"label": "Fuel Avg", "tag": "fuel_avg", "default": 3.57},
            {"label": "Fuel Max", "tag": "fuel_max", "default": 3.67},
        ],
        [
            {"label": "StiLa Min", "tag": "stint_laps_min", "default": 0.00},
            {"label": "StiLa Avg", "tag": "stint_laps_avg", "default": 0.00},
            {"label": "StiLa Max", "tag": "stint_laps_max", "default": 0.00},
        ],

        [{"section": "LAP RANGE"}],
        [
            {"label": "Fast Lap (s)", "tag": "target_fast_lap", "default": 119.5},
            {"label": "Target Lap (s)", "tag": "target_lap", "default": 121.5},
            {"label": "Fuel Saving Lap (s)", "tag": "target_fuel_lap", "default": 123.0},
        ],
    ]

    BASIC_STRATEGY_RESULT_GRID = [
        [{"section": "Basic Strategy"}],
        [
            {"label": "Fuel/Lap (Min)", "tag": "res_fpl_min", "readonly": True},
            {"label": "Fuel/Lap (Avg)", "tag": "res_fpl_avg", "readonly": True},
            {"label": "Fuel/Lap (Max)", "tag": "res_fpl_max", "readonly": True},
        ],
        [
            {"label": "Laps per Stint (Min)", "tag": "res_lps_min", "readonly": True},
            {"label": "Laps per Stint (Avg)", "tag": "res_lps_avg", "readonly": True},
            {"label": "Laps per Stint (Max)", "tag": "res_lps_max", "readonly": True},

        ],
        [
            {"label": "Stops (Min)", "tag": "res_stops_min", "readonly": True},
            {"label": "Stops (Avg)", "tag": "res_stops_avg", "readonly": True},
            {"label": "Stops (Max)", "tag": "res_stops_max", "readonly": True},
        ],
        [
            {"label": "Last Stint (Min)", "tag": "last_stint_min", "readonly": True},
            {"label": "Last Stint  (Avg)", "tag": "last_stint_avg", "readonly": True},
            {"label": "Last Stint  (Max)", "tag": "last_stint_max", "readonly": True},
        ],
    ]

    BASIC_EQUAL_STRATEGY_RESULT_GRID = [
        [{"section": "Equal Stint Strategy"}],
        [
            {"label": "Target Fuel/Lap (l)", "tag": "target_fuel", "default": 0.00},
            {"label": "Lap Length (km)", "tag": "lap_length2", "default": 5.807},
            {"label": "Total Laps", "tag": "total_laps2", "default": 0, "readonly": True},
        ]
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ps = PitStrategist(self.ctx)

    def build(self):
        """Main entry point for building this panel."""

        # Create the two-column main layout
        with dpg.table(header_row=False, resizable=True):
            dpg.add_table_column(init_width_or_weight=600, width_fixed=True)  # LEFT COLUMN (inputs)
            dpg.add_table_column()  # RIGHT COLUMN (strategies)

            with dpg.table_row():
                # ----------------------------------
                # LEFT COLUMN — your existing grid
                # ----------------------------------
                with dpg.group():
                    self.build_input_grid(self.INPUT_GRID, columns=3)
                    self.build_input_grid(self.BASIC_STRATEGY_RESULT_GRID, columns=3)

                    # Allow subclasses to continue
                    self.build_extra()

                # ----------------------------------
                # RIGHT COLUMN — empty for now
                # ----------------------------------
                with dpg.group(tag="strategy_column"):
                    self.build_input_grid(self.BASIC_EQUAL_STRATEGY_RESULT_GRID, columns=3)
                    # Placeholder container for any dynamic content added at runtime
                    dpg.add_group(tag="full_race_distance_equal_stint_strategy")
                    self.build_extra_right()

    def build_extra(self):
        """Add custom UI below the grid."""
        dpg.add_button(label="Initialise", callback=self.initialise_action)

    def build_extra_right(self):
        """Add custom UI below the grid."""
        dpg.add_button(label="Recalculate", callback=self.calculate_full_distance_strategies)

    def build_stint_plan_grid(self, plan: dict):
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
        grid.append([{"section": "Stint Plan Summary"}])

        grid.append([
            {"label": "Total Stints", "tag": "res_total_stints", "default": str(plan['stints']), "readonly": True},
            {"label": "Total Stops", "tag": "res_total_stops", "default": str(plan['stops']), "readonly": True},
            {"label": "Free Tyre Laps", "tag": "res_free_tyre_laps", "default": str(plan['laps_for_free_tyres']), "readonly": True},
        ])

        # --- Section: Per-Stint Breakdown ---
        grid.append([{"section": "Per-Stint Breakdown"}, {"section": "Laps"}, {"section": "Fuel (l)"}])

        stint_count = plan.get("stints", 0)

        for i in range(stint_count):
            lap_val = str(plan["stint_laps"][i])
            fuel_val = str(plan["fuel_requirements"][i])

            grid.append([
                {"section": f"Stint {i + 1}"},
                {"tag": f"res_stint_{i + 1}_laps", "default": lap_val, "readonly": True},
                {"tag": f"res_stint_{i + 1}_fuel", "default": fuel_val, "readonly": True},
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

    # --------------------------------------------
    # TAB ACTIONS
    # --------------------------------------------
    def initialise_action(self):
        """
        This action initialises the UI elements based on user inputs.
        :return:
        """

        self.ctx.logger.info(f"Crew Chief Reporting for Duty!")

        self.get_race_distance_action()

        self.calculate_stila_action()

        self.get_pit_stop_report_action()

        self.calculate_full_race_distance_basic_strategy()

        # Set our target_fuel to match fuel_avg
        dpg.set_value("target_fuel", dpg.get_value("fuel_avg"))

    def get_race_distance_action(self):
        # Set the no of laps we expect to complete based on race distance
        race_distance = dpg.get_value("race_distance")
        lap_length = dpg.get_value("lap_length")
        no_of_laps = self.ps.calculate_total_laps(race_distance, lap_length)
        dpg.set_value("total_laps", no_of_laps)

    def get_pit_stop_report_action(self):
        # Get the Pit Lane report based on manual observations
        tpt = dpg.get_value("total_pit_time")
        st = dpg.get_value("service_time")
        tc = dpg.get_value("tank_capacity")
        tct = dpg.get_value("tyre_change_time")
        af = dpg.get_value("fuel_avg")
        pll, rr, tcli, tcla = self.ps.get_pit_stop_report(tpt, st, tc, tct, af)
        dpg.set_value("pit_lane_loss", pll)
        dpg.set_value("refuelling_rate", rr)
        dpg.set_value("tyre_change_litres", tcli)
        dpg.set_value("tyre_change_laps", tcla)

    def calculate_stila_action(self):
        # Calculate the no of laps per stint based on expected fuel usage
        total_fuel = dpg.get_value("tank_capacity")
        fuel_to_stila = {
            "fuel_min": "stint_laps_min",
            "fuel_avg": "stint_laps_avg",
            "fuel_max": "stint_laps_max",
        }

        for fuel_tag, stila_tag in fuel_to_stila.items():
            fuel_lap = dpg.get_value(fuel_tag)
            laps = self.ps.calculate_laps_in_tank(total_fuel, fuel_lap)
            dpg.set_value(stila_tag, laps)

    def calculate_full_distance_strategies(self):
        self.calculate_full_race_distance_equal_stint_strategy()
        self.calculate_full_race_distance_final_stint_strategy()

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
            dpg.set_value(f"res_fpl_{label}", f"{fuel_lap:.3f}")
            dpg.set_value(f"res_lps_{label}", stint_plan["laps_per_stint"])
            dpg.set_value(f"res_stops_{label}", stint_plan["stops"])
            dpg.set_value(f"last_stint_{label}", stint_plan["last_stint_laps"])

    def calculate_full_race_distance_equal_stint_strategy(self):
        """ Basic Equal Stint Strategy assumes that the team completes all 173 laps regardless of their finishing position.
            This strategy equalises the stints to avoid any 'splash and dash' at the end.
        :return:
        """
        total_laps = dpg.get_value("total_laps")
        tank_capacity = dpg.get_value("tank_capacity")
        tyre_change_litres = dpg.get_value("tyre_change_litres")
        target_fuel = dpg.get_value("target_fuel")

        stint_array = self.ps.calculate_equal_stint_plan(
            total_laps=total_laps,
            tank_capacity=tank_capacity,
            fuel_per_lap=target_fuel,
            tyre_change_litres=tyre_change_litres
        )

        # Clear existing dynamic content from the group.
        dpg.delete_item("full_race_distance_equal_stint_strategy", children_only=True)

        if stint_array.get("status") == "passed":
            # Build the stint grid plan and then build into the group.
            stint_grid_plan = self.build_stint_plan_grid(stint_array)
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

        total_laps = dpg.get_value("total_laps")
        tank_capacity = dpg.get_value("tank_capacity")
        tyre_change_litres = dpg.get_value("tyre_change_litres")
        target_fuel = dpg.get_value("target_fuel")

        # Build a stint array based on maximum stints except last two which are equalised
        stint_array = self.ps.calculate_final_stint_plan(
            total_laps=total_laps,
            tank_capacity=tank_capacity,
            fuel_per_lap=target_fuel,
            tyre_change_litres=tyre_change_litres
        )

        print(stint_array)


