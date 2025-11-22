import dearpygui.dearpygui as dpg

from modules.ui.base_widget import BaseWidget

class SessionWidget(BaseWidget):
    LABEL = "Session"
    TAG = "session_group"

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
            "SessionID": f"{self.section_tag}_id",
            "SessionStatus": f"{self.section_tag}_status",
            "SessionTick": f"{self.section_tag}_tick",

            "SessionTimeOfDay": f"{self.section_tag}_time_of_day",
            "SessionTime": f"{self.section_tag}_time",
            "SessionTimeRemain": f"{self.section_tag}_time_remain",

            "SessionLapsTotal": f"{self.section_tag}_laps_total",
            "SessionLapsRemainEx": f"{self.section_tag}_laps_remain_ex",
            "PlayerCarIdx": f"{self.section_tag}_player_car_idx",
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
                dpg.add_table_column(width_stretch=True)

                # Row 1
                with dpg.table_row():
                    self.get_vertical_table_cell(label="SessionID", key="SessionID")
                    self.get_vertical_table_cell(label="TOD", key="SessionTimeOfDay")
                    self.get_vertical_table_cell(label="Status", key="SessionStatus")

                # Row 1
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Tick", key="SessionTick")
                    self.get_vertical_table_cell(label="Race Time", key="SessionTime")
                    self.get_vertical_table_cell(label="SessionLapsTotal", key="SessionLapsTotal")

                # Row 1
                with dpg.table_row():
                    self.get_vertical_table_cell(label="PC. Idx", key="PlayerCarIdx")
                    self.get_vertical_table_cell(label="Time Remain", key="SessionTimeRemain")
                    self.get_vertical_table_cell(label="SessionLapsRemainEx", key="SessionLapsRemainEx")

        dpg.bind_item_theme(self.table_tag, self.theme_tag)



