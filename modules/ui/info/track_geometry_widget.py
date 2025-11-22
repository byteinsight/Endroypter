import dearpygui.dearpygui as dpg

from modules.ui.base_widget import BaseWidget

class TrackGeometryWidget(BaseWidget):
    LABEL = "Track Geometry"
    TAG = "track_geometry_group"
    CELL_WIDTH = 192

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
            "TrackLengthKM": f"{self.section_tag}_track_length_km",
            "TrackNumTurns": f"{self.section_tag}_track_num_turns",
            "TrackPitSpeedLimitKPH": f"{self.section_tag}_track_pit_speed_limit_kph",
            "TrackCleanup": f"{self.section_tag}_track_cleanup",
            "TrackDynamicTrack": f"{self.section_tag}_track_dynamic_track",
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

                for i in range(1,4):
                    dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_stretch=True)

                # Row 1
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Length (km)", key="TrackLengthKM", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Turns", key="TrackNumTurns", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Pit Speed (kph)", key="TrackPitSpeedLimitKPH", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Cleanup", key="TrackCleanup", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Dynamic", key="TrackDynamicTrack", width=self.CELL_WIDTH)

        dpg.bind_item_theme(self.table_tag, self.theme_tag)



