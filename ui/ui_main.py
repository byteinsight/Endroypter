# main_ui.py
import dearpygui.dearpygui as dpg

from ui.help_panel import HelpPanel
from ui.settings import SettingsPanel
from ui.timing_panel import TimingPanel
from ui.crewchief_panel import CrewChiefPanel

class UIMain:

    def __init__(self):
        self.panels = [
            CrewChiefPanel(),
            TimingPanel(),
            SettingsPanel(),
            HelpPanel(),
        ]

    def build(self):
        with dpg.window(
            tag="main_window",
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            no_collapse=True,
            no_close=True
        ):
            with dpg.tab_bar():
                for panel in self.panels:
                    with dpg.tab(label=panel.label, tag=panel.label.lower()):
                        panel.build()
