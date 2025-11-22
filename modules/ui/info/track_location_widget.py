import dearpygui.dearpygui as dpg

from modules.ui.base_widget import BaseWidget

class TrackLocationWidget(BaseWidget):
    LABEL = "Track Location"
    TAG = "track_location_group"
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
            "TrackCity": f"{self.section_tag}_track_city",
            "TrackCountry": f"{self.section_tag}_track_country",
            "TrackLatitude": f"{self.section_tag}_track_latitude",

            "TrackLongitude": f"{self.section_tag}_track_longitude",
            "TrackAltitudeM": f"{self.section_tag}_track_altitude_m",
            "TrackNorthOffsetRad": f"{self.section_tag}_track_north_offset_rad",
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

                for i in range(5):
                    dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_stretch=True)

                with dpg.table_row():
                    self.get_vertical_table_cell(label="City", key="TrackCity", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Country", key="TrackCountry", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Latitude", key="TrackLatitude", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Longitude", key="TrackLongitude", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Altitude (m)", key="TrackAltitudeM", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="North Offset", key="TrackNorthOffsetRad", width=self.CELL_WIDTH)

        dpg.bind_item_theme(self.table_tag, self.theme_tag)



