from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    ui_node = Node(
        package='robot3_ui',
        executable='ui_server',
        name='robot3_ui_server',
        output='screen'
    )

    return LaunchDescription([
        ui_node
    ])
