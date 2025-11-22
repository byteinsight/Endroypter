import dearpygui.dearpygui as dpg
from modules.ui.base_panel import BasePanel


# -------------------------------------------------------------
# SIMPLE MARKDOWN → DEAR PYGUI RENDERER
# -------------------------------------------------------------
def render_markdown(path, parent):
    """
    Lightweight Markdown → DPG renderer with 3 heading levels.
    Updated to use add_spacer() instead of deprecated add_spacing().
    """

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        dpg.add_text("Help file not found.", parent=parent, color=(255, 100, 100))
        return

    for line in lines:
        stripped = line.rstrip()

        # Blank line → vertical spacing
        if not stripped:
            dpg.add_spacer(parent=parent)
            continue

        # -------------------------------------------------------------
        # HEADING LEVEL 1 (# )
        # -------------------------------------------------------------
        if stripped.startswith("# "):
            dpg.add_text(
                stripped[2:],
                parent=parent,
                color=(255, 220, 0)
            )
            dpg.add_spacer(parent=parent)
            continue

        # -------------------------------------------------------------
        # HEADING LEVEL 2 (## )
        # -------------------------------------------------------------
        if stripped.startswith("## "):
            dpg.add_text(
                stripped[3:],
                parent=parent,
                color=(200, 200, 255)
            )
            dpg.add_spacer(parent=parent)
            continue

        # -------------------------------------------------------------
        # HEADING LEVEL 3 (### )
        # -------------------------------------------------------------
        if stripped.startswith("### "):
            dpg.add_text(
                stripped[4:],
                parent=parent,
                indent=10,
                color=(180, 180, 180)
            )
            continue

        # -------------------------------------------------------------
        # LIST ITEM
        # -------------------------------------------------------------
        if stripped.startswith("- "):
            dpg.add_text("• " + stripped[2:], parent=parent, indent=20)
            continue

        # -------------------------------------------------------------
        # SEPARATOR
        # -------------------------------------------------------------
        if stripped == "---":
            dpg.add_separator(parent=parent)
            continue

        # -------------------------------------------------------------
        # PARAGRAPH
        # -------------------------------------------------------------
        dpg.add_text(stripped, parent=parent)




# -------------------------------------------------------------
# HELP PANEL
# -------------------------------------------------------------
class HelpPanel(BasePanel):
    LABEL = "Help"
    root_tag = "help_panel"
    HELP_FILE = "README.md"   # <- Change this as needed

    def __init__(self, ctx):
        super().__init__(ctx)
        self.ctx = ctx

    def build(self):
        dpg.add_text("Help & Documentation")
        dpg.add_separator()

        with dpg.child_window(border=False, autosize_x=True, height=600):
            container = dpg.last_item()
            render_markdown(self.HELP_FILE, container)
