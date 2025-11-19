# ui/timing_panel.py
import dearpygui.dearpygui as dpg

from modules.ui.base_panel import BasePanel


class TimingPanel(BasePanel):
    LABEL = "Timing"
    MAX_CARS = 64
    TIMING_TABLE_SCHEMA = {
        "CarIdxPosition": {"label": "Pos", "tag": "car_idx_pos", "datatype": "int", "default": ""},
        "CarIdxClassPosition": {"label": "Class Pos", "tag": "car_idx_class_pos", "datatype": "int", "default": ""},
        "DriverName": {"label": "Driver", "tag": "driver_name", "datatype": "text", "default": ""},
        "CarNumber": {"label": "Num", "tag": "car_number", "datatype": "text", "default": ""},
        "License": {"label": "Lic", "tag": "driver_license", "datatype": "text", "default": ""},
        "CarIdxLap": {"label": "Lap", "tag": "car_idx_lap", "datatype": "int", "default": ""},
        "CarIdxLastLapTime": {"label": "Last Lap", "tag": "car_idx_last_laptime", "datatype": "time", "default": ""},
        "CarIdxF2Time": {"label": "F2 Time", "tag": "car_idx_f2_time", "datatype": "time", "default": ""},
        "CarIdxTrackSurface": {"label": "TS", "tag": "car_idx_track_surface", "datatype": "int", "default": ""},
        "CarIdxOnPitRoad": {"label": "Pits", "tag": "car_idx_in_pits", "datatype": "int", "default": ""},
        "CurDriverIncidentCount": {"label": "Inc", "tag": "driver_incidents", "datatype": "int", "default": ""},
    }

    # Tags in the Timing Table for quick updating of timing data
    timing_table_tags = None

    def __init__(self, ctx):
        super().__init__(ctx)

        self.create_row_themes()

    def build(self):
        """Builds the timing table inside the tab created by MainUI."""


        dpg.add_text("Live Timing")
        dpg.add_separator()

        # Build static table structure from schema
        self.timing_table_tags = self.build_timing_table(
            schema=self.TIMING_TABLE_SCHEMA
        )

    def build_timing_table(self, schema: dict):
        """
        Build the timing table using TIMING_TABLE_SCHEMA.
        Creates:
            - Columns using schema['label']
            - Cell tags using schema['tag'] + row index
            - MAX_CARS rows (preallocated)
        Returns:
            dict[(schema_key, row)] = cell_tag
        """
        with dpg.table(
                tag="timing_table",
                header_row=True,
                resizable=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_innerH=True
        ):
            # Create columns using schema labels
            for key, col in schema.items():
                dpg.add_table_column(label=col["label"])

            # Dictionary to store cell tags for fast updates
            cell_tags = {}

            # Preallocate rows (max cars)
            for row in range(self.MAX_CARS):
                with dpg.table_row():
                    for key, col in schema.items():
                        cell_tag = f"{col['tag']}_{row}"
                        dpg.add_text(col["default"], tag=cell_tag)
                        cell_tags[(key, row)] = cell_tag

        return cell_tags

    def create_row_themes(self):
        with dpg.theme() as self.theme_row_highlight:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 0))  # yellow text
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (50, 50, 50))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (40, 40, 40))

        with dpg.theme() as self.theme_row_normal:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (220, 220, 220))

    def update(self, update_data: dict):
        if update_data['timing_data'] is None:
            return

        # Create a copy and enrich it with driver info
        timing_snapshot = update_data['timing_data'].copy()
        timing_snapshot = self.enrich_timing_with_driver_data(timing_snapshot, update_data['driver_data'])

        # Determine car order first
        sorted_car_indices = self.sort_car_indices_by_position(timing_snapshot)
        player_idx = update_data["PlayerCarIdx"]

        for row, car_idx in enumerate(sorted_car_indices):
            for key, col in self.TIMING_TABLE_SCHEMA.items():
                values = timing_snapshot.get(key, [])
                datatype = col.get("datatype")

                raw = values[car_idx] if car_idx < len(values) else col["default"]
                formatted = self.format_timing_value(raw, datatype)

                cell = self.timing_table_tags[(key, row)]
                dpg.set_value(cell, formatted)

                # Highlight rule
                if car_idx == player_idx:
                    dpg.bind_item_theme(cell, self.theme_row_highlight)
                else:
                    dpg.bind_item_theme(cell, self.theme_row_normal)

    def enrich_timing_with_driver_data(self, timing_data, driver_data):
        """
        Adds driver-related fields into timing_data using the iRacing driver_data
        dictionary stored on self.ir.driver_data. All arrays are indexed by CarIdx.
        """
        if not driver_data:
            return timing_data

        max_cars = self.MAX_CARS

        # Prepare arrays
        names = [""] * max_cars
        numbers = [""] * max_cars
        licenses = [""] * max_cars
        incidents = [""] * max_cars

        for car_idx, d in driver_data.items():
            if car_idx >= max_cars:
                continue

            names[car_idx] = d.get("UserName", "")
            numbers[car_idx] = d.get("CarNumber", "")
            licenses[car_idx] = d.get("LicString", "")
            incidents[car_idx] = d.get("CurDriverIncidentCount", "")

        timing_data["DriverName"] = names
        timing_data["CarNumber"] = numbers
        timing_data["License"] = licenses
        timing_data["CurDriverIncidentCount"] = incidents

        return timing_data

    @staticmethod
    def sort_car_indices_by_position(timing_data):
        """Return list of car_idx sorted by CarIdxPosition ascending (1 = leader)."""

        positions = timing_data.get("CarIdxPosition", [])

        indexed_positions = []

        for car_idx, pos in enumerate(positions):
            if pos > 0:  # ignore entries with 0 or invalid
                indexed_positions.append((pos, car_idx))

        # Sort by race position
        indexed_positions.sort(key=lambda x: x[0])

        # Return list of car_idx in race order
        return [car_idx for (_, car_idx) in indexed_positions]

    @staticmethod
    def format_timing_value(value, datatype: str):
        """Format raw timing values into display-safe strings."""

        # Empty or sentinel values
        if value is None:
            return ""

        # Negative values in iRacing often mean 'invalid' or 'not set'
        if isinstance(value, (int, float)) and value < 0:
            return ""

        # Dispatch by datatype
        if datatype == "int":
            return str(int(value))

        if datatype == "float":
            # e.g. lap time floats – you may want fixed decimals
            return f"{value:.3f}"

        if datatype == "time":
            # Convert raw seconds → mm:ss.xxx
            # Example: 73.123 → "1:13.123"
            seconds = float(value)
            minutes = int(seconds // 60)
            remainder = seconds % 60
            return f"{minutes}:{remainder:06.3f}"

        # Fallback – return raw
        return str(value)


