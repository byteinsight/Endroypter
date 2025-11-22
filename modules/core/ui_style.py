from dataclasses import dataclass
from typing import Tuple

Color = Tuple[int, int, int, int]

@dataclass(frozen=True)
class UIStyle:
    """
    Fixed UI style configuration.
    Backwards-compatible conversion of the previous constant class into a dataclass.
    All existing attribute names are preserved.
    """
    TEXT_LIGHT = (240, 240, 240)
    TEXT_DARK  = (35, 35, 35)

    # ---------------------------------------------------------
    # TEAM STAR / BYTE INSIGHT — OFFICIAL COLOR CONSTANTS
    # Extracted from TeamStarByteColors.ase
    # ---------------------------------------------------------

    # Primary Oranges (use PRIMARY_ORANGE_DEFAULT as your main brand orange)
    PRIMARY_ORANGE_LIGHT = (255, 136, 99)  # Primary #FF8863
    PRIMARY_ORANGE_MEDIUM = (255, 105, 57)  # Primary #FF6939  (your "default")
    PRIMARY_ORANGE_STRONG = (243, 61, 4)  # Primary #F33D04
    PRIMARY_ORANGE_DARK = (191, 46, 0)  # Primary #BF2E00
    PRIMARY_ORANGE_DEEP = (150, 36, 0)  # Primary #962400

    PRIMARY_ORANGE_DEFAULT = PRIMARY_ORANGE_STRONG

    # Secondary Blue Set
    SECONDARY_BLUE_LIGHT = (77, 142, 181)  # #4D8EB5
    SECONDARY_BLUE_MEDIUM = (43, 119, 163)  # #2B77A3
    SECONDARY_BLUE_STRONG = (11, 101, 152)  # #0B6598
    SECONDARY_BLUE_VIVID = (7, 71, 250)  # #0747FA
    SECONDARY_BLUE_DARK = (4, 61, 95)  # #043D5F

    # Recommended default
    SECONDARY_BLUE_DEFAULT = SECONDARY_BLUE_STRONG

    # Secondary Green Set
    SECONDARY_GREEN_LIGHT = (164, 235, 91)  # #A4EB5B
    SECONDARY_GREEN_MEDIUM = (141, 230, 51)  # #8DE633
    SECONDARY_GREEN_BRIGHT = (112, 219, 4)  # #70DB04
    SECONDARY_GREEN_STRONG = (87, 172, 0)  # #57AC00
    SECONDARY_GREEN_DARK = (68, 135, 0)  # #448700

    # Recommended default
    SECONDARY_GREEN_DEFAULT = SECONDARY_GREEN_BRIGHT

    # WCAG compliant mapped text colors
    TEXT_ON_PRIMARY_ORANGE  = TEXT_DARK
    TEXT_ON_SECONDARY_BLUE  = TEXT_LIGHT
    TEXT_ON_SECONDARY_GREEN = TEXT_DARK

    # ------------------------------------------------------------
    # ORIGINAL FIELDS (unchanged — preserve compatibility)
    # ------------------------------------------------------------
    HEADER: Color = (220, 220, 255, 255)  # Very Light Periwinkle / Pale Lavender (#DCDCFF)
    WARNING: Color = (255, 120, 120, 255)  # Soft Red / Light Coral (#FF7878)
    WARNING_LABEL: Color = (255, 200, 180, 255)  # Light Peach / Pale Salmon ()
    INFO: Color = (255, 255, 180, 255)  # Soft Yellow / Pastel Yellow (#FFFFB4)
    SUGGESTION: Color = (255, 170, 100, 255)  # Warm Orange / Light Amber (#FFAA64)
    SECTION_LABEL: Color = (230, 230, 230, 255)  # Light Grey / Silver (#E6E6E6)

    # ------------------------------------------------------------
    # NEW EXCEL-STYLE EXTENDED PALETTE
    # Excel-style colour palette following recognised financial modelling
    # conventions: blue for inputs, yellow for outputs, white for calculations,
    # red/orange for warnings, and green for notes.
    #
    # All colours are RGBA tuples (0–255) suitable for DearPyGui.
    # ------------------------------------------------------------

    # -------------------------
    # INPUTS (user-entered data)
    # -------------------------
    INPUT_BG: Color = (191, 239, 255, 255)  # Light blue (#BFEFFF)
    INPUT_TEXT: Color = (0, 0, 0, 255)  # Black

    # -------------------------
    # CALCULATIONS (formulas)
    # -------------------------
    CALC_BG: Color = (255, 255, 255, 255)  # White (#FFFFFF)
    CALC_BG_ALT: Color = (242, 242, 242, 255)  # Light grey (#F2F2F2)
    CALC_TEXT: Color = (0, 0, 0, 255)

    # -------------------------
    # OUTPUTS (highlighted results)
    # -------------------------
    OUTPUT_BG: Color = (255, 242, 204, 255)  # Light yellow (#FFF2CC)
    OUTPUT_TEXT: Color = (0, 0, 0, 255)

    # -------------------------
    # WARNINGS / ERRORS
    # -------------------------
    WARNING_BG: Color = (248, 203, 173, 255)  # Light peach/red (#F8CBAD)
    WARNING_TEXT: Color = (120, 0, 0, 255)  # Dark red

    # -------------------------
    # NOTES / ASSUMPTIONS
    # -------------------------
    NOTE_BG: Color = (226, 240, 217, 255)  # Light green (#E2F0D9)
    NOTE_TEXT: Color = (0, 60, 0, 255)  # Deep green

    # -------------------------
    # STRUCTURAL LABELS
    # -------------------------
    LABEL: Color = (230, 230, 230, 255)  # Neutral grey (#E6E6E6)
    TEXT: Color = (20, 20, 20, 255)

    # -------------------------
    # GENERAL
    # -------------------------
    BORDER_COLOR: Color = (180, 180, 180, 255)
    DISABLED_BG: Color = (210, 210, 210, 255)
    BACKGROUND: Color = (25, 25, 30, 255)


    # -------------------------
    # SESSION SPECIFIC
    # -------------------------
    SESSION_BORDER_COLOR: Color = (180, 180, 180, 255)
    SESSION_BACKGROUND_COLOR: Color = (25, 25, 30, 255)



    # -------------------------
    # TABLE SPACING ETC
    # -------------------------
    TABLE_BORDER: int = 10
    TABLE_CORNER_RADIUS: int = 3
    SPACING_X: int = 4
    SPACING_Y: int = 4

    # Optional helper to get colors as hex
    @staticmethod
    def to_hex(color: Color) -> str:
        r, g, b, _ = color
        return f"#{r:02X}{g:02X}{b:02X}"

