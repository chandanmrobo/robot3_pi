#!/usr/bin/env python3
"""
UI Command Listener - Subscribes to all topics the UI publishes to
Use this to verify that UI is sending commands correctly
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json


class UICommandListener(Node):
    def __init__(self):
        super().__init__("ui_command_listener")
        
        self.get_logger().info("=" * 70)
        self.get_logger().info("🎧 UI Command Listener - Monitoring all UI→Robot commands")
        self.get_logger().info("=" * 70)
        
        # Subscribe to all UI command topics
        self.create_subscription(String, "/ui/move_cmd", self.cb_move, 10)
        self.create_subscription(String, "/ui/seed_cmd", self.cb_seed, 10)
        self.create_subscription(String, "/ui/check_soil_moisture", self.cb_soil_check, 10)
        self.create_subscription(String, "/ui/detection_mode", self.cb_detection_mode, 10)
        self.create_subscription(String, "/ui/settings_seed_gap", self.cb_seed_gap, 10)
        self.create_subscription(String, "/ui/settings_soil_interval", self.cb_soil_interval, 10)
        self.create_subscription(String, "/ui/settings_wifi", self.cb_wifi, 10)
        
        self.get_logger().info("✅ Listening on:")
        self.get_logger().info("   • /ui/move_cmd")
        self.get_logger().info("   • /ui/seed_cmd")
        self.get_logger().info("   • /ui/check_soil_moisture")
        self.get_logger().info("   • /ui/detection_mode")
        self.get_logger().info("   • /ui/settings_seed_gap")
        self.get_logger().info("   • /ui/settings_soil_interval")
        self.get_logger().info("   • /ui/settings_wifi")
        self.get_logger().info("-" * 70)
        self.get_logger().info("📝 Now interact with the UI and watch commands appear here...")
        self.get_logger().info("=" * 70)
        
        self.command_count = 0
    
    def cb_move(self, msg: String):
        """Movement command from UI"""
        self.command_count += 1
        self.get_logger().info("")
        self.get_logger().info(f"[{self.command_count}] 🚗 MOVEMENT COMMAND")
        self.get_logger().info(f"    Direction: {msg.data}")
        self.get_logger().info(f"    Topic: /ui/move_cmd")
        
        # Parse direction
        if "r1_" in msg.data:
            robot = "Robot 1"
            direction = msg.data.replace("r1_", "")
        elif "r2_" in msg.data:
            robot = "Robot 2"
            direction = msg.data.replace("r2_", "")
        else:
            robot = "Unknown"
            direction = msg.data
        
        self.get_logger().info(f"    Robot: {robot}")
        self.get_logger().info(f"    Action: {direction.upper()}")
    
    def cb_seed(self, msg: String):
        """Seed dispense command from UI"""
        self.command_count += 1
        self.get_logger().info("")
        self.get_logger().info(f"[{self.command_count}] 🌱 SEED DISPENSE COMMAND")
        self.get_logger().info(f"    Command: {msg.data}")
        self.get_logger().info(f"    Topic: /ui/seed_cmd")
    
    def cb_soil_check(self, msg: String):
        """Manual soil check from UI"""
        self.command_count += 1
        self.get_logger().info("")
        self.get_logger().info(f"[{self.command_count}] 💧 SOIL CHECK TRIGGERED")
        self.get_logger().info(f"    Command: {msg.data}")
        self.get_logger().info(f"    Topic: /ui/check_soil_moisture")
    
    def cb_detection_mode(self, msg: String):
        """Detection mode change from UI"""
        self.command_count += 1
        self.get_logger().info("")
        self.get_logger().info(f"[{self.command_count}] 🔍 DETECTION MODE CHANGE")
        self.get_logger().info(f"    Mode: {msg.data}")
        self.get_logger().info(f"    Topic: /ui/detection_mode")
    
    def cb_seed_gap(self, msg: String):
        """Seed gap setting from UI"""
        self.command_count += 1
        self.get_logger().info("")
        self.get_logger().info(f"[{self.command_count}] ⚙️  SEED GAP SETTING")
        self.get_logger().info(f"    Value: {msg.data}")
        self.get_logger().info(f"    Topic: /ui/settings_seed_gap")
    
    def cb_soil_interval(self, msg: String):
        """Soil check interval setting from UI"""
        self.command_count += 1
        self.get_logger().info("")
        self.get_logger().info(f"[{self.command_count}] ⚙️  SOIL INTERVAL SETTING")
        self.get_logger().info(f"    Value: {msg.data}")
        self.get_logger().info(f"    Topic: /ui/settings_soil_interval")
    
    def cb_wifi(self, msg: String):
        """WiFi settings from UI"""
        self.command_count += 1
        self.get_logger().info("")
        self.get_logger().info(f"[{self.command_count}] 📡 WIFI SETTINGS")
        try:
            data = json.loads(msg.data)
            ssid = data.get("ssid", "")
            password = data.get("password", "")
            self.get_logger().info(f"    SSID: {ssid}")
            self.get_logger().info(f"    Password: {'*' * len(password)}")
        except:
            self.get_logger().info(f"    Raw: {msg.data}")
        self.get_logger().info(f"    Topic: /ui/settings_wifi")


def main(args=None):
    rclpy.init(args=args)
    node = UICommandListener()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\n")
        node.get_logger().info("=" * 70)
        node.get_logger().info(f"🛑 Listener Stopped - Total Commands Received: {node.command_count}")
        node.get_logger().info("=" * 70)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()