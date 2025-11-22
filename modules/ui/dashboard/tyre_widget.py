import dearpygui.dearpygui as dpg

import dearpygui.dearpygui as dpg

from modules.ui.base_widget import BaseWidget

class TyreWidget(BaseWidget):
    LABEL = "Tyres"
    TAG = "tyre_group"
    CELL_WIDTH = 120
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

            # ============================
            # TYRE USAGE
            # ============================

            # Left-Front
            "LF_temp_CL": f"{self.section_tag}_LF_temp_CL",
            "LF_temp_CM": f"{self.section_tag}_LF_temp_CM",
            "LF_temp_CR": f"{self.section_tag}_LF_temp_CR",

            "LF_wear_L": f"{self.section_tag}_LF_wear_L",
            "LF_wear_M": f"{self.section_tag}_LF_wear_M",
            "LF_wear_R": f"{self.section_tag}_LF_wear_R",

            # Right-Front
            "RF_temp_CL": f"{self.section_tag}_RF_temp_CL",
            "RF_temp_CM": f"{self.section_tag}_RF_temp_CM",
            "RF_temp_CR": f"{self.section_tag}_RF_temp_CR",

            "RF_wear_L": f"{self.section_tag}_RF_wear_L",
            "RF_wear_M": f"{self.section_tag}_RF_wear_M",
            "RF_wear_R": f"{self.section_tag}_RF_wear_R",

            # Left-Rear
            "LR_temp_CL": f"{self.section_tag}_LR_temp_CL",
            "LR_temp_CM": f"{self.section_tag}_LR_temp_CM",
            "LR_temp_CR": f"{self.section_tag}_LR_temp_CR",

            "LR_wear_L": f"{self.section_tag}_LR_wear_L",
            "LR_wear_M": f"{self.section_tag}_LR_wear_M",
            "LR_wear_R": f"{self.section_tag}_LR_wear_R",

            # Right-Rear
            "RR_temp_CL": f"{self.section_tag}_RR_temp_CL",
            "RR_temp_CM": f"{self.section_tag}_RR_temp_CM",
            "RR_temp_CR": f"{self.section_tag}_RR_temp_CR",

            "RR_wear_L": f"{self.section_tag}_RR_wear_L",
            "RR_wear_M": f"{self.section_tag}_RR_wear_M",
            "RR_wear_R": f"{self.section_tag}_RR_wear_R",

            # ============================
            # TYRE DATA (timestamps)
            # ============================
            "LF_time": f"{self.section_tag}_LF_time",
            "RF_time": f"{self.section_tag}_RF_time",
            "LR_time": f"{self.section_tag}_LR_time",
            "RR_time": f"{self.section_tag}_RR_time",
        }

    # BUILD UI
    def inner_build(self):
        with dpg.group(tag=self.section_tag): # , border=True, autosize_x=True):
            with dpg.table(
                tag=self.table_tag,
                header_row=False,
                resizable=False,
                policy=dpg.mvTable_SizingFixedFit,
                borders_innerH=True,
                borders_innerV=True,
                borders_outerH=True,
                borders_outerV=True
            ):
                # 9 columns: Position | Time | Metric | 3x Left | 3x Right
                dpg.add_table_column(width_fixed=True)  # Position
                dpg.add_table_column(width_fixed=True)  # Metric
                dpg.add_table_column(width_fixed=True)  # LF/LR Left
                dpg.add_table_column(width_fixed=True)  # LF/LR Center
                dpg.add_table_column(width_fixed=True)  # LF/LR Right
                dpg.add_table_column(width_fixed=True)  # RF/RR Left
                dpg.add_table_column(width_fixed=True)  # RF/RR Center
                dpg.add_table_column(width_fixed=True)  # RF/RR Right
                dpg.add_table_column(width_fixed=True)  # Time Label
                dpg.add_table_column(width_stretch=True)  # Time

                # ============================================================
                # HEADER ROW
                # ============================================================

                # ---- Front: Temperature Row ----
                with dpg.table_row():

                    # No Data
                    dpg.add_text("")
                    dpg.add_text("")

                    # Left Side Labels
                    self.get_label_table_cell("C. Out", key=f"{self.table_tag}_lclft")
                    self.get_label_table_cell("C. Mid", key=f"{self.table_tag}_lcmid")
                    self.get_label_table_cell("C. Inn", key=f"{self.table_tag}_lcrgt")

                    # Right Side Labels
                    self.get_label_table_cell("C. Inn", key=f"{self.table_tag}_rclft")
                    self.get_label_table_cell("C. Mid", key=f"{self.table_tag}_rcmid")
                    self.get_label_table_cell("C. Out", key=f"{self.table_tag}_rcrgt")

                    # Time Label
                    dpg.add_text("")
                    self.get_label_table_cell("Time", key=f"{self.table_tag}_tyre_time")


                # ============================================================
                # FRONT AXLE
                # ============================================================

                # ---- Front: Temperature Row ----
                with dpg.table_row():
                    self.get_label_table_cell("Front", key=f"{self.table_tag}_front")
                    self.get_label_table_cell("Temp", key=f"{self.table_tag}_ftemp")

                    # LF Temps
                    self.get_value_table_cell("LF_temp_CL", width=self.CELL_WIDTH)
                    self.get_value_table_cell("LF_temp_CM", width=self.CELL_WIDTH)
                    self.get_value_table_cell("LF_temp_CR", width=self.CELL_WIDTH)

                    # RF Temps
                    self.get_value_table_cell("RF_temp_CL", width=self.CELL_WIDTH)
                    self.get_value_table_cell("RF_temp_CM", width=self.CELL_WIDTH)
                    self.get_value_table_cell("RF_temp_CR", width=self.CELL_WIDTH)

                    self.get_label_table_cell("Left", key=f"{self.table_tag}_lf_time")
                    self.get_value_table_cell("LF_time")  # Time (Left)

                # ---- Front: Wear Row ----
                with dpg.table_row():
                    dpg.add_text("")  # Position (blank)
                    self.get_label_table_cell("Wear", key=f"{self.table_tag}_fwear")

                    # LF Wear
                    self.get_value_table_cell("LF_wear_L")
                    self.get_value_table_cell("LF_wear_M")
                    self.get_value_table_cell("LF_wear_R")

                    # RF Wear
                    self.get_value_table_cell("RF_wear_L")
                    self.get_value_table_cell( "RF_wear_M")
                    self.get_value_table_cell("RF_wear_R")

                    self.get_label_table_cell("Right", key=f"{self.table_tag}_rf_time")
                    self.get_value_table_cell("RF_time")  # Time (Right)

                # ============================================================
                # REAR AXLE
                # ============================================================

                # ---- Rear: Temperature Row ----
                with dpg.table_row():
                    self.get_label_table_cell("Rear", key=f"{self.table_tag}_rear")
                    self.get_label_table_cell("Temp", key=f"{self.table_tag}_rtemp")

                    # LR Temps
                    self.get_value_table_cell("LR_temp_CL")
                    self.get_value_table_cell( "LR_temp_CM")
                    self.get_value_table_cell( "LR_temp_CR")

                    # RR Temps
                    self.get_value_table_cell( "RR_temp_CL")
                    self.get_value_table_cell( "RR_temp_CM")
                    self.get_value_table_cell( "RR_temp_CR")

                    self.get_label_table_cell("Left", key=f"{self.table_tag}_lr_time")
                    self.get_value_table_cell("LR_time")  # Time (Left)

                # ---- Rear: Wear Row ----
                with dpg.table_row():
                    dpg.add_text("")  # Position (blank)
                    self.get_label_table_cell("Wear", key=f"{self.table_tag}_rwear")

                    # LR Wear
                    self.get_value_table_cell("LR_wear_L")
                    self.get_value_table_cell("LR_wear_M")
                    self.get_value_table_cell("LR_wear_R")

                    # RR Wear
                    self.get_value_table_cell("RR_wear_L")
                    self.get_value_table_cell("RR_wear_M")
                    self.get_value_table_cell("RR_wear_R")

                    self.get_label_table_cell("Right", key=f"{self.table_tag}_rr_time")
                    self.get_value_table_cell("RR_time")  # Time (Right Rear)

        dpg.bind_item_theme(self.table_tag, self.theme_tag)

    # -----------------------
    # UPDATE METHOD
    # -----------------------
    def update(self, formatted_data: dict):
        # self.ctx.logger.debug(f"Tyre Update: {formatted_data}")
        for key, tag in self.tags.items():
            if key not in formatted_data:
                continue
            if not dpg.does_item_exist(tag):
                self.ctx.logger.error(f"Missing widget value tag: {tag} for {formatted_data[key]}.")
                continue
            dpg.set_value(tag, formatted_data[key])