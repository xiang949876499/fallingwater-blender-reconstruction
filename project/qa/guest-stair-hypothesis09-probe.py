"""Numerical C-hypothesis only. Does not import Blender or edit production.

Run with any Python 3.10+. The generated JSON distinguishes source facts,
assumed registration and construction feasibility. No navigation PASS is issued.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa"
SX, SY = 0.05256, 0.05272
RMIN, RMAX, GMIN, GMAX = 0.13, 0.19, 0.25, 0.40
HEAD, RADIUS = 1.95, 0.18
TREAD_THICKNESS, LANDING_THICKNESS = 0.13, 0.21


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


PRODUCTION = [ROOT / "scripts/guest_house.py", ROOT / "scripts/tour.py",
              ROOT / "data/guest_house.json"]
before = {str(p.relative_to(ROOT)): sha(p) for p in PRODUCTION}
source = json.loads((QA / "guest-stair-source09-review.json").read_text(encoding="utf-8"))
data = json.loads((ROOT / "data/guest_house.json").read_text(encoding="utf-8"))
B1, L1, L2 = (data["levels"][k]["offset"] for k in ("B1", "L1", "L2"))


def possibilities(left_length, right_length, low, high):
    out = []
    for nl in range(2, 31):
        for nr in range(2, 31):
            rise = (high - low) / (nl + nr)
            gl, gr = left_length / (nl - 1), right_length / (nr - 1)
            if (RMIN <= rise <= RMAX and GMIN <= gl <= GMAX and GMIN <= gr <= GMAX):
                out.append(dict(left_risers=nl, right_risers=nr, uniform_riser_m=rise,
                                left_going_m=gl, right_going_m=gr,
                                intermediate_z_relative_m=low + nl * rise))
    return out


cases = {}
for name, ly, ry, low, high, note in [
    ("lower_visible_edges", 673.1 - 655.8, 400.8 - 350.0, B1, L1,
     "Uses first-to-last visible B1 edge, not the entire door/landing enclosure."),
    ("lower_enclosure_optimistic", 676.0 - 648.0, 400.8 - 350.0, B1, L1,
     "Sensitivity only: treats the whole enclosure as going length; consumes drawn landing, so not selected."),
    ("upper_visible_nominal", 405.5 - 372.6, 405.5 - 382.0, L1, L2,
     "Approximate visible-outline coordinates; nominal arithmetic failure is smaller than raster uncertainty."),
    ("upper_opening_inclusive_C", 405.5 - 369.0, 405.5 - 382.0, L1, L2,
     "C: north opening cap becomes the start of the hidden/partial left flight; level assignment unproved."),
]:
    lengths = [ly * SY, ry * SY]
    cases[name] = dict(lengths_m=lengths, note=note,
                       feasible=possibilities(*lengths, low, high),
                       riser_count_bounds_from_going=[
                           [math.ceil(1 + ll / GMAX - 1e-12), math.floor(1 + ll / GMIN + 1e-12)]
                           for ll in lengths])

lower = cases["lower_visible_edges"]["feasible"][0]
upper = cases["upper_opening_inclusive_C"]["feasible"][0]
LOW_MID, HIGH_MID = lower["intermediate_z_relative_m"], upper["intermediate_z_relative_m"]
door_wall = next(w for w in data["walls"] if w["id"] == "GUEST_B1_BASE_EAST")
door_t = sum(door_wall["openings"][0]["span"]) / 2
door_y = door_wall["a"][1] + (door_wall["b"][1] - door_wall["a"][1]) * door_t
inset_offset = door_y - 648.0


def flight(fid, sheet, x, y0, y1, width_px, z0, z1, count, lines, evidence, transform_y=0.0):
    return dict(id=fid, source_sheet=sheet, source_start_px=[x, y0], source_end_px=[x, y1],
                source_visible_edge_count=lines, source_line_count_is_riser_count=False,
                tested_start_px=[x, y0 + transform_y], tested_end_px=[x, y1 + transform_y],
                tested_source_width_px=width_px,
                z_start_relative_m=z0, z_end_relative_m=z1,
                z_start_world_m=8.4 + z0, z_end_world_m=8.4 + z1,
                risers=count, goings=count - 1, riser_m=(z1 - z0) / count,
                going_m=abs(y1 - y0) * SY / (count - 1),
                footprint_width_m=width_px * SX,
                geometry_and_storey_assignment_evidence="C",
                reference_evidence=evidence,
                registration_note=("C: B1 inset door station648 aligned to existing modeled door midpoint, not surveyed registration."
                                   if transform_y else "C: sheet01/02 local plan stations overlaid without claiming a surveyed inter-sheet transform."))


flights = [
    flight("F1_B1_LEFT_SOUTH", "guest01 separate B1 inset", 296.25, 655.8, 673.1,
           14.5, B1, LOW_MID, 4, 4,
           "A visible four edges and printed2ft5 width; no explicit UP/DN or B1 datum in crop.", inset_offset),
    flight("F2_LOWER_RIGHT_NORTH", "guest01 first-floor plan", 316.35, 400.8, 350.0,
           15.9, LOW_MID, L1, 9, 10,
           "A UP toward decreasing page Y; assigning its endpoints to lower intermediate/L1 is C."),
    flight("F3_L1_LEFT_SOUTH", "guest02 second-floor plan", 296.75, 369.0, 405.5,
           15.5, L1, HIGH_MID, 8, 7,
           "A continuous UP south and north opening boundary; C includes369..372.6 before visible run."),
    flight("F4_UPPER_RIGHT_NORTH", "guest02 second-floor plan", 316.35, 405.5, 382.0,
           15.9, HIGH_MID, L2, 5, 5,
           "A continuous UP north; C interpretation as final half flight to L2."),
]


def rect(name, xmin, xmax, ymin, ymax, z, thickness, role):
    return dict(name=name, rect_px=[xmin, xmax, min(ymin, ymax), max(ymin, ymax)],
                z_top=z, thickness=thickness, role=role)


def treads(f):
    # N risers at boundaries, N-1 constant-height tread rectangles. Last riser
    # joins the high landing; no additional invisible full tread is appended.
    x, y0 = f["tested_start_px"]
    y1 = f["tested_end_px"][1]
    width = f["tested_source_width_px"]
    n = f["risers"]
    return [rect(f'{f["id"]}_tread_{j:02d}', x - width / 2, x + width / 2,
                 y0 + (y1 - y0) * j / (n - 1), y0 + (y1 - y0) * (j + 1) / (n - 1),
                 f["z_start_relative_m"] + f["riser_m"] * (j + 1),
                 TREAD_THICKNESS, f["id"]) for j in range(n - 1)]


flight_surfaces = {f["id"]: treads(f) for f in flights}
f1_end = flights[0]["tested_end_px"][1]
f1_start = flights[0]["tested_start_px"][1]
platforms = [
    rect("P_B1_DOOR", 289, 303.5, door_y - 4, f1_start, B1, .18, "B1 landing C registration"),
    rect("P_LOWER_LEFT_RETURN", 289, 304.5, f1_end, 400.8, LOW_MID, .21, "C lower return stub"),
    rect("P_LOWER_SOUTH_RETURN", 289, 324.3, 400.8, 414.9, LOW_MID, .21, "C lower return;14.1px depth borrowed, not source datum"),
    rect("P_L1_NORTH", 289, 324.3, 340, 350, L1, .21, "C north landing extent"),
    rect("P_L1_LEFT_APPROACH", 289, 304.5, 350, 369, L1, .21, "C north return approach to upper-left"),
    rect("P_UPPER_SOUTH_RETURN", 289, 324.3, 405.5, 419.6, HIGH_MID, .21, "A drawn return footprint; Z C"),
    rect("P_L2_NORTH", 289, 324.3, 340, 369, L2, .21, "C upper north floor with left opening"),
    rect("P_L2_RIGHT_APPROACH", 308.4, 324.3, 369, 382, L2, .21, "C upper right approach; keeps left stair void"),
]
by_name = {p["name"]: p for p in platforms}
L2_FLOORS = [by_name[n] for n in ("P_L2_NORTH", "P_L2_RIGHT_APPROACH")]
UPPER_WORKS = flight_surfaces[flights[2]["id"]] + flight_surfaces[flights[3]["id"]] + [by_name["P_UPPER_SOUTH_RETURN"]]


def headroom_pairs(walk_surfaces, overhead_surfaces):
    # Exact minimum for each constant-height lower tread centerline and a disk
    # radius .18m against overhead rectangles, not a coarse point sample. This
    # is a numerical envelope, not a mesh/capsule navigation test.
    pairs = []
    for walk in walk_surfaces:
        x0, x1, wy0, wy1 = walk["rect_px"]
        cx = (x0 + x1) / 2
        for ceiling in overhead_surfaces:
            ox0, ox1, oy0, oy1 = ceiling["rect_px"]
            dx_m = max(ox0 - cx, 0, cx - ox1) * SX
            if dx_m > RADIUS:
                continue
            reach_y = math.sqrt(max(0, RADIUS ** 2 - dx_m ** 2)) / SY
            lo, hi = max(wy0, oy0 - reach_y), min(wy1, oy1 + reach_y)
            if hi - lo <= 1e-10:
                continue
            clear = ceiling["z_top"] - ceiling["thickness"] - walk["z_top"]
            pairs.append(dict(walk=walk["name"], overhead=ceiling["name"],
                              available_headroom_m=clear, headroom_margin_m=clear - HEAD,
                              witness_center_px=[cx, (lo + hi) / 2], interval_px=[lo, hi]))
    pairs.sort(key=lambda p: p["available_headroom_m"])
    return dict(minimum=pairs[0] if pairs else None, rectangle_pair_count=len(pairs),
                failed_pairs=[p for p in pairs if p["available_headroom_m"] < HEAD], all_pairs=pairs)


headroom = {
    "lower_left_and_B1_door": headroom_pairs(
        flight_surfaces[flights[0]["id"]] + [by_name["P_B1_DOOR"]],
        UPPER_WORKS + L2_FLOORS + [by_name["P_L1_NORTH"], by_name["P_L1_LEFT_APPROACH"]]),
    "lower_right_and_return": headroom_pairs(
        flight_surfaces[flights[1]["id"]] + [by_name["P_LOWER_LEFT_RETURN"], by_name["P_LOWER_SOUTH_RETURN"]],
        UPPER_WORKS + L2_FLOORS),
    "upper_left_at_L2_north_slab": headroom_pairs(
        flight_surfaces[flights[2]["id"]] + [by_name["P_L1_NORTH"], by_name["P_L1_LEFT_APPROACH"]], L2_FLOORS),
}
limiting = min((h["minimum"] for h in headroom.values() if h["minimum"]), key=lambda p: p["available_headroom_m"])

# Keep unchanged model slabs explicit as contradictions, rather than erasing
# them from the production file or calling the hypothetical clear envelope PASS.
old_slabs = {}
for sid in ("GUEST_L1_HALL_SOUTH", "GUEST_L2_STAIR_TOP_LANDING", "GUEST_L2_STAIR_PASSAGE"):
    s = next(s for s in data["slabs"] if s["id"] == sid)
    xs, ys = zip(*s["polygon"])
    old_slabs[sid] = rect(sid, min(xs), max(xs), min(ys), max(ys),
                          data["levels"][s["level"]]["offset"], s["thickness"], "existing production slab")
context = {
    "lower_return_under_existing_L1_south": headroom_pairs(
        [by_name["P_LOWER_SOUTH_RETURN"]], [old_slabs["GUEST_L1_HALL_SOUTH"]]),
    "upper_return_under_existing_L2_south": headroom_pairs(
        [by_name["P_UPPER_SOUTH_RETURN"]], [old_slabs["GUEST_L2_STAIR_TOP_LANDING"]]),
    "upper_left_under_existing_L2_west_strip": headroom_pairs(
        flight_surfaces[flights[2]["id"]], [old_slabs["GUEST_L2_STAIR_PASSAGE"]]),
    "existing_L1_south_walk_under_new_upper_return": headroom_pairs(
        [old_slabs["GUEST_L1_HALL_SOUTH"]], [by_name["P_UPPER_SOUTH_RETURN"]]),
}

nominal_shortfall = 7 * GMIN - cases["upper_visible_nominal"]["lengths_m"][0]
after = {str(p.relative_to(ROOT)): sha(p) for p in PRODUCTION}
assert before == after, "Shared production changed during numeric probe; rerun against fresh inputs."
assert len(cases["upper_opening_inclusive_C"]["feasible"]) == 1
assert not cases["upper_visible_nominal"]["feasible"]
assert all(not h["failed_pairs"] for h in headroom.values())
assert all(h["failed_pairs"] for h in context.values())

result = {
    "schema_version": 1,
    "date": "2026-09-21",
    "status": "CONDITIONAL_INTRINSIC_NUMERICAL_FEASIBILITY_ONLY; NOT_INSTALLABLE_WITH_UNCHANGED08_SLABS",
    "scope": "Four half-flight C construction hypothesis; no Blender imports, meshes, render, production edit or navigation acceptance.",
    "source_scene_context": {"file": "scene/Fallingwater_iteration08.blend",
                             "sha256_from_frozen08_acceptance": "c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7",
                             "loaded_in_this_numeric_probe": False},
    "sources": {"review": "qa/guest-stair-source09-review.json", "review_sha256": sha(QA / "guest-stair-source09-review.json"),
                "facts": source["facts"], "crop_manifest": "qa/guest-stair-source09-crops.json"},
    "production_hashes_unchanged": before,
    "model_conventions": {
        "units": "meters; relative L1 datum=0; world guest datum+8.4 remains C",
        "source_pixels": "Width1024 normalized, explicitly separate sheets and basement inset. Scales borrowed from existing registration C for this overlay.",
        "scale_m_per_px": [SX, SY],
        "stair_count": "N risers and N-1 going intervals between lowest and highest riser lines; never equate visible raster lines with validated riser count.",
        "riser_interval_m": [RMIN, RMAX], "going_interval_m": [GMIN, GMAX],
        "criterion_evidence": "C explicit design-screen bounds, not a statement of building-code compliance or surveyed original dimensions.",
        "headroom_minimum_m": HEAD, "body_radius_m": RADIUS,
        "threshold_note": "Existing project1.95m/.18m thresholds retained; no clearance relaxation.",
        "assumed_tread_thickness_m": TREAD_THICKNESS, "assumed_landing_thickness_m": LANDING_THICKNESS,
        "thickness_evidence": "C; borrowed current structural thicknesses, not section-proven stair construction.",
        "not_tested": ["actual scene mesh/body collision", "walls/doors/handrails/roof", "platform-to-main connector access", "finish protrusions", "source-confirmed storey assignment"]
    },
    "datums": {"B1_relative_m": B1, "B1_evidence": "C current provisional datum, no numeric label found",
               "L1_relative_m": L1, "L1_evidence": "A printed0ft0in",
               "L2_relative_m": L2, "L2_evidence": "A printed7ft8 5/8in; platform/storey assignment remains C"},
    "integer_enumeration": cases,
    "visible_outline_sensitivity": {
        "extra_left_length_required_for8_risers_at_minimum_going_m": nominal_shortfall,
        "equivalent_px": nominal_shortfall / SY,
        "min_left_start_y_for8_risers": 405.5 - 7 * GMIN / SY,
        "existing_approximate_visible_start_y": 372.6,
        "explicit_opening_inclusive_start_y": 369.0,
        "inference": "Nominal visible-only NO_SOLUTION is not robust to subpixel tracing uncertainty; a0.29423px north shift fits minimum goings without using all the cap. Cannot refute the source hypothesis from this alone."
    },
    "north_cap_source_limit": {
        "actually_viewed_again": "qa/guest-stair-source09-guest02-service.png",
        "drawn_outer_cap_y": 369.0,
        "drawn_inner_cap_or_first_visible_run_y": 372.6,
        "band_depth_m": (372.6 - 369.0) * SY,
        "observed": "The native crop shows an outlined northern cap/frame band, not an unambiguous empty walking strip at the proposed L1 elevation.",
        "candidate_assumption": "C: the cap is a higher-level projected edge and a first riser can sit below it. This is precisely where the hypothetical L2-slab envelope leaves only11.7mm headroom reserve.",
        "acceptance": "U until cap level/solid construction is resolved. Opening-inclusive arithmetic feasibility does not approve using this band or moving/removing the cap."
    },
    "selected_C_flights": flights,
    "intermediate_datums": {
        "lower_selected_relative_m": LOW_MID,
        "lower_feasible_visible_range_m": [min(q["intermediate_z_relative_m"] for q in cases["lower_visible_edges"]["feasible"]), max(q["intermediate_z_relative_m"] for q in cases["lower_visible_edges"]["feasible"])],
        "upper_selected_and_only_opening_inclusive_relative_m": HIGH_MID,
        "evidence": "C numerical outcomes conditional on provisional B1 and stated footprint/going assumptions; not measured platform levels."},
    "registration_C": {
        "B1_inset_door_station_y": 648.0, "existing_model_door_midpoint_plan_y": door_y,
        "selected_inset_to_plan_y_translation_px": inset_offset,
        "selected_flight1_tested_y_interval": [f1_start, f1_end],
        "alternative_align_last_visible_B1_edge_to_G01_right_start_offset_px": 400.8 - 673.1,
        "alternative_would_move_door_from_existing_m": ((648 + 400.8 - 673.1) - door_y) * SY,
        "lower_left_to_right_return_y_difference_m": (400.8 - f1_end) * SY,
        "unresolved": "Existing door preserved numerically, but first/second-floor homologous control alignment and lower return extent remain U. No door moved to fit this hypothesis."},
    "hypothetical_platform_rectangles": platforms,
    "width_and_turn_screen": {
        "B1_printed_finished_width_m": .7366, "B1_body_side_margin_m": (.7366 - 2 * RADIUS) / 2,
        "upper_left_raster_width_m": 15.5 * SX, "upper_right_raster_width_m": 15.9 * SX,
        "drawn_upper_return_depth_m": (419.6 - 405.5) * SY,
        "depth_less_body_diameter_m": (419.6 - 405.5) * SY - 2 * RADIUS,
        "limitation": "Only nominal width/disk-turn envelope; it does not demonstrate whole-room route or 08 actual wall clearance."},
    "intrinsic_headroom_exact_rectangular_envelope": headroom,
    "limiting_intrinsic_headroom": limiting,
    "limiting_slab_thickness_sensitivity": {
        "equation": "L2 - thickness - first_upper_left_riser >=1.95",
        "maximum_combined_slab_and_unmodeled_downward_finish_m": L2 - upper["uniform_riser_m"] - HEAD,
        "selected_slab_m": .21,
        "remaining_downward_finish_allowance_m": L2 - upper["uniform_riser_m"] - HEAD - .21,
        "warning": "Only11.7mm nominal reserve; unverified finish/beam/cap geometry may invalidate candidate. No mesh PASS implied."},
    "unchanged08_context_conflicts": context,
    "decision": {
        "intrinsic_four_half_flights": "CONDITIONALLY_FEASIBLE under explicit C overlay and north floor void hypothesis",
        "unchanged08_construction": "INCOMPATIBLE: three existing flat slabs conflict with the proposed levels",
        "source_confirmation": "U; neither numerical feasibility nor arbitrary slab removal establishes the historical construction",
        "next_gate": "Root decides whether a separate reversible model candidate is justified; resolve actual platform-floor extent/levels, north cap identity, tight north-slab headroom and connector/door access first. This probe authorizes no production edit."
    },
    "independent_numeric_review": {
        "agent": "nav08_semantics",
        "completed": True,
        "confirmed": ["Three lower integer solutions", "Nominal visible upper zero solutions", "Opening-inclusive unique8+5", "15.512mm nominal shortfall is not robust to raster uncertainty", "Old south floors and west return strip conflict with hypothetical midlevels"],
        "additional_implementation_limit": "Current guest stair builder divides run by N and emits N slabs; this numerical study uses N risers with N-1 goings. Do not pass these counts into the old builder unchanged.",
        "work_performed": "Read-only independent arithmetic; no scene meshes, render or production changes."
    },
    "run_provenance": {"script": "qa/guest-stair-hypothesis09-probe.py", "script_sha256": sha(__file__),
                       "numeric_only": True, "blender_used": False, "production_unchanged": before == after},
}
(QA / "guest-stair-hypothesis09.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": result["status"], "counts": {k: len(v["feasible"]) for k, v in cases.items()},
                  "limiting_headroom": limiting,
                  "existing_context_minima": {k: v["minimum"]["available_headroom_m"] for k, v in context.items()},
                  "production_unchanged": before == after}, indent=2))
