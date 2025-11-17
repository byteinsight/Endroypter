# ui/timing_panel.py
import dearpygui.dearpygui as dpg
from ui.base_panel import BasePanel


class TimingPanel(BasePanel):
    label = "Timing"

    def build(self):
        """Builds the timing table inside the tab created by MainUI."""

        dpg.add_text("Standings")
        dpg.add_separator()

        # Store table + cell IDs
        self.rows = []

        with dpg.table(
            header_row=True,
            resizable=True,
            borders_innerH=True,
            borders_innerV=True,
            borders_outerH=True,
            borders_outerV=True
        ) as self.table_id:

            dpg.add_table_column(label="Pos")
            dpg.add_table_column(label="Driver")
            dpg.add_table_column(label="Gap")

            # Create example rows
            for i in range(20):
                with dpg.table_row() as row_id:
                    pos_id = dpg.add_text(str(i + 1))
                    driver_id = dpg.add_text(f"Driver {i + 1}")
                    gap_id = dpg.add_text("+0.0")

                    # Store each cell for updates
                    self.rows.append({
                        "row": row_id,
                        "pos": pos_id,
                        "driver": driver_id,
                        "gap": gap_id,
                    })

    def update(self, timing_data):
        """
        Refresh timing rows. Expected timing_data format:
        [
            {"pos": 1, "driver": "Smith", "gap": "+0.0"},
            {"pos": 2, "driver": "Jones", "gap": "+1.4"},
            ...
        ]
        """

        if not timing_data:
            return

        for idx, entry in enumerate(timing_data):
            if idx >= len(self.rows):
                break  # avoid extra data

            row = self.rows[idx]

            dpg.set_value(row["pos"], str(entry.get("pos", "")))
            dpg.set_value(row["driver"], entry.get("driver", ""))
            dpg.set_value(row["gap"], entry.get("gap", ""))
