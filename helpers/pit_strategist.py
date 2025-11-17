from math import ceil, floor

from helpers.app_context import AppContext


class PitStrategist:

    def __init__(self, ctx: AppContext):
        self.ctx = ctx

    @staticmethod
    def calculate_total_laps(dist, lap_len):
        total = ceil(dist / lap_len) if lap_len > 0 else 0
        return total

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

        # --- 1. Minimum stint length needed to hide tyre change inside fuelling ---
        laps_for_free_tyres = ceil(self.get_free_tyre_laps(tyre_change_litres, fuel_per_lap))

        # --- 2. Total fuel required ---
        total_fuel = total_laps * fuel_per_lap

        # --- 3. Required number of stints (fuel-limited) ---
        stints = ceil(total_fuel / tank_capacity)
        stops = stints - 1

        # --- 4. Start with an even distribution across stints ---
        base = total_laps // stints if stints > 0 else total_laps
        extra = total_laps % stints if stints > 0 else total_laps

        stint_laps = [
            base + 1 if i < extra else base
            for i in range(stints)
        ]

        # --- 5. Ensure last and penultimate stints meet tyre-change minimum ---
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

        # --- 6. Final legality check (every stint must fit in tank) ---
        max_legal_laps = self.max_stint_laps(tank_capacity, fuel_per_lap)

        illegal = []
        for idx, laps in enumerate(stint_laps):
            if laps > max_legal_laps:
                illegal.append({
                    "stint": idx + 1,
                    "laps": laps,
                    "max_legal": max_legal_laps,
                    "fuel_saving_required": laps - max_legal_laps,
                })

        if illegal:
            return {
                "status": "fuel_limited",
                "message": "One or more stints exceed tank capacity using this fuel_per_lap.",
                "max_legal_laps": max_legal_laps,
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

    def calculate_final_stint_plan(self, total_laps: int, tank_capacity: float, fuel_per_lap: float, tyre_change_litres: float):

        # Calculate the minimum stint length needed to hide tyre change inside fuelling and the maximum stint length
        laps_for_free_tyres = ceil(self.get_free_tyre_laps(tyre_change_litres, fuel_per_lap))
        max_stint_laps = self.max_stint_laps(tank_capacity, fuel_per_lap)

        # Calculate the number of full_stints and any potential splash and dash
        full_stints = total_laps // max_stint_laps
        remainder = total_laps % max_stint_laps

        # If full_stints is zero then we don't have enough laps for anything.
        if full_stints == 0:
            return {
                "status": "not_enough_laps",
                "message": "Not enough laps for even one full stint.",
                 "max_legal_laps": max_stint_laps,
                 "total_laps": total_laps,
                 "stint_laps": max_stint_laps
            }

        # Calculate the total number of laps across the last 2 stints and how they are split
        last_two_total = max_stint_laps + remainder

        # Calculate the split
        last_stint = last_two_total // 2
        penultimate_stint = last_two_total - last_stint

        # Swap them around if the penultimate is less (more allowance for a tyre change
        if penultimate_stint < last_stint:
            penultimate_stint, last_stint = last_stint, penultimate_stint

        # Tyre-change legality
        if penultimate_stint < laps_for_free_tyres or last_stint < laps_for_free_tyres:
            return {
                "status": "tyre_limited",
                "message": "Final two stints too short for a free tyre stop.",
                "max_stint_laps": max_stint_laps,
                "laps_required": laps_for_free_tyres,
                "penultimate": penultimate_stint,
                "final": last_stint,
                "total_laps": total_laps,
                "remainder": remainder,
                "suggestion": "Use fuel_per_avg or reduce stint length (driver must fuel save).",
            }


        # Fuel legality
        for name, laps in (("penultimate", penultimate_stint), ("final", last_stint)):
            if laps * fuel_per_lap > tank_capacity:
                return {
                    "status": "fuel_limited",
                    "message": f"{name.capitalize()} stint exceeds tank capacity.",
                    "laps": laps,
                    "fuel_per_lap": fuel_per_lap,
                    "tank_capacity": tank_capacity,
                    "fuel_required": laps * fuel_per_lap,
                },

        # Build our stint laps list including our equalised final stints.
        stint_laps = [max_stint_laps] * (full_stints - 1) + [penultimate_stint, last_stint]

        # For each of the stints calculate the fuel load
        fuel_requirements = [round(laps * fuel_per_lap, 3) for laps in stint_laps]

        return {
            "status": "passed",
            "stints": len(stint_laps),
            "stops": len(stint_laps) -1,
            "laps_for_free_tyres": laps_for_free_tyres,
            "stint_laps": stint_laps,
            "fuel_requirements": fuel_requirements,
            "last_two_total": last_two_total,
            "last_two": (penultimate_stint, last_stint),
        }

    def _debug_log(self, message):
        if self.ctx.get("debug"):
            self.ctx.logger.debug(f"[PitStrategist] {message}")
