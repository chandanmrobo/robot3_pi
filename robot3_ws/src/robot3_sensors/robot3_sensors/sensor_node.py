import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

from robot3_msgs.msg import DHT11
from robot3_msgs.msg import SoilMoisture

from robot3_sensors.sensor_log import write_log_once

# Change detection threshold
CHANGE_THRESHOLD = 0.2


class SensorNode(Node):
    def __init__(self):
        super().__init__("sensor_node_robot1")

        self.robot_id = 1

        # Declare parameters
        self.declare_parameter("temp_topic", "/robot1/dht11_temperature")
        self.declare_parameter("hum_topic", "/robot1/dht11_humidity")
        self.declare_parameter("soil_topic", "/robot1/soil_moisture")

        # Load parameters
        temp_topic = self.get_parameter("temp_topic").value
        hum_topic = self.get_parameter("hum_topic").value
        soil_topic = self.get_parameter("soil_topic").value

        # Create subscriptions
        self.sub_temp = self.create_subscription(Float32, temp_topic, self.cb_temp, 10)
        self.sub_hum = self.create_subscription(Float32, hum_topic, self.cb_hum, 10)
        self.sub_soil = self.create_subscription(Float32, soil_topic, self.cb_soil, 10)

        # Create publishers
        self.pub_dht = self.create_publisher(DHT11, "/robot1/dht11_status", 10)
        self.pub_soil = self.create_publisher(SoilMoisture, "/robot1/soil_status", 10)

        # Last received values — used for change detection
        self.last_temp = None
        self.last_hum = None
        self.last_soil = None

        self.get_logger().info(
            f"SensorNode Robot 1 started:\n"
            f"  Temp topic: {temp_topic}\n"
            f"  Humidity topic: {hum_topic}\n"
            f"  Soil topic: {soil_topic}"
        )

    # ==================================================================
    # TEMPERATURE
    # ==================================================================
    def cb_temp(self, msg):
        val = float(msg.data)

        # First time OR changed
        if self.last_temp is None or abs(val - self.last_temp) >= CHANGE_THRESHOLD:
            self.last_temp = val

            # Log once per change
            write_log_once(f"Robot_1 temperature updated: {val:.1f}°C")

            # Publish DHT combined message
            self.publish_dht()

    # ==================================================================
    # HUMIDITY
    # ==================================================================
    def cb_hum(self, msg):
        val = float(msg.data)

        if self.last_hum is None or abs(val - self.last_hum) >= CHANGE_THRESHOLD:
            self.last_hum = val

            write_log_once(f"Robot_1 humidity updated: {val:.1f}%")

            self.publish_dht()

    # ==================================================================
    # SOIL MOISTURE
    # ==================================================================
    def cb_soil(self, msg):
        val = float(msg.data)

        if self.last_soil is None or abs(val - self.last_soil) >= CHANGE_THRESHOLD:
            self.last_soil = val

            write_log_once(f"Robot_1 soil moisture updated: {val:.1f}%")

            # Publish soil message
            out = SoilMoisture()
            out.moisture = val
            self.pub_soil.publish(out)

            # Also refresh DHT (UI sensor panel updates together)
            self.publish_dht()

    # ==================================================================
    # ALWAYS SEND LATEST VALUES WHEN ANY SENSOR CHANGES
    # ==================================================================
    def publish_dht(self):
        msg = DHT11()
        msg.temperature = float(self.last_temp) if self.last_temp is not None else 0.0
        msg.humidity   = float(self.last_hum)  if self.last_hum  is not None else 0.0
        self.pub_dht.publish(msg)


def main():
    rclpy.init()
    node = SensorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
