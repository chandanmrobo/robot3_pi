from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    movement_node = Node(
        package='robot3_movements',
        executable='movement_node',
        name='robot3_movement_node',
        output='screen'
    )

    return LaunchDescription([
        movement_node
    ])
