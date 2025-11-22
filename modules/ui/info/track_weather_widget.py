import dearpygui.dearpygui as dpg

from modules.ui.base_widget import BaseWidget

class TrackWeatherWidget(BaseWidget):
    LABEL = "Track Weather"
    TAG = "track_weather_group"
    CELL_WIDTH = 180
    def __init__(self, ctx, prefix=None, show_header=True):
        super().__init__(ctx, prefix, show_header)
        """
        Initialize the widget and inherit the BaseWidget tagging framework.

        Inherited from BaseWidget:
        - section_tag: root container tag unique to this widget instance.
        - theme_tag: tag used to create and bind the widget's theme.
        - table_tag: default table tag for widgets that render a DearPyGUI table.
        - tags: dictionary for storing element tags used during updates.

        `prefix` optionally namespaces all tags to allow multiple instances of
        the same widget to coexist without collisions.
        """

        # Derived tags
        self.tags = {
            "TrackWeatherType": f"{self.section_tag}_track_weather_type",
            "TrackSkies": f"{self.section_tag}_track_skies",
            "TrackSurfaceTempC": f"{self.section_tag}_track_surface_temp_c",
            "TrackAirTempC": f"{self.section_tag}_track_air_temp_c",
            "TrackAirPressureHg": f"{self.section_tag}_track_air_pressure_hg",
            "TrackRelativeHumidityPct": f"{self.section_tag}_track_relative_humidity_pct",
            "TrackFogLevelPct": f"{self.section_tag}_track_fog_level_pct",
            "TrackWindVelMS": f"{self.section_tag}_track_wind_vel_ms",
            "TrackWindDirRad": f"{self.section_tag}_track_wind_dir_rad",
        }

    # BUILD UI
    def inner_build(self):

        with dpg.group(tag=self.section_tag): # , border=True, autosize_x=True):
            with dpg.table(
                tag=self.table_tag,
                header_row=False,
                resizable=False,
                policy=dpg.mvTable_SizingFixedFit,
                borders_innerH=False,
                borders_innerV=False,
                borders_outerH=True,
                borders_outerV=True
            ):

                for i in range(1,5):
                    dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_stretch=True)

                # Row 1
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Air Temp", key="TrackAirTempC", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Humidity (%)", key="TrackRelativeHumidityPct", width=self.CELL_WIDTH)
                    dpg.add_spacer()
                    self.get_vertical_table_cell(label="Pressure (Hg)", key="TrackAirPressureHg", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Surface Temp", key="TrackSurfaceTempC", width=self.CELL_WIDTH)

                # Row 2
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Weather Type", key="TrackWeatherType", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Skies", key="TrackSkies", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Fog (%)", key="TrackFogLevelPct", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Wind (m/s)", key="TrackWindVelMS", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Wind Dir (rad)", key="TrackWindDirRad", width=self.CELL_WIDTH)


        dpg.bind_item_theme(self.table_tag, self.theme_tag)



