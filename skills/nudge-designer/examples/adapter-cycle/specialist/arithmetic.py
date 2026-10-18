"""Exact local arithmetic for the stipulated synthetic upward throw."""
from fractions import Fraction
import json


u = Fraction(18)
g = Fraction(9)
a = -g


def velocity(t):
    return u + a * t


def displacement(t):
    return u * t + a * t * t / 2


t_top = -u / a
h_top = displacement(t_top)
times = [Fraction(0), Fraction(1), Fraction(19, 10), t_top,
         Fraction(21, 10), Fraction(3)]
v_before = velocity(Fraction(19, 10))
v_after = velocity(Fraction(21, 10))
around_top_acceleration = (v_after - v_before) / Fraction(1, 5)
held_velocity_before = Fraction(0)
held_velocity_after = Fraction(0)
held_acceleration = (held_velocity_after - held_velocity_before) / Fraction(1, 5)

checks = {
    "turning_time_is_2_s": t_top == 2,
    "turning_velocity_is_zero": velocity(t_top) == 0,
    "turning_height_is_18_m": h_top == 18,
    "height_agrees_with_v_squared_relation": h_top == u * u / (2 * g),
    "velocity_before_top_is_positive": v_before > 0,
    "velocity_after_top_is_negative": v_after < 0,
    "change_in_velocity_over_0_2_s_gives_minus_9": around_top_acceleration == -9,
    "held_at_rest_has_zero_acceleration": held_acceleration == 0,
    "same_zero_velocity_different_acceleration": velocity(t_top) == held_velocity_before
        and a != held_acceleration,
}
result = {
    "purpose": "Local arithmetic only; does not establish learner understanding or independent review.",
    "model": {"u_m_per_s": str(u), "g_m_per_s_squared": str(g),
              "a_m_per_s_squared": str(a), "positive_direction": "upward", "drag": "none"},
    "rows": [{"time_s": str(t), "velocity_m_per_s": str(velocity(t)),
              "displacement_m": str(displacement(t)), "acceleration_m_per_s_squared": str(a)}
             for t in times],
    "turning_time_s": str(t_top),
    "turning_height_m": str(h_top),
    "around_top": {"t_before_s": "19/10", "t_after_s": "21/10",
                   "delta_t_s": "1/5", "delta_velocity_m_per_s": str(v_after - v_before),
                   "acceleration_m_per_s_squared": str(around_top_acceleration)},
    "held_at_rest": {"velocity_m_per_s": "0", "acceleration_m_per_s_squared": str(held_acceleration)},
    "checks": checks,
    "status": "PASS" if all(checks.values()) else "FAIL",
}
print(json.dumps(result, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
