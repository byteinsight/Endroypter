# modules/irace_sdk/irsdk_formatter.py

from datetime import timedelta, datetime
import math

from .irsdk_constants import IrConstants

class Formatter:

    def __init__(self, app_context):
        self.logger = app_context.logger
        self.constants = IrConstants()

    @staticmethod
    def decode_flags(flag_code, flag_object):
        flags = [a for a in dir(flag_object) if not a.startswith('__')]
        enabled_flags = []
        for attr in flags:
            flag_mask = (getattr(flag_object, attr))
            try:
                if flag_code & flag_mask:
                    attr = attr.replace("_", " ").title()
                    enabled_flags.append(attr)
            except TypeError as error:
                print(flag_code, flag_mask)
        return enabled_flags

    def decode_session_flags(self, flag_code):
        """

        :param flag_code:
        :return:
        """
        return ', '.join(self.decode_flags(flag_code, irsdk.Flags))

    def get_sky_type(self, sky_index):
        return self.constants.SKY_TYPE.get(sky_index, "Unknown")

    def get_track_wetness(self, track_index):
        return self.constants.TRACK_WETNESS.get(track_index, "Unknown")

    @staticmethod
    def get_dict_value(dictionary, key, default="--"):
        """ Return value from dictionary if exists"""
        if not isinstance(dictionary, dict):
            return default

        if key not in dictionary:
            return default

        return dictionary[key]

    def make_speed_string(self, speed_metres_second, unit=None):
        if unit:
            return "{0:.1f} {1:s}".format(speed_metres_second * self.constants.MS2KPH, unit)
        return "{0:.1f}".format(speed_metres_second * self.constants.MS2KPH)

    def make_time_string(self, time_in_seconds):
        """
        Given the number of seconds as a float number return a formatted timedelta string.
        :param time_in_seconds:
        :return: datetime.timedelta
        """
        try:
            if time_in_seconds <= 0.0 or time_in_seconds > 60000:
                return_value = "00:00:00"
            else:
                return_value = str(timedelta(seconds=time_in_seconds))[2:-3]
        except TypeError as error:
            self.logger.error(f"Make Time String TypeError with {time_in_seconds}. {error}")
            return time_in_seconds
        except ValueError as error:
            self.logger.error(f"Make Time String ValueError with {time_in_seconds}. {error}")
            return time_in_seconds
        return return_value

    @staticmethod
    def make_daytime_string(time_in_seconds):
        if time_in_seconds <= 0.0:
            return "00:00:00"
        return str(timedelta(seconds=time_in_seconds))

    def make_average_float_string(self, raw_numbers, unit=None):
        return self.make_float_string(sum(raw_numbers) / len(raw_numbers), unit)

    def make_float_string(self, raw_number, unit=None):
        try:
            if raw_number:
                if unit:
                    return "{0:.2f} {1}".format(float(raw_number), unit)
                return "{0:.2f}".format(float(raw_number))
        except TypeError as e:
            self.logger.debug("make_float_string: TypeError - {0} and {1}".format(raw_number, unit))
        except ValueError as error:
            self.logger.debug("make_float_string: ValueError - {0} and {1}".format(raw_number, unit))
        return "--"

    def make_percent_string(self, raw_number, fraction=True):
        try:
            if fraction:
                raw_number = raw_number * 100
            return "{0:.2f} {1}".format(float(raw_number), "%")
        except TypeError as e:
            self.logger.debug("make_float_string - TypeError - " + str(raw_number))
            return raw_number
        except ValueError as error:
            self.logger.debug("make_float_string - ValueError - " + str(raw_number) + str(error))
        return raw_number

    @staticmethod
    def make_int_string(raw_number):
        return str(raw_number)

    @staticmethod
    def convert_rad_to_degrees(raw_number, formatted=True):
        degrees = raw_number * (180 / math.pi)
        if formatted:
            return "{0:.2f} \xB0".format(float(degrees))
        return degrees

    def format_session(self, session_data):
        session_data['SessionState'] = self.constants.SESSION_STATE.get(session_data['SessionState'], None)

    @staticmethod
    def convert_air_pressure_mbar(raw_data, formatted=False):
        kpa = float(raw_data / 100)
        if formatted:
            return f"{kpa:.2f} Mb".format()
        return kpa

    @staticmethod
    def make_bool(raw_value):
        if raw_value:
            return "T"
        return "F"

    def format_idx(self, idx_data, idx_labels):
        try:
            # Remove cars with 0 position - do we need to
            idx_data = idx_data.loc[~(idx_data['CarIdxPosition'] == 0)]

            # Format Time Columns
            idx_data.loc[:, 'CarIdxF2Time'] = idx_data.CarIdxF2Time.apply(self.make_time_string)
            idx_data.loc[:, 'CarIdxLastLapTime'] = idx_data.CarIdxLastLapTime.apply(self.make_time_string)
            idx_data.loc[:, 'CarIdxBestLapTime'] = idx_data.CarIdxBestLapTime.apply(self.make_time_string)
            idx_data.loc[:, 'CarIdxEstTime'] = idx_data.CarIdxEstTime.apply(self.make_time_string)

            # Format Numbers and Percentages
            idx_data.loc[:, 'CarIdxLapDistPct'] = idx_data.CarIdxLapDistPct.apply(self.make_float_string)
            idx_data.loc[:, 'CarIdxSteer'] = idx_data.CarIdxSteer.apply(self.make_float_string)
            idx_data.loc[:, 'CarIdxRPM'] = idx_data.CarIdxRPM.apply(self.make_float_string)
            idx_data.loc[:, 'CarIdxRPM'] = idx_data.CarIdxRPM.apply(self.make_float_string)

            # Do some replacements
            idx_data.loc[:, 'CarIdxTrackSurface'] = idx_data.CarIdxTrackSurface.replace(self.constants.TRACK_LOCATION)
            idx_data.loc[:, 'CarIdxTrackSurfaceMaterial'] = idx_data.CarIdxTrackSurfaceMaterial.replace(self.constants.TRACK_SURFACE)

            # Finally sort values into position and replace col names with labels.
            idx_data = idx_data.sort_values(by=['CarIdxPosition'])
            idx_data.columns = idx_labels
        except AttributeError as error:
            pass
        return idx_data

    def format_player(self, player_data):
        player_data['PlayerCarPitSvStatus'] = self.constants.PIT_SV_STATUS.get(player_data['PlayerCarPitSvStatus'], None)
        player_data['PlayerTrackSurface'] = self.constants.TRACK_LOCATION.get(player_data['PlayerTrackSurface'], None)
        player_data['PlayerTrackSurfaceMaterial'] = self.constants.TRACK_SURFACE.get(player_data['PlayerTrackSurfaceMaterial'], None)

    def format_car(self, car_data):
        car_data['CarLeftRight'] = self.constants.CAR_LEFT_RIGHT.get(car_data['CarLeftRight'], None)
        car_data['PaceMode'] = self.constants.PACE_MODE.get(car_data['PaceMode'], None)
        car_data['PitSvFlags'] = self.constants.SRV_FLAGS.get(car_data['PitSvFlags'], None)

    def get_session_state(self, session_num, session_state):
        """ Returns the session state as both a number and label"""
        state = self.constants.SESSION_STATE.get(session_state, "Unknown")
        num = self.constants.SESSION_NUMBER.get(session_num, "X")
        return f"{num} {state}"

    @staticmethod
    def format_ephemeral_string(data):
        return ", ".join(data['local_time'])

    @staticmethod
    def get_session_laps(raw_number):
        """ Returns the number of session laps completed or pending based on raw_number.
        Assumes that 32767 is undefined - seen in replays. """
        if raw_number == 32767:
            return "N/A"
        return str(raw_number)

    @staticmethod
    def get_time_difference(start_time, end_time):
        """
        Get Time difference returns a time string showing the difference between two times in seconds.
        :param start_time:
        :param end_time:
        :return:
        """
        if start_time and end_time:
            time_in_seconds = (end_time - start_time)
            time_delta = timedelta(seconds=time_in_seconds)

            # Get the hours, minutes, and seconds.
            minutes, seconds = divmod(time_delta.seconds, 60)
            hours, minutes = divmod(minutes, 60)

            # Round the microseconds to millis.
            micro_string = f"{time_delta.microseconds:03}"[:3]

            output = f"{hours:02}:{minutes:02}:{seconds:02}.{micro_string}"
            return output
        return "00:00:00.000"


