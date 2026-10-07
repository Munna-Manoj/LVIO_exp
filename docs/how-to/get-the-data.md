# Get the data

Where every dataset comes from, how big it is, and where lvx expects it. The authoritative list is
[`configs/datasets.yaml`](https://github.com/Munna-Manoj/LVIO_exp/blob/main/configs/datasets.yaml).

> [!TIP]
> You need **no data** for the course's Build-it track (synthetic). Download only what the chapters you
> are doing use (the "Used by" column).

## Where lvx looks

Each dataset has a default folder under your `data_root` (column "Put it in" below). If a dataset already
lives elsewhere, don't move it; point lvx at it:

```bash
lvx init --data-root ~/datasets/lvx                    # once per machine (git-ignored lvx.local.yaml)
lvx init --dataset grandtour=/path/to/grandtour/missions   # any dataset, anywhere
lvx data check                                         # ✅ ready / ⬜ missing for every dataset
```

Chapters, labs and experiments never contain a path; they name datasets (`sad-ulhk`). Experiments and
labs find them through `lvx`. A chapter takes the folder on the command line, so it stays self-contained:

```bash
cd course/chapters/I01-real-imus-and-allan-variance
python main.py --data "$(lvx config get dataset sad-ulhk)"
```

## All datasets

Generated from `configs/datasets.yaml`. "Used by" lists the course chapters (book chapters, 🔗 bridge
chapters I01–I07, capstone) that read the dataset.

<!-- course:begin datasets -->
| Dataset | What | Size | Put it in (default) | Files lvx checks | Used by |
|---|---|---|---|---|---|
| `sad-builtin` | SAD built-in data (IMU/RTK text, sample PCDs, EPFL registration pairs, map tiles) | 0.7 GB | (ships with SAD) | `ch3/10.txt`, `ch5/*.pcd`, `ch7/EPFL` | B01, B02, I02, B03, B04, C02, C03, D01 |
| `sad-2dmapping` | 2dmapping: 2D LiDAR, shopping mall floors | 0.34 GB | `<data_root>/sad/2dmapping/` | `floor1.bag` | C04, C05 |
| `sad-ulhk` | UrbanLoco (ULHK): 3D LiDAR + IMU, urban roads in Hong Kong ([official](https://github.com/weisongwen/UrbanLoco)) | 13 GB | `<data_root>/sad/ulhk/` | `test2.bag`, `test3.bag` | I01, D03, I03, D04, I07 |
| `sad-wxb` | WXB: 3D LiDAR + IMU, campus | 7.9 GB | `<data_root>/sad/wxb/` | `test1.bag` | D03 |
| `sad-nclt` | NCLT: Velodyne HDL-32 + IMU + RTK, University of Michigan campus ([official](http://robots.engin.umich.edu/nclt/)) | 138 GB | `<data_root>/sad/NCLT/` | `20120115.bag` | E02, I04, E03, F01, F02, I06, F03, G03 |
| `sad-avia` | AVIA: DJI Livox Avia solid-state LiDAR | 1.8 GB | `<data_root>/sad/avia/` | `*.bag` | – (extra) |
| `sad-utbm` | UTBM: 3D LiDAR, roads in France ([official](https://epan-utbm.github.io/utbm_robocar_dataset/)) | 71 GB | `<data_root>/sad/UTBM/` | `*.bag` | – (extra) |
| `grandtour` | GrandTour (ANYmal legged robot): Hesai + Livox + STIM320 IMU + cameras, prism GT by total station ([official](https://grand-tour.leggedrobotics.com/)) | ~10 GB / mission | `<data_root>/grandtour/` | `*_ARC-6_release_*/comfort_offline/imu.txt` | I01, I02, I03, I04, I05, I06, I07, G02, G03 |
<!-- course:end datasets -->

## SAD book datasets

The six SAD datasets are published by the book authors on one share:
**[OneDrive](https://1drv.ms/u/s!AgNFVSzSYXMahcEZejoUwCaHRcactQ?e=YsOYy2)** or
**[Baidu Cloud](https://pan.baidu.com/s/1ELOcF1UTKdfiKBAaXnE8sQ?pwd=feky)** (extraction code `feky`).
See also the [SAD README](https://github.com/gaoxiang12/slam_in_autonomous_driving#datasets).
Unpack them so the folder names match the "Put it in" column.

> [!NOTE]
> NCLT is large (138 GB). One sequence (`20120115.bag`) is enough for every chapter that uses it.

> [!TIP]
> The bridge chapters read the SAD bags straight from Python with `pip install -e ".[data]"` (the `rosbags`
> package): no ROS installation needed.

## GrandTour (capstone and ablation study)

| What | Link |
|---|---|
| Dataset home | [grand-tour.leggedrobotics.com](https://grand-tour.leggedrobotics.com/) |
| Download (HuggingFace) | [leggedrobotics/grand_tour_dataset](https://huggingface.co/datasets/leggedrobotics/grand_tour_dataset) |
| Localization benchmark (COMFORT) | [tasks/localization](https://grand-tour.leggedrobotics.com/tasks/localization) |

Each mission is about 10 GB of LiDAR, IMU, prism GT and one camera. The missions used here are listed
in [`configs/missions.yaml`](https://github.com/Munna-Manoj/LVIO_exp/blob/main/configs/missions.yaml).
Conversion to the `comfort_offline` layout is tracked as ROADMAP M0.5.

## Terms of use

Each dataset has its own licence; read it on the official page before use or redistribution. This
repository never commits dataset files or ground truth (ADR-0006).
