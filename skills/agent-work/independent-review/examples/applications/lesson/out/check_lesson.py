"""Disposable exact-arithmetic witness for the local lesson source review.

The reviewer read the page before deriving these checks. This is an arithmetic
and conceptual consistency check, not a learner trial or a blind transfer test.
Run: python /workspace/scratch/52eed2252c51/tmp/ir-forward/lesson/out/check_lesson.py
"""

from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json


SOURCE = Path('/workspace/scratch/52eed2252c51/tmp/ir-forward/lesson/inputs/lesson.md')
OUTPUT = Path(__file__).with_name('calculation-log.json')


def exact(value):
    value = F(value)
    return {'fraction': str(value), 'decimal': float(value)}


def signed_area(v0, acceleration, start, end):
    # Integral of v0 + a*t between the stated times.
    return v0 * (end - start) + acceleration * (end**2 - start**2) / 2


def motion(v0, acceleration, duration):
    end_velocity = v0 + acceleration * duration
    boundaries = [F(0), duration]
    zero = None if acceleration == 0 else -v0 / acceleration
    reverses_inside = zero is not None and 0 < zero < duration
    if reverses_inside:
        boundaries.insert(1, zero)
    areas = [signed_area(v0, acceleration, left, right)
             for left, right in zip(boundaries, boundaries[1:])]
    return {
        'initial_velocity_m_per_s': exact(v0),
        'acceleration_m_per_s_squared': exact(acceleration),
        'duration_s': exact(duration),
        'final_velocity_m_per_s': exact(end_velocity),
        'change_in_velocity_m_per_s': exact(end_velocity - v0),
        'zero_velocity_time_s': None if zero is None else exact(zero),
        'reversal_inside_interval': reverses_inside,
        'signed_interval_displacements_m': [exact(area) for area in areas],
        'signed_displacement_m': exact(sum(areas)),
        'distance_m': exact(sum(abs(area) for area in areas)),
    }


raw = SOURCE.read_bytes()
main = motion(F(3), F(-2), F(4))
zero_acceleration = motion(F(3), F(0), F(4))

# A geometric check uses the two triangles in the velocity-time graph.
turn_time = F(3, 2)
positive_triangle = F(1, 2) * turn_time * F(3)
negative_triangle_magnitude = F(1, 2) * (F(4) - turn_time) * F(5)

# A reviewer-created contrary example checks that a positive acceleration does
# not itself imply rightward motion. It is not included in the candidate and is
# not evidence of learner transfer.
contrary = motion(F(-4), F(1), F(6))

assert main['final_velocity_m_per_s']['fraction'] == '-5'
assert main['change_in_velocity_m_per_s']['fraction'] == '-8'
assert main['zero_velocity_time_s']['fraction'] == '3/2'
assert main['signed_displacement_m']['fraction'] == '-4'
assert main['distance_m']['fraction'] == '17/2'
assert main['reversal_inside_interval']
assert positive_triangle == F(9, 4)
assert negative_triangle_magnitude == F(25, 4)
assert positive_triangle - negative_triangle_magnitude == F(-4)
assert positive_triangle + negative_triangle_magnitude == F(17, 2)
assert zero_acceleration['final_velocity_m_per_s']['fraction'] == '3'
assert zero_acceleration['signed_displacement_m']['fraction'] == '12'
assert zero_acceleration['distance_m']['fraction'] == '12'
assert not zero_acceleration['reversal_inside_interval']
assert contrary['zero_velocity_time_s']['fraction'] == '4'
assert contrary['signed_displacement_m']['fraction'] == '-6'
assert contrary['distance_m']['fraction'] == '10'

log = {
    'executed_utc': datetime.now(timezone.utc).isoformat(),
    'source_path': str(SOURCE),
    'source_sha256': sha256(raw).hexdigest(),
    'method': 'Exact rational integration of linear velocity, split at an internal zero; triangular velocity-time areas cross-check the supplied case.',
    'assumptions': ['One spatial dimension', 'Right is positive', 'Acceleration stays constant over each stated interval', 'Duration begins at t=0'],
    'main_case': main,
    'geometric_cross_check': {
        'rightward_triangle_m': exact(positive_triangle),
        'leftward_triangle_magnitude_m': exact(negative_triangle_magnitude),
        'signed_displacement_m': exact(positive_triangle - negative_triangle_magnitude),
        'distance_m': exact(positive_triangle + negative_triangle_magnitude),
    },
    'conceptual_snapshots': [
        {'t_s': '1/2', 'velocity_m_per_s': '2', 'acceleration_m_per_s_squared': '-2', 'interpretation': 'Moving right and slowing: velocity and acceleration have opposite signs.'},
        {'t_s': '3/2', 'velocity_m_per_s': '0', 'acceleration_m_per_s_squared': '-2', 'interpretation': 'Instantaneously at rest at the turn; acceleration remains nonzero.'},
        {'t_s': '2', 'velocity_m_per_s': '-1', 'acceleration_m_per_s_squared': '-2', 'interpretation': 'Moving left and speeding up: velocity and acceleration have the same sign.'},
    ],
    'zero_acceleration_case': zero_acceleration,
    'reviewer_created_contrary_case': contrary,
    'contrary_interpretation': 'At t=1 s, v=-3 m/s while a=+1 m/s^2: the cart still moves left while its signed velocity increases. Reversal occurs at t=4 s.',
    'unit_check_by_inspection': 'a*t has units m/s; v0*t and a*t^2 each have units m; velocity-time areas have units m.',
    'assertions': 'All 17 arithmetic and interval assertions passed.',
    'limits': 'The original candidate answers were visible before this derivation. No learners, generator, UI, external benchmarks, experiments, or classroom results were tested.',
}
OUTPUT.write_text(json.dumps(log, indent=2) + '\n')
print(json.dumps(log, indent=2))
