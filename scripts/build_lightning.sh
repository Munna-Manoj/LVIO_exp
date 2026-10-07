#!/bin/bash
# Fetch lightning-lm at the pinned commit into $LVX_RUN_ROOT/systems/ and build it with our headless runner.
# Upstream has no licence, so its source never enters this repository (ADR-0003); only this script and
# systems/lightning-lm/* (our files) are tracked.
#   bash scripts/build_lightning.sh            # on the reference host
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
COMMIT=$(python3 -c "import yaml; print(yaml.safe_load(open('$REPO/systems/systems.yaml'))['lightning-lm']['pinned_commit'])")
IMAGE=$(cd "$REPO" && python3 -m lvx config get image lightning-lm)
WS="$(cd "$REPO" && python3 -m lvx config get system-root lightning-lm)/lightning-lm-$COMMIT"   # colcon workspace
DST="$WS/src/lightning-lm"                                          # upstream checkout, binaries land in $DST/bin

if [ ! -d "$DST/.git" ]; then
  mkdir -p "$WS/src"
  git clone https://github.com/gaoxiang12/lightning-lm "$DST"
  git -C "$DST" checkout --detach "$COMMIT"
fi
cp "$REPO/systems/lightning-lm/runner/run_lio_tum.cc" "$DST/src/app/run_lio_tum.cc"
grep -q run_lio_tum "$DST/src/app/CMakeLists.txt" || cat >> "$DST/src/app/CMakeLists.txt" <<'CMK'

# LVIO_exp headless runner (added by scripts/build_lightning.sh)
add_executable(run_lio_tum run_lio_tum.cc)
target_link_libraries(run_lio_tum ${PROJECT_NAME}.libs ${third_party_libs})
CMK

if ! podman image exists "$IMAGE"; then
  cp "$DST/thirdparty/Pangolin-0.9.3.zip" "$REPO/systems/lightning-lm/" 2>/dev/null || true
  podman build -t "$IMAGE" -f "$REPO/systems/lightning-lm/Containerfile" "$REPO/systems/lightning-lm"
  rm -f "$REPO/systems/lightning-lm/Pangolin-0.9.3.zip"
fi
podman run --rm -v "$WS":/ws -w /ws "$IMAGE" bash -c \
  "source /opt/ros/humble/setup.bash && colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release"
test -x "$DST/bin/run_lio_tum" && echo "built $DST/bin/run_lio_tum"
