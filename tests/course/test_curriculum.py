"""The curriculum is consistent, and labs never run inside the SAD tree."""
import subprocess

from lvx import course


def test_curriculum_is_valid_and_ordered():
    assert course.validate() == []


def test_every_book_part_maps_to_sad_chapters():
    cur = course.curriculum()
    covered = sorted({c["sad"]["chapter"] for c in cur["chapters"] if c.get("sad")})
    assert covered == list(range(2, 11))                     # SAD chapters 2-10 all covered


def test_capstone_is_last_and_covers_both_systems():
    ids = [c["id"] for c in course.chapters()]
    assert ids[-4:] == ["X01", "X02", "X03", "X04"]
    titles = " ".join(c["title"] for c in course.chapters() if c["part"] == "X")
    assert "lightning-lm" in titles and "SE(3)-LVIO" in titles


def test_lab_runs_in_a_sandbox_with_read_only_sources(tmp_path, monkeypatch):
    sad = tmp_path / "sad"
    (sad / "bin").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(sad)], check=True)
    monkeypatch.setenv("LVX_SAD_ROOT", str(sad))
    monkeypatch.setenv("LVX_RUN_ROOT", str(tmp_path / "runs"))
    monkeypatch.setenv("LVX_DATA_ROOT", str(tmp_path / "data"))
    ulhk = tmp_path / "data" / "sad" / "ulhk"
    ulhk.mkdir(parents=True)
    for f in ("test2.bag", "test3.bag"):
        (ulhk / f).touch()
    m = course.run_lab("sad-ch7-ndt-lo", dry_run=True)
    cmd = m["command"]
    assert f"{sad}:/sad_src:ro" in cmd                       # SAD tree mounted read-only
    assert f"{ulhk}:/data:ro" in cmd                          # only the lab's dataset, read-only
    assert "/sandbox:/sad" in cmd and "-w /sad" in cmd        # the app's ./data writes land in the sandbox
    assert "--bag_path /data/test2.bag" in cmd
    assert "image" not in {k for k in m if k != "image_id"}   # no local image tag in the record
    assert not (tmp_path / "runs").exists()                   # dry run creates nothing


def test_bridge_chapters_fill_gaps_with_real_data():
    bridges = [c for c in course.chapters() if c.get("kind") == "bridge"]
    assert [c["id"] for c in bridges] == [f"I{i:02d}" for i in range(1, len(bridges) + 1)]   # numbered in order
    for c in bridges:
        assert not c.get("sad")                                   # not in the book
        assert c["datasets"]                                      # always on real data
    ids = [c["id"] for c in course.chapters()]
    assert ids.index("I04") == ids.index("E02") + 1               # placed where the course needs it
