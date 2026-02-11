from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    sensor_node = Node(
        package='robot3_sensors',
        executable='sensor_node',
        name='robot1_sensor_node',
        output='screen',
        parameters=[
            {"temp_topic": "/robot1/dht11_temperature"},
            {"hum_topic": "/robot1/dht11_humidity"},
            {"soil_topic": "/robot1/soil_moisture"}
        ]
    )

    return LaunchDescription([
        sensor_node
    ])
