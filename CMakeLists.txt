cmake_minimum_required(VERSION 3.8)
project(robot_diff_drive)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config rviz urdf
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
