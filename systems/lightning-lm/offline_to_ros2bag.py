"""comfort_offline -> ROS 2 bag (sqlite3) for lightning-lm: /imu (sensor_msgs/Imu) and /points (PointCloud2, RoboSense layout).

python offline_to_ros2bag.py <comfort_offline> <out_bag_dir> [--imu-dt S] [--min-range M]
Points: x y z intensity (float32) + timestamp (float64, absolute s), header stamp = scan start (file name).
IMU time gets +imu_dt, the same shift se3lio_run.py --imu-dt applies.
"""
import argparse, glob, os
import numpy as np
from rosbags.rosbag2 import Writer
from rosbags.typesys import Stores, get_typestore

XT32 = np.dtype({'names': ['x', 'y', 'z', 'intensity', 'ring', 'timestamp'], 'formats': ['<f4', '<f4', '<f4', '<f4', '<u2', '<f8'],
                 'offsets': [0, 4, 8, 12, 16, 18], 'itemsize': 26})
OUT = np.dtype([('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('intensity', '<f4'), ('timestamp', '<f8')])

ap = argparse.ArgumentParser()
ap.add_argument('offline'); ap.add_argument('out')
ap.add_argument('--imu-dt', type=float, default=0.0)
ap.add_argument('--min-range', type=float, default=0.6)
a = ap.parse_args()

ts = get_typestore(Stores.ROS2_HUMBLE)
Imu, PC2, PF, Hdr, Time = (ts.types[k] for k in ('sensor_msgs/msg/Imu', 'sensor_msgs/msg/PointCloud2', 'sensor_msgs/msg/PointField',
                                                    'std_msgs/msg/Header', 'builtin_interfaces/msg/Time'))
Q, V3 = ts.types['geometry_msgs/msg/Quaternion'], ts.types['geometry_msgs/msg/Vector3']
fields = [PF(name=n, offset=o, datatype=d, count=1) for n, o, d in (('x', 0, 7), ('y', 4, 7), ('z', 8, 7), ('intensity', 12, 7), ('timestamp', 16, 8))]
zero9 = np.zeros(9)

def stamp(ns):
    return Time(sec=int(ns // 1_000_000_000), nanosec=int(ns % 1_000_000_000))

imu = np.loadtxt(os.path.join(a.offline, 'imu.txt'))
imu_ns = (imu[:, 0] + round(a.imu_dt * 1e9)).astype(np.int64)
scans = sorted(glob.glob(os.path.join(a.offline, 'lidar', '*.bin')), key=lambda f: int(os.path.basename(f)[:-4]))
events = [(int(t), 0, i) for i, t in enumerate(imu_ns)] + [(int(os.path.basename(f)[:-4]), 1, i) for i, f in enumerate(scans)]
events.sort()
with Writer(a.out, version=5) as w:
    ci = w.add_connection('/imu', Imu.__msgtype__, typestore=ts)
    cl = w.add_connection('/points', PC2.__msgtype__, typestore=ts)
    for t, kind, i in events:
        if kind == 0:
            r = imu[i]
            m = Imu(header=Hdr(stamp=stamp(t), frame_id='imu'), orientation=Q(x=0., y=0., z=0., w=1.), orientation_covariance=zero9,
                    angular_velocity=V3(x=r[1], y=r[2], z=r[3]), angular_velocity_covariance=zero9,
                    linear_acceleration=V3(x=r[4], y=r[5], z=r[6]), linear_acceleration_covariance=zero9)
            w.write(ci, t, ts.serialize_cdr(m, Imu.__msgtype__))
        else:
            p = np.fromfile(scans[i], dtype=XT32)
            p = p[np.sqrt(p['x'] ** 2 + p['y'] ** 2 + p['z'] ** 2) > a.min_range]
            o = np.empty(len(p), OUT)
            for k in OUT.names:
                o[k] = p[k]
            m = PC2(header=Hdr(stamp=stamp(t), frame_id='lidar'), height=1, width=len(o), fields=fields, is_bigendian=False,
                    point_step=OUT.itemsize, row_step=OUT.itemsize * len(o), data=o.view(np.uint8), is_dense=True)
            w.write(cl, t, ts.serialize_cdr(m, PC2.__msgtype__))
print('imu', len(imu), 'scans', len(scans))
