#!/usr/bin/env python3
"""Seven-page A4 vector PDF for a DISPOSABLE pillar/reveal experiment.

This creates test transfer templates, never final approved fabrication designs.
Paper tiles overlap by 10 mm at world y=140; join paper before tracing card.
Requires reportlab. PDF must be printed at ACTUAL SIZE and measured physically.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
DEFAULT = HERE / "mockup_candidate_v1.json"
INK = (0.07, 0.15, 0.20)
MUTED = (0.30, 0.39, 0.44)
ALERT = (0.61, 0.14, 0.12)


def pt(x):
    return x * mm


def label(c, x, y, text, size=8, color=INK):
    c.setFillColorRGB(*color)
    c.setFont("Helvetica", size)
    c.drawString(pt(x), pt(y), text)


def line(c, x1, y1, x2, y2, width=.3, color=INK, dash=None):
    c.setStrokeColorRGB(*color)
    c.setLineWidth(pt(width))
    c.setDash(dash or [])
    c.line(pt(x1), pt(y1), pt(x2), pt(y2))
    c.setDash([])


def rect(c, x, y, w, h, width=.35, color=INK):
    c.setStrokeColorRGB(*color)
    c.setLineWidth(pt(width))
    c.rect(pt(x), pt(y), pt(w), pt(h), fill=0, stroke=1)


def cross(c, x, y):
    line(c, x-2.5, y, x+2.5, y, .2, MUTED)
    line(c, x, y-2.5, x, y+2.5, .2, MUTED)


def footer(c, n, note, vertical=True):
    label(c, 14, 285, "PUPPET-415-STAGE-01 / TRIAL TEMPLATE / NOT FINAL FABRICATION", 8, ALERT)
    label(c, 14, 279, note, 7, MUTED)
    label(c, 14, 6, f"Sheet {n} | A4 210 x 297 mm | Print at 100%, no fit-to-page", 7, MUTED)
    line(c, 15, 20, 115, 20, .9)
    line(c, 15, 17, 15, 23, .5)
    line(c, 115, 17, 115, 23, .5)
    label(c, 45, 23, "100 mm CHECK", 8)
    if vertical:
        line(c, 177, 22, 177, 72, .7)
        line(c, 174, 22, 180, 22, .5)
        line(c, 174, 72, 180, 72, .5)
        label(c, 182, 48, "50 mm", 7)


def pillar_tile(c, cfg, idx):
    a, b = cfg["template"]["tiled_pillar_regions_y"][idx]
    x0, y0 = 15, 100
    rect(c, x0, y0, 180, b-a, .25, MUTED)
    for x in (0, 180):
        line(c, x0+x, y0, x0+x, y0+b-a, .7)
    for world_y in (0, 280):
        if a <= world_y <= b:
            line(c, x0, y0+world_y-a, x0+180, y0+world_y-a, .7)
    if b > cfg["pillar"]["opening_bottom"] and a < cfg["pillar"]["opening_top"]:
        lo, hi = max(a, cfg["pillar"]["opening_bottom"]), min(b, cfg["pillar"]["opening_top"])
        for x in (20, 160):
            line(c, x0+x, y0+lo-a, x0+x, y0+hi-a, .7)
    for world_y in (cfg["pillar"]["opening_bottom"], cfg["pillar"]["opening_top"]):
        if a <= world_y <= b:
            line(c, x0+20, y0+world_y-a, x0+160, y0+world_y-a, .7)
    if a <= 140 <= b:
        for x in (20, 90, 160):
            cross(c, x0+x, y0+140-a)
        line(c, x0, y0+140-a, x0+180, y0+140-a, .2, MUTED, [2, 2])
    label(c, 15, 260, "PILLAR FRAME - PAPER TILE " + ("LOWER" if idx == 0 else "UPPER"), 11)
    label(c, 15, 254, f"Full pillar: 180 x 280 | World y={a}..{b}; shared 10-mm overlap", 8)
    label(c, 15, 90, "TRANSFER OUTER BORDER; CUT THE INNER OPENING AFTER JOINING TILES", 7)
    label(c, 15, 84, "ALIGN registration crosses at world y=140; tape PAPER only.", 8)
    label(c, 15, 78, "Frame needs >=200 x 300 mm of cardboard or a reinforced joined blank.", 7)
    footer(c, idx+1, "Coordinate transfer, NOT a direct cardboard feed")
    c.showPage()


def doors(c, cfg):
    leaf = cfg["leaves"]
    y = 29  # 237-mm leaves need space above the 100-mm calibration/footer
    label(c, 14, 285, "TWO TEST DOORS - ADJUSTED CLEARANCE FIT", 11)
    label(c, 14, 279, "Outer vertical hinges; doors swing REARWARD; adult cuts.", 8)
    for i, x in enumerate((20, 121)):
        is_left = (i == 0)
        w, h = leaf["width"], leaf["height"]
        rect(c, x, y, w, h, .7)
        hinged_x = x if is_left else x+w
        free_x = x+w if is_left else x
        line(c, hinged_x, y, hinged_x, y+h, 1.3)
        hole_x = free_x-10 if is_left else free_x+10
        hole_y = y + leaf["pull_hole_height_above_leaf_bottom"]
        c.setLineWidth(pt(.35))
        c.circle(pt(hole_x), pt(hole_y), pt(leaf["pull_hole_diameter"]/2), fill=0, stroke=1)
        cross(c, hole_x, hole_y)
        label(c, x+2, y+h-9, ("LEFT" if is_left else "RIGHT") + f"  {w} x {h}", 8)
        label(c, x+2, y+9, "HINGE " + ("LEFT" if is_left else "RIGHT"), 7)
        label(c, x+2, y+128, "PULL: dia 2", 7)
        label(c, x+2, y+123, "10 mm from edge", 7)
    footer(c, 3, "Trial door leaves - do NOT glue doors to frame", vertical=False)
    c.showPage()


def silhouette_gauge(c, cfg, width, page, name):
    label(c, 14, 265, name, 11)
    label(c, 14, 259, "Rectangle only; replace with actual Narasimha cutout for final clearance.", 8)
    x = 59 if width == 92 else 28
    rect(c, x, 65, width, 180, .7)
    label(c, x+15, 155, f"{width} x 180", 10)
    label(c, 14, 54, "NOT a character cutting template. Include real rods before M1 PASS.", 8)
    label(c, 14, 47, "Keep blessing arm DOWN throughout the doorway passage.", 8)
    footer(c, page, "Conservative bounding-envelope trial", vertical=(width == 92))
    c.showPage()


def adult_instructions(c):
    label(c, 14, 280, "PILLAR MOCK-UP: PARENT BUILD ORDER", 13)
    rows = [
        "1. Print on A4 at ACTUAL SIZE (100%); turn off fit-to-page.",
        "2. Measure the 100-mm horizontal and 50-mm vertical calibration.",
        "3. Tape two pillar paper tiles at three world y=140 registration crosses.",
        "4. Transfer full outer 180 x 280 and inner 140 x 240 aperture to card.",
        "5. Adult cuts inner aperture (20-mm posts, 15-mm sill, 25-mm lintel).",
        "6. Cut two door leaves 69 x 237, each with one dia-2 pull hole.",
        "7. Fix outer vertical edges with flexible tape so doors swing rearward.",
        "8. Mount door plane z40, rear wall z150; NEVER glue flush.",
        "9. Keep x305..445 and z15..140 shaft corridor OPEN below stage.",
        "10. Allow 140 mm below baseline; avoid solid floor across rods.",
        "11. Try manual 90-degree opening with soft stops FIRST.",
        "12. Compare one-pull only after manual hold test; check strings.",
        "13. Check 2-mm seam; blessing arm DOWN until fully in front.",
        "14. Run five full reveals with declared operators and hands.",
        "15. STOP for unstable stand, trapped rod or visible hidden N.",
    ]
    y = 264
    for text in rows:
        label(c, 14, y, text, 8)
        y -= 13
    label(c, 14, 58, "SAFETY: adult cutting/punching, blunt rods, gentle pull, no springs.", 8, ALERT)
    label(c, 14, 48, "Paper template passes do not establish physical prototype acceptance.", 8, ALERT)
    footer(c, 6, "This is a disposable first mock-up, not a final puppet kit")
    c.showPage()


def test_receipt(c):
    label(c, 14, 280, "STAGE-01 TEST RECEIPT - PHYSICAL OBSERVATIONS", 12)
    label(c, 14, 270, "Date: ______  Operator count: ____   Material thickness: _____", 8)
    label(c, 14, 263, "Puppet source: __________   Kit revision: __________________", 8)
    tests = [
        ("M1", "Passage incl rods", ">=10 mm actual gap"),
        ("M2", "Five reveal cycles", "5/5 smooth; doors stay open"),
        ("M3", "Handoff and hands", "No unassigned helper"),
        ("M4", "Concealment", "Invisible from class seats"),
        ("M5", "Prahlada 15-20 degree bow", ">=10 mm real gap"),
        ("M6", "King tap/exit", "3 gestures, clear exit"),
        ("M7", "Open shaft corridor", "140 mm below + 110 mm travel"),
        ("M8", "1:15-1:25 reveal", "N visible by 1:25"),
        ("M9", "Full 180-second show", "Separate later gate"),
    ]
    y = 248
    for task, label_text, criterion in tests:
        label(c, 14, y, task + " " + label_text + " | " + criterion, 7.5)
        label(c, 18, y-6, "PASS/FAIL/NOT_RUN: ____  Measurements / observations: _________________", 7)
        y -= 21
    label(c, 14, 53, "STOP on failed M1-M3. Revise geometry or handoff before final art.", 8, ALERT)
    label(c, 14, 45, "Blank fields mean NOT_RUN; no manufacturing approval granted.", 8, ALERT)
    footer(c, 7, "Document real measurements and actual operator count")
    c.showPage()


def validate(cfg):
    p, leaf, t = cfg["pillar"], cfg["leaves"], cfg["template"]
    assert p["outer_width"] == 180 and p["outer_height"] == 280
    assert p["opening_right"] - p["opening_left"] == 140
    assert p["opening_top"] - p["opening_bottom"] == 240
    assert 2*leaf["width"] < 140
    assert leaf["height"] < 240
    assert math.isclose(140-2*leaf["width"], leaf["nominal_center_seam_gap"])
    assert math.isclose(240-leaf["height"], leaf["clearance_under_lintel"]+leaf["clearance_above_sill"])
    assert t["tiled_pillar_regions_y"] == [[0, 145], [135, 280]]
    assert leaf["height"] == 237
    assert p["outer_height"] - p["opening_top"] >= 25
    assert t["overlap"] == 10 and t["calibration_bar_mm"] == 100


def build(cfg, out):
    validate(cfg)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out), pagesize=A4, pageCompression=1, invariant=1)
    c.setTitle("PUPPET-415-STAGE-01 disposable full-scale pillar mock-up")
    c.setAuthor("Candidate source / not manufacturing approved")
    for idx in range(2):
        pillar_tile(c, cfg, idx)
    doors(c, cfg)
    silhouette_gauge(c, cfg, 92, 4, "NARASIMHA ARM-DOWN PASSAGE ENVELOPE")
    silhouette_gauge(c, cfg, 155, 5, "NARASIMHA BLESSING-POSE ENVELOPE")
    adult_instructions(c)
    test_receipt(c)
    c.save()
    return out


if __name__ == "__main__":
    cfg = json.loads(Path(sys.argv[1] if len(sys.argv)>1 else DEFAULT).read_text())
    out = Path(sys.argv[2] if len(sys.argv)>2 else HERE / "STAGE01_MOCKUP_TRIAL_100pct_A4.pdf")
    print(build(cfg, out))
