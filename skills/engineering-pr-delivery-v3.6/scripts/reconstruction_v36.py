"""Shared continuation instructions, not an examiner or execution controller."""

CONTINUATION_GUIDANCE = """## v3.6 continuation: both modes
No takeover questionnaire, Q1-Q5 exam, agent pass mark or scored admission.
For a selected BuddyRunner, two-pass or three-pass flow, use its native stages
only. Once that flow is completed, additional reconstruction is NOT_APPLICABLE:
reuse its output and continue the next authorized task. Do not add a preliminary
or final reconstruction pass, repeat a closed flow or demand another report.
A generated prompt alone is not a completed flow. Address new facts with a
targeted update; do not reset the whole process.
With a usable Oracle OnBoard Prompt, check essential originals/current candidate
and execute the bounded task within existing authority. Treat its explanation as
revisable: report source-backed corrections, actual results, changed understanding,
remaining parent work and the next justified action. No separate reconstruction
report is needed. This is an optional instruction type, not another mode or role.
Only a cold takeover with neither usable context nor a selected context flow uses
independent source reconstruction. In your own words, connect Owner purpose/amendments to actual
inputs, exact candidate, producer-to-consumer behavior and remaining outcome.
Separate FACT / CLAIM / HYPOTHESIS / UNKNOWN; substantiate decisive claims with
source-backed witnesses and a meaningful contrary check. Reuse valid prior work,
identify drift and high-value improvements, and explain the next bounded action,
its authority, success/failure evidence and remaining integration work.
Check actual checkout/input/tool access early. A missing capability limits its
dependent proof; report the attempt, restriction and next feasible route. Continue
unaffected authorized work. Refer to references/INDEPENDENT_RECONSTRUCTION.md in
the selected v3.6 source for the full method. This text does not execute it, prove
understanding, grant custody or replace product validation and Owner acceptance.
"""
