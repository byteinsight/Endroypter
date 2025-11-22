import dearpygui.dearpygui as dpg

from modules.irace_sdk.irsdk_formatter import Formatter
from modules.ui.base_panel import BasePanel
from modules.ui.dashboard.session_widget import SessionWidget
from modules.ui.dashboard.weather_widget import WeatherWidget
from modules.ui.dashboard.pitstop_widget import PitStopWidget
from modules.ui.dashboard.tyre_widget import TyreWidget

class DashPanel(BasePanel):
    LABEL = "Dashboard"


    def __init__(self, ctx):
        super().__init__(ctx)
        self.ctx = ctx
        self.format = Formatter(ctx)
        self.root_tag = "dashboard_root"

        self.session_widget = SessionWidget(ctx)
        self.weather_widget = WeatherWidget(ctx)
        self.pit_widget = PitStopWidget(ctx)
        self.tyre_widget = TyreWidget(ctx)

    # -------------------------------------------------------
    # BUILD UI
    # -------------------------------------------------------
    def build(self):
        with dpg.tab(label=self.LABEL, tag=self.root_tag):

            with dpg.group(tag="dashboard_top_section"):
                with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchSame  ):
                    dpg.add_table_column()  # left column
                    dpg.add_table_column()  # right column

                    with dpg.table_row():
                        with dpg.group():
                            self.session_widget.build()

                        with dpg.group():
                            # dpg.add_text("Weather")
                            self.weather_widget.build()
            # Bottom section
            self.pit_widget.build()
            self.tyre_widget.build()


    def update(self, update_data: dict):
        """
        {'SessionID': 278339615, 'SessionNum': 0, 'SessionState': 4, 'SessionTick': 65738, 'SessionTimeOfDay': 55000.0,
        'SessionTime': 100.6433339436849, 'SessionTimeRemain': 79.3566660563151, 'SessionLapsTotal': 32767, 'SessionLapsRemainEx': 32767, 'PlayerCarIdx': 17}
        :param update_data:
        :return:
        """
        try:
            # self.ctx.logger.info(f"Dashboard Panel Updates: {update_data}")

            if update_data.get("session_data") is not None:
                formatted_session_data = self.format_session_data(update_data["session_data"])
                # self.ctx.logger.debug(formatted_session_data)
                self.session_widget.update(formatted_session_data)

            if update_data.get("weather_data") is not None:
                formatted_weather_data = self.format_weather_data(update_data['weather_data'])
                # self.ctx.logger.debug(update_data['weather_data'])
                self.weather_widget.update(formatted_weather_data)

            if update_data.get("pit_data") is not None:

                # Extract pit_data payload
                pit_data = update_data["pit_data"]
                # self.ctx.logger.debug(pit_data)

                # --- PIT STOP MAIN DATA ---
                formatted_pit_data = self.format_pit_stop_data(pit_data)
                self.pit_widget.update(formatted_pit_data)

                # --- TYRE DATA (if available) ---
                tyre_usage = pit_data.get("tyre_usage")
                tyre_events = pit_data.get("tyre_data")  # your LF/RF/LR/RR times dict

                if tyre_usage is not None or tyre_events is not None:
                    formatted_tyre_data = self.format_tyre_data(
                        tyre_usage or {},  # safe: always a dict
                        tyre_events or {}
                    )

                    self.tyre_widget.update(formatted_tyre_data)

        except Exception as error:
            self.ctx.logger.error(f"[DashboardPanel] Update Error: {error}")


    def format_weather_data(self, weather_data):
        formatted = {
            'AirTemp': self.format.get_temp_str(weather_data['AirTemp']),  # 'AirTemp': 28.45831871032715,
            'RelativeHumidity': self.format.make_percent_string(weather_data['RelativeHumidity']),  # 'RelativeHumidity': 0.26265791058540344,
            'TrackTempCrew': self.format.get_temp_str(weather_data['TrackTempCrew']),  #  'TrackTempCrew': 46.111114501953125,
            'AirDensity': self.format.convert_air_density(weather_data['AirDensity']), #  'AirDensity': 1.1515016555786133,
            'AirPressure': self.format.convert_air_pressure_mbar(weather_data['AirPressure'], formatted=True), # 'AirPressure': 100076.2109375,
            'FogLevel': self.format.make_percent_string(weather_data['FogLevel']), #  'FogLevel': 0.0,
            'Skies': self.format.get_sky_type(weather_data['Skies']),  #  'Skies': 0,
            'Precipitation': self.format.make_percent_string(weather_data['Precipitation']),   #  'Precipitation': 0.0,
            'WindDir': self.format.convert_rad_to_degrees(weather_data['WindDir']),  #  'WindDir': 2.8396360874176025,
            'WindVel': self.format.make_speed_string(weather_data['WindVel'], "kph"),  #  'WindVel': 4.038610458374023,
            'TrackWetness': self.format.get_track_wetness(weather_data['TrackWetness']),  #  'TrackWetness': 1,
            'WeatherDeclaredWet': self.format.make_bool(weather_data['WeatherDeclaredWet'])  #  'WeatherDeclaredWet': False,
        }
        return formatted

    def format_session_data(self, session_data):
        formatted = {
            'SessionID': session_data['SessionID'],  # 'SessionID': 278339615,
            'SessionStatus': self.format.get_session_state(session_data['SessionNum'], session_data['SessionState']),  # 'SessionState': 5, 'SessionTick': 525868,
            'SessionTick': self.format.make_int_string(session_data['SessionTick']),  # 'SessionTick': 525988,
            'SessionTimeOfDay': self.format.make_daytime_string('SessionTimeOfDay'),  # 'SessionTimeOfDay': 56142.0,
            'SessionTime': self.format.make_time_string(session_data['SessionTime']),  # 'SessionTime': 342.4133382161458,
            'SessionTimeRemain': self.format.make_time_string(session_data['SessionTimeRemain']),  # 'SessionTimeRemain': 137.5866617838542,
            'SessionLapsTotal': self.format.make_int_string(session_data['SessionLapsTotal']),  # 'SessionLapsTotal': 2,
            'SessionLapsRemainEx': self.format.make_int_string(session_data['SessionLapsRemainEx']),  # 'SessionLapsRemainEx': 0,
            'PlayerCarIdx': self.format.make_int_string(session_data['PlayerCarIdx']),  # 'PlayerCarIdx': 17
        }
        return formatted

    def format_pit_stop_data(self, pit_data):
        f = self.format

        formatted = {
            # --- Core timing fields ---
            'box_in_time': f.make_time_string(pit_data.get('box_in_time', 0.0)),
            'pit_in_time': f.make_time_string(pit_data.get('pit_in_time', 0.0)),
            'service_start_time': f.make_time_string(pit_data.get('service_start_time', 0.0)),
            'service_end_time': f.make_time_string(pit_data.get('service_end_time', 0.0)),
            'pit_out_time': f.make_time_string(pit_data.get('pit_out_time', 0.0)),
            'back_on_track': f.make_time_string(pit_data.get('back_on_track', 0.0)),

            # --- Durations ---
            'service_time': f.make_time_string(pit_data.get('service_time', 0.0)),
            'stop_length': f.make_time_string(pit_data.get('stop_length', 0.0)),
            'total_pit_stop': f.make_time_string(pit_data.get('total_pit_stop', 0.0)),

            # --- Lap ---
            'box_in_lap': f"on lap {f.make_int_string(pit_data.get('box_in_lap', 0))}",

            # --- Repairs ---
            'tow_time': f.make_time_string(pit_data.get('tow_time', 0.0)),
            'repairs': pit_data.get('repairs', 0.0),
            'opt_repairs_max': pit_data.get('opt_repairs_max', 0.0),
            'opt_repairs_remaining': pit_data.get('opt_repairs_remaining', 0.0),

            # --- Fuel ---
            # 'fuel_filling': pit_data.get('fuel_filling', False),
            'fuel_start_time': f.make_time_string(pit_data.get('fuel_start_time', 0.0)),
            'fuel_start_level': pit_data.get('fuel_start_level', 0.0),
            'fuel_end_time': f.make_time_string(pit_data.get('fuel_end_time', 0.0)),
            'fuel_end_level': pit_data.get('fuel_end_level', 0.0),
            'fuel_fill_time': f.make_time_string(pit_data.get('fuel_fill_time', 0.0)),
            'fuel_fill_amount': pit_data.get('fuel_fill_amount', 0.0),
            'fuel_per_sec': pit_data.get('fuel_per_sec', 0.0),

            # --- Tyre process ---
            # 'tyres_changing': pit_data.get('tyres_changing', False),
            'tyres_start_time': f.make_time_string(pit_data.get('tyres_start_time', 0.0)),
            'tyres_finish_time': f.make_time_string(pit_data.get('tyres_finish_time', 0.0)),
            'tyre_change_time': f.make_time_string(pit_data.get('tyre_change_time', 0.0)),
            'litres_over_tyres': pit_data.get('litres_over_tyres', 0.0),

            # --- Jacks ---
            # 'on_jacks': pit_data.get('on_jacks', False),
            'on_jacks_time': f.make_time_string(pit_data.get('on_jacks_time', 0.0)),
            'off_jacks_time': f.make_time_string(pit_data.get('off_jacks_time', 0.0)),
            'total_jack_time': f.make_time_string(pit_data.get('off_jacks_time', 0.0)),

        }

        return formatted

    def format_tyre_data(self, tyre_usage: dict, tyre_data: dict):
        """
        Convert raw iRacing tyre usage and tyre timestamp data into
        formatted values matching the UI tag naming convention.
        """

        f = self.format
        formatted = {}

        # ------------------------------------------
        # 1. Map tyre_usage keys to formatted names
        # ------------------------------------------
        for key, value in tyre_usage.items():

            # Temperature keys: LFtempCL → LF_temp_CL
            if "temp" in key:
                # Split “LFtempCL” into “LF”, “CL”
                tyre = key[:2]  # LF, RF, LR, RR
                suffix = key.replace(tyre + "temp", "")  # CL, CM, CR

                ui_key = f"{tyre}_temp_{suffix}"
                formatted[ui_key] = f.get_temp_str(value)
                continue

            # Wear keys: LFwearL → LF_wear_L
            if "wear" in key:
                tyre = key[:2]  # LF, RF, LR, RR
                suffix = key.replace(tyre + "wear", "")  # L, M, R

                ui_key = f"{tyre}_wear_{suffix}"
                formatted[ui_key] = f.make_percent_string(value)
                continue

            # If something unexpected appears, pass raw value through:
            formatted[key] = value

        # ------------------------------------------
        # 2. Map tyre_data timestamps to LF_time, RF_time...
        # ------------------------------------------
        for key, value in tyre_data.items():
            tyre = key  # LF, RF, LR, RR
            ui_key = f"{tyre}_time"

            formatted[ui_key] = f.make_time_string(value)

        return formatted

