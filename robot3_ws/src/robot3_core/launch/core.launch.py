# /home/chandan/robot3_ws/src/robot3_core/launch/core.launch.py

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    battery_pkg = os.path.join(
        get_package_share_directory('robot3_battery'),
        'launch', 'battery.launch.py'
    )

    sensors_pkg = os.path.join(
        get_package_share_directory('robot3_sensors'),
        'launch', 'sensors.launch.py'
    )

    ui_pkg = os.path.join(
        get_package_share_directory('robot3_ui'),
        'launch', 'ui.launch.py'
    )

    movements_pkg = os.path.join(
        get_package_share_directory('robot3_movements'),
        'launch', 'movements.launch.py'
    )

    seeds_pkg = os.path.join(
        get_package_share_directory('robot3_seeds'),
        'launch', 'seeds.launch.py'
    )

    soil_check_pkg = os.path.join(
        get_package_share_directory('robot3_soil_check'),
        'launch', 'soil_check.launch.py'
    )

    detection_bridge_pkg = os.path.join(
        get_package_share_directory('robot3_detection_bridge'),
        'launch', 'detection_bridge.launch.py'
    )

    dashboard_pkg = os.path.join(
        get_package_share_directory('robot3_dashboard'),
        'launch', 'dashboard.launch.py'
    )

    # Micro-ROS agent (background, no output)
    micro_ros_agent = ExecuteProcess(
        cmd=['ros2', 'run', 'micro_ros_agent', 'micro_ros_agent', 'udp4', '--port', '8888'],
        output='log',  # Suppress terminal output
        shell=False
    )

    return LaunchDescription([
        # Start micro-ros agent FIRST
        micro_ros_agent,
        
        IncludeLaunchDescription(PythonLaunchDescriptionSource(battery_pkg)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(sensors_pkg)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(ui_pkg)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(movements_pkg)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(seeds_pkg)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(soil_check_pkg)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(detection_bridge_pkg)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(dashboard_pkg)),
    ])