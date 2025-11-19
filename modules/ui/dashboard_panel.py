import dearpygui.dearpygui as dpg

from modules.irace_sdk.irsdk_formatter import Formatter
from modules.ui.base_panel import BasePanel


class DashPanel(BasePanel):
    LABEL = "Dashboard"


    def __init__(self, ctx):
        super().__init__(ctx)
        self.ctx = ctx
        self.format = Formatter(ctx)

    # -------------------------------------------------------
    # BUILD UI
    # -------------------------------------------------------
    def build(self):
        with dpg.group(horizontal=True):
            dpg.add_text("SessionID", tag="SessionID")
            dpg.add_text("SessionNum", tag="SessionNum")

    def update(self, update_data: dict):
        """
        {'SessionID': 278339615, 'SessionNum': 0, 'SessionState': 4, 'SessionTick': 65738, 'SessionTimeOfDay': 55000.0,
        'SessionTime': 100.6433339436849, 'SessionTimeRemain': 79.3566660563151, 'SessionLapsTotal': 32767, 'SessionLapsRemainEx': 32767, 'PlayerCarIdx': 17}
        :param update_data:
        :return:
        """
        if update_data['session_data'] is not None:

            SessionNum = update_data['session_data']['SessionNum']
            SessionState = update_data['session_data']['SessionState']

            dpg.set_value("SessionID", f"SessionID: {update_data['session_data']['SessionID']}.")
            dpg.set_value("SessionNum", f"SessionNum & State: {self.format.get_session_state(SessionNum, SessionState)}.")



