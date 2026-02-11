from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    detection_bridge = Node(
        package='robot3_detection_bridge',
        executable='detection_bridge_node',
        name='robot3_detection_bridge',
        output='screen'
    )
    detection_mode_bridge = Node(
        package='robot3_detection_bridge',
        executable='detection_mode_bridge',
        name='robot3_detection_mode_bridge',
        output='screen'
    )

    return LaunchDescription([
        detection_bridge,
        detection_mode_bridge
    ])
