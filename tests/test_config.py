"""Machine configuration: logical names resolve per machine, and nothing machine-specific is tracked."""
import pytest

from lvx import config
from tools import check_tree


def test_datasets_resolve_under_data_root_and_overrides_win(tmp_path, monkeypatch):
    config.write_local({"data_root": str(tmp_path / "d"), "datasets": {"sad-nclt": str(tmp_path / "big" / "NCLT")}})
    assert config.dataset_dir("sad-ulhk") == tmp_path / "d" / "sad" / "ulhk"
    assert config.dataset_dir("sad-nclt") == tmp_path / "big" / "NCLT"
    monkeypatch.setenv("LVX_DATA_ROOT", str(tmp_path / "env"))          # environment beats the file
    assert config.dataset_dir("sad-ulhk") == tmp_path / "env" / "sad" / "ulhk"


def test_missing_dataset_error_names_the_official_source(tmp_path):
    config.write_local({"data_root": str(tmp_path)})
    with pytest.raises(SystemExit) as e:
        config.dataset("sad-ulhk")
    assert "1drv.ms" in str(e.value) and "lvx init --dataset" in str(e.value)
    (tmp_path / "sad" / "ulhk").mkdir(parents=True)
    for f in ("test2.bag", "test3.bag"):
        (tmp_path / "sad" / "ulhk" / f).touch()
    assert config.dataset("sad-ulhk") == tmp_path / "sad" / "ulhk"


def test_unconfigured_machine_says_what_to_do():
    with pytest.raises(SystemExit) as e:
        config.data_root()
    assert "lvx init" in str(e.value)


def test_tracked_images_are_neutral_and_local_tags_override():
    assert config.image("sad").startswith("lvx/")
    config.write_local({"systems": {"sad": {"image": "my-local:tag"}}})
    assert config.image("sad") == "my-local:tag"


def test_tree_has_no_machine_paths_or_private_tokens(monkeypatch):
    assert check_tree.check() == []
    absent = "lvx" + "_never_" + "used_word"                             # never spelled out in any file
    monkeypatch.setattr(check_tree, "private_tokens", lambda: [absent])
    assert check_tree.check() == []                                      # absent word -> still clean
    monkeypatch.setattr(check_tree, "private_tokens", lambda: ["reference"])
    assert any("private token 'reference'" in e for e in check_tree.check())   # present word -> flagged
