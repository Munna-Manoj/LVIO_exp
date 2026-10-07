// Headless LIO frontend: reads /imu and /points from a ROS 2 bag and writes one IMU pose per scan (TUM, lidar end time).
// Same calls as run_frontend_offline.cc, without the Pangolin UI and the grid map.
// --timing writes stamp,ms,rss_mb per scan (ProcessPointCloud2 + Run wall time), the same columns lvx reads from SE(3)-LVIO.
#include <gflags/gflags.h>
#include <glog/logging.h>
#include <sys/resource.h>

#include <chrono>
#include <fstream>
#include <iomanip>

#include "core/lio/laser_mapping.h"
#include "wrapper/bag_io.h"
#include "wrapper/ros_utils.h"

DEFINE_string(input_bag, "", "ROS 2 bag");
DEFINE_string(config, "", "config yaml");
DEFINE_string(output, "lio.tum", "TUM output: t x y z qx qy qz qw (IMU frame)");
DEFINE_string(timing, "", "optional CSV: stamp,ms,rss_mb per scan");

static double PeakRssMb() {
    rusage u{};
    getrusage(RUSAGE_SELF, &u);
    return u.ru_maxrss / 1024.0;  // Linux: kB
}

int main(int argc, char** argv) {
    google::InitGoogleLogging(argv[0]);
    FLAGS_stderrthreshold = google::WARNING;
    google::ParseCommandLineFlags(&argc, &argv, true);
    using namespace lightning;

    RosbagIO rosbag(FLAGS_input_bag);
    LaserMapping lio;
    if (!lio.Init(FLAGS_config)) return -1;

    std::ofstream out(FLAGS_output);
    out << std::fixed << std::setprecision(9);
    std::ofstream timing;
    if (!FLAGS_timing.empty()) {
        timing.open(FLAGS_timing);
        timing << "stamp,ms,rss_mb\n" << std::fixed;
    }
    double last_t = -1;
    int scans = 0;
    rosbag
        .AddImuHandle("/imu", [&lio](IMUPtr imu) { lio.ProcessIMU(imu); return true; })
        .AddPointCloud2Handle("/points",
                              [&](sensor_msgs::msg::PointCloud2::SharedPtr cloud) {
                                  const auto t0 = std::chrono::steady_clock::now();
                                  lio.ProcessPointCloud2(cloud);
                                  const bool ok = lio.Run();
                                  const double ms =
                                      std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
                                  if (!ok) return true;
                                  const NavState s = lio.GetState();
                                  if (timing.is_open())
                                      timing << std::setprecision(9) << s.timestamp_ << "," << std::setprecision(3) << ms
                                             << "," << std::setprecision(0) << PeakRssMb() << "\n";
                                  if (s.timestamp_ <= last_t) return true;
                                  last_t = s.timestamp_;
                                  const SE3 T = s.GetPose();
                                  const Eigen::Quaterniond q = T.unit_quaternion();
                                  out << s.timestamp_ << " " << T.translation().x() << " " << T.translation().y() << " "
                                      << T.translation().z() << " " << q.x() << " " << q.y() << " " << q.z() << " " << q.w()
                                      << "\n";
                                  if (++scans % 500 == 0) LOG(WARNING) << "scans " << scans;
                                  return true;
                              })
        .Go();
    Timer::PrintAll();
    LOG(WARNING) << "done, poses " << scans;
    return 0;
}
