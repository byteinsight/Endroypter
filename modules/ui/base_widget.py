import dearpygui.dearpygui as dpg

class BaseWidget:
    """
    Generic base widget for any DearPyGui UI component that:

    - Provides tag namespacing via prefix
    - Defines build() -> root_tag
    - Supports update(data_dict or kwargs)
    - Handles theming and post-build binding
    - Adds helper APIs for label/value tag generation

    Subclasses must implement:
        _build()
    Optionally override:
        build_themes()
        apply_themes()
        update()
    """

    LABEL = None        # Optional text header
    TAG = None          # Required: base tag for widget

    header_tag = None
    header_container = None
    header_value_key = None
    header_value_tag = None

    header_theme = "section_label_theme"
    input_label_theme = "input_label_theme"
    section_label_theme = "section_label_theme"

    def __init__(self, ctx, prefix=None, show_header=True):
        self.ctx = ctx
        self.prefix = prefix
        self.show_header = show_header

        # Widget namespace (already present)
        self.section_tag = f"{prefix}_{self.TAG}" if prefix else self.TAG

        # Theme namespace (new)
        self.theme_tag = f"{self.section_tag}_theme"

        # Table namespace (new)
        self.table_tag = f"{self.section_tag}_table"

        # Optional: create a dict for any sub-tags you may want
        self.tags = {}
        self.label_tags = []

        # Store theme handles (subclasses fill these)
        self.themes = {}

    # -----------------------
    # Main Build Entry Point
    # -----------------------
    def build(self):
        """
        Build wrapper that handles:
        - optional header
        - the main widget body via _build()
        - theme generation
        - theme binding
        """

        if self.show_header and self.LABEL:

            # container for static + dynamic header elements
            self.header_container = f"{self.section_tag}_header_container"
            with dpg.group(horizontal=True, tag=self.header_container):
                # Left: static label
                self.header_tag = f"{self.section_tag}_header"
                dpg.add_text(self.LABEL, tag=self.header_tag)

                # Right: dynamic value (optional, hidden initially)
                self.header_value_tag = f"{self.section_tag}_header_value"
                dpg.add_text("", tag=self.header_value_tag, show=False)

            # Bind header theme
            dpg.bind_item_theme(self.header_tag, self.header_theme)
            dpg.bind_item_font(self.header_tag, self.ctx.font_manager.title)
            dpg.bind_item_theme(self.header_value_tag, self.header_theme)
            dpg.bind_item_font(self.header_value_tag, self.ctx.font_manager.title)

        # Build actual widget layout
        self.inner_build()

        # Apply themes (subclasses may override)
        self.apply_themes()

        self.ctx.logger.info(f"Header prepared with header_value_tag:{self.header_value_tag}; and header_value_key: {self.header_value_key}")

        return self.section_tag

    # -----------------------
    # Methods subclasses implement
    # -----------------------
    def inner_build(self):
        """Subclasses create DearPyGui widgets here."""
        raise NotImplementedError

    # -----------------------
    # Table Cell Builders
    # -----------------------
    def get_vertical_table_cell(self, label: str, key: str, width: int = -1):
        """Create a vertical cell consisting of a label and an input field.

        Parameters
        ----------
        label : str
            The label text to display.
        key : str
            Key into self.weather_tags (e.g., "AirTemp", "RelativeHumidity").
        width : int
            Width of the input widget. Defaults to -1 for auto-stretch.
        """
        tag = self.tags[key]
        label_tag = self.label_for(tag)

        with dpg.group():
            dpg.add_text(f"{label}", tag=label_tag)
            dpg.add_input_text(tag=tag, default_value="---", readonly=True, width=width)

    def get_label_table_cell(self, label: str, key: str):
        """
        Creates a standalone label cell. The key is treated as the base tag
        for this table cell (no lookup inside self.tags).
        """
        label_tag = f"{key}_label"
        self.label_tags.append(label_tag)

        with dpg.group():
            dpg.add_text(label, tag=label_tag)

        return label_tag

    def get_value_table_cell(self, key: str, width: int = -1):
        value_tag = self.tags[key]

        with dpg.group():
            dpg.add_input_text(
                tag=value_tag,
                default_value="---",
                readonly=True,
                width=width
            )

        return value_tag


    # -----------------------
    # UPDATE METHOD
    # -----------------------
    def update(self, formatted_data: dict):
        # 1. Standard tag updates (unchanged)
        for key, tag in self.tags.items():
            if key not in formatted_data:
                continue
            if not dpg.does_item_exist(tag):
                # self.ctx.logger.error(f"Missing widget value tag: {tag} for {formatted_data[key]}.")
                continue
            dpg.set_value(tag, formatted_data[key])

        # 2. Optional dynamic header update
        if self.header_value_key and self.header_value_key in formatted_data:
            # self.ctx.logger.error(f"Found Header Value Key: {self.header_value_key} for {formatted_data[self.header_value_key]}.")
            self.update_header_value(formatted_data[self.header_value_key])

    def update_header_value(self, value: str | None):
        """
        Update the dynamic header value next to the main label.
        Pass None or empty string to hide it.
        """
        if not hasattr(self, "header_value_tag"):
            return

        if value:
            # self.ctx.logger.info(f"Updating Header Tag: {self.header_value_tag} with Value: {value}")
            dpg.set_value(self.header_value_tag, f"  {value}")  # spacing prefix
            dpg.configure_item(self.header_value_tag, show=True)
        else:
            dpg.configure_item(self.header_value_tag, show=False)

    # -----------------------
    # Optional theme system
    # -----------------------
    def apply_themes(self):
        """Apply section, label, and value themes for all tag entries."""

        # 1. Bind the section background/theme
        if hasattr(self, "section_tag"):
            dpg.bind_item_theme(self.section_tag, self.section_label_theme)
            dpg.bind_item_font(self.section_tag, self.ctx.font_manager.title)

        # 2. Apply label theme + fonts for each tag
        for field_tag in self.tags.values():
            label_tag = self.label_for(field_tag)
            if not dpg.does_item_exist(label_tag):
                # self.ctx.logger.error(f"Missing widget label tag: {label_tag}")
                continue
            dpg.bind_item_theme(label_tag, self.input_label_theme)
            dpg.bind_item_font(label_tag, self.ctx.font_manager.input_label)

        # 3. Apply value theme
        for field_tag in self.tags.values():
            if not dpg.does_item_exist(field_tag):
                # self.ctx.logger.error(f"Missing widget value tag: {field_tag}")
                continue
            dpg.bind_item_theme(field_tag, "output_cell_theme")
            dpg.bind_item_font(field_tag, self.ctx.font_manager.default_font)

        # 4. Apply label-only themes (table labels, headers, or standalone labels)
        for label_tag in self.label_tags:

            if not dpg.does_item_exist(label_tag):
                # self.ctx.logger.error(f"Missing solo label widget: {label_tag}")
                continue

            dpg.bind_item_theme(label_tag, self.input_label_theme)
            dpg.bind_item_font(label_tag, self.ctx.font_manager.input_label)


    # -----------------------
    # Helper functions
    # -----------------------
    @staticmethod
    def label_for(tag):
        """Return tag for the label associated with this widget."""
        return f"{tag}_label"
