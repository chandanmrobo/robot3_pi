from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    robot1 = Node(
        package='robot3_battery',
        executable='battery_node',
        name='robot1_battery_node',
        parameters=[
            {"robot_id": 1},
            {"voltage_topic": "/robot1/battery_voltage"},
            {"status_topic": "/robot1/battery_status"}
        ],
        output='screen'
    )

    robot2 = Node(
        package='robot3_battery',
        executable='battery_node',
        name='robot2_battery_node',
        parameters=[
            {"robot_id": 2},
            {"voltage_topic": "/robot2/battery_voltage"},
            {"status_topic": "/robot2/battery_status"}
        ],
        output='screen'
    )

    return LaunchDescription([
        robot1,
        robot2
    ])
