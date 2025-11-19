from math import ceil, floor

from modules.core.app_context import AppContext


class PitStrategist:

    def __init__(self, ctx: AppContext):
        self.ctx = ctx

    @staticmethod
    def calculate_total_laps_on_distance(dist, lap_len):
        total = ceil(dist / lap_len) if lap_len > 0 else 0
        return total

    @staticmethod
    def calculate_total_laps_on_time(total_time, lap_time):
        total = ceil((total_time*60) / lap_time) if lap_time > 0 else 0
        return total

    @staticmethod
    def calculate_adjusted_total_laps(total_laps, target_lap_time, leader_pace):
        """ Calculate the adjusted total laps based on the leaders pace and target lap time """
        race_time_seconds = total_laps * leader_pace
        your_laps = int(race_time_seconds // target_lap_time)
        return your_laps

    @staticmethod
    def calculate_laps_in_tank(total_fuel, fuel_lap):
        return total_fuel / fuel_lap if fuel_lap > 0 else 0

    def get_pit_stop_report(self, total_pit_time, service_time, tank_capacity, tyre_change_time, fuel_lap):
        # Pit Lane Loss (entry → stop → exit) minus the time spent refuelling/tyres
        # i.e., the *fixed time* cost of visiting pit lane
        pit_lane_loss = total_pit_time - service_time if service_time > 0 else 0
        self._debug_log(f"PSR: tpt:{total_pit_time} - st:{service_time} =  pll:{pit_lane_loss};")

        # Refuelling Rate (litres per second)
        # How long the service took based on filling a fuel tank being the longest component
        refuelling_rate = tank_capacity / service_time if service_time > 0 else 0
        self._debug_log(f"PSR: tc:{tank_capacity} / st:{service_time} =  rr:{refuelling_rate};")

        # Litres that can be added during the tyre-change window
        # During tyre change, fuel continues to flow — so this is "free fuel"
        tyre_change_litres = ceil(tyre_change_time * refuelling_rate)
        tyre_change_laps = self.get_free_tyre_laps(tyre_change_litres, fuel_lap)
        self._debug_log(f"PSR: tct:{tyre_change_time} * rr:{refuelling_rate} = tcli:{tyre_change_litres} / tcla:{tyre_change_laps};")

        return pit_lane_loss, refuelling_rate, tyre_change_litres, tyre_change_laps

    @staticmethod
    def get_free_tyre_laps(tyre_change_litres, fuel_lap):
        # Convert that amount of fuel into equivalent laps
        tyre_change_stint = tyre_change_litres / fuel_lap if fuel_lap > 0 else 0
        return tyre_change_stint

    @staticmethod
    def max_stint_laps(tank_capacity, fuel_per_lap):
        max_laps = floor(tank_capacity / fuel_per_lap) if fuel_per_lap > 0 else 0
        return max_laps

    @staticmethod
    def basic_stint_plan(total_laps: int, fuel_per_lap: float, laps_per_stint: float) -> dict:
        """
        :param total_laps:
        :param fuel_per_lap:
        :param laps_per_stint:
        :return:
        """
        stints         = ceil(total_laps / laps_per_stint)
        stops          = stints - 1
        last_stint     = total_laps - (stints - 1) * laps_per_stint
        return {
            "fuel_per_lap": fuel_per_lap,
            "laps_per_stint": laps_per_stint,
            "stints": stints,
            "stops": stops,
            "last_stint_laps": last_stint,
        }

    def calculate_equal_stint_plan(self, total_laps: int, tank_capacity: float, fuel_per_lap: float, tyre_change_litres: float):
        """
        Compute the stint structure so that the last and penultimate stints
        are long enough to afford a free tyre change (i.e. >= required fuel).

        Returns:
            {
                "stints": int,
                "stops": int,
                "laps_for_free_tyres": int,
                "stint_laps": [list of stint lengths]
            }
        """

        # Minimum stint length needed to hide tyre change inside fuelling.
        laps_for_free_tyres = ceil(self.get_free_tyre_laps(tyre_change_litres, fuel_per_lap))

        # Total fuel required across the race
        total_race_fuel = total_laps * fuel_per_lap

        # Required number of stints (fuel-limited)
        stints = ceil(total_race_fuel / tank_capacity)
        stops = stints - 1

        # Start with an even distribution across stints
        base = int(total_laps // stints if stints > 0 else total_laps)
        extra = int(total_laps % stints if stints > 0 else total_laps)

        # Calculate our equal stint area
        stint_laps = [int(base + 1) if i < extra else base for i in range(stints)]

        # Ensure last and penultimate stints meet tyre-change minimum
        # If not, rebalance by moving laps from earlier stints.
        for i in [-1, -2]:  # last and second-last
            while stint_laps[i] < laps_for_free_tyres:
                # take 1 lap from the earliest stint that can spare one
                for j in range(stints - 2):  # avoid touching last two
                    if stint_laps[j] > base:  # only reduce if safe
                        stint_laps[j] -= 1
                        stint_laps[i] += 1
                        break
                else:
                    # fallback: take from any stint except last two
                    for j in range(stints - 2):
                        if stint_laps[j] > 1:
                            stint_laps[j] -= 1
                            stint_laps[i] += 1
                            break

        # Final legality check (every stint must fit in tank) ---
        max_stint_laps = self.max_stint_laps(tank_capacity, fuel_per_lap)

        illegal = []
        for idx, laps in enumerate(stint_laps):
            if laps > max_stint_laps:
                illegal.append({
                    "stint": idx + 1,
                    "laps": laps,
                    "max_legal": max_stint_laps,
                    "fuel_saving_required": laps - max_stint_laps,
                })

        if illegal:
            return {
                "status": "fuel_limited",
                "message": "One or more stints exceed tank capacity using this fuel_per_lap.",
                "max_stint_laps": max_stint_laps,
                "illegal_stints": illegal,
                "suggestion": "Use fuel_per_avg or reduce stint length (driver must fuel save).",
                "stint_laps": stint_laps,
            }

        # For each of the stints calculate the fuel load
        fuel_requirements = [round(laps * fuel_per_lap, 3) for laps in stint_laps]

        return {
            "status": "passed",
            "stints": stints,
            "stops": stops,
            "laps_for_free_tyres": laps_for_free_tyres,
            "stint_laps": stint_laps,
            "fuel_requirements": fuel_requirements,
        }

    def calculate_final_stint_plan(self, total_laps: int, tank_capacity: float,
                                   fuel_per_lap: float, tyre_change_litres: float):

        # Calculate min stint length needed to hide tyre change and max stint length
        laps_for_free_tyres = ceil(self.get_free_tyre_laps(tyre_change_litres, fuel_per_lap))
        max_stint_laps = self.max_stint_laps(tank_capacity, fuel_per_lap)
        self.ctx.logger.debug(f"max_stint_laps: {max_stint_laps}; laps_for_free_tyres: {laps_for_free_tyres}")

        # Calculate full stints and remainder
        full_stints = int(total_laps // max_stint_laps)
        remainder = total_laps % max_stint_laps
        self.ctx.logger.debug(f"full_stints: {full_stints}; remainder: {remainder}")

        if full_stints == 0:
            return {
                "status": "not_enough_laps",
                "message": "Not enough laps for even one full stint.",
                "max_legal_laps": max_stint_laps,
                "total_laps": total_laps,
                "stint_laps": max_stint_laps,
            }

        # Combine the last two stints
        last_two_total = max_stint_laps + remainder

        # Balance them as per our rules
        success, penultimate_stint, last_stint = self.balance_final_stints(last_two_total, laps_for_free_tyres)
        self.ctx.logger.debug(f"{success} penultimate_stint: {penultimate_stint}, last_stint: {last_stint}")


        # --- Fuel legality using unified 'illegal_stints' structure ---
        illegal = []
        for name, laps in (("penultimate", penultimate_stint), ("final", last_stint)):
            if laps > max_stint_laps:
                illegal.append({
                    "stint_name": name,
                    "laps": laps,
                    "max_legal": max_stint_laps,
                    "fuel_saving_required": laps - max_stint_laps,
                })

        if illegal:
            return {
                "status": "fuel_limited",
                "message": "One or more final stints exceed tank capacity.",
                "max_legal_laps": max_stint_laps,
                "fuel_per_lap": fuel_per_lap,
                "tank_capacity": tank_capacity,
                "illegal_stints": illegal,
                "stint_laps": [max_stint_laps] * (full_stints - 1) + [penultimate_stint, last_stint],
                "suggestion": "Use fuel_per_avg or reduce stint length (driver must fuel save).",
            }

        # Build stint plan
        stint_laps = [max_stint_laps] * (full_stints - 1) + [penultimate_stint, last_stint]
        fuel_requirements = [round(laps * fuel_per_lap, 3) for laps in stint_laps]

        return {
            "status": "passed",
            "stints": len(stint_laps),
            "stops": len(stint_laps) - 1,
            "laps_for_free_tyres": laps_for_free_tyres,
            "stint_laps": stint_laps,
            "fuel_requirements": fuel_requirements,
            "last_two_total": last_two_total,
            "last_two": (penultimate_stint, last_stint),
        }

    @staticmethod
    def balance_final_stints(total_laps: int, min_penultimate: int) -> tuple[bool, int, int]:
        """
        Split the final two stints as evenly as possible while ensuring that the
        penultimate stint meets the minimum lap requirement for tyre legality.

        Rules:
            - penultimate_stint should be >= min_penultimate (if mathematically possible)
            - final_stint has no minimum requirement
            - aim for the most even split possible, but legality takes priority

        Returns:
            {
                "status": "ok" | "impossible",
                "penultimate": int,
                "final": int
            }
        """

        # Initial near-even split; penultimate always the longer
        penultimate = int((total_laps + 1) // 2)
        final = int(total_laps - penultimate)

        # If already legal, return early
        if penultimate >= min_penultimate:
            return True, penultimate, final


        # Otherwise, we must pull laps from the final stint
        deficit = min_penultimate - penultimate

        # Number of laps we can transfer from final → penultimate
        transferable = min(deficit, final)

        penultimate += transferable
        final -= transferable

        # Check if we managed to achieve legality
        if penultimate < min_penultimate:
            return False, penultimate, final

        return True, penultimate, final

    def _debug_log(self, message):
        if self.ctx.get("debug"):
            self.ctx.logger.debug(f"[PitStrategist] {message}")
