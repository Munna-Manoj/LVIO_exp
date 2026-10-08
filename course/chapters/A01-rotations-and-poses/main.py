"""A01 · Run the three lessons: which side a turn goes on, nudging a rotation vector, and the banana.

python main.py      # about 20 s; prints the output quoted in the README, writes results/
The animations are separate: python live_box.py, python live_walk.py, python live_dots.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np  # noqa: E402

import lesson1_sides  # noqa: E402
import lesson2_jacobian  # noqa: E402
import lesson3_banana  # noqa: E402
import lesson3_walk  # noqa: E402

OUT = Path(__file__).parent / "results"


def v(x, f="{:.2f}"):
    return "(" + ", ".join(f.format(a) for a in x) + ")"


def main():
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(0)
    m = {"box": lesson1_sides.scene_box(OUT, rng), "pose": lesson1_sides.scene_pose(OUT),
         "example": lesson2_jacobian.scene_example(), "arrows": lesson2_jacobian.scene_arrows(OUT),
         "jacobian": lesson2_jacobian.scene_error(OUT, rng),
         "one": lesson3_walk.scene_one_robot(OUT, np.random.default_rng(3)),
         "many": lesson3_walk.scene_many(OUT, rng), "arc": lesson3_walk.scene_exp_arc(OUT),
         "banana": lesson3_banana.scene_recipes(OUT, rng), "knob": lesson3_banana.scene_knob(rng)}
    box, pose, ex, ar, jac = m["box"], m["pose"], m["example"], m["arrows"], m["jacobian"]
    one, many, arc, ban = m["one"], m["many"], m["arc"], m["banana"]
    lines = [
        "LESSON 1  which side: the box faces +y, delta = 40 deg about x",
        f"  nose at the start {v(box['nose_start'])}, after R·Exp(δ) {v(box['nose_right'])}, "
        f"after Exp(δ)·R {v(box['nose_left'])}",
        f"  the two results are {box['right_vs_left_deg']:.1f}° apart; Eq. 5 converts one into the other "
        f"to {box['eq5_max_error']:.1e}",
        "  knob, how the box faces before the turn -> gap: "
        + ", ".join(f"{k}° {g:.1f}°" for k, g in box["gap_by_start_yaw_deg"].items()),
        f"  a pose 10 m from the origin, turned 5°: on the right it moves {pose['right_moved_m']:.2f} m, "
        f"on the left {pose['left_moved_m']:.2f} m",
        "LESSON 2  nudge the rotation vector w = 90 deg about z by 0.01 along x",
        f"  the body really turns by {v(ex['example_exact'], '{:+.5f}')}: {ex['example_shrink']:.2f} times as much, "
        f"tilted {ex['example_tilt_deg']:.1f}°; J_r predicts {v(ex['example_jr'], '{:+.5f}')}",
        "  length of J_r·δ for |w| = " + ", ".join(f"{k}° {a:.2f}" for k, a in ar["arrow_length"].items()),
        f"  error / |δ| without J_r: {jac['plain_at_10deg']:.3f} at 10°, {jac['plain_at_60deg']:.3f} at 60°, "
        f"{jac['plain_at_170deg']:.2f} at 170°; with J_r {jac['jr_at_60deg']:.5f} at 60°",
        f"  knob, nudge along w's own axis at 60°: {jac['along_w_at_60deg']:.5f} without J_r",
        "LESSON 3  one robot, 10 x (walk 1 m, then slip by a random turn, std 6 deg)",
        "  slips (deg): " + " ".join(f"{t:+.1f}" for t in one["turns_deg"]),
        "  facing after each slip (deg): " + " ".join(f"{f:+.1f}" for f in one["facings_deg"][1:]),
        "  corners: " + " ".join(v(c) for c in one["corners"][1:]),
        f"  cos/sin and se3_exp (Eq. 9) agree to {one['cos_sin_vs_se3_max_m']:.0e} m",
        f"2000 robots: facing spread ±{many['facing_std_deg']:.1f}°, end y ±{many['end_y_std_m']:.2f} m, "
        f"distance from the start {many['end_r_mean_m']:.2f} ± {many['end_r_std_m']:.2f} m, "
        f"x as low as {many['end_x_min_m']:.2f} m",
        f"  slips forgotten instead of added up: end y ±{many['forgotten_end_y_std_m']:.2f} m",
        f"  se3_exp, 10 m while turning 20°: ends at {v(arc['arc_end_20deg'])}; turning 40°: {v(arc['arc_end_40deg'])}",
        "the banana, 6-D noise per step (1 cm, 0.5° roll and pitch, 6° yaw):",
        f"  x {ban['x_mean_m']:.2f} ± {ban['x_std_m']:.2f} m, y ± {ban['y_std_m']:.2f} m; "
        f"the x-y average is {ban['mean_gap_cm']:.1f} cm from the nearest robot",
        f"  off the cloud: A (bell curve in x-y, fitted) {ban['off_xy']:.1%}, "
        f"B (over xi, predicted) {ban['off_se3']:.1%}",
        f"  the same draws of xi through SO(3)xR3 (Eq. 11 left): {ban['off_separate']:.1%}",
        f"  one draw: forward {ban['example_xi'][0]:+.2f} m, sideways {ban['example_xi'][1]:+.2f} m, "
        f"yaw {np.degrees(ban['example_xi'][5]):+.1f}° -> SO(3)xR3 {v(ban['example_separate'])}, "
        f"SE(3) {v(ban['example_together'])}",
        f"  Eq. 10 predicts: forward ±{ban['pred_std'][0]:.3f} m, sideways ±{ban['pred_std'][1]:.2f} m, "
        f"yaw ±{np.degrees(ban['pred_std'][5]):.1f}°",
        f"  Monte Carlo / predicted: total {ban['trace_ratio']:.2f}, lateral {ban['lateral_ratio']:.2f}, "
        f"along-track {ban['along_track_ratio']:.1f}",
        "knob, yaw noise per step -> facing doubt after 10 m -> off the cloud SO(3)xR3 / SE(3):",
    ] + [f"  {deg:4.1f}° -> ±{r['facing_std_deg']:4.1f}° -> {r['off_separate']:5.1%} / {r['off_se3']:5.1%}"
         for deg, r in m["knob"].items()]
    text = "\n".join(lines)
    print(text)
    (OUT / "output.txt").write_text(text + "\n")
    (OUT / "metrics.json").write_text(json.dumps(m, indent=2) + "\n")


if __name__ == "__main__":
    main()
