from modules.irace_sdk.irsdk_formatter import Formatter


class PitCrew:

    # Set when the car is
    approaching_pits = False
    on_pit_lane = False
    pit_stop_active = False
    service_in_progress = False


    # Basic Times
    box_in_time = -0.0
    pit_in_time = -0.0
    service_start_time = -0.0
    service_end_time = -0.0
    pit_out_time = -0.0
    back_on_track = -0.0

    service_time = -0.0
    stop_length = -0.0
    total_pit_stop = 0.0
    pit_in_lap = 0

    # Tows and Repairs
    tow_time = -0.0
    repairs = -0.0
    opt_repairs = -0.0

    # Fuel Values
    fuel_filling = False
    fuel_start_time = -0.0
    fuel_start_level = -0.0
    fuel_end_time = -0.0
    fuel_end_level = -0.0
    fuel_fill_time = -0.0
    fuel_fill_amount = -0.0
    fuel_per_sec = -0.0

    # Tyre Values
    tyre_data = {}
    tyres_changing = False
    tyres_start_time = -0.0
    tyres_finish_time = -0.0
    tyre_change_time = -0.0
    litres_over_tyres = -0.0

    tyre_flags = {"FL": None, "FR": None, "RL": None, "RR": None}

    # Jack Monitoring
    on_jacks = False
    on_jacks_time = 0.0
    off_jacks_time = 0.0

    def __init__(self, ctx):
        self.ctx = ctx
        self.format = Formatter(ctx)

    def box_box_box(self, session_time, car_idx_lap):
        self.box_in_time = session_time
        self.pit_in_lap = car_idx_lap
        self.approaching_pits = True

        box_in_time_str = self.format.make_time_string(self.box_in_time)
        self.ctx.logger.info(f"PitCrew: Approaching Pits started at {box_in_time_str} on lap {self.pit_in_lap}.")

    def approaching_pit_box(self, session_time):
        self.on_pit_lane = True
        self.pit_in_time = session_time

        pit_in_time_str = self.format.make_time_string(self.pit_in_time)
        self.ctx.logger.info(f"PitCrew: Approaching Pit Box at {pit_in_time_str}.")

    def in_pit_box(self, session_time, fuel_level, pit_sv_flags):

        self.fuel_service_update(session_time, fuel_level, pit_sv_flags)
        self.tyre_service_update(session_time, pit_sv_flags)

        # If this is the first in-pit tick then we have just started.
        if not self.pit_stop_active:
            self.service_start_time = session_time
            self.pit_stop_active = True

    def update_on_repairs(self, tow_time, repairs, opt_repairs):
        self.tow_time = tow_time
        self.repairs = repairs
        self.opt_repairs = opt_repairs

    def fuel_service_update(self, session_time, fuel_level, pit_sv_flags):
        try:

            # Fuel Filling is starting
            if pit_sv_flags & 0x10 and not self.fuel_filling:
                self.fuel_filling = True
                self.fuel_start_time = session_time
                self.fuel_start_level = fuel_level
                self.ctx.logger.info(f"PitCrew: Fuel Filling Started at: {self.fuel_start_time} - Start Level = {self.fuel_start_level}")

            # Fuel Filling has finished
            if self.fuel_filling and not (pit_sv_flags & 0x10):
                self.fuel_filling = False
                self.fuel_end_time = session_time
                self.fuel_end_level = fuel_level
                self.fuel_fill_time = self.fuel_end_time - self.fuel_start_time
                self.fuel_fill_amount = self.fuel_end_level - self.fuel_start_level
                self.fuel_per_sec = self.fuel_fill_amount / (self.fuel_end_time - self.fuel_start_time)
                self.ctx.logger.info(f"PitCrew: Fuel Filling Ends: {self.fuel_end_time} taking {self.fuel_fill_time}.")
                self.ctx.logger.info(f"PitCrew: Fuel Level: {self.fuel_end_level} Added: {self.fuel_fill_amount} at {self.fuel_per_sec} l/s")

        except KeyError as error:
            self.ctx.logger.error(f"PitCrew: Fuel/KeyError: {error}.")
            pass

    def tyre_service_update(self, session_time, pit_sv_flags):
        try:

            # Tyre changes are in the flag code so changes are being done
            if pit_sv_flags & 0x01 or pit_sv_flags & 0x02 or pit_sv_flags & 0x04 or pit_sv_flags & 0x08:

                # This is the first tyre if the flag is not yet set.
                if not self.tyres_changing:
                    self.tyres_changing = True
                    self.tyres_start = session_time
                    self.ctx.logger.info(f"PitCrew: Tyre Changes Started at: {self.tyres_start}")

                # Time the individual Tyres
                if (pit_sv_flags & 0x01) == 0 and self.tyre_flags['FL'] is None:
                    self.tyre_flags['FL'] = session_time
                    self.ctx.logger.info(f"FL-0x01: {session_time}")

                if (pit_sv_flags & 0x02) == 0 and self.tyre_flags['FR'] is None:
                    self.tyre_flags['FR'] = session_time
                    self.ctx.logger.info(f"FR-0x02: {session_time}")

                if (pit_sv_flags & 0x04) == 0 and self.tyre_flags['RL'] is None:
                    self.tyre_flags['RL'] = session_time
                    self.ctx.logger.info(f"RL-0x04: {session_time}")

                if (pit_sv_flags & 0x08) == 0 and self.tyre_flags['RR'] is None:
                    self.tyre_flags['RR'] = session_time
                    self.ctx.logger.info(f"RR-0x08: {session_time}")

            # There are no tyre flags in the flag code, and we did start changing them, it must be over
            elif self.tyres_changing:
                self.tyres_changing = False
                self.tyres_finish = session_time
                self.tyre_change_time = self.tyres_finish - self.tyres_start
                self.ctx.logger.info(f"PitCrew: Tyres Finished at: {self.tyres_finish} taking {self.tyre_change_time}")

        except KeyError as error:
            self.ctx.logger.error(f"PitCrew: Tyres/KeyError: {error}.")
            pass

    def on_jack_monitoring(self, session_time, velocity_z):

        # Looking at VelocityZ to determine car going onto jacks
        if not self.on_jacks and float(velocity_z) > 0.01:  # and 1 < self.ir['PitSvFlags'] < 16:
            # self.logger.info(f"On Jacks - VelocityZ: {self.ir['VelocityZ']}")
            self.on_jacks = True
            if self.on_jacks_time is None:
                self.on_jacks_time = session_time

        if self.on_jacks and velocity_z < -0.04:  # and self.ir['PitSvFlags'] > 16:
            # self.logger.info(f"Off Jacks - VelocityZ: {self.ir['VelocityZ']}")
            self.on_jacks = False
            self.off_jacks_time = session_time

    def service_completed(self, session_time):
        self.pit_stop_active = False
        self.service_end_time = session_time
        self.service_time = self.service_end_time - self.service_start_time

    def leaving_pit_box(self, session_time):
        self.pit_out_time = session_time
        self.on_pit_lane = False
        self.stop_length = session_time - self.pit_in_time
        self.ctx.logger.info(f"Leaving Pit Box @ {self.pit_out_time} ({self.pit_in_time}) Total Stop = {self.stop_length}")

    def leaving_pit_lane(self, session_time):
        self.back_on_track = session_time
        self.approaching_pits = False
        self.total_pit_stop = session_time - self.box_in_time
        self.ctx.logger.info(f"Leaving Pit Lane at {self.back_on_track} ({self.box_in_time}) Total Delta = {self.total_pit_stop}")

    def get_pit_data_dict(self):
        if self.pit_in_lap == 0:
            return None
        # If we have a tyre time and fuel/sec we can calculate the free tyre liters.
        if self.tyres_finish and self.tyres_start and self.fuel_per_sec:
            self.litres_over_tyres = (self.tyres_finish - self.tyres_start) * self.fuel_per_sec

        pit_data_dict = self.__dict__
        pit_data_dict.pop('logger', None)
        pit_data_dict.pop('formatter', None)
        pit_data_dict.pop('fuel_filling', None)
        pit_data_dict.pop('tyres_changing', None)
        return pit_data_dict

    def get_free_tyre_stop_laps(self, fuel_per_lap):
        if self.litres_over_tyres:
            return self.litres_over_tyres / fuel_per_lap
        return 0.0

    def get_jack_time_report(self):
        total_jacks = self.format.get_time_difference(self.on_jacks_time, self.off_jacks_time)
        self.ctx.logger.info(f"Jack Time: Up at {self.on_jacks_time} and down at {self.off_jacks_time}.  Total time: {total_jacks}.")

