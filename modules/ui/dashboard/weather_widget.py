import dearpygui.dearpygui as dpg

from modules.ui.base_widget import BaseWidget

class WeatherWidget(BaseWidget):
    LABEL = "Weather"
    TAG = "weather_group"

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
            "AirTemp": f"{self.section_tag}_air_temp",
            "RelativeHumidity": f"{self.section_tag}_relative_humidity",
            "AirDensity": f"{self.section_tag}_air_density",
            "AirPressure": f"{self.section_tag}_air_pressure",
            "TrackTempCrew": f"{self.section_tag}_track_temp",
            "TrackWetness": f"{self.section_tag}_track_wetness",
            "WindDir": f"{self.section_tag}_wind_dir",
            "WindVel": f"{self.section_tag}_wind_vel",
            "FogLevel": f"{self.section_tag}_fog_level",
            "Skies": f"{self.section_tag}_skies",
            "Precipitation": f"{self.section_tag}_precipitation",
            "WeatherDeclaredWet": f"{self.section_tag}_weather_declared_wet",
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
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_stretch=True)

                # Row 1
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Air Temp", key="AirTemp")
                    self.get_vertical_table_cell(label="Rel. Humidity", key="RelativeHumidity")
                    self.get_vertical_table_cell(label="Air Density", key="AirDensity")
                    self.get_vertical_table_cell(label="Air Pressure", key="AirPressure")

                # Row 1
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Track Temp", key="TrackTempCrew")
                    self.get_vertical_table_cell(label="Track Wet", key="TrackWetness")
                    self.get_vertical_table_cell(label="Wind Dir", key="WindDir")
                    self.get_vertical_table_cell(label="Wind Vel", key="WindVel")

                # Row 1
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Fog Level", key="FogLevel")
                    self.get_vertical_table_cell(label="Skies", key="Skies")
                    self.get_vertical_table_cell(label="Precip", key="Precipitation")
                    self.get_vertical_table_cell(label="Dec. Wet", key="WeatherDeclaredWet")

        dpg.bind_item_theme(self.table_tag, self.theme_tag)






