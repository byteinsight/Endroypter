import irsdk
from time import time

from modules.core.app_context import AppContext
from modules.irace_sdk.irsdk_pitcrew import PitCrew
from modules.irace_sdk.irsdk_constants import IrConstants

class IRState:
    ir_connected = False
    last_car_setup_tick = -1


class IRSDKService:

    throttle = {
        "session": {"last": 0, "cooldown": 30.0},
        "drivers": {"last": 0, "cooldown": 30.0},
        "weekend": {"last": 0, "cooldown": 60.0},
        "weather": {"last": 0, "cooldown": 30.0},
    }
    last_session_tick = None
    session_tracker = None

    timing_data = None
    session_data = None
    driver_data = None
    weather_data = None
    pit_data = None
    weekend_data = None

    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.constants = IrConstants()
        self.pitcrew = PitCrew(ctx)
        # Initialize both the ir connection and a state object used to track availability of data.
        self.ir = irsdk.IRSDK()
        self.state = IRState()

    def check_sim_connection(self):
        # still connected?
        if self.state.ir_connected:
            if not (self.ir.is_initialized and self.ir.is_connected):
                self.ctx.logger.debug("IRSDK Disconnected")
                self.state.ir_connected = False
                self.state.last_car_setup_tick = -1
                self.ir.shutdown()
            return

        # currently NOT connected → try to connect
        if self.ir.startup() and self.ir.is_initialized and self.ir.is_connected:
            self.ctx.logger.debug("IRSDK Connected.\n")
            self.state.ir_connected = True

    def detect_session_changes(self):
        """
        Detects changes to SessionID, SessionNum, and SessionState.
        Returns a dict describing what changed so the caller
        can decide which subsystems to refresh.
        """
        changes = {}

        # Read current values
        sid = self.ir["WeekendInfo"]["SessionID"]
        snum = self.ir["SessionNum"]
        sstate = self.ir["SessionState"]
        # self.ctx.logger.debug(f"DSC: sid:{sid}; snum:{snum}; sstate:{sstate}")

        # Initialise tracking store on first call OR if reset/None
        if not hasattr(self, "session_tracker") or self.session_tracker is None:
            self.session_tracker = {
                "SessionID": sid,
                "SessionNum": snum,
                "SessionState": sstate
            }
            return changes  # First call → no changes reported

        last = self.session_tracker

        # Detect server change
        if sid != last["SessionID"]:
            changes["server_changed"] = True

        # Detect P→Q→R change
        if snum != last["SessionNum"]:
            changes["session_phase_changed"] = True

        # Detect state transitions (e.g. warmup → racing)
        if sstate != last["SessionState"]:
            changes["state_changed"] = True

        # Save new values
        self.session_tracker = {
            "SessionID": sid,
            "SessionNum": snum,
            "SessionState": sstate
        }

        return changes

    def is_throttled(self, key: str) -> bool:
        """
        Determine whether the specified throttle key is still under its cooldown period.

        This method checks the last recorded update timestamp for the given key and
        compares it against the configured cooldown window. If the cooldown has not
        elapsed, it returns True (meaning the caller should skip its update). If the
        cooldown has expired, the method updates the timestamp and returns False.

        Args:
            key (str): Identifier for the subsystem being throttled
                       (e.g., "weather", "session", "track").

        Returns:
            bool: True if the key is still within its cooldown period,
                  False if an update should proceed.
        """
        now = time()  # Current timestamp
        entry = self.throttle.get(key)  # Fetch throttle record

        # Create default throttle entry if missing
        if entry is None:
            self.throttle[key] = {"last": 0, "cooldown": 1.0}  # Default 1s cooldown
            entry = self.throttle[key]

        # If cooldown window has not expired, skip update
        if now - entry["last"] < entry["cooldown"]:
            return True

        # Cooldown expired → update timestamp and allow update
        entry["last"] = now
        return False

    def get_update(self):
        """
        This is the entry point into the wrapper.
        We check the SDK connection and freeze buffer with live telemetry.
        We then gather and calculate data based on the car's position on track
        :return Boolean: Returns a dict of booleans:
        """

        available_updates = {
            "timing": False,
            "weather": False,
            "session": False,
            "weekend": False,
            "pitstop": False,
        }

        self.check_sim_connection()
        if not self.state.ir_connected:
            # self.ctx.logger.debug('IRSDK Not Connected')
            return available_updates

        # This is so we get consistent data from inside that tick
        # and the data isn't updated by apis inbetween calls.
        self.ir.freeze_var_buffer_latest()

        # This method has no throttling attached to it
        available_updates["timing"] = self.get_timing_data_fast()

        available_updates['pitstop'] = self.get_pit_stop_data_fast()

        # Detect changes across SessionID, SessionNum, SessionState
        session_changes = self.detect_session_changes()

        # Server changed → reload EVERYTHING
        if "server_changed" in session_changes:
            available_updates["session"] = self.update_session_status()
            available_updates["weather"] = self.update_weather_data()
            # self.update_track_info()
            # self.update_driver_roster()

        # SessionNum changed (P→Q→R) → reload session metadata
        elif "session_phase_changed" in session_changes:
            available_updates["session"] = self.update_session_status()
            available_updates["weather"] = self.update_weather_data()
            # self.update_driver_roster()

        # SessionState changed (Warmup→Racing→Checkered) → update only what depends on state
        elif "state_changed" in session_changes:
            available_updates["session"] = self.update_session_status()
            available_updates["weather"] = self.update_weather_data()

        # These are throttled updates and if called via tracked changes the last call is updated.
        # So these updates get skipped internally to avoid duplication
        available_updates["session"] = self.update_session_status()
        available_updates["drivers"] = self.update_driver_data()
        available_updates["weather"] = self.update_weather_data()
        available_updates["weekend"] = self.update_weekend_data()

        return available_updates

    def update_weekend_data(self):
        if self.is_throttled("weekend"):
            return False

        self.weekend_data = {
            'info': {
                "TrackName": self.ir["WeekendInfo"]["TrackName"],
                "TrackID": self.ir["WeekendInfo"]["TrackID"],
                "TrackLengthKM": self.ir["WeekendInfo"]["TrackLength"],
                "TrackDisplayName": self.ir["WeekendInfo"]["TrackDisplayName"],
                "TrackDisplayShortName": self.ir["WeekendInfo"]["TrackDisplayShortName"],
                "TrackConfigName": self.ir["WeekendInfo"]["TrackConfigName"],
                "TrackCity": self.ir["WeekendInfo"]["TrackCity"],
                "TrackCountry": self.ir["WeekendInfo"]["TrackCountry"],
                "TrackAltitudeM": self.ir["WeekendInfo"]["TrackAltitude"],
                "TrackLatitude": self.ir["WeekendInfo"]["TrackLatitude"],
                "TrackLongitude": self.ir["WeekendInfo"]["TrackLongitude"],
                "TrackNorthOffsetRad": self.ir["WeekendInfo"]["TrackNorthOffset"],
                "TrackNumTurns": self.ir["WeekendInfo"]["TrackNumTurns"],
                "TrackPitSpeedLimitKPH": self.ir["WeekendInfo"]["TrackPitSpeedLimit"],
                "TrackType": self.ir["WeekendInfo"]["TrackType"],
                "TrackWeatherType": self.ir["WeekendInfo"]["TrackWeatherType"],
                "TrackSkies": self.ir["WeekendInfo"]["TrackSkies"],
                "TrackSurfaceTempC": self.ir["WeekendInfo"]["TrackSurfaceTemp"],
                "TrackAirTempC": self.ir["WeekendInfo"]["TrackAirTemp"],
                "TrackAirPressureHg": self.ir["WeekendInfo"]["TrackAirPressure"],
                "TrackWindVelMS": self.ir["WeekendInfo"]["TrackWindVel"],
                "TrackWindDirRad": self.ir["WeekendInfo"]["TrackWindDir"],
                "TrackRelativeHumidityPct": self.ir["WeekendInfo"]["TrackRelativeHumidity"],
                "TrackFogLevelPct": self.ir["WeekendInfo"]["TrackFogLevel"],
                "TrackCleanup": self.ir["WeekendInfo"]["TrackCleanup"],
                "TrackDynamicTrack": self.ir["WeekendInfo"]["TrackDynamicTrack"],
            },
            'options': {
                "NumStarters": self.ir["WeekendInfo"]["WeekendOptions"]["NumStarters"],
                "StartingGrid": self.ir["WeekendInfo"]["WeekendOptions"]["StartingGrid"],
                "QualifyScoring": self.ir["WeekendInfo"]["WeekendOptions"]["QualifyScoring"],
                "CourseCautions": self.ir["WeekendInfo"]["WeekendOptions"]["CourseCautions"],
                "StandingStart": self.ir["WeekendInfo"]["WeekendOptions"]["StandingStart"],
                "Restarts": self.ir["WeekendInfo"]["WeekendOptions"]["Restarts"],
                "WeatherType": self.ir["WeekendInfo"]["WeekendOptions"]["WeatherType"],
                "Skies": self.ir["WeekendInfo"]["WeekendOptions"]["Skies"],
                "WindDirection": self.ir["WeekendInfo"]["WeekendOptions"]["WindDirection"],
                "WindSpeed": self.ir["WeekendInfo"]["WeekendOptions"]["WindSpeed"],
                "WeatherTemp": self.ir["WeekendInfo"]["WeekendOptions"]["WeatherTemp"],
                "RelativeHumidity": self.ir["WeekendInfo"]["WeekendOptions"]["RelativeHumidity"],
                "FogLevel": self.ir["WeekendInfo"]["WeekendOptions"]["FogLevel"],
                "Unofficial": self.ir["WeekendInfo"]["WeekendOptions"]["Unofficial"],
                "CommercialMode": self.ir["WeekendInfo"]["WeekendOptions"]["CommercialMode"],
                "NightMode": self.ir["WeekendInfo"]["WeekendOptions"]["NightMode"],
                "IsFixedSetup": self.ir["WeekendInfo"]["WeekendOptions"]["IsFixedSetup"],
                "StrictLapsChecking": self.ir["WeekendInfo"]["WeekendOptions"]["StrictLapsChecking"],
                "HasOpenRegistration": self.ir["WeekendInfo"]["WeekendOptions"]["HasOpenRegistration"],
            }
        }

        return True

    def get_player_car_idx(self):
        return self.session_data['PlayerCarIdx'] or self.ir['PlayerCarIdx'] or None

    def get_timing_data_fast(self):
        """
        Only update timing if SessionTick has advanced.
        Returns True if timing data was updated this tick.
        """
        tick = self.ir["SessionTick"]

        # If tick is None (loading, switching sessions), skip
        if tick is None:
            return False

        # If this is the first tick, initialise and return False
        if self.last_session_tick is None:
            self.last_session_tick = tick
            return False

        # If tick has NOT changed → no new data → skip
        if tick == self.last_session_tick:
            return False

        # tick changed → new physics frame
        self.last_session_tick = tick

        # Pull timing data fresh for this frame
        self.timing_data = {
            'CarIdxPosition': self.ir['CarIdxPosition'],  # Cars position in race by car index,
            'CarIdxClassPosition': self.ir['CarIdxClassPosition'],  # Cars class position in race by car index,
            'CarIdxLap': self.ir['CarIdxLap'],  # Laps completed count
            'CarIdxLastLapTime': self.ir['CarIdxLastLapTime'],
            'CarIdxF2Time': self.ir['CarIdxF2Time'],
            'CarIdxTrackSurface': self.ir['CarIdxTrackSurface'],
            'CarIdxOnPitRoad': self.ir['CarIdxOnPitRoad'],
        }
        return True

    def update_session_status(self):
        """
        Get Session Data gets data specific to the session but src the Player Car Index for accessing IDX.
        :return:
        """
        if self.is_throttled("session"):
            return False

        self.session_data = {
            'SessionID': self.ir['WeekendInfo']['SessionID'],
            'SessionNum': self.ir['SessionNum'],  # Session number
            'SessionState': self.ir['SessionState'],  # Session state, irsdk_SessionState
            'SessionTick': self.ir['SessionTick'],  # Current update number
            'SessionTimeOfDay': self.ir['SessionTimeOfDay'],  # Time of day in seconds
            'SessionTime': self.ir['SessionTime'],  # Seconds since session start
            'SessionTimeRemain': self.ir['SessionTimeRemain'],  # Seconds left till session ends
            'SessionLapsTotal': self.ir['SessionLapsTotal'],  # Total number of laps in.
            'SessionLapsRemainEx': self.ir['SessionLapsRemainEx'],  # New improved laps left till session ends
            'PlayerCarIdx': self.ir['PlayerCarIdx'],  # PlayerCarIdx
        }
        return True

    def update_driver_data(self):
        """
        Pulls DriverInfo from the iRacing SDK and builds a drivers dictionary
        indexed by CarIdx. Safe to call repeatedly; throttling prevents overload.
        """
        if self.is_throttled("drivers"):
            return False

        try:
            di = self.ir['DriverInfo']
            drivers = di.get('Drivers', [])

            driver_dict = {}

            for d in drivers:
                idx = d.get("CarIdx")
                if idx is None:
                    continue

                driver_dict[idx] = {
                    # Core identity
                    "CarIdx": idx,
                    "UserName": d.get("UserName"),
                    "AbbrevName": d.get("AbbrevName"),
                    "Initials": d.get("Initials"),
                    "UserID": d.get("UserID"),

                    # Car
                    "CarNumber": d.get("CarNumber"),
                    "CarNumberRaw": d.get("CarNumberRaw"),
                    "CarPath": d.get("CarPath"),
                    "CarScreenNameShort": d.get("CarScreenNameShort"),
                    "CarClassID": d.get("CarClassID"),
                    "CarID": d.get("CarID"),

                    # Competitive
                    "IRating": d.get("IRating"),
                    "LicString": d.get("LicString"),
                    "LicColor": d.get("LicColor"),
                    "CurDriverIncidentCount": d.get("CurDriverIncidentCount"),

                    # Team
                    "TeamName": d.get("TeamName"),
                    "TeamID": d.get("TeamID"),

                    # Status flags
                    "CarIsAI": d.get("CarIsAI"),
                    "IsSpectator": d.get("IsSpectator"),


                }

            # Store for later usage by timing table, overlays, strategy, etc.
            self.driver_data = driver_dict
            # self.ctx.logger.info(f"Updated driver info: {self.driver_data}")
            return True

        except Exception as error:
            self.ctx.logger.error(f"Driver data update failed: {error}")
            return False

    def update_weather_data(self):
        if self.is_throttled("weather"):
            return False

        self.weather_data = {
            'CustID': 12345,  # self.app_context.config.user.IRACE_CUSTID,
            'SessionID': self.ir['WeekendInfo']['SessionID'],
            'AirTemp': self.ir['AirTemp'],  # Temperature of air at start/finish line (C)
            'RelativeHumidity': self.ir['RelativeHumidity'],  # Relative Humidity (%age)
            'TrackTempCrew': self.ir['TrackTempCrew'],  # Temperature of track measured by crew around track (C)
            'AirDensity': self.ir['AirDensity'],  # Density of air at start/finish line (kg/m^3)
            'AirPressure': self.ir['AirPressure'],  # Pressure of air at start/finish line (Pa)
            'FogLevel': self.ir['FogLevel'],  # Fog Level at Start Finish Line (%age)
            'Skies': self.ir['Skies'],  # Skies (0=clear/1=p cloudy/2=m cloudy/3=overcast)
            'Precipitation': self.ir['Precipitation'],  # Precipitation at start/finish line (%age)
            'WindDir': self.ir['WindDir'],  # Wind direction at start/finish line (rad)
            'WindVel': self.ir['WindVel'],  # Wind velocity at start/finish line (m/s)
            'TrackWetness': self.ir['TrackWetness'],  # How wet is the average track surface, irsdk_TrackWetness
            'WeatherDeclaredWet': self.ir['WeatherDeclaredWet']  # The steward says rain tires can be used
            # Sun Set Time.
        }
        return True

    def get_pit_stop_data_fast(self):
        player_car_idx = self.ir['PlayerCarIdx']

        # Enable test mode for replays in debug mode.
        self.pitcrew.set_test_mode(self.ir['IsReplayPlaying'] and self.ctx.settings.get('debug', False))

        updated = self.pitcrew.update(
            surface=self.ir['CarIdxTrackSurface'][player_car_idx],
            on_pit_road=self.ir['OnPitRoad'],
            car_idx_on_pit_road=self.ir['CarIdxOnPitRoad'][player_car_idx],
            pitstop_active=self.ir['PitstopActive'],
            sv_status=self.ir['PlayerCarPitSvStatus'],
            session_time = self.ir['SessionTime'],
            car_idx_lap = self.ir['CarIdxLap'][player_car_idx],
            sv_flags = self.ir['PitSvFlags'],
            fuel_level = self.ir['FuelLevel'],
            tow_time = self.ir['PlayerCarTowTime'],
            repairs = self.ir['PitRepairLeft'],
            opt_repairs = self.ir['PitOptRepairLeft'],
            velocity_z = self.ir['VelocityZ']
        )

        if updated:
            self.pit_data = self.pitcrew.get_completed_pit_report()
            self.pit_data['tyre_usage'] = self.get_tyre_report()

        return updated

    def get_tyre_report(self):
        # Add the tyre wear & temps from the Pit Stop
        return {
            'LFtempCL': self.ir['LFtempCL'], 'LFtempCM': self.ir['LFtempCM'], 'LFtempCR': self.ir['LFtempCR'],
            'LFwearL': self.ir['LFwearL'], 'LFwearM': self.ir['LFwearM'], 'LFwearR': self.ir['LFwearR'],
            'RFtempCL': self.ir['RFtempCL'], 'RFtempCM': self.ir['RFtempCM'], 'RFtempCR': self.ir['RFtempCR'],
            'RFwearL': self.ir['RFwearL'], 'RFwearM': self.ir['RFwearM'], 'RFwearR': self.ir['RFwearR'],
            'LRtempCL': self.ir['LRtempCL'], 'LRtempCM': self.ir['LRtempCM'], 'LRtempCR': self.ir['LRtempCR'],
            'LRwearL': self.ir['LRwearL'], 'LRwearM': self.ir['LRwearM'], 'LRwearR': self.ir['LRwearR'],
            'RRtempCL': self.ir['RRtempCL'], 'RRtempCM': self.ir['RRtempCM'], 'RRtempCR': self.ir['RRtempCR'],
            'RRwearL': self.ir['RRwearL'], 'RRwearM': self.ir['RRwearM'], 'RRwearR': self.ir['RRwearR'],
        }




