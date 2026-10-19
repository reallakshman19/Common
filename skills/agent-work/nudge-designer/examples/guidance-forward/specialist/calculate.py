"""Reproduce the supplied uniform-bar reference using exact arithmetic.

This is an arithmetic check, not a finite-element solver or bucket assessment.
Run with: PYTHONDONTWRITEBYTECODE=1 python -B calculate.py
"""

from fractions import Fraction
import hashlib
import json
from pathlib import Path


def quantity(value, unit):
    value = Fraction(value)
    return {"exact": str(value), "value": float(value), "unit": unit}


case_path = Path(__file__).with_name("case.md")
case_sha256 = hashlib.sha256(case_path.read_bytes()).hexdigest()

# Original stipulated magnitudes; millimetre-newton convention.
length_mm = Fraction(900)
area_mm2 = Fraction(250)
modulus_GPa = Fraction(160)
load_kN = Fraction(18)
load_N = load_kN * 1000
modulus_N_per_mm2 = modulus_GPa * 1000

stress_N_per_mm2 = load_N / area_mm2
strain = stress_N_per_mm2 / modulus_N_per_mm2
extension_mm = load_N * length_mm / (area_mm2 * modulus_N_per_mm2)

# Same idealization evaluated in SI units and via stress -> strain -> extension.
length_m = length_mm / 1000
area_m2 = area_mm2 / 1_000_000
modulus_Pa = modulus_GPa * 1_000_000_000
extension_SI_m = load_N * length_m / (area_m2 * modulus_Pa)
extension_via_strain_mm = strain * length_mm

# A meaningful contrast: the unsupported handover modulus replaces a given.
handover_modulus_GPa = Fraction(200)
handover_extension_mm = load_N * length_mm / (
    area_mm2 * handover_modulus_GPa * 1000
)
reported_extension_mm = Fraction("0.324")
implied_modulus_GPa = (
    load_N * length_mm / (area_mm2 * reported_extension_mm) / 1000
)
relative_extension_change = (handover_extension_mm - extension_mm) / extension_mm

checks = {
    "stress_equals_72_MPa": stress_N_per_mm2 == 72,
    "strain_equals_0_00045": strain == Fraction("0.00045"),
    "original_extension_equals_0_405_mm": extension_mm == Fraction("0.405"),
    "SI_and_mm_calculations_agree_exactly": extension_SI_m * 1000 == extension_mm,
    "stress_strain_and_direct_calculations_agree_exactly": (
        extension_via_strain_mm == extension_mm
    ),
    "zero_load_gives_zero_extension": (
        Fraction(0) * length_mm / (area_mm2 * modulus_N_per_mm2) == 0
    ),
    "double_load_doubles_extension": (
        2 * load_N * length_mm / (area_mm2 * modulus_N_per_mm2)
        == 2 * extension_mm
    ),
    "200_GPa_gives_0_324_mm": handover_extension_mm == reported_extension_mm,
    "reported_0_324_mm_does_not_equal_original_reference": (
        reported_extension_mm != extension_mm
    ),
    "modulus_change_does_not_change_uniform_axial_stress": (
        load_N / area_mm2 == stress_N_per_mm2
    ),
}

report = {
    "scope": "Executed exact rational arithmetic for the supplied ideal axial bar only",
    "source": {"path": "case.md", "sha256": case_sha256},
    "convention": "Magnitudes; N, mm, N/mm^2. 1 N/mm^2 = 1 MPa.",
    "relations": {
        "stress": "sigma = P/A",
        "strain": "epsilon = sigma/E",
        "displacement": "u(x) = P*x/(A*E), u(0)=0",
        "free_end_extension": "delta = P*L/(A*E)",
    },
    "inputs": {
        "length": quantity(length_mm, "mm"),
        "area": quantity(area_mm2, "mm^2"),
        "modulus": quantity(modulus_GPa, "GPa"),
        "load": quantity(load_kN, "kN"),
        "load_converted": quantity(load_N, "N"),
        "modulus_converted": quantity(modulus_N_per_mm2, "N/mm^2"),
        "length_SI": quantity(length_m, "m"),
        "area_SI": quantity(area_m2, "m^2"),
        "modulus_SI": quantity(modulus_Pa, "Pa"),
    },
    "original_reference": {
        "stress": quantity(stress_N_per_mm2, "MPa"),
        "strain": quantity(strain, "dimensionless"),
        "extension": quantity(extension_mm, "mm"),
        "extension_SI": quantity(extension_SI_m, "m"),
        "extension_via_strain": quantity(extension_via_strain_mm, "mm"),
        "double_load_extension": quantity(2 * extension_mm, "mm"),
    },
    "handover_contrast": {
        "substituted_modulus": quantity(handover_modulus_GPa, "GPa"),
        "conditional_extension": quantity(handover_extension_mm, "mm"),
        "reported_extension": quantity(reported_extension_mm, "mm"),
        "conditional_implied_modulus": quantity(implied_modulus_GPa, "GPa"),
        "extension_difference_from_original": quantity(
            handover_extension_mm - extension_mm, "mm"
        ),
        "relative_extension_change": quantity(relative_extension_change, "dimensionless"),
        "stress_for_same_P_and_A": quantity(stress_N_per_mm2, "MPa"),
        "limit": "Numerical consistency under identical ideal-bar inputs does not identify the cause of unseen screenshots.",
    },
    "checks": checks,
    "all_checks_pass": all(checks.values()),
    "execution_limits": {
        "solver_run": "NOT_RUN",
        "screenshots_inspected": "NONE_SUPPLIED",
        "bucket_geometry_or_root_stress_evaluated": False,
        "independent_domain_review": "NOT_PERFORMED",
        "host_model": "UNKNOWN",
        "reasoning_effort": "UNKNOWN",
        "formal_qualification": "UNKNOWN",
        "engineering_acceptance_authority": "NOT_ASSIGNED",
    },
}

print(json.dumps(report, indent=2, sort_keys=True))
if not all(checks.values()):
    raise SystemExit(1)
