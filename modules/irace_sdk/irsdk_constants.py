from dataclasses import dataclass

@dataclass(frozen=True)
class IrConstants:


    PIT_SV_IN_PROGRESS = 1
    PIT_SV_COMPLETE = 2
    PIT_SV_STATUS = {0: "none", 1: "in_progress", 2: "complete", 100: "too_far_left", 101: "too_far_right",
                     102: "too_far_forward", 103: "too_far_back", 104: "bad_angle", 105: "cant_fix_that"}

    # SESSION Encode Dictionaries
    SESSION_NUMBER = {0: "Practice", 1: "Qualifying", 2: "Race", }
    SESSION_STATE = {0: "Invalid", 1: "Get In Car", 2: "Warm Up", 3: "Parade Laps",
                     4: "In Progress", 5: "Checkered", 6: "Cool Down"}

    # IDX Encode Dictionaries

    # From: irsdk_TrkLoc
    IN_PIT_BOX = 1
    ON_PIT_LANE = 2
    TRACK_LOCATION = {-1: "--", 0: "Off", 1: "P.Box", 2: "P.Lne", 3: "Trk"}

    TRACK_SURFACE = {-1: "--", 0: "UN", 1: "A1", 2: "A2", 3: "A3", 4: "A4", 5: "C1", 6: "C2", 7: "RD1", 8: "RD2",
                     9: "P1", 10: "P2", 11: "R1", 12: "R2", 13: "R3", 14: "R4", 15: "G1", 16: "G2",
                     17: "G3", 18: "G4", 19: "D1", 20: "D2", 21: "D3", 22: "D4", 23: "S", 24: "GL1",
                     25: "GL2", 26: "GC", 27: "AT"}

    # WEATHER Encode Dictionaries
    WEATHER_TYPE = {0: "Const", 1: "Dyn"}
    SKY_TYPE = {0: "Clear", 1: "Cloud-", 2: "Cloud+", 3: "Overcast"}

    # CAR Encode Dictionaries
    CAR_LEFT_RIGHT = {1: "clear", 2: "car_left", 3: "car_right", 4: "car_left_right",
                      5: "two_cars_left", 6: "two_cars_right"}

    PACE_MODE = {0: "single_file_start", 1: "double_file_start", 2: "single_file_restart",
                 3: "double_file_restart", 4: "not_pacing"}

    SRV_FLAGS = {0x01: "lf_tire_change", 0x02: "rf_tire_change", 0x04: "lr_tire_change", 0x08: "rr_tire_change",
                 0x10: "fuel_fill", 0x20: "windshield_tearoff", 0x40: "fast_repair"}

    MS2KPH = 3.6

    TRACK_WETNESS = {0: "Unknown", 1: "Dry", 2: "Mostly Dry", 3: "Very Lightly Wet", 4: "Lightly Wet",
                     5: "Moderately Wet", 6: "Very Wet", 7: "Extremely Wet"}