import dearpygui.dearpygui as dpg
from helpers.app_context import AppContext

class BasePanel:
    """
    Base UI panel with optional automatic grid rendering.
    Subclasses may:
        - supply INPUT_GRID for auto-build
        - override build_extra() to add custom UI elements
        - override update() if needed
    """

    label = "Panel"
    INPUT_GRID = None

    def __init__(self, label=None, parent=None):
        self.label = label or self.label
        self.parent = parent
        self.ctx = AppContext.instance()
        self.id = None

    # -----------------------------------------------------
    # DEFAULT BUILD METHOD (calls grid + extra UI)
    # -----------------------------------------------------
    def build(self):
        """Main entry point for building this panel."""
        dpg.add_text(self.label)
        dpg.add_separator()

        # Auto-build grid if defined
        if self.INPUT_GRID:
            self.build_input_grid(self.INPUT_GRID)

        # Allow subclasses to continue
        self.build_extra()

    def build_extra(self):
        """Optional: subclasses can override to add widgets below the grid."""
        pass

    # --------------------------------------------
    # GRID BUILDER
    # --------------------------------------------
    def build_input_grid(self, grid_data, columns=3):

        with dpg.table(
                header_row=False,
                borders_innerH=True,
                borders_innerV=True,
                borders_outerH=True,
                borders_outerV=True,
                policy=dpg.mvTable_SizingStretchProp,
        ):
            for _ in range(columns):
                dpg.add_table_column()

            for row in grid_data:

                with dpg.table_row():

                    # section-only row: [{"section": "..."}]
                    if len(row) == 1 and "section" in row[0]:
                        self._add_section_cell(row[0]["section"])
                        for _ in range(columns - 1):
                            dpg.add_text("")
                        continue

                    col_count = 0

                    for cell in row:
                        # section cell inside row
                        if "section" in cell:
                            self._add_section_cell(cell["section"])
                            col_count += 1
                            continue

                        # horizontal cell (label + input on one line)
                        if cell.get("horizontal", False):
                            self._add_horizontal_input_cell(cell)
                            col_count += 1
                            continue

                        # normal vertical cell (label above input)
                        if "tag" in cell:
                            self._add_vertical_input_cell(cell)
                            col_count += 1
                            continue

                        # fallback
                        self._add_fallback_cell(cell)
                        col_count += 1

                    # pad missing columns
                    for _ in range(columns - col_count):
                        dpg.add_text("")

    # --------------------------------------------
    # CELL HELPERS
    # --------------------------------------------
    @staticmethod
    def _add_section_cell(text: str):
        return dpg.add_text(text)

    def _add_horizontal_input_cell(self, cell: dict):
        label = cell.get("label", None)
        with dpg.group(horizontal=True):
            if label:  # only render label if not None/empty
                dpg.add_text(cell["label"])
            return self._create_input_widget(cell)

    def _add_vertical_input_cell(self, cell: dict):
        label = cell.get("label", None)
        with dpg.group(horizontal=False):
            if label:  # only render label if not None/empty
                dpg.add_text(cell["label"])
            return self._create_input_widget(cell)

    @staticmethod
    def _add_fallback_cell(cell):
        return dpg.add_text(str(cell))

    @staticmethod
    def _create_input_widget(cell: dict):
        tag = cell["tag"]
        default = cell.get("default", "")
        readonly = cell.get("readonly", False)
        width = cell.get("width", 180)

        explicit_type = cell.get("type")
        inferred_type = explicit_type or type(default).__name__

        # Float
        if inferred_type in ("float", "double"):
            return dpg.add_input_float(
                tag=tag, default_value=float(default), width=width, readonly=readonly
            )

        # Integer
        if inferred_type in ("int", "integer"):
            return dpg.add_input_int(
                tag=tag, default_value=int(default), width=width, readonly=readonly
            )

        # Boolean
        if inferred_type in ("bool", "boolean"):
            return dpg.add_checkbox(tag=tag, default_value=bool(default))

        # String / Text
        return dpg.add_input_text(
            tag=tag, default_value=str(default), width=width, readonly=readonly
        )

    def update(self, data):
        """Optional refresh behavior"""
        pass
