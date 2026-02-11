from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    seed_node = Node(
        package='robot3_seeds',
        executable='seed_node',
        name='robot3_seed_node',
        output='screen',
        emulate_tty=True
    )

    return LaunchDescription([
        seed_node
    ])
