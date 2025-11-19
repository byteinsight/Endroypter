"""
irsdk_helper.py - system wrapper to the IRSDK Liibrary

All the "Player" variables are specific to the local driver
CarIdxTireCompound              	Cars current tire compound
PlayerTireCompound              	:Players car current tire compound

Version 1.00

"""
from datetime import datetime
import irsdk
import json
import os
from statistics import mean

from iraceinsight.modules.helpers.format_helper import Formatter
from iraceinsight.modules.helpers.pitstop_helper import PitStopHelper
from iraceinsight.modules.helpers.weather_helper import WeatherHelper


class IRState:
    ir_connected = False
    last_car_setup_tick = -1


class IRSDKServiceOld:
    """
    A IRSDK Wrapper or Helper Class that provides an interface between my application
    and the IRSDK (https://github.com/kutu/pyirsdk)
    """
    # Sim Data is stored in these at either every tick or lap.
    session_info = None
    session_data = None  # This holds session data and the player IDX
    driver_stat_data = None  # This holds data prefixed with player or lap
    weather_data = None  # This holds data relating to weather
    car_data = None  # This holds data  relating to the car
    idx_data = None  # This data is mixed data from both IDX and calculations.

    car_name = None
    track_name = None

    # We use this to monitor if the sim is running.
    # Session Time is Seconds since session start, s
    session_id = None
    session_num = None
    last_session_time = 0.0

    # We use these to track the fuel level and fuel used
    last_lap_fuel_level = None
    fuel_used_last_lap = 0.0
    fuel_data = []
    lap_data = []
    fuel_lap_data = {}
    incidents_counted = 0

    # The lap percent distance is used to determine laps completed.
    lap_dist_pct = 0
    laps_counted = 0

    # We use these variable to monitor a pit stop.
    approaching_pits = False
    pit_approach_start_time = None
    pit_approach_end_time = None
    on_pit_lane = False
    pit_stop_in_progress = False
    pit_stop_active = False
    on_jacks = False
    on_jacks_time = None
    off_jacks_time = None
    pit_data = None
    pit_stop_object = None
    pit_data_tyres = None

    velocity_z = []

    def __init__(self, app_context):
        """
        In INIT we initialize both the ir connection and a state object used to track availability of data.
        """
        self.app_context = app_context
        self.config = app_context.config
        self.logger = app_context.logger

        # Set up a formatter for iRacing objects and flags.
        self.formatter = Formatter(app_context)
        self.weather_helper = WeatherHelper(app_context)

        # Initialize both the ir connection and a state object used to track availability of data.
        self.ir = irsdk.IRSDK()
        self.state = IRState()

    def get_car_name(self):
        return self.car_name

    def reset_on_new_session(self):
        self.session_num = None
        self.session_info = None
        self.reset_on_new_session_num()

    def reset_on_new_session_num(self):
        self.last_session_time = 0.0
        self.session_data = None
        self.driver_stat_data = None
        self.weather_data = None
        self.car_data = None
        self.idx_data = None
        self.last_lap_fuel_level = None
        self.fuel_used_last_lap = 0.0
        self.fuel_data = []
        self.lap_data = []
        self.fuel_lap_data = {}
        self.lap_dist_pct = 0
        self.laps_counted = 0
        self.on_pit_lane = False
        self.pit_stop_active = False
        self.pit_data = None
        self.pit_stop_object = None
        self.incidents_counted = 0

    def get_session_status_string(self):
        """ Creates an updated session string that is printed at the bottom of the UI window. """
        session_state = self.formatter.get_session_state(self.ir['SessionNum'], self.ir['SessionState'])
        return f"SDK LIVE: Player IDX: {self.ir['PlayerCarIdx']};  State: {session_state};  Tick: {self.ir['SessionTick']}"

    def get_session_header(self):
        return {
            'CustID': self.config.user.IRACE_CUSTID,
            'TeamID': self.ir['DriverInfo']['Drivers'][self.ir['PlayerCarIdx']]['TeamID'],
            'SessionID': self.ir['WeekendInfo']['SessionID'],
            'SessionNum': self.ir['SessionNum']
        }

    def update_session_info(self):

        sun_rise_set = self.weather_helper.get_ephemeral(
            self.ir['WeekendInfo']['TrackLongitude'],
            self.ir['WeekendInfo']['TrackLatitude'],
            self.ir['WeekendInfo']['TrackAltitude'],
            self.ir['WeekendInfo']['WeekendOptions']['Date'],
        )
        # self.logger.info(f"Weather Helper returns Sunrise {sunrise} & Sunset {sunset}")

        self.session_info = {
            'SeriesID': self.ir['WeekendInfo']['SeriesID'],
            'SeasonID': self.ir['WeekendInfo']['SeasonID'],
            'SessionID': self.ir['WeekendInfo']['SessionID'],
            'SubSessionID': self.ir['WeekendInfo']['SubSessionID'],
            'LeagueID': self.ir['WeekendInfo']['LeagueID'],
            'TrackID': self.ir['WeekendInfo']['TrackID'],
            'TeamRacing': self.ir['WeekendInfo']['TeamRacing'],
            'CarID': self.ir['DriverInfo']['Drivers'][self.ir['PlayerCarIdx']]['CarID'],
            'CarFuel_KgPerLtr': self.ir['DriverInfo']['DriverCarFuelKgPerLtr'],
            'CarFuel_MaxLtr': self.ir['DriverInfo']['DriverCarFuelMaxLtr'],
            'CarFuel_FuelPct': self.ir['DriverInfo']['DriverCarMaxFuelPct'],
            'Event_Date': self.ir['WeekendInfo']['WeekendOptions']['Date'],
            'Ephemeral': sun_rise_set
        }

        self.car_name = self.ir['DriverInfo']['Drivers'][self.ir['PlayerCarIdx']]['CarScreenName']
        self.track_name = self.ir['WeekendInfo']['TrackName']

    def update_session_status(self):
        """
        Get Session Data gets data specific to the session but src the Player Car Index for accessing IDX.
        :return:
        """

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

    def update_weather_data(self):

        self.weather_data = {
            'CustID': self.app_context.config.user.IRACE_CUSTID,
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

    def update_car_data(self):
        self.car_data = {
            'SteeringWheelPctDamper': self.ir['SteeringWheelPctDamper'],  # Force feedback % max damping, (%age)
            'SteeringWheelPctIntensity': self.ir['SteeringWheelPctIntensity'],  # Force feedback % max intensity, (%age)
            'SteeringWheelPctSmoothing': self.ir['SteeringWheelPctSmoothing'],  # Force feedback % max smoothing, (%age)
            'SteeringWheelPctTorque': self.ir['SteeringWheelPctTorque'],  # Force feedback % max torque on steering shaft unsigned, (%age)
            'SteeringWheelPeakForceNm': self.ir['SteeringWheelPeakForceNm'],  # Peak torque mapping to direct input units for FFB, (N*m)
            'SteeringWheelTorque': self.ir['SteeringWheelTorque'],  # Output torque on steering shaft, (N*m)
        }

    def update_fuel_calculations(self):
        """

        :return:
        """
        # This is the first lap
        if not self.last_lap_fuel_level:
            self.last_lap_fuel_level = self.ir['FuelLevel']
            self.fuel_used_last_lap = 0.0

        # This is all other laps.
        else:
            self.fuel_used_last_lap = self.last_lap_fuel_level - self.ir['FuelLevel']
            self.last_lap_fuel_level = self.ir['FuelLevel']

    def update_idx_data(self, player_car_idx):
        """
        update_idx_data retrieves the data for the car from the IDX array which src the other cars.

        :param player_car_idx:
        :return:
        """

        if self.ir['LapCompleted'] and self.ir['LapCompleted'] >= 0:
            self.idx_data = {
                'CarIdxLap': int(self.ir['CarIdxLap'][player_car_idx]),  # Laps completed count
                'CarIdxClassPosition': self.ir['CarIdxClassPosition'][player_car_idx],  # Cars class position in race by car index,
                'CarIdxPosition': self.ir['CarIdxPosition'][player_car_idx],  # Cars position in race by car index,
                'CarIdxLastLapTime': self.ir['CarIdxLastLapTime'][player_car_idx],
                'CarIdxF2Time': self.ir['CarIdxF2Time'][player_car_idx],
                'clean_lap': self.incident_tracker(self.ir['PlayerCarTeamIncidentCount']),
                'fuel_used': self.fuel_used_last_lap,
                'TrackTempCrew': self.ir['TrackTempCrew'],  # Temperature of track measured by crew around track (C)
                'TrackWetness': self.ir['TrackWetness'],  # How wet is the average track surface, irsdk_TrackWetness
            }
        else:
            self.idx_data = None

    def incident_tracker(self, latest_count):
        return_value = latest_count - self.incidents_counted
        self.incidents_counted = latest_count
        return return_value

    def update_driver_stat_data(self, player_car_idx):
        """
        Get Fuel Data builds our stat record of fuel used and lap times
        :return:
        """

        # Start with the basics.
        self.driver_stat_data = {
            'Lap': self.ir['Lap'],  # Laps started count
            'LapCompleted': self.ir['LapCompleted'],  # Laps completed count
            'LapBestLapTime': self.ir['LapBestLapTime'],  # Players best lap time (s)

            'PlayerTireCompound': self.ir['PlayerTireCompound'],  # Players car current tire compound
            'LapLastNLapTime': self.ir['LapLastNLapTime'],  # Player last N average lap time (s)

            'PlayerCarDriverIncidentCount': self.ir['PlayerCarDriverIncidentCount'],  # Teams current drivers incident count for this session,
            'PlayerCarTeamIncidentCount': self.ir['PlayerCarTeamIncidentCount'],  # Players team incident count for this session
        }

        # Starting with the fuel
        if self.fuel_used_last_lap > 0.0:
            self.fuel_data.append(self.fuel_used_last_lap)
            self.driver_stat_data['last_lap_fuel'] = self.fuel_used_last_lap
            self.driver_stat_data['avg_lap_fuel'] = mean(self.fuel_data)
            self.driver_stat_data['min_lap_fuel'] = min(self.fuel_data)
            self.driver_stat_data['max_lap_fuel'] = max(self.fuel_data)
            self.driver_stat_data['last_five_laps'] = mean(self.fuel_data[-5:])

        # Now the lap times
        if self.ir['CarIdxLastLapTime'][player_car_idx] > 0.0:
            if len(self.lap_data) > 0:
                previous_lap = self.lap_data[-1]  # Store the previous lap in a temp variable so its not confused by the last lap completed.
            else:
                previous_lap = 0.0
            self.lap_data.append(self.ir['CarIdxLastLapTime'][player_car_idx])
            self.driver_stat_data['last_lap'] = self.ir['CarIdxLastLapTime'][player_car_idx]
            self.driver_stat_data['session_previous_lap'] = previous_lap
            self.driver_stat_data['session_best_lap'] = min(self.lap_data)
            self.driver_stat_data['session_opt_lap'] = 0.0
            self.driver_stat_data['average_lap_time'] = mean(self.lap_data)

    def update_track_position(self, player_car_idx):
        """

        @todo # Forum says store your own lap counter based on so something like if self.lap_dist_pct > self.ir['LapDistPct']:

        :return: dict
        """

        # If update is made true we will update the other widgets
        track_update = False

        # NEW LAP:  Recording passing the start/finish line.
        if self.ir['CarIdxLapCompleted'][player_car_idx] and self.ir['CarIdxLapCompleted'][player_car_idx] > self.laps_counted:
            track_update = True
            self.laps_counted = self.ir['CarIdxLapCompleted'][player_car_idx]
            self.lap_dist_pct = self.ir['LapDistPct']
            self.logger.info(f"New Lap {self.laps_counted} at {self.ir['LapDistPct']:.3f}%")

        # APPROACHING PITS
        if self.ir['CarIdxTrackSurface'][player_car_idx] == 2 and self.approaching_pits is False:
            self.pit_approach_start_time = self.ir['SessionTime']
            self.approaching_pits = True
            self.ctx.logger.info(f"Approaching Pits started at {self.pit_approach_start_time}")

        # PIT IN:  If the CarIdxOnPitRoad is True and on_pit_lane is False we have just entered the pits.
        if bool(self.ir['CarIdxOnPitRoad'][player_car_idx]) is True and self.on_pit_lane is False:
            track_update = True  # We update on pit lane entry

            # Create a new pit stop object and set on_pit_lane object to True
            self.on_pit_lane = True
            self.pit_stop_object = PitStopHelper(self.app_context, self.ir['SessionTime'], self.ir['CarIdxLap'][player_car_idx])

        # PIT STOP ACTIVE:  If on_pit_lane is True and PitstopActive is True we are servicing the car
        if self.on_pit_lane and bool(self.ir['PitstopActive']):
            self.pit_stop_object.in_pits_update(self.ir['SessionTime'], self.ir['FuelLevel'], self.ir['PitSvFlags'])

            # CAR IS JACKED
            self.velocity_z.append(float(self.ir['VelocityZ']))

            # Looking at VelocityZ to determine car going onto jacks
            if not self.on_jacks and float(self.ir['VelocityZ']) > 0.01:  # and 1 < self.ir['PitSvFlags'] < 16:
                # self.logger.info(f"On Jacks - VelocityZ: {self.ir['VelocityZ']}")
                self.on_jacks = True
                if self.on_jacks_time is None:
                    self.on_jacks_time = self.ir['SessionTime']

            if self.on_jacks and self.ir['VelocityZ'] < -0.04:  # and self.ir['PitSvFlags'] > 16:
                # self.logger.info(f"Off Jacks - VelocityZ: {self.ir['VelocityZ']}")
                self.on_jacks = False
                self.off_jacks_time = self.ir['SessionTime']


            # This is the first time we have landed
            if not self.pit_stop_active:
                self.pit_stop_active = True
                self.pit_stop_object.service_started(
                    self.ir['SessionTime'],
                    self.ir['PlayerCarTowTime'],
                    self.ir['PitRepairLeft'],
                    self.ir['PitOptRepairLeft']
                )
                self.logger.info(f"Pit Servicing Starting at {self.ir['SessionTime']}")

        # PIT SERVICE STATUS:  in_progress = 1 and complete = 2
        if self.ir['PlayerCarPitSvStatus'] == 1 and self.pit_stop_in_progress is False:
            self.logger.info(f"Pit Status In Progress Starting Now: {self.ir['SessionTime']}")
            self.pit_stop_in_progress = True
        elif self.ir['PlayerCarPitSvStatus'] == 2 and self.pit_stop_in_progress is True:
            self.logger.info(f"Pit Status Completed Now: {self.ir['SessionTime']}")
            self.pit_stop_in_progress = False

        # PIT STOP INACTIVE: We have stopped servicing but have not left the box.
        if self.pit_stop_active and not bool(self.ir['PitstopActive']):
            self.pit_stop_active = False
            self.pit_stop_object.in_pits_update(self.ir['SessionTime'], self.ir['FuelLevel'], self.ir['PitSvFlags'])
            self.pit_stop_object.service_ended(self.ir['SessionTime'])
            self.logger.info(f"Pit Servicing Completed at {self.ir['SessionTime']}")

        # PIT STOP END: If on_pit_lane is true, car_idx_on_pit_road is True we are exiting the pits.
        if self.on_pit_lane is True and bool(self.ir['CarIdxOnPitRoad'][player_car_idx]) is False:

            # It's possible to miss the service finishing so if pit_stop_active still true we record it here.
            if self.pit_stop_active:
                self.pit_stop_active = False
                self.pit_stop_object.in_pits_update(self.ir['SessionTime'], self.ir['FuelLevel'], self.ir['PitSvFlags'])
                self.pit_stop_object.service_ended(self.ir['SessionTime'])
                self.logger.info(f"Pit Servicing Ended at {self.ir['SessionTime']}")
            else:
                self.pit_stop_object.in_pits_update(self.ir['SessionTime'], self.ir['FuelLevel'], self.ir['PitSvFlags'])

        # PIT OUT: If on_pit_lane is true and car_idx_on_pit_road has turned False we have just left the pits.
        if self.on_pit_lane is True and bool(self.ir['CarIdxOnPitRoad'][player_car_idx]) is False:
            track_update = True

            # Update pit exit time and other values.
            self.on_pit_lane = False
            self.pit_stop_object.out_update(self.ir['SessionTime'])
            self.pit_data = self.pit_stop_object.get_pit_data_dict()
            self.logger.info(f"Pit Left Pits at {self.ir['SessionTime']}")

            # Add the tyre wear & temps from the Pit Stop
            if self.pit_data:
                self.pit_data['tyres'] = {
                    'LFtempCL': self.ir['LFtempCL'], 'LFtempCM': self.ir['LFtempCM'], 'LFtempCR': self.ir['LFtempCR'],
                    'LFwearL': self.ir['LFwearL'], 'LFwearM': self.ir['LFwearM'], 'LFwearR': self.ir['LFwearR'],
                    'RFtempCL': self.ir['RFtempCL'], 'RFtempCM': self.ir['RFtempCM'], 'RFtempCR': self.ir['RFtempCR'],
                    'RFwearL': self.ir['RFwearL'], 'RFwearM': self.ir['RFwearM'], 'RFwearR': self.ir['RFwearR'],
                    'LRtempCL': self.ir['LRtempCL'], 'LRtempCM': self.ir['LRtempCM'], 'LRtempCR': self.ir['LRtempCR'],
                    'LRwearL': self.ir['LRwearL'], 'LRwearM': self.ir['LRwearM'], 'LRwearR': self.ir['LRwearR'],
                    'RRtempCL': self.ir['RRtempCL'], 'RRtempCM': self.ir['RRtempCM'], 'RRtempCR': self.ir['RRtempCR'],
                    'RRwearL': self.ir['RRwearL'], 'RRwearM': self.ir['RRwearM'], 'RRwearR': self.ir['RRwearR'],
                }

            total_jacks = self.formatter.get_time_difference(self.on_jacks_time, self.off_jacks_time)
            self.logger.info(f"Jack Time: Up at {self.on_jacks_time} and down at {self.off_jacks_time}.  Total time: {total_jacks}.")
            self.logger.debug(f"[{', '.join(self.velocity_z)}]")

        # LEAVING PITS: If we have previously approached the pits and the track surface is neither irsdk_AproachingPits or irsdk_InPitStall
        # then we must have exited the pits
        # if self.approaching_pits is True and (self.ir['CarIdxTrackSurface'][player_car_idx] != 2 or self.ir['CarIdxTrackSurface'][player_car_idx] != 1):
        #    self.pit_approach_end_time = self.ir['SessionTime']
        #    self.approaching_pits = False
        #    self.logger.info(f"Approaching Pits ended at {self.pit_approach_end_time}")

        # Return a boolean that says whether data has been updated.
        return track_update

    def check_sim_connection(self):
        """
        The check_sim_connection function comes from the IRSDK examples.
        We check if we are connected to the SDK/Sim and if we can retrieve data
        :return: None
        """
        if self.state.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            self.state.ir_connected = False
            # don't forget to reset your State variables
            self.state.last_car_setup_tick = -1
            # we are shutting down ir library (clearing all internal variables)
            self.ir.shutdown()
            self.logger.debug('IRSDK Disconnected')
        elif not self.state.ir_connected and self.ir.startup() and self.ir.is_initialized and self.ir.is_connected:
            self.state.ir_connected = True
            self.logger.debug('IRSDK Connected')

    @staticmethod
    def get_session_id(sdk_session_id):
        if sdk_session_id != 0:
            return sdk_session_id
        # now = datetime.now().strftime("%Y_%m_%d_%H")  # current date and time
        return 0

    def get_update(self):
        """
        This is the entry point into the wrapper.
        We check the SDK connection and freeze buffer with live telemetry.
        We then gather and calculate data based on the car's position on track
        :return Boolean: Returns true if new data has been collected.
        """
        session_update = False
        session_id_change = False
        session_num_change = False
        track_update = False

        self.check_sim_connection()
        if self.state.ir_connected:

            # This is so we get consistent data from inside that tick
            # and the data isn't updated by apis inbetween calls.
            self.ir.freeze_var_buffer_latest()

            # If the sim is in replay mode, and we are not in debug mode.
            if self.ir['IsReplayPlaying'] and not self.config.user.DEBUG:
                session_update = False

            # Else process data
            else:
                session_update = True

                # NEW SESSION: We have moved onto a new server.
                # Reset all the variables used to monitor our status and update session info.
                if self.session_id != self.ir['WeekendInfo']['SessionID']:
                    self.session_id = self.get_session_id(self.ir['WeekendInfo']['SessionID'])
                    session_id_change = True
                    self.reset_on_new_session()
                    self.update_session_info()
                    self.logger.info(f"NEW SESSION LOADED: {self.session_id} at {self.session_info['TrackID']}. (OLD SESSION: {self.ir['WeekendInfo']['SessionID']})")

                # NEW SESSION NUM: E.G. we have moved from quali to race.
                # Need to update our session_num and reset laps_counted.
                if self.session_num != self.ir['SessionNum']:
                    self.session_num = self.ir['SessionNum']
                    session_num_change = True
                    self.reset_on_new_session_num()
                    self.logger.info(
                        f"SESSION NUM CHANGE: {self.ir['SessionNum']}; State={self.ir['SessionState']}; Session Time={self.ir['SessionTime']}.")

                # Get the session data and see if time has moved on.
                # If it hasn't then this is a sign that the sim is paused or stopped.
                if self.last_session_time < self.ir['SessionTime']:

                    # If the session has moved on then store our last recorded session time.
                    self.last_session_time = self.ir['SessionTime']

                    # These variables get updated every tick
                    self.update_session_status()

                    # These variable groups only get updated when we have passed the start finish line.
                    if self.update_track_position(self.ir['PlayerCarIdx']):
                        self.update_fuel_calculations()
                        self.update_weather_data()
                        self.update_car_data()
                        self.update_idx_data(self.ir['PlayerCarIdx'])
                        self.update_driver_stat_data(self.ir['PlayerCarIdx'])

                        # Get Update returns True every time any data (including session) is updated.
                        track_update = True

        return session_update, session_id_change, session_num_change, track_update

    def get_dict_keys(self, current_dict):
        key_dict = {}
        if current_dict:
            for key, value in current_dict.items():
                if isinstance(value, dict):
                    sub_key_dict = self.get_dict_keys(value)
                    key_dict[key] = sub_key_dict
                elif isinstance(value, list):
                    if value:
                        key_dict[key] = self.get_dict_keys(value[0])
                    else:
                        key_dict[key] = []
                else:
                    key_dict[key] = ""
        return key_dict

    def get_the_vars(self):
        self.check_sim_connection()
        if self.state.ir_connected:

            # This is so we get consistent data from inside that tick
            # and the data isn't updated by apis inbetween calls.
            self.ir.freeze_var_buffer_latest()

            self.logger.info(f"Getting the SDK Vars from Session ID: {self.ir['WeekendInfo']['SessionID']}")

            race_vars = {}
            var_headers = self.ir._var_headers_dict
            for k, v in var_headers.items():
                race_vars[k] = {'desc': v.desc, 'unit': v.unit}

            sdk_dictionary = {
                'RaceVars': race_vars,
                'WeekendInfo': self.get_dict_keys(self.ir['WeekendInfo']),
                'SessionInfo': self.get_dict_keys(self.ir['SessionInfo']),
                'QualifyResultsInfo': self.get_dict_keys(self.ir['QualifyResultsInfo']),
                'CameraInfo': self.get_dict_keys(self.ir['CameraInfo']),
                'RadioInfo': self.get_dict_keys(self.ir['RadioInfo']),
                'DriverInfo': self.get_dict_keys(self.ir['DriverInfo']),
                'SplitTimeInfo': self.get_dict_keys(self.ir['SplitTimeInfo']),
                'CarSetup': self.get_dict_keys(self.ir['CarSetup']),
            }

            json_file_name = os.path.join(self.app_context.paths.RESOURCE_ROOT, "data", "sdk_vars.json")
            with open(json_file_name, 'w') as fp:
                json.dump(sdk_dictionary, fp, indent=4)

    def get_the_setup(self):
        self.check_sim_connection()
        if self.state.ir_connected:

            # This is so we get consistent data from inside that tick
            # and the data isn't updated by apis inbetween calls.
            self.ir.freeze_var_buffer_latest()

            # Retrieve CarSetup from session data
            try:
                car_setup = self.ir['CarSetup']
                if car_setup:

                    # Get the CarSetUp Tick with ir.get_session_info_update_by_key(key)
                    car_setup_tick = self.ir.get_session_info_update_by_key('CarSetup')

                    setup_name = car_setup.get('SetupName', None)

                    if setup_name is None and self.car_name and self.track_name:
                        setup_name = f"{self.car_name}_{self.track_name}_{car_setup_tick}"
                    else:
                        setup_name = f"unknown_baseline"

                    self.logger.info(f"Current Setup is called: {setup_name} for {self.car_name} and {self.track_name}.")

                    # But first you need to request data, before checking if its updated
                    if car_setup_tick != self.state.last_car_setup_tick:
                        self.state.last_car_setup_tick = car_setup_tick
                        car_setup_count = car_setup['UpdateCount']
                        self.logger.debug(f'get_the_setup update_count: {car_setup["UpdateCount"]}')
                        # now you can go to garage, and do some changes with your setup
                        # this line will be printed, only when you change something
                        # and press apply button, but not every 1 sec
                        return car_setup, setup_name
                    return None, None

            except Exception as error:
                self.logger.error(f"get_the_setup exception {error}.")
        return None, None
