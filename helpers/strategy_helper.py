# --- 2. Helper Functions ---

import math

class StrategyHelper:
    def __init__(self, tank_capacity, total_laps):
        self.tank_capacity = tank_capacity
        self.total_laps = total_laps

    def stint_plan(self, fuel_per_lap: float, laps_per_stint: float) -> dict:
        stints         = math.ceil(self.total_laps / laps_per_stint)
        stops          = stints - 1
        last_stint     = self.total_laps - (stints - 1) * laps_per_stint
        return {
            "fuel_per_lap": fuel_per_lap,
            "laps_per_stint": laps_per_stint,
            "stints": stints,
            "stops": stops,
            "last_stint_laps": last_stint,
        }

    @staticmethod
    def simulate_laps_with_pits(
            total_race_laps: int,
            leader_lap_time: float,
            leader_pit_loss: float,
            leader_stint_laps: int,
            your_lap_time: float,
            your_pit_loss: float,
            your_stint_laps: int,
    ) -> int:
        """
        Return how many laps YOU complete by the time the LEADER finishes total_race_laps,
        accounting for pit stop time.

        All times in seconds.
        - *_lap_time = normal lap time on track
        - *_pit_loss = total extra time per pit stop (pit lane + service)
        - *_stint_laps = how many laps per fuel tank / stint
        """

        # --- 1) Compute when the leader finishes the race (time in seconds) ---
        leader_time = 0.0
        for lap in range(1, total_race_laps + 1):
            leader_time += leader_lap_time  # lap itself

            # Pit at end of a stint, but not after the final lap
            if lap % leader_stint_laps == 0 and lap != total_race_laps:
                leader_time += leader_pit_loss

        # --- 2) Compute how many laps YOU complete by that time ---
        your_time = 0.0
        your_laps = 0

        lap = 0
        while True:
            # Next lap time
            if your_time + your_lap_time > leader_time:
                break

            lap += 1
            your_laps += 1
            your_time += your_lap_time

            # If this ends a stint, see if there's time to complete the pit loss
            if lap % your_stint_laps == 0:
                if your_time + your_pit_loss > leader_time:
                    break
                your_time += your_pit_loss

        return your_laps

    @staticmethod
    def stint_laps(fuel_per_lap, tank_capacity):
        max_laps = math.floor(tank_capacity / fuel_per_lap)
        return max_laps

    @staticmethod
    def calculate_stint_plan(
            total_laps: int,
            tank_capacity: float,
            fuel_per_lap: float,
            tyre_change_litres: float,
    ):
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
        laps_for_free_tyres = math.ceil(tyre_change_litres / fuel_per_lap)

        # --- 2. Total fuel required ---
        total_fuel = total_laps * fuel_per_lap

        # --- 3. Required number of stints (fuel-limited) ---
        stints = math.ceil(total_fuel / tank_capacity)
        stops = stints - 1

        # --- 4. Start with an even distribution across stints ---
        base = total_laps // stints
        extra = total_laps % stints

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
        max_legal_laps = math.floor(tank_capacity / fuel_per_lap)

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
                "suggestion": (
                    "Use fuel_per_avg or reduce stint length (driver must fuel save)."
                ),
                "stint_laps": stint_laps,
            }

        return {
            "stints": stints,
            "stops": stops,
            "laps_for_free_tyres": laps_for_free_tyres,
            "stint_laps": stint_laps,
        }

    @staticmethod
    def fuel_required_per_stint(laps, fuel_per_lap):
        """
        Return a list of litres of fuel required for each stint.
        """
        return laps * fuel_per_lap


    @staticmethod
    def build_last_two_even_from_full_stint(
            total_laps: int,
            max_stint_laps: int,
            fuel_per_lap: float,
            tyre_change_litres: float,
            tank_capacity: float,
    ):
        """
        Build stints by:
          - taking (N-1) full max stints
          - merging the last full stint + leftover laps
          - splitting them into two even, tyre-compatible stints
        """

        # Minimum laps needed for a free tyre stop
        laps_for_free_tyres = math.ceil(tyre_change_litres / fuel_per_lap)

        # Compute full stints and remainder
        full_stints = total_laps // max_stint_laps  # e.g. 6
        remainder = total_laps % max_stint_laps  # e.g. 5

        # Need at least one full stint + remainder to split
        if full_stints == 0:
            raise ValueError("Not enough laps for even one full stint.")

        # Combine the *last* full stint with the remainder
        last_two_total = max_stint_laps + remainder  # e.g. 28 + 5 = 33

        # Evenly split
        last_stint = last_two_total // 2
        penultimate_stint = last_two_total - last_stint

        # Ensure penultimate >= last (optional aesthetic)
        if penultimate_stint < last_stint:
            penultimate_stint, last_stint = last_stint, penultimate_stint

        # Tyre-change check
        if penultimate_stint < laps_for_free_tyres or last_stint < laps_for_free_tyres:
            raise ValueError(
                f"Cannot create tyre-change-compatible final stints. "
                f"Needed ≥ {laps_for_free_tyres}, got {penultimate_stint}, {last_stint}"
            )

        # Fuel legality
        for laps in (penultimate_stint, last_stint):
            if laps * fuel_per_lap > tank_capacity:
                raise ValueError("Final stints exceed tank capacity.")

        # Build stint list: (full_stints - 1) max stints + 2 final stints
        stint_laps = (
                [max_stint_laps] * (full_stints - 1)
                + [penultimate_stint, last_stint]
        )

        return {
            "stint_laps": stint_laps,
            "full_stints_used": full_stints - 1,
            "last_two_total": last_two_total,
            "last_two": (penultimate_stint, last_stint),
            "laps_for_free_tyres": laps_for_free_tyres,
        }

    @staticmethod
    def format_strategy_summary(s: dict) -> str:
        """Return a list of formatted strategy summary strings."""
        summary_str_list = [
            f"fuel/lap: {s['fuel_per_lap']};",
            f"laps/stint: {s['laps_per_stint']};",
            f"stints: {s['stints']};",
            f"stops: {s['stops']};",
            f"last_stint_laps: {s['last_stint_laps']};",
        ]
        return " ".join(summary_str_list)

    def format_stint_array_results(self, stints: list, fuel_per_avg) -> str:
        """ Loop through the results and output each stint with its length and fuel required.
        :param stints:
        :param fuel_per_avg:
        :return:
        """
        summary_str_list = []
        for i, laps in enumerate(stints, start=1):
            fuel = self.fuel_required_per_stint(laps, fuel_per_avg)
            summary_str_list.append(f"Stint {i}: {laps} laps → {fuel:.2f} L")
        return "\n".join(summary_str_list)

    @staticmethod
    def print_fuel_limited_warning(result: dict):
        """
        Pretty-print a warning if the stint plan is fuel-limited.
        """
        if result.get("status") != "fuel_limited":
            return  # nothing to do

        print("\n⚠️  Fuel-Limited Stint Configuration Detected")
        print("--------------------------------------------------")

        msg = result.get("message", "")
        if msg:
            print(f"{msg}\n")

        max_laps = result.get("max_legal_laps")
        if max_laps is not None:
            print(f"Maximum legal laps per stint at this burn: {max_laps}")

        illegal = result.get("illegal_stints", [])
        if illegal:
            print("\nStints exceeding fuel capacity:")
            for item in illegal:
                stint = item.get("stint")
                laps = item.get("laps")
                max_legal = item.get("max_legal")
                fs = item.get("fuel_saving_required")
                print(f"  • Stint {stint}: {laps} laps (max {max_legal}) -> needs {fs} lap(s) fuel saving")

        suggestion = result.get("suggestion")
        if suggestion:
            print(f"\nSuggestion: {suggestion}")

        print("--------------------------------------------------\n")
