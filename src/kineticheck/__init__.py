"""KinetiCheck public scientific API.

Importing this module never imports Tkinter, Qt, or matplotlib.
"""

from kineticheck.application import evaluate_mapping
from kineticheck.core import (
    ANDERSON_DEFAULT_THRESHOLD,
    MEARS_DEFAULT_THRESHOLD,
    WEISZ_PRATER_DEFAULT_THRESHOLD,
    anderson_internal_heat,
    mears_external_heat,
    mears_external_mass,
    weisz_prater,
)
from kineticheck.models import CriterionResult, ScreeningReport

__all__ = [
    "ANDERSON_DEFAULT_THRESHOLD",
    "MEARS_DEFAULT_THRESHOLD",
    "WEISZ_PRATER_DEFAULT_THRESHOLD",
    "CriterionResult",
    "ScreeningReport",
    "anderson_internal_heat",
    "evaluate_mapping",
    "mears_external_heat",
    "mears_external_mass",
    "weisz_prater",
]

__version__ = "0.1.0"
