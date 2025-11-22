import dearpygui.dearpygui as dpg

from modules.ui.base_widget import BaseWidget

class WeekendWidget(BaseWidget):
    LABEL = "Weekend Options"
    TAG = "weekend_group"
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
            "NumStarters": f"{self.section_tag}_num_starters",
            "StartingGrid": f"{self.section_tag}_starting_grid",
            "QualifyScoring": f"{self.section_tag}_qualify_scoring",
            "CourseCautions": f"{self.section_tag}_course_cautions",
            "StandingStart": f"{self.section_tag}_standing_start",
            "Restarts": f"{self.section_tag}_restarts",
            "WeatherType": f"{self.section_tag}_weather_type",
            "Skies": f"{self.section_tag}_skies",
            "WindDirection": f"{self.section_tag}_wind_direction",
            "WindSpeed": f"{self.section_tag}_wind_speed",
            "WeatherTemp": f"{self.section_tag}_weather_temp",
            "RelativeHumidity": f"{self.section_tag}_relative_humidity",
            "FogLevel": f"{self.section_tag}_fog_level",
            "Unofficial": f"{self.section_tag}_unofficial",
            "CommercialMode": f"{self.section_tag}_commercial_mode",
            "NightMode": f"{self.section_tag}_night_mode",
            "IsFixedSetup": f"{self.section_tag}_is_fixed_setup",
            "StrictLapsChecking": f"{self.section_tag}_strict_laps_checking",
            "HasOpenRegistration": f"{self.section_tag}_has_open_registration",
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

                for i in range(1,6):
                    dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_stretch=True)

                # 5 columns per row
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Num Starters", key="NumStarters", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Starting Grid", key="StartingGrid", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Qualify Scoring", key="QualifyScoring", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Course Cautions", key="CourseCautions", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Standing Start", key="StandingStart", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Restarts", key="Restarts", width=self.CELL_WIDTH)

                with dpg.table_row():
                    self.get_vertical_table_cell(label="Skies", key="Skies", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Wind Direction", key="WindDirection", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Wind Speed", key="WindSpeed", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Weather Temp", key="WeatherTemp", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Relative Humidity", key="RelativeHumidity", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Fog Level", key="FogLevel", width=self.CELL_WIDTH)

                with dpg.table_row():
                    self.get_vertical_table_cell(label="Weather Type", key="WeatherType", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Night Mode", key="NightMode", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Fixed Setup", key="IsFixedSetup", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Strict Laps Check", key="StrictLapsChecking", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Unofficial", key="Unofficial", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Commercial Mode", key="CommercialMode", width=self.CELL_WIDTH)
                    # self.get_vertical_table_cell(label="Open Registration", key="HasOpenRegistration", width=self.CELL_WIDTH)


        dpg.bind_item_theme(self.table_tag, self.theme_tag)



