"""Shared, GUI-independent result models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class ScreeningStatus(str, Enum):
    """Outcome of a stated screening threshold comparison."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    NOT_EVALUATED = "NOT_EVALUATED"


@dataclass(frozen=True)
class CriterionResult:
    """One dimensionless criterion result with its complete interpretation context."""

    criterion: str
    symbol: str
    value: float
    threshold: float
    status: ScreeningStatus
    equation: str
    convention: str
    reference: str
    assumptions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


@dataclass(frozen=True)
class ScreeningReport:
    """Results for one operating point."""

    run_id: str
    volumetric_rate_mol_m3_s: float
    rate_conversion: str
    results: tuple[CriterionResult, ...]
    warnings: tuple[str, ...] = ()

    @property
    def status(self) -> ScreeningStatus:
        if not self.results:
            return ScreeningStatus.NOT_EVALUATED
        if any(result.status is ScreeningStatus.FAIL for result in self.results):
            return ScreeningStatus.FAIL
        if self.warnings:
            return ScreeningStatus.WARN
        return ScreeningStatus.PASS

    @property
    def interpretation(self) -> str:
        if self.status is ScreeningStatus.FAIL:
            return (
                "At least one selected screening threshold is exceeded under the supplied "
                "assumptions; transport influence should be investigated."
            )
        if self.status is ScreeningStatus.PASS:
            return (
                "No significant limitation was detected by the selected criteria under the "
                "supplied assumptions and input properties. This does not prove intrinsic kinetics."
            )
        if self.status is ScreeningStatus.WARN:
            return (
                "Selected criteria are below their thresholds, but input or scope warnings require "
                "review. This does not prove intrinsic kinetics."
            )
        return "No criterion was evaluated."

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status.value,
            "interpretation": self.interpretation,
            "volumetric_rate_mol_m3_s": self.volumetric_rate_mol_m3_s,
            "rate_conversion": self.rate_conversion,
            "warnings": list(self.warnings),
            "results": [result.to_dict() for result in self.results],
        }
