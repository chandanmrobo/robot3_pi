import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from robot3_msgs.msg import BatteryStatus

from robot3_battery.battery_utils import voltage_to_percent


class BatteryNode(Node):
    def __init__(self):
        # Use unique node name per robot
        super().__init__('battery_node_main')

        # Declare parameters
        self.declare_parameter("robot_id", 1)
        self.declare_parameter("voltage_topic", "/robot1/battery_voltage")
        self.declare_parameter("status_topic", "/robot1/battery_status")

        # Load parameters
        self.robot_id = self.get_parameter("robot_id").value
        voltage_topic = self.get_parameter("voltage_topic").value
        status_topic = self.get_parameter("status_topic").value

        # ROS2 Subscriber: Voltage input
        self.sub_voltage = self.create_subscription(
            Float32,
            voltage_topic,
            self.cb_voltage,
            10
        )

        # ROS2 Publisher: Battery status output
        self.pub_status = self.create_publisher(
            BatteryStatus,
            status_topic,
            10
        )

        self.get_logger().info(
            f"BatteryNode for Robot {self.robot_id} started\n"
            f"  Listening on:  {voltage_topic}\n"
            f"  Publishing to: {status_topic}"
        )

    # --------------------------------------------------------------
    # VOLTAGE → PERCENT → STATUS
    # --------------------------------------------------------------
    def cb_voltage(self, msg):
        voltage = float(msg.data)

        # Convert voltage to %
        percent = voltage_to_percent(voltage)

        # LOW battery <= 30%
        low_flag = percent <= 30

        # Prepare BatteryStatus message
        status = BatteryStatus()
        status.voltage = voltage
        status.percent = float(percent)
        status.low_flag = low_flag

        # Publish status
        self.pub_status.publish(status)


# --------------------------------------------------------------
# MAIN
# --------------------------------------------------------------
def main():
    rclpy.init()
    node = BatteryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
