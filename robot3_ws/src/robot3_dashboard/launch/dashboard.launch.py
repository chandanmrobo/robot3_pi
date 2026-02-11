from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([

        # -----------------------------------------------------
        # ROS2 Dashboard Storage Node (kept same)
        # -----------------------------------------------------
        Node(
            package="robot3_dashboard",
            executable="dashboard_node",
            name="dashboard_node",
            output="screen"
        )
    ])
