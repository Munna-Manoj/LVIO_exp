# Set up

Get a working `lvx` on a laptop (docs, specs, reports) and on the compute host (runs).

## 1. Clone with the SE(3)-LVIO submodule

```bash
git clone --recurse-submodules https://github.com/Munna-Manoj/LVIO_exp.git
cd LVIO_exp
git submodule status        # systems/se3-lvio at the commit pinned in systems/systems.yaml
```

## 2. Install lvx

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"            # laptop: specs, reports, checkers, docs
pip install -e ".[dev,eval]"       # compute host: + evo for ATE
lvx exp list                       # -> EXP-000  planned  P0  How large is run-to-run noise, …
```

## 3. Configure this machine (one command, one git-ignored file)

```bash
lvx init --data-root ~/datasets/lvx --run-root ~/lvx_runs \
         --private-token <your-user-name> --private-token <your-host-name>
bash scripts/install_hooks.sh        # refuse commits that contain machine paths or those words
lvx config show
```

This writes `lvx.local.yaml` (template: `configs/local.example.yaml`). It is the **only** file that knows
where things are on this machine. Tracked code asks for datasets and systems **by name**.

> [!WARNING]
> Never put a path, host name or user name in a tracked file, report or commit message. `tools/check_tree.py`
> and the hooks reject machine-specific paths and every `private_tokens` word.

## 4. Download data, then check what each chapter can use

Follow [Get the data](get-the-data.md) and place each dataset at its default folder under `data_root`, or
point lvx at it wherever it already is:

```bash
lvx init --dataset sad-nclt=/path/to/bigdisk/NCLT    # a dataset somewhere else
lvx data check                                        # ✅ ready / ⬜ missing, and the chapters that use each
lvx course status                                     # per chapter: real-data step and C++ labs runnable?
```

Chapters reach data only through `lvx.data.dataset("<name>")`, so once `lvx data check` shows ✅ the matching
chapters just run.

## 5. Build the systems (compute host only)

```bash
# SAD (course C++ labs): build the book code with its Dockerfile, then tell lvx where it is and its image tag
lvx init --system sad.root=/path/to/slam_in_autonomous_driving --system sad.image=<your-local-tag>
lvx lab run sad-ch3-imu-integration                   # runs in a sandbox, records a manifest

# lightning-lm at the pinned commit + our runner
bash scripts/build_lightning.sh
```

> [!TIP]
> The **Build it** track of the course needs none of this: `python course/chapters/B01-imu-propagation/run.py`
> works right after `pip install -e .`.

## 6. Check everything

```bash
ruff check lvx tools tests && pytest -q
python tools/check_tree.py && python tools/check_experiments.py && python tools/check_reports.py
mkdocs serve                                 # docs at http://127.0.0.1:8000
```
