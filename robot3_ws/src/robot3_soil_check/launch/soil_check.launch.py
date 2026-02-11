from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    soil_check_node = Node(
        package='robot3_soil_check',
        executable='soil_check_node',
        name='soil_check_node',
        output='screen'
    )

    return LaunchDescription([
        soil_check_node
    ])
