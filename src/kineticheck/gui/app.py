"""Small Tk/ttk adapter around the shared application service."""

from __future__ import annotations

import argparse
import json
import tempfile
import tkinter as tk
from collections.abc import Sequence
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from kineticheck.application import evaluate_mapping
from kineticheck.models import ScreeningReport


class KinetiCheckApp(ttk.Frame):
    """One-window operating-point screening workflow."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=12)
        self.grid(sticky="nsew")
        self.report: ScreeningReport | None = None
        self.values: dict[str, tk.StringVar] = {}
        self.use_wp = tk.BooleanVar(value=True)
        self.use_mm = tk.BooleanVar(value=True)
        self.use_mh = tk.BooleanVar(value=True)
        self.use_ah = tk.BooleanVar(value=True)
        self._build()

    def _field(
        self,
        parent: ttk.Frame,
        row: int,
        key: str,
        label: str,
        default: str,
        unit: str = "",
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=2)
        variable = tk.StringVar(value=default)
        self.values[key] = variable
        ttk.Entry(parent, textvariable=variable, width=15).grid(
            row=row, column=1, sticky="ew", pady=2
        )
        ttk.Label(parent, text=unit).grid(row=row, column=2, sticky="w", padx=(6, 0), pady=2)

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        title = ttk.Label(
            self,
            text="KinetiCheck — transport-limitation screening",
            font=("TkDefaultFont", 15, "bold"),
        )
        title.grid(row=0, column=0, sticky="w")
        ttk.Label(
            self,
            text="Threshold screens support decisions; they do not prove intrinsic kinetics.",
        ).grid(row=1, column=0, sticky="w", pady=(2, 10))
        notebook = ttk.Notebook(self)
        notebook.grid(row=2, column=0, sticky="nsew")
        self.rowconfigure(2, weight=1)

        common = ttk.Frame(notebook, padding=10)
        notebook.add(common, text="Operating point")
        self._field(common, 0, "run_id", "Run ID", "gui-example")
        self._field(common, 1, "rate", "Observed rate", "0.002", "mol kgcat⁻¹ s⁻¹")
        self._field(common, 2, "density", "Apparent pellet density", "1000", "kg m⁻³")
        self._field(common, 3, "radius", "Particle radius", "1.0", "mm")

        mass = ttk.Frame(notebook, padding=10)
        notebook.add(mass, text="Mass transfer")
        ttk.Checkbutton(mass, text="Weisz–Prater", variable=self.use_wp).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )
        self._field(mass, 1, "deff", "Effective diffusivity", "1e-5", "m² s⁻¹")
        self._field(mass, 2, "surface_c", "Surface concentration", "10", "mol m⁻³")
        ttk.Checkbutton(mass, text="Mears external mass", variable=self.use_mm).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )
        self._field(mass, 4, "order", "Reaction-order magnitude", "1", "")
        self._field(mass, 5, "kc", "Mass-transfer coefficient", "0.02", "m s⁻¹")
        self._field(mass, 6, "bulk_c", "Bulk concentration", "10", "mol m⁻³")

        heat = ttk.Frame(notebook, padding=10)
        notebook.add(heat, text="Heat transfer")
        ttk.Checkbutton(heat, text="Mears external heat", variable=self.use_mh).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )
        self._field(heat, 1, "enthalpy", "Reaction enthalpy", "-100", "kJ mol⁻¹")
        self._field(heat, 2, "activation", "Activation energy", "80", "kJ mol⁻¹")
        self._field(heat, 3, "h", "Heat-transfer coefficient", "250", "W m⁻² K⁻¹")
        self._field(heat, 4, "bulk_t", "Bulk temperature", "600", "K")
        ttk.Checkbutton(heat, text="Anderson internal heat", variable=self.use_ah).grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )
        self._field(heat, 6, "lambda", "Effective pellet conductivity", "0.5", "W m⁻¹ K⁻¹")
        self._field(heat, 7, "surface_t", "Surface temperature", "600", "K")

        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, sticky="ew", pady=10)
        ttk.Button(buttons, text="Evaluate", command=self.calculate).pack(side="left")
        ttk.Button(buttons, text="Export JSON…", command=self.export_dialog).pack(
            side="left", padx=8
        )
        self.status_text = tk.StringVar(value="Ready")
        ttk.Label(buttons, textvariable=self.status_text).pack(side="right")

        self.tree = ttk.Treeview(
            self,
            columns=("criterion", "value", "threshold", "status"),
            show="headings",
            height=5,
        )
        for column, width in (
            ("criterion", 250),
            ("value", 100),
            ("threshold", 100),
            ("status", 80),
        ):
            self.tree.heading(column, text=column.replace("_", " ").title())
            self.tree.column(column, width=width, anchor="w")
        self.tree.grid(row=4, column=0, sticky="nsew")
        self.interpretation = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.interpretation, wraplength=760).grid(
            row=5, column=0, sticky="w", pady=(8, 0)
        )

    def _number(self, key: str) -> float:
        try:
            return float(self.values[key].get())
        except ValueError as error:
            raise ValueError(f"{key} must be numeric") from error

    def payload(self) -> dict[str, object]:
        criteria: dict[str, object] = {}
        if self.use_wp.get():
            criteria["weisz_prater"] = {
                "effective_diffusivity": {"value": self._number("deff"), "unit": "m^2/s"},
                "surface_concentration": {"value": self._number("surface_c"), "unit": "mol/m^3"},
            }
        if self.use_mm.get():
            criteria["mears_mass"] = {
                "reaction_order": self._number("order"),
                "mass_transfer_coefficient": {"value": self._number("kc"), "unit": "m/s"},
                "bulk_concentration": {"value": self._number("bulk_c"), "unit": "mol/m^3"},
            }
        common_heat: dict[str, object] = {
            "reaction_enthalpy": {"value": self._number("enthalpy"), "unit": "kJ/mol"},
            "activation_energy": {"value": self._number("activation"), "unit": "kJ/mol"},
        }
        if self.use_mh.get():
            criteria["mears_heat"] = {
                **common_heat,
                "heat_transfer_coefficient": {"value": self._number("h"), "unit": "W/m^2/K"},
                "bulk_temperature": {"value": self._number("bulk_t"), "unit": "K"},
            }
        if self.use_ah.get():
            criteria["anderson_heat"] = {
                **common_heat,
                "effective_thermal_conductivity": {
                    "value": self._number("lambda"),
                    "unit": "W/m/K",
                },
                "surface_temperature": {"value": self._number("surface_t"), "unit": "K"},
            }
        return {
            "run_id": self.values["run_id"].get(),
            "rate": {
                "value": self._number("rate"),
                "unit": "mol/kg/s",
                "basis": "mass_catalyst",
                "pellet_density": {"value": self._number("density"), "unit": "kg/m^3"},
            },
            "particle_radius": {"value": self._number("radius"), "unit": "mm"},
            "criteria": criteria,
        }

    def calculate(self, *, show_errors: bool = True) -> ScreeningReport | None:
        try:
            report = evaluate_mapping(self.payload())
        except ValueError as error:
            if show_errors:
                messagebox.showerror("KinetiCheck input error", str(error), parent=self)
                return None
            raise
        self.report = report
        self.tree.delete(*self.tree.get_children())
        for result in report.results:
            self.tree.insert(
                "",
                "end",
                values=(
                    result.criterion,
                    f"{result.value:.6g}",
                    f"{result.threshold:.6g}",
                    result.status.value,
                ),
            )
        self.status_text.set(report.status.value)
        self.interpretation.set(report.interpretation)
        return report

    def export_to(self, path: Path) -> None:
        report = self.report
        if report is None:
            report = self.calculate(show_errors=False)
            if report is None:
                raise RuntimeError("evaluation did not produce a report")
        path.write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def export_dialog(self) -> None:
        raw = filedialog.asksaveasfilename(
            parent=self,
            title="Export KinetiCheck result",
            defaultextension=".json",
            filetypes=(("JSON", "*.json"),),
        )
        if not raw:
            return
        try:
            self.export_to(Path(raw))
        except (OSError, ValueError, RuntimeError) as error:
            messagebox.showerror("KinetiCheck export error", str(error), parent=self)


def create_window() -> tuple[tk.Tk, KinetiCheckApp]:
    root = tk.Tk()
    root.title("KinetiCheck")
    root.geometry("820x690")
    root.minsize(700, 580)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    return root, KinetiCheckApp(root)


def run(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m kineticheck.gui")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args(argv)
    root, app = create_window()
    if args.smoke_test:
        root.withdraw()
        with tempfile.TemporaryDirectory(prefix="kineticheck-gui-smoke-") as temporary:
            report = app.calculate(show_errors=False)
            if report is None or len(report.results) != 4:
                raise RuntimeError("GUI smoke did not calculate all four criteria")
            destination = Path(temporary) / "gui-result.json"
            app.export_to(destination)
            if not destination.is_file():
                raise RuntimeError("GUI smoke did not export the result")
        root.update_idletasks()
        root.destroy()
        print("KinetiCheck GUI smoke PASS: window, calculation, export, close")
        return 0
    root.mainloop()
    return 0
