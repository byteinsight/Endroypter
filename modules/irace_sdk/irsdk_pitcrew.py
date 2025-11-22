import copy

from modules.irace_sdk.irsdk_formatter import Formatter
from .irsdk_constants import IrConstants

class PitCrew:

    # Velocity_Z: Normalised thresholds (helps prevent noise-triggered flips)
    LIFT_THRESHOLD = 0.01
    DROP_THRESHOLD = -0.04

    # Tracking the current state
    state = "ON_TRACK"
    last_state = "UN_SET"

    # For Testing
    test_mode = False
    srv_sim_state = None

    # For tracking pit-stops and the pit history
    cycle_completed = False
    current_cycle = {}
    pit_history = []

    def __init__(self, ctx):
        self.ctx = ctx
        self.format = Formatter(ctx)
        self.current_cycle = self.new_pit_cycle()

    @staticmethod
    def new_pit_cycle():
        return {

            # Basic Times & Totals
            "box_in_time": 0.0,
            "pit_in_time": 0.0,
            "service_start_time": 0.0,
            "service_end_time": 0.0,
            "pit_out_time": 0.0,
            "back_on_track": 0.0,
            "service_time": 0.0,
            "stop_length": 0.0,
            "total_pit_stop": 0.0,
            "box_in_lap": 0,

            # Tows and Repairs
            "tow_time": 0.0,
            "repairs": 0.0,
            "opt_repairs_max": 0.0,
            "opt_repairs_remaining": 0.0,

            # Fuel Values
            "fuel_filling": False,
            "fuel_start_time": 0.0,
            "fuel_start_level": 0.0,
            "fuel_end_time": 0.0,
            "fuel_end_level": 0.0,
            "fuel_fill_time": 0.0,
            "fuel_fill_amount": 0.0,
            "fuel_per_sec": 0.0,

            # Tyre Values
            "tyre_data": {"LF": None, "RF": None, "LR": None, "RR": None},
            "tyres_changing": False,
            "tyres_start_time": 0.0,
            "tyres_finish_time": 0.0,
            "tyre_change_time": 0.0,
            "litres_over_tyres": 0.0,

            # Jack Monitoring
            "on_jacks": False,
            "on_jacks_time": 0.0,
            "off_jacks_time": 0.0,
            "total_jack_time": 0.0
        }

    def reset_pit_cycle(self):
        """
        Reset the pit cycle after a completed stop and prepare a fresh
        tracking structure for the next pit event.
        """
        self.state = "ON_TRACK"
        self.last_state = "UN_SET"
        self.srv_sim_state = None
        self.current_cycle = self.new_pit_cycle()  # create fresh dict
        self.cycle_completed = False  # reset marker

        self.ctx.logger.info("Pit cycle reset — ready for next stop.")

    def update(self, surface, on_pit_road, car_idx_on_pit_road, pitstop_active, sv_status, session_time, car_idx_lap,
               sv_flags, fuel_level, tow_time, repairs, opt_repairs, velocity_z):

        sv_flags, sv_status = self.simulate_random_srv_flags(sv_flags, sv_status)

        if self.state in {"ENTERING_PIT_BOX", "IN_PIT_BOX_IDLE", "SERVICE_IN_PROGRESS"}:
            self.in_pit_box(session_time, sv_flags, fuel_level, velocity_z, tow_time, repairs, opt_repairs)

        match self.state:

            # 1. ON TRACK → pit entry line seen
            case "ON_TRACK":
                if surface == IrConstants.ON_PIT_LANE and not on_pit_road:
                    self.state = "APPROACHING_PIT_ENTRY"

            # 2. Passing entry → fully on pit road
            case "APPROACHING_PIT_ENTRY":
                if on_pit_road:
                    self.state = "ENTERING_PIT_LANE"

            # 3. Enter pit lane → drive lane OR straight into stall
            case "ENTERING_PIT_LANE":
                if surface == IrConstants.IN_PIT_BOX:
                    self.state = "ENTERING_PIT_BOX"
                elif surface == IrConstants.ON_PIT_LANE and on_pit_road:
                    self.state = "DRIVING_DOWN_PIT_LANE"

            # 4. NEW: driving down lane → stall entry
            case "DRIVING_DOWN_PIT_LANE":
                if surface == IrConstants.IN_PIT_BOX:
                    self.state = "ENTERING_PIT_BOX"

            # 5. Entering pit box → detect alignment/service/idle
            case "ENTERING_PIT_BOX":
                if sv_status not in IrConstants.PIT_SV:
                    self.state = "IN_PIT_BOX_ALIGNMENT_ERROR"
                elif sv_status == IrConstants.PIT_SV_IN_PROGRESS:
                    self.state = "SERVICE_IN_PROGRESS"
                elif sv_status == IrConstants.PIT_SV_COMPLETE:
                    self.state = "SERVICE_COMPLETE"
                else:
                    # Replay-safe fallback
                    self.state = "IN_PIT_BOX_IDLE"

            # 6. Idle in box (waiting)
            case "IN_PIT_BOX_IDLE":
                if sv_status == IrConstants.PIT_SV_IN_PROGRESS:
                    self.state = "SERVICE_IN_PROGRESS"
                elif sv_status == IrConstants.PIT_SV_COMPLETE:
                    self.state = "SERVICE_COMPLETE"
                elif surface == IrConstants.ON_PIT_LANE:
                    # driver leaves without service
                    self.state = "EXITING_PIT_BOX"

            # 7. Alignment error in stall
            case "IN_PIT_BOX_ALIGNMENT_ERROR":
                if sv_status == IrConstants.PIT_SV_IN_PROGRESS:
                    self.state = "SERVICE_IN_PROGRESS"
                elif sv_status == IrConstants.PIT_SV_COMPLETE:
                    self.state = "SERVICE_COMPLETE"
                elif surface == IrConstants.ON_PIT_LANE:
                    self.state = "EXITING_PIT_BOX"

            # 8. Service happening
            case "SERVICE_IN_PROGRESS":
                if sv_status == IrConstants.PIT_SV_COMPLETE:
                    self.state = "SERVICE_COMPLETE"
                elif surface == IrConstants.ON_PIT_LANE:
                    # Replay fallback or aborted service
                    self.state = "EXITING_PIT_BOX"

            # 9. Service complete → leaving stall
            case "SERVICE_COMPLETE":
                if surface == IrConstants.ON_PIT_LANE:
                    self.state = "EXITING_PIT_BOX"

            # 10. Leaving stall → moving to pit exit
            case "EXITING_PIT_BOX":
                if on_pit_road:
                    self.state = "DRIVING_TO_PIT_EXIT"
                else:
                    self.state = "EXITING_PIT_LANE"

            # 11. Driving to pit exit → exit lane
            case "DRIVING_TO_PIT_EXIT":
                if not on_pit_road:
                    self.state = "EXITING_PIT_LANE"

            # 12. Leaving pit lane → back on track
            case "EXITING_PIT_LANE":
                # Back on track when: not in box; not on lane; not on pit road.
                if surface not in IrConstants.PIT_AREA_SURFACES and not on_pit_road:
                    self.state = "BACK_ON_TRACK"

        # Log state transition
        if self.state != self.last_state:

            # Process any on state changing tracking
            self.on_state_change(session_time, car_idx_lap)

            # Log out what has happened.
            self.ctx.logger.info(f"Pit Crew Status changed: {self.last_state} → {self.state}")
            self.ctx.logger.info(f"Surface:{surface}; OnPitRoad:{on_pit_road}/IDX:{car_idx_on_pit_road}; "
                                 f"PitStopActive:{pitstop_active}; SvStatus:{sv_status}; SvFlags:{sv_flags}.\n")

            # Update our state history and return True so the UI is update aware
            self.last_state = self.state

            # Only return True when a pit cycle is completed
            if self.cycle_completed:
                return True

        return False

    def on_state_change(self, session_time, car_idx_lap):
        self.ctx.logger.info(f"{self.last_state} → {self.state} at {session_time} on Lap {car_idx_lap}.")

        match (self.last_state, self.state):

            # 1. Approaching pits
            case ("ON_TRACK", "APPROACHING_PIT_ENTRY"):
                self.box_box_box(session_time, car_idx_lap)

            # 2. Entering stall
            case ("DRIVING_DOWN_PIT_LANE", "ENTERING_PIT_BOX"):
                self.pit_box_arrival(session_time)

            # 5. Service completes
            case (_, "SERVICE_COMPLETE"):  # from any stall state
                self.service_completed(session_time)

            # 6. Leaving stall
            case ("IN_PIT_BOX_IDLE", "EXITING_PIT_BOX") | \
                 ("SERVICE_COMPLETE", "EXITING_PIT_BOX") | \
                 ("SERVICE_IN_PROGRESS", "EXITING_PIT_BOX"):
                self.leaving_pit_box(session_time)

            # 7. Leaving pit lane
            case ("DRIVING_TO_PIT_EXIT", "EXITING_PIT_LANE"):
                self.leaving_pit_lane(session_time)

            # Optional: cycle finished
            case ("EXITING_PIT_LANE", "BACK_ON_TRACK"):
                self.finish_pit_cycle(session_time)

            case ("BACK_ON_TRACK", "ON_TRACK"):
                if self.cycle_completed:
                    self.reset_pit_cycle()


    # -------------------------------------------------------
    # Stage Change Methods
    # -------------------------------------------------------
    def box_box_box(self, session_time, car_idx_lap):
        """
        Record the initial phase of a pit cycle when the driver is approaching
        the pit entry line ("box, box, box"). This method stores the entry
        time and lap into the current pit-cycle tracking dictionary and logs
        the event for reporting and debugging purposes.

        Parameters
        ----------
        session_time : float
            The current session time when the pit-entry call is detected.
        car_idx_lap : int
            The lap number at which the car is instructed to box.
        """

        # Store into current cycle structure
        self.current_cycle["box_in_time"] = session_time
        self.current_cycle["box_in_lap"] = car_idx_lap

        # Format for logging
        box_in_time_str = self.format.make_time_string(session_time)

        # Logging
        self.ctx.logger.info(
            f"PitCrew: box_box_box at {box_in_time_str} on lap {car_idx_lap}."
        )

    def pit_box_arrival(self, session_time):
        """
        Record the moment the car reaches the pit stall entry point.
        This stores the pit-in (stall arrival) time into the current pit-cycle
        dictionary and logs the event for timing and analysis.

        Parameters
        ----------
        session_time : float
            The session timestamp at which the vehicle crosses into the
            physical pit stall area.
        """

        # Store timestamp in the cycle dictionary
        self.current_cycle["pit_in_time"] = session_time

        # Format for logging
        pit_in_time_str = self.format.make_time_string(session_time)

        # Log event
        self.ctx.logger.info(
            f"PitCrew: Approaching Pit Box at {pit_in_time_str}."
        )

    def in_pit_box(self, session_time, sv_flags, fuel_level, velocity_z, tow_time, repairs, opt_repairs):
        """
        Handle continuous per-tick service logic while the vehicle is inside
        the pit stall. This method is responsible for tracking the start of
        the service window, updating fuel and tyre service data, and ensuring
        that service timing information is stored in the current pit-cycle
        dictionary.

        Parameters
        ----------
        session_time : float
            Current session timestamp for this update tick.
        sv_flags : int
            The active pit-service bitmask (fuel, tyres, etc.).
        fuel_level : float
            The current fuel level of the car used to calculate fuel fill
            rates and quantities.
        velocity_z : float
        """

        # ------------------------------------------------------
        # Update fuel and tyre operations
        # ------------------------------------------------------
        self.fuel_service_update(session_time, sv_flags, fuel_level)
        self.tyre_service_update(session_time, sv_flags)
        self.on_jack_monitoring(session_time, velocity_z=velocity_z)
        self.update_on_repairs(tow_time, repairs, opt_repairs)

        # ------------------------------------------------------
        # Detect the beginning of service inside the stall
        # ------------------------------------------------------
        if not self.current_cycle.get("service_start_time"):
            # Mark when pit service officially begins
            self.current_cycle["service_start_time"] = session_time
            self.ctx.logger.info(
                f"PitCrew: Service window started at {self.format.make_time_string(session_time)}."
            )

    def service_completed(self, session_time):
        """
        Mark the end of pit service operations. This records the service end
        timestamp in the current pit-cycle dictionary and computes the total
        service duration based on the previously stored service start time.

        Parameters
        ----------
        session_time : float
            The session timestamp at which pit service is detected as complete.
        """
        # Record end-of-service timestamp
        self.current_cycle["service_end_time"] = session_time

        # If we never saw a natural final lowering, insert a synthetic one
        if self.current_cycle["on_jacks"] == True or not self.current_cycle["off_jacks_time"]:
            self.current_cycle["off_jacks_time"] = session_time
            self.current_cycle["on_jacks"] = False
            self.ctx.logger.info(f"PitCrew: Artificial Off Jacks completed at {session_time}.")

        # Get a Jack Time Report
        self.get_jack_time_report()

        # Calculate overall service duration (stall-time servicing)
        start = self.current_cycle.get("service_start_time")
        if self.current_cycle:
            self.current_cycle["service_time"] = session_time - start
        else:
            self.current_cycle["service_time"] = 0.0  # fallback, should never happen

        # Log event
        end_str = self.format.make_time_string(session_time)
        self.ctx.logger.info(f"PitCrew: Service completed at {end_str}.")

    def leaving_pit_box(self, session_time):
        """
        Record the moment the car exits its physical pit stall. This method
        stores the pit-out time and computes the total stall stop length
        based on the previously recorded pit-in (stall arrival) time.

        Parameters
        ----------
        session_time : float
            The session timestamp at which the vehicle begins moving out
            of the pit box (stall exit).
        """
        # Store stall-exit timestamp
        self.current_cycle["pit_out_time"] = session_time

        # Compute stop length if pit-in time is available
        pit_in = self.current_cycle.get("pit_in_time")
        if pit_in:
            self.current_cycle["stop_length"] = session_time - pit_in
        else:
            self.current_cycle["stop_length"] = 0.0  # fallback

        # Logging
        pit_out_str = self.format.make_time_string(session_time)
        pit_in_str = self.format.make_time_string(pit_in) if pit_in else "N/A"
        self.ctx.logger.info(
            f"Leaving Pit Box @ {pit_out_str} ({pit_in_str}) "
            f"Total Stop = {self.current_cycle['stop_length']}"
        )

    def leaving_pit_lane(self, session_time):
        """
        Record the moment the car fully exits the pit lane back onto the race
        track. This updates the current pit-cycle dictionary with the final
        pit-lane exit timestamp and computes the overall pit-lane delta
        (entry to exit time).

        Parameters
        ----------
        session_time : float
            The session timestamp when the car leaves the pit lane and
            rejoins the main track.
        """
        # Store pit-lane exit timestamp
        self.current_cycle["back_on_track"] = session_time

        # Compute total pit-lane delta from box-in call to pit-lane exit
        box_in = self.current_cycle["box_in_time"]
        self.current_cycle["total_pit_stop"] = session_time - box_in

        # Logging
        back_str = self.format.make_time_string(session_time)
        box_str = self.format.make_time_string(box_in)

        self.ctx.logger.info(
            f"Leaving Pit Lane at {back_str} ({box_str}) "
            f"Total Delta = {self.current_cycle['total_pit_stop']}"
        )

    def finish_pit_cycle(self, session_time):
        """
        Finalise the pit cycle when the car has fully exited the pit lane.
        Compiles the current_cycle dict into a finished pit stop report,
        appends it to pit_history, and marks the cycle as completed.
        """

        self.current_cycle["back_on_track"] = session_time

        # Compute final totals (safety checks)
        box_in = self.current_cycle.get("box_in_time")
        if box_in is not None:
            self.current_cycle["total_pit_stop"] = session_time - box_in

        # Append a deep copy to history (so future changes don't mutate it)
        self.pit_history.append(copy.deepcopy(self.current_cycle))

        self.ctx.logger.info("Finish Pit Cycle")
        self.ctx.logger.info(f"Stored Pit Cycle #{len(self.pit_history)}")

        # Mark current cycle finished (but DO NOT wipe yet)
        self.cycle_completed = True

    # -------------------------------------------------------
    # Service Monitoring
    # -------------------------------------------------------
    def fuel_service_update(self, session_time, sv_flags, fuel_level):
        """
        Track fuel service progress inside the pit stall. This detects and
        records the start and end of fuel filling, computes fill metrics, and
        stores all fuel-related values inside the current pit-cycle tracking
        dictionary.

        Parameters
        ----------
        session_time : float
            Current session timestamp for this update tick.
        sv_flags : int
            Pit service bitmask including the fuel service flag.
        fuel_level : float
            Current fuel level used to determine fill amount and rate.
        """
        fuel_active = bool(sv_flags & IrConstants.FUEL_FLAG)

        # ------------------------------------------------------------------
        # Fuel START event
        # ------------------------------------------------------------------
        if fuel_active and not self.current_cycle.get("fuel_filling"):
            self.current_cycle["fuel_filling"] = True
            self.current_cycle["fuel_start_time"] = session_time
            self.current_cycle["fuel_start_level"] = fuel_level

            time_str = self.format.make_time_string(session_time)
            self.ctx.logger.info(
                f"PitCrew: Fuel Filling Started at {time_str} "
                f"(Start Level={fuel_level:.2f})"
            )
            return

        # ------------------------------------------------------------------
        # Fuel END event
        # ------------------------------------------------------------------
        if self.current_cycle.get("fuel_filling") and not fuel_active:
            self.current_cycle["fuel_filling"] = False
            self.current_cycle["fuel_end_time"] = session_time
            self.current_cycle["fuel_end_level"] = fuel_level

            # Compute fill metrics
            dt = max(session_time - self.current_cycle["fuel_start_time"], 0.001)
            df = self.current_cycle["fuel_end_level"] - self.current_cycle["fuel_start_level"]

            self.current_cycle["fuel_fill_time"] = dt
            self.current_cycle["fuel_fill_amount"] = df
            self.current_cycle["fuel_per_sec"] = df / dt

            # Optional: call your reporting/logging method
            self.get_fuel_report()

    def tyre_service_update(self, session_time, sv_flags):
        """
        Update tyre service progress based on tyre-related service flags.
        Tracks start time, individual tyre completion timestamps, and the
        overall tyre service duration. All values are stored inside the
        current pit-cycle dictionary.
        """
        tyre_data = self.current_cycle["tyre_data"]

        # Detect whether ANY tyre flag is active
        any_tyre_active = any(sv_flags & bit for bit in IrConstants.TYRE_BITS)

        # ------------------------------------------------------------
        # Tyre service START
        # ------------------------------------------------------------
        if any_tyre_active and not self.current_cycle.get("tyres_changing"):
            self.current_cycle["tyres_changing"] = True
            self.current_cycle["tyres_start_time"] = session_time

            ts = self.format.make_time_string(session_time)
            self.ctx.logger.info(f"PitCrew: Tyre Changes Started at: {ts}")

        # ------------------------------------------------------------
        # Individual tyre completion detection
        # A tyre completes when its flag bit turns OFF.
        # ------------------------------------------------------------
        if self.current_cycle.get("tyres_changing"):
            for tyre_bit in IrConstants.TYRE_BITS:
                tyre_name = IrConstants.TYRE_TO_NAME[tyre_bit]

                # If the bit turned OFF AND we haven't recorded completion yet
                if not (sv_flags & tyre_bit) and tyre_data[tyre_name] is None:
                    tyre_data[tyre_name] = session_time
                    self.ctx.logger.info(f"{tyre_name}-{hex(tyre_bit)}: {session_time}")

        # ------------------------------------------------------------
        # Tyre service END
        # ------------------------------------------------------------
        if self.current_cycle.get("tyres_changing") and not any_tyre_active:
            self.current_cycle["tyres_changing"] = False
            self.current_cycle["tyres_finish_time"] = session_time
            start_time = self.current_cycle.get("tyres_start_time", session_time)
            self.current_cycle["tyre_change_time"] = session_time - start_time

            self.get_tyre_report()

    def on_jack_monitoring(self, session_time, velocity_z):
        """
        Monitor vertical velocity to detect jack lift/lower events.
        Only the FIRST lift time is stored in current_cycle["on_jacks_time"],
        but every up/down transition is logged. This prevents overwriting
        the true start-of-service time even if the car cycles multiple times
        on/off the jacks during a tyre change sequence.
        """

        vel = float(velocity_z)
        on_jacks = self.current_cycle.get("on_jacks", False)

        # ------------------------------------------------------------
        # Detect LIFT (car going up)
        # ------------------------------------------------------------
        if not on_jacks and vel > self.LIFT_THRESHOLD:

            # Mark state
            self.current_cycle["on_jacks"] = True

            # Record FIRST lift only
            if self.current_cycle.get("on_jacks_time") in (None, 0.0):
                self.current_cycle["on_jacks_time"] = session_time
                ts = self.format.make_time_string(session_time)
                self.ctx.logger.info(f"PitCrew: Car lifted onto jacks at {ts}")
            else:
                # Car lifted again later, but don't overwrite the true first lift
                ts = self.format.make_time_string(session_time)
                self.ctx.logger.debug(
                    f"PitCrew: Car lifted again at {ts} (not updating on_jacks_time)"
                )

        # ------------------------------------------------------------
        # Detect DROP (car going down)
        # ------------------------------------------------------------
        elif on_jacks and vel < self.DROP_THRESHOLD:

            self.current_cycle["on_jacks"] = False
            self.current_cycle["off_jacks_time"] = session_time

            ts = self.format.make_time_string(session_time)
            self.ctx.logger.info(f"PitCrew: Car lowered from jacks at {ts}")

    def update_on_repairs(self, tow_time, repairs, opt_repairs):
        """
        Update pit-cycle repair and tow-time tracking. Tow-time and required
        repairs decrease toward zero as they count down, so we store only
        their maximum (initial) values. Optional repairs are tracked both as
        a maximum and as their current remaining value.

        Parameters
        ----------
        tow_time : float
            Current tow-time remaining (counts down to 0).
        repairs : float
            Required repairs remaining (counts down to 0).
        opt_repairs : float
            Optional repairs remaining (counts down to 0).
        """
        # ------------------------------------------------------------
        # Tow time — store maximum value only
        # ------------------------------------------------------------
        if "tow_time" not in self.current_cycle or tow_time > self.current_cycle["tow_time"]:
            self.current_cycle["tow_time"] = tow_time

        # ------------------------------------------------------------
        # Required repairs — store maximum value only
        # ------------------------------------------------------------
        if "repairs" not in self.current_cycle or repairs > self.current_cycle["repairs"]:
            self.current_cycle["repairs"] = repairs

        # ------------------------------------------------------------
        # Optional repairs — store BOTH:
        #   1. the maximum value
        #   2. the current remaining value
        #
        # This allows:
        #   - knowing how many opt repairs were available
        #   - knowing how many remained when leaving the stall
        # ------------------------------------------------------------
        if "opt_repairs_max" not in self.current_cycle or opt_repairs > self.current_cycle["opt_repairs_max"]:
            self.current_cycle["opt_repairs_max"] = opt_repairs

        # always store latest remaining optional repairs
        self.current_cycle["opt_repairs_remaining"] = opt_repairs

    # -------------------------------------------------------
    # Report Methods
    # -------------------------------------------------------
    def get_tyre_report(self):
        """
        Log a summary of tyre changes for the current pit cycle, including
        start/end times, total change duration, and per-tyre timestamps.
        """

        start_time = self.current_cycle.get("tyres_start_time")
        finish_time = self.current_cycle.get("tyres_finish_time")
        total_time = self.current_cycle.get("tyre_change_time")
        tyre_times = self.current_cycle.get("tyre_data", {})

        # Format timestamps safely
        start_str = self.format.make_time_string(start_time) if start_time else "N/A"
        finish_str = self.format.make_time_string(finish_time) if finish_time else "N/A"

        # Overall tyre service summary
        self.ctx.logger.info(
            f"PitCrew: Tyres Finished at: {finish_str} "
            f"(Started at {start_str}, Duration={total_time:.3f}s)"
        )

        # Individual tyre timestamps
        for tyre_name, ts in tyre_times.items():
            ts_str = self.format.make_time_string(ts) if ts else "N/A"
            self.ctx.logger.info(f"PitCrew: Tyre {tyre_name} completed at {ts_str}")

    def get_fuel_report(self):
        """
        Log a summary of the completed fuel fill operation using the
        values stored in the current pit-cycle dictionary.
        """

        end_time = self.current_cycle.get("fuel_end_time")
        duration = self.current_cycle.get("fuel_fill_time")
        amount = self.current_cycle.get("fuel_fill_amount")
        rate = self.current_cycle.get("fuel_per_sec")
        end_level = self.current_cycle.get("fuel_end_level")

        # Use formatted session time string
        end_str = self.format.make_time_string(end_time) if end_time else "N/A"

        self.ctx.logger.info(
            f"PitCrew: Fuel Filling Ended at {end_str} "
            f"(Duration={duration:.3f}s)"
        )

        self.ctx.logger.info(
            f"PitCrew: Fuel Added={amount:.3f}L "
            f"Rate={rate:.3f} L/s "
            f"(Final Level={end_level:.2f})"
        )

    def get_jack_time_report(self):
        """
        Compute and log a summary of jack lift/lower times for the current
        pit cycle. Handles missing values, invalid sequences, and updates
        self.current_cycle["total_jack_time"] when applicable.

        Returns
        -------
        dict
            {
                "on_time": float or None,
                "off_time": float or None,
                "total_jack_time": float,
                "valid": bool
            }
        """

        on_time = self.current_cycle.get("on_jacks_time")
        off_time = self.current_cycle.get("off_jacks_time")

        result = {
            "on_time": on_time,
            "off_time": off_time,
            "total_jack_time": 0.0,
            "valid": False,
        }

        # ------------------------------------------------------------
        # Case 1: No jack data at all
        # ------------------------------------------------------------
        if on_time in (None, 0.0) and off_time in (None, 0.0):
            self.ctx.logger.info(
                "Jack Time: No jack lift or lowering events were recorded for this cycle."
            )
            # Persist zero
            self.current_cycle["total_jack_time"] = 0.0
            return result

        # ------------------------------------------------------------
        # Case 2: Missing first lift
        # ------------------------------------------------------------
        if on_time in (None, 0.0):
            ts = self.format.make_time_string(off_time) if off_time else "N/A"
            self.ctx.logger.warning(
                f"Jack Time: Car lowering was detected at {ts}, "
                "but no initial jack lift was recorded."
            )
            self.current_cycle["total_jack_time"] = 0.0
            return result

        # ------------------------------------------------------------
        # Case 3: Missing final lowering
        # ------------------------------------------------------------
        if off_time in (None, 0.0):
            ts = self.format.make_time_string(on_time)
            self.ctx.logger.warning(
                f"Jack Time: Car was lifted onto jacks at {ts}, "
                "but no lowering event was recorded."
            )
            self.current_cycle["total_jack_time"] = 0.0
            return result

        # ------------------------------------------------------------
        # Case 4: Invalid sequence (off <= on)
        # ------------------------------------------------------------
        if off_time <= on_time:
            on_str = self.format.make_time_string(on_time)
            off_str = self.format.make_time_string(off_time)
            self.ctx.logger.warning(
                f"Jack Time: Invalid jack sequence (up at {on_str}, down at {off_str})."
            )
            self.current_cycle["total_jack_time"] = 0.0
            return result

        # ------------------------------------------------------------
        # Valid jack data → compute duration
        # ------------------------------------------------------------
        total = off_time - on_time
        result["total_jack_time"] = total
        result["valid"] = True

        # Store in the pit-cycle dict
        self.current_cycle["total_jack_time"] = total

        # Format for logging
        on_str = self.format.make_time_string(on_time)
        off_str = self.format.make_time_string(off_time)
        total_str = f"{total:.3f}s"

        # Final log
        self.ctx.logger.info(
            f"Jack Time: Lifted at {on_str}, lowered at {off_str}. "
            f"Total on-jacks time = {total_str}."
        )

        return result

        # ------------------------------------------------------------
        # Compute duration safely
        # ------------------------------------------------------------
        if off_time <= on_time:
            # This state indicates telemetry noise or logic error
            on_str = self.format.make_time_string(on_time)
            off_str = self.format.make_time_string(off_time)
            self.ctx.logger.warning(
                f"Jack Time: Invalid jack timing sequence "
                f"(up at {on_str}, down at {off_str})."
            )
            return

        total = off_time - on_time

        # ------------------------------------------------------------
        # Format output
        # ------------------------------------------------------------
        on_str = self.format.make_time_string(on_time)
        off_str = self.format.make_time_string(off_time)
        total_str = f"{total:.3f}s"

        # ------------------------------------------------------------
        # Log clean report
        # ------------------------------------------------------------
        self.ctx.logger.info(
            f"Jack Time: Lifted at {on_str}, lowered at {off_str}. "
            f"Total on-jacks time = {total_str}."
        )

    def get_completed_pit_report(self):
        """
        Return the most recently completed pit cycle as a dictionary.
        Prefer reading from pit_history to avoid issues if current_cycle
        has already been reset for the next pit stop.

        Returns
        -------
        dict | None
            A deep copy of the most recent completed pit cycle.
        """
        # If we have at least one entry in history, prefer that
        if self.pit_history:
            return copy.deepcopy(self.pit_history[-1])

        # If no history yet but the current cycle is marked completed
        if getattr(self, "cycle_completed", False):
            return copy.deepcopy(self.current_cycle)

        # Nothing completed yet
        return None

    def get_completed_pit_report_pretty(self):
        """
        Return a UI/print-friendly version of the completed pit cycle.
        All timestamps are formatted using make_time_string(), but raw
        numeric values are also preserved.
        """
        report = self.get_completed_pit_report()
        if not report:
            return None

        out = {}
        for key, value in report.items():
            # time fields end in '_time' and should be formatted
            if "time" in key and isinstance(value, (int, float)):
                out[key] = {
                    "raw": value,
                    "formatted": self.format.make_time_string(value)
                }
            else:
                out[key] = value

        return out

    # -------------------------------------------------------
    # TESTING METHODS used during replay/debug development
    # -------------------------------------------------------
    def set_test_mode(self, enabled: bool):
        self.test_mode = enabled

        # Reset simulation when toggled
        if not enabled:
            self.srv_sim_state = None

    def is_in_pit_box(self):
        return self.state in {
            "ENTERING_PIT_BOX",
            "IN_PIT_BOX_IDLE",
            "SERVICE_IN_PROGRESS",
        }

    def simulate_random_srv_flags(self, base_flags=0, sv_status=0):
        """
        Realistic SRV_FLAG simulator.
        Active only when pit crew is in test mode.
        Otherwise returns base_flags unchanged.
        """

        # 1. When not testing → return real data unchanged
        if not self.test_mode:
            return base_flags, sv_status

        # 2. Only simulate when physically in the pit box
        if not self.is_in_pit_box():
            return base_flags, sv_status

        # 2. Run the realistic pit-cycle simulator
        return self.simulate_pit_cycle()

    def simulate_pit_cycle(self):
        import time
        import random

        now = time.time()

        # -----------------------------------------------------------
        # Start a new pit cycle
        # -----------------------------------------------------------
        if self.srv_sim_state is None:
            self.srv_sim_state = {
                "active": True,
                "active_flags": 0,
                "fuel_end_time": now + random.uniform(4.0, 20.0),
                "next_tyre_event": now + random.uniform(1.0, 2.0),
                "tyres_remaining": IrConstants.TYRE_BITS.copy(),
            }

            # Start with fuel + all tyres active
            flags = IrConstants.FUEL_FLAG
            for tyre in IrConstants.TYRE_BITS:
                flags |= tyre

            self.srv_sim_state["active_flags"] = flags
            fuel_end_time = self.format.make_time_string(self.srv_sim_state['fuel_end_time'])
            next_tyre_event = self.format.make_time_string(self.srv_sim_state['next_tyre_event'])
            self.ctx.logger.info(f"[SIM] Fake Pit cycle started: Fuel @ {fuel_end_time} + 4 tyres @ {next_tyre_event} ea.")

            # Status = IN_PROGRESS immediately when services start
            return flags, IrConstants.PIT_SV_IN_PROGRESS

        state = self.srv_sim_state

        # -----------------------------------------------------------
        # If cycle already finished
        # -----------------------------------------------------------
        if not state["active"]:
            return 0, IrConstants.PIT_SV_COMPLETE

        # -----------------------------------------------------------
        # Stop fuel at predefined time
        # -----------------------------------------------------------
        if state["active_flags"] & IrConstants.FUEL_FLAG:
            if now >= state["fuel_end_time"]:
                state["active_flags"] &= ~IrConstants.FUEL_FLAG
                self.ctx.logger.info("[SIM] Fuel service completed.")

        # -----------------------------------------------------------
        # Sequential tyre replacement
        # -----------------------------------------------------------
        if state["tyres_remaining"] and now >= state["next_tyre_event"]:
            tyre = state["tyres_remaining"].pop(0)
            state["active_flags"] &= ~tyre

            tyre_to_name = IrConstants.TYRE_TO_NAME.get(tyre, f"Unknown({tyre})")
            self.ctx.logger.info(f"[SIM] Tyre replaced: {tyre_to_name}")

            state["next_tyre_event"] = now + random.uniform(1.0, 2.0)

        # -----------------------------------------------------------
        # Check if all services are complete
        # -----------------------------------------------------------
        if state["active_flags"] == 0:
            state["active"] = False
            self.ctx.logger.info("[SIM] All pit services completed (TEST MODE).")
            return 0, IrConstants.PIT_SV_COMPLETE

        # Service still in progress
        return state["active_flags"], IrConstants.PIT_SV_IN_PROGRESS


