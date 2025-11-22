import dearpygui.dearpygui as dpg

from modules.irace_sdk.irsdk_formatter import Formatter
from modules.ui.base_panel import BasePanel
from modules.ui.info.track_geometry_widget import TrackGeometryWidget
from modules.ui.info.track_identity_widget import TrackIdentityWidget
from modules.ui.info.track_location_widget import TrackLocationWidget
from modules.ui.info.track_weather_widget import TrackWeatherWidget
from modules.ui.info.weekend_widget import WeekendWidget

class InfoPanel(BasePanel):
    LABEL = "Information"


    def __init__(self, ctx):
        super().__init__(ctx)
        self.ctx = ctx
        self.format = Formatter(ctx)
        self.root_tag = "info_root"

        self.track_geometry_widget = TrackGeometryWidget(ctx)
        self.track_identity_widget = TrackIdentityWidget(ctx)
        self.track_location_widget = TrackLocationWidget(ctx)
        self.track_weather_widget = TrackWeatherWidget(ctx)
        self.weekend_widget = WeekendWidget(ctx)

    # -------------------------------------------------------
    # BUILD UI
    # -------------------------------------------------------
    def build(self):
        with dpg.tab(label=self.LABEL, tag=self.root_tag):

            with dpg.group(tag="info_top_section"):
                self.track_identity_widget.build()
                self.track_geometry_widget.build()
                self.track_location_widget.build()
                self.track_weather_widget.build()
                self.weekend_widget.build()


    def update(self, update_data: dict):
        """
        {'SessionID': 278339615, 'SessionNum': 0, 'SessionState': 4, 'SessionTick': 65738, 'SessionTimeOfDay': 55000.0,
        'SessionTime': 100.6433339436849, 'SessionTimeRemain': 79.3566660563151, 'SessionLapsTotal': 32767, 'SessionLapsRemainEx': 32767, 'PlayerCarIdx': 17}
        :param update_data:
        :return:
        """
        try:
            # self.ctx.logger.info(f"InfoPanel Updates: {update_data}")
            formatted_session_data = self.format_weekend_data(update_data)

            if formatted_session_data.get("identity") is not None:
                # self.ctx.logger.debug(formatted_session_data["identity"])
                self.track_identity_widget.update(formatted_session_data["identity"])

            if formatted_session_data.get("location") is not None:
                # self.ctx.logger.debug(formatted_session_data["location"])
                self.track_location_widget.update(formatted_session_data["location"])

            if formatted_session_data.get("geometry") is not None:
                # self.ctx.logger.debug(formatted_session_data["geometry"])
                self.track_geometry_widget.update(formatted_session_data["geometry"])

            if formatted_session_data.get("weather") is not None:
                # self.ctx.logger.debug(formatted_session_data["weather"])
                self.track_weather_widget.update(formatted_session_data["weather"])

            if formatted_session_data.get("options") is not None:
                # self.ctx.logger.debug(f"Update Weekend: {formatted_session_data['options']}")
                self.weekend_widget.update(formatted_session_data["options"])


        except Exception as error:
            self.ctx.logger.error(f"[Info] Update Error: {error}")

    @staticmethod
    def format_weekend_data(data):

        info = data['info']
        options = data['options']

        # ---------- IDENTITY ----------
        identity = {
            'TrackName': info['TrackName'],
            'TrackDisplayName': info['TrackDisplayName'],
            'TrackDisplayShortName': info['TrackDisplayShortName'],
            'TrackConfigName': info['TrackConfigName'],
            'TrackType': info['TrackType'],
        }

        # ---------- LOCATION ----------
        location = {
            'TrackCity': info['TrackCity'],
            'TrackCountry': info['TrackCountry'],
            'TrackLatitude': info['TrackLatitude'],
            'TrackLongitude': info['TrackLongitude'],
            'TrackAltitudeM': info['TrackAltitudeM'],
            'TrackNorthOffsetRad': info['TrackNorthOffsetRad'],
        }

        # ---------- GEOMETRY ----------
        geometry = {
            'TrackLengthKM': info['TrackLengthKM'],
            'TrackNumTurns': info['TrackNumTurns'],
            'TrackPitSpeedLimitKPH': info['TrackPitSpeedLimitKPH'],

            # Your original geometry block included these two
            # so I kept them here:
            'TrackCleanup': info['TrackCleanup'],
            'TrackDynamicTrack': info['TrackDynamicTrack'],
        }

        # ---------- WEATHER ----------
        weather = {
            'TrackWeatherType': info['TrackWeatherType'],
            'TrackSkies': info['TrackSkies'],
            'TrackSurfaceTempC': info['TrackSurfaceTempC'],
            'TrackAirTempC': info['TrackAirTempC'],
            'TrackAirPressureHg': info['TrackAirPressureHg'],
            'TrackRelativeHumidityPct': info['TrackRelativeHumidityPct'],
            'TrackFogLevelPct': info['TrackFogLevelPct'],
            'TrackWindVelMS': info['TrackWindVelMS'],
            'TrackWindDirRad': info['TrackWindDirRad'],
        }

        options = {
            'NumStarters': options['NumStarters'],
            'StartingGrid': options['StartingGrid'],
            'QualifyScoring': options['QualifyScoring'],
            'CourseCautions': options['CourseCautions'],
            'StandingStart': options['StandingStart'],
            'Restarts': options['Restarts'],
            'WeatherType': options['WeatherType'],
            'Skies': options['Skies'],
            'WindDirection': options['WindDirection'],
            'WindSpeed': options['WindSpeed'],
            'WeatherTemp': options['WeatherTemp'],
            'RelativeHumidity': options['RelativeHumidity'],
            'FogLevel': options['FogLevel'],
            'Unofficial': options['Unofficial'],
            'CommercialMode': options['CommercialMode'],
            'NightMode': options['NightMode'],
            'IsFixedSetup': options['IsFixedSetup'],
            'StrictLapsChecking': options['StrictLapsChecking'],
            'HasOpenRegistration': options['HasOpenRegistration'],
        }

        return {
            'identity': identity,
            'location': location,
            'geometry': geometry,
            'weather': weather,
            'options': options
        }




