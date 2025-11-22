import dearpygui.dearpygui as dpg
from modules.core.app_context import AppContext

class BasePanel:
    """
    Base UI panel with optional automatic grid rendering.
    Subclasses may:
        - supply INPUT_GRID for auto-build
        - override build_extra() to add custom UI elements
        - override update() if needed
    """

    LABEL = "Panel"
    TAG = "tag"
    INPUT_GRID = None
    DEFAULT_WIDTH = 180

    header_tag = None
    header_theme_tag = None
    header_theme = None

    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.id = None

    # --------------------------------------------
    # THREAD and View/Hide Methods
    # --------------------------------------------
    requires_update = False

    def on_show(self):
        self.requires_update = True

    def on_hide(self):
        self.requires_update = False

    def update(self, data):
        """Override in subclasses to update UI widgets."""
        pass

    # -----------------------------------------------------
    # DEFAULT BUILD METHOD (calls grid + extra UI)
    # -----------------------------------------------------
    def build(self):
        """Main entry point for building this panel."""
        dpg.add_text(self.LABEL)
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
                dpg.add_table_column(width_fixed=True)

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

                        # Treat {} as a blank cell
                        if not cell:
                            dpg.add_text("")  # or a clearer empty placeholder
                            col_count += 1
                            continue

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

                        # label-only cell (IMPORTANT: before "tag" check)
                        if cell.get("type") == "label":
                            self._build_label(cell)
                            col_count += 1
                            continue

                        # normal vertical cell (label above input)
                        if "tag" in cell:
                            self._add_vertical_input_cell(cell)
                            col_count += 1
                            continue

                        # fallback
                        self._add_fallback_cell(cell)

                        # Increment the column counting
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
        label = cell.get("label")

        with dpg.group(horizontal=True):
            if label:
                dpg.add_text(label)

            widget = self._create_input_widget(cell)

            # Apply style AFTER widget creation
            tag = cell.get("tag")
            self._apply_input_style(tag, cell)
            return widget

    def _add_vertical_input_cell(self, cell: dict):
        label = cell.get("label", None)
        with dpg.group(horizontal=False):
            if label:  # only render label if not None/empty
                dpg.add_text(cell["label"])

            widget = self._create_input_widget(cell)

            # Apply style AFTER widget creation
            tag = cell.get("tag")
            self._apply_input_style(tag, cell)
            return widget

            # return self._create_input_widget(cell)

    @staticmethod
    def _add_fallback_cell(cell):
        return dpg.add_text(str(cell))

    def _create_input_widget(self, cell: dict):
        """
        Creates a DPG widget for an input grid cell.
        Actual widget creation is delegated to helper functions.
        """

        # 1. Blank cell
        if not cell or cell.get("type") == "blank":
            return self._build_blank(cell)

        # 2. Extract common fields
        widget_type = cell.get("type")
        default = cell.get("default", "")
        inferred_type = widget_type or type(default).__name__

        # 3. Dispatch table
        builder = {

            "label": self._build_label,

            "checkbox": self._build_checkbox,
            "bool": self._build_checkbox,
            "boolean": self._build_checkbox,

            "dropdown": self._build_dropdown,
            "combo": self._build_dropdown,
            "select": self._build_dropdown,

            "button": self._build_button,

            "float": self._build_float,
            "double": self._build_float,

            "int": self._build_int,
            "integer": self._build_int,

        }.get(inferred_type, self._build_text)  # fallback to text

        return builder(cell)

    @staticmethod
    def _build_blank(cell):
        return dpg.add_text("")

    @staticmethod
    def _build_checkbox(cell):
        return dpg.add_checkbox(
            tag=cell.get("tag"),
            default_value=bool(cell.get("default", False)),
            enabled=not cell.get("readonly", False)
        )

    def _build_dropdown(self, cell):
        items = cell.get("items", [])
        default = cell.get("default", "")

        if items and default not in items:
            default = items[0]

        return dpg.add_combo(
            tag=cell.get("tag"),
            items=items,
            default_value=default,
            width=cell.get("width", self.DEFAULT_WIDTH),
            enabled=not cell.get("readonly", False)
        )

    def _build_button(self, cell):
        label = cell.get("label", cell.get("default", cell.get("tag")))
        return dpg.add_button(
            tag=cell.get("tag") or 0,
            label=label,
            width=cell.get("width", self.DEFAULT_WIDTH),
            callback=cell.get("callback")
        )

    def _build_float(self, cell):
        return dpg.add_input_float(
            tag=cell.get("tag"),
            default_value=float(cell.get("default", 0.0)),
            width=cell.get("width", self.DEFAULT_WIDTH),
            readonly=cell.get("readonly", False)
        )

    def _build_int(self, cell):
        return dpg.add_input_int(
            tag=cell.get("tag"),
            default_value=int(cell.get("default", 0)),
            width=cell.get("width", self.DEFAULT_WIDTH),
            readonly=cell.get("readonly", False)
        )

    def _build_text(self, cell):
        return dpg.add_input_text(
            tag=cell.get("tag"),
            default_value=str(cell.get("default", "")),
            width=cell.get("width", self.DEFAULT_WIDTH),
            readonly=cell.get("readonly", False)
        )

    @staticmethod
    def _build_label(cell):
        text = cell.get("label", cell.get("default", ""))

        color = cell.get("color")      # optional RGB tuple
        width = cell.get("width", 0)   # 0 = auto

        # Labels don't use tags in most cases, but allow it for consistency
        tag = cell.get("tag")

        return dpg.add_text(
            text,
            tag=tag,
            color=color,
            wrap=width if width else -1
        )

    @staticmethod
    def _apply_input_style(tag: str, cell: dict):

        style = cell.get("style")  # None = no styling

        if style is None:
            return  # normal appearance (fallback)

        if style == "user_input":
            dpg.bind_item_theme(tag, "theme_user_input")

        elif style == "calculated":
            dpg.bind_item_theme(tag, "theme_calculated")
            dpg.configure_item(tag, readonly=True)

        elif style == "output":
            dpg.bind_item_theme(tag, "theme_output")
            dpg.configure_item(tag, readonly=True)


    # -----------------------
    # THEME BUILDERS
    # -----------------------
    def build_title_header_theme(self):
        with dpg.theme(tag=self.header_theme_tag) as theme:
            with dpg.theme_component(dpg.mvText):
                dpg.add_theme_color(dpg.mvThemeCol_Text, self.ctx.styles.TEXT_LIGHT)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4)

                # Optional: background behind the text (requires mvThemeCol_ChildBg or mvThemeCol_WindowBg)
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (40, 40, 40))
        return theme



