import dearpygui.dearpygui as dpg

from modules.ui.base_widget import BaseWidget

class PitStopWidget(BaseWidget):
    LABEL = "Pit Stop"
    TAG = "pits_group"
    CELL_WIDTH=120

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

        self.header_value_key = "box_in_lap"
        self.ctx.logger.error(f"[PitStopWidget.__init__] header_value_key set to {self.header_value_key}")

        # Derived tags
        self.tags = {
            # --- Core Start Timings ---
            "box_in_time": f"{self.section_tag}_box_in_time",
            "pit_in_time": f"{self.section_tag}_pit_in_time",
            "service_start_time": f"{self.section_tag}_service_start_time",

            # --- Core End Times
            "service_end_time": f"{self.section_tag}_service_end_time",
            "pit_out_time": f"{self.section_tag}_pit_out_time",
            "back_on_track": f"{self.section_tag}_back_on_track",

            # --- Durations ---
            "service_time": f"{self.section_tag}_service_time",
            "stop_length": f"{self.section_tag}_stop_length",
            "total_pit_stop": f"{self.section_tag}_total_pit_stop",

            # --- Fuel ---
            "fuel_start_time": f"{self.section_tag}_fuel_start_time",
            "fuel_start_level": f"{self.section_tag}_fuel_start_level",
            "fuel_end_time": f"{self.section_tag}_fuel_end_time",
            "fuel_end_level": f"{self.section_tag}_fuel_end_level",
            "fuel_fill_time": f"{self.section_tag}_fuel_fill_time",
            "fuel_fill_amount": f"{self.section_tag}_fuel_fill_amount",
            "fuel_per_sec": f"{self.section_tag}_fuel_per_sec",

            # --- Tyre process state ---
            "tyres_start_time": f"{self.section_tag}_tyres_start_time",
            "tyres_finish_time": f"{self.section_tag}_tyres_finish_time",
            "tyre_change_time": f"{self.section_tag}_tyre_change_time",
            "litres_over_tyres": f"{self.section_tag}_litres_over_tyres",

            # --- Jacks ---
            "on_jacks_time": f"{self.section_tag}_on_jacks_time",
            "off_jacks_time": f"{self.section_tag}_off_jacks_time",
            "total_jack_time": f"{self.section_tag}_total_jack_time",


            # --- Lap reference ---
            "box_in_lap": f"{self.section_tag}_box_in_lap",

            # --- Repairs ---
            "tow_time": f"{self.section_tag}_tow_time",
            "repairs": f"{self.section_tag}_repairs",
            "opt_repairs_max": f"{self.section_tag}_opt_repairs_max",
            "opt_repairs_remaining": f"{self.section_tag}_opt_repairs_remaining",
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
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_stretch=True)

                # Row 1: Start Times
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Box In", key="box_in_time", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Pit In", key="pit_in_time", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Srv Srt", key="service_start_time", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Tyre Srt", key="tyres_start_time", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Ful Srt", key="fuel_start_time", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Start Lvl", key="fuel_start_level", width=self.CELL_WIDTH)

                    #self.get_vertical_table_cell(label="Lap In", key="box_in_lap", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Fuel/T", key="fuel_per_sec", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Tow Time", key="tow_time", width=self.CELL_WIDTH)
                    self.get_vertical_table_cell(label="Jack Up", key="on_jacks_time", width=self.CELL_WIDTH)

                # Row 2: End Times
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Box Out", key="back_on_track")
                    self.get_vertical_table_cell(label="Pit Out", key="pit_out_time")
                    self.get_vertical_table_cell(label="Srv End", key="service_end_time")
                    self.get_vertical_table_cell(label="Tyre End", key="tyres_finish_time")
                    self.get_vertical_table_cell(label="Fuel End", key="fuel_end_time")
                    self.get_vertical_table_cell(label="End Lvl", key="fuel_end_level")

                    self.get_vertical_table_cell(label="L/Tyre", key="litres_over_tyres")
                    self.get_vertical_table_cell(label="Rep Time", key="repairs")
                    self.get_vertical_table_cell(label="Jack Dwn", key="off_jacks_time")

                # Row 3:  Total Times
                with dpg.table_row():
                    self.get_vertical_table_cell(label="Ttl Time", key="total_pit_stop")
                    self.get_vertical_table_cell(label="Pit Time", key="stop_length")
                    self.get_vertical_table_cell(label="Srv. Time", key="service_time")
                    self.get_vertical_table_cell(label="Tyre Time", key="tyre_change_time")
                    self.get_vertical_table_cell(label="Fuel Time", key="fuel_fill_time")
                    self.get_vertical_table_cell(label="Fuel Ttl", key="fuel_fill_amount")




                    self.get_vertical_table_cell(label="Opt Rem", key="opt_repairs_remaining")
                    self.get_vertical_table_cell(label="Opt Time", key="opt_repairs_max")
                    self.get_vertical_table_cell(label="Ttl Jack", key="total_jack_time")

        dpg.bind_item_theme(self.table_tag, self.theme_tag)





