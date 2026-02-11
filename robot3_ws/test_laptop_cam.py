#!/usr/bin/env python3
"""
Complete Bidirectional UI Test
- Publishes: Camera feed + all sensor/status data
- Subscribes: All UI commands to verify bidirectional communication
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
from robot3_msgs.msg import BatteryStatus, DHT11, SoilMoisture
import json
import cv2
import numpy as np
import time
import random


class BidirectionalUITest(Node):
    def __init__(self):
        super().__init__("bidirectional_ui_test")
        
        self.get_logger().info("=" * 70)
        self.get_logger().info("🔄 BIDIRECTIONAL UI TEST - Camera + Commands")
        self.get_logger().info("=" * 70)
        
        # ============================================================
        # PUBLISHERS (Robot → UI)
        # ============================================================
        self.pub_r1_batt = self.create_publisher(BatteryStatus, "/robot1/battery_status", 10)
        self.pub_r2_batt = self.create_publisher(BatteryStatus, "/robot2/battery_status", 10)
        self.pub_dht = self.create_publisher(DHT11, "/robot1/dht11_status", 10)
        self.pub_soil = self.create_publisher(SoilMoisture, "/robot1/soil_status", 10)
        self.pub_plant = self.create_publisher(String, "/ui/plant_detection", 10)
        self.pub_bird = self.create_publisher(String, "/ui/bird_detection", 10)
        self.pub_seed_event = self.create_publisher(String, "/dashboard/seed_event", 10)
        self.pub_soil_event = self.create_publisher(String, "/dashboard/soil_event", 10)
        self.pub_camera = self.create_publisher(CompressedImage, "/robot2/camera/image_raw/compressed", 10)
        
        # ============================================================
        # SUBSCRIBERS (UI → Robot)
        # ============================================================
        self.create_subscription(String, "/ui/move_cmd", self.cb_move_cmd, 10)
        self.create_subscription(String, "/ui/seed_cmd", self.cb_seed_cmd, 10)
        self.create_subscription(String, "/ui/check_soil_moisture", self.cb_soil_check, 10)
        self.create_subscription(String, "/ui/detection_mode", self.cb_detection_mode, 10)
        self.create_subscription(String, "/ui/settings_seed_gap", self.cb_seed_gap, 10)
        self.create_subscription(String, "/ui/settings_soil_interval", self.cb_soil_interval, 10)
        self.create_subscription(String, "/ui/settings_wifi", self.cb_wifi, 10)
        
        self.get_logger().info("✅ Publishers created (Robot → UI)")
        self.get_logger().info("✅ Subscribers created (UI → Robot)")
        
        # ============================================================
        # CAMERA SETUP
        # ============================================================
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.get_logger().warn("⚠️  Webcam not available, using test patterns")
            self.cap = None
        else:
            self.get_logger().info("📹 Webcam opened successfully")
        
        # ============================================================
        # TIMERS
        # ============================================================
        # Camera: 20 FPS
        self.create_timer(1/20, self.publish_camera)
        
        # Sensor data: Every 2 seconds
        self.create_timer(2.0, self.publish_sensors)
        
        # Battery: Every 3 seconds
        self.create_timer(3.0, self.publish_battery)
        
        # Detection events: Every 5 seconds
        self.create_timer(5.0, self.publish_detection)
        
        # Dashboard events: Every 7 seconds
        self.create_timer(7.0, self.publish_events)
        
        self.get_logger().info("=" * 70)
        self.get_logger().info("🎯 READY - Streaming data and listening for commands")
        self.get_logger().info("📱 Open UI: http://127.0.0.1:5000")
        self.get_logger().info("=" * 70)
        
        # Stats
        self.frame_count = 0
        self.command_count = 0
    
    # ================================================================
    # PUBLISHERS
    # ================================================================
    
    def publish_camera(self):
        """Publish camera frames"""
        if self.cap:
            ret, frame = self.cap.read()
            if not ret:
                self.get_logger().warn("Frame capture failed")
                return
            frame = cv2.resize(frame, (640, 480))
        else:
            # Generate test pattern if no camera
            frame = self.generate_test_pattern()
        
        # Encode JPEG
        ok, jpeg = cv2.imencode(".jpg", frame)
        if not ok:
            return
        
        msg = CompressedImage()
        msg.format = "jpeg"
        msg.data = jpeg.tobytes()
        self.pub_camera.publish(msg)
        
        self.frame_count += 1
        if self.frame_count % 100 == 0:
            self.get_logger().info(f"📹 Camera frames: {self.frame_count}")
    
    def publish_sensors(self):
        """Publish sensor data"""
        # DHT11
        msg_dht = DHT11()
        msg_dht.temperature = 25.0 + random.uniform(-3, 3)
        msg_dht.humidity = 60.0 + random.uniform(-10, 10)
        self.pub_dht.publish(msg_dht)
        
        # Soil
        msg_soil = SoilMoisture()
        msg_soil.moisture = 45.0 + random.uniform(-5, 5)
        self.pub_soil.publish(msg_soil)
        
        self.get_logger().info(f"🌡️  Sensors: {msg_dht.temperature:.1f}°C, {msg_dht.humidity:.1f}%, Soil {msg_soil.moisture:.1f}%")
    
    def publish_battery(self):
        """Publish battery status"""
        # Robot 1
        msg_batt1 = BatteryStatus()
        msg_batt1.voltage = 7.5 + random.uniform(-0.5, 0.5)
        msg_batt1.percent = 70.0 + random.uniform(-10, 10)
        msg_batt1.low_flag = msg_batt1.percent < 30
        self.pub_r1_batt.publish(msg_batt1)
        
        # Robot 2
        msg_batt2 = BatteryStatus()
        msg_batt2.voltage = 7.3 + random.uniform(-0.5, 0.5)
        msg_batt2.percent = 65.0 + random.uniform(-10, 10)
        msg_batt2.low_flag = msg_batt2.percent < 30
        self.pub_r2_batt.publish(msg_batt2)
        
        self.get_logger().info(f"🔋 Battery: R1={msg_batt1.percent:.1f}%, R2={msg_batt2.percent:.1f}%")
    
    def publish_detection(self):
        """Publish detection results"""
        diseases = ["Healthy", "Corn Leaf Blight", "Gray Leaf Spot", "Rust"]
        birds = ["No Bird", "Crow", "Sparrow", "Pigeon"]
        
        msg_plant = String()
        msg_plant.data = random.choice(diseases)
        self.pub_plant.publish(msg_plant)
        
        msg_bird = String()
        msg_bird.data = random.choice(birds)
        self.pub_bird.publish(msg_bird)
        
        self.get_logger().info(f"🔍 Detection: Plant={msg_plant.data}, Bird={msg_bird.data}")
    
    def publish_events(self):
        """Publish dashboard events"""
        # Seed event
        seed_data = {
            "count": random.randint(1, 5),
            "totalCount": random.randint(100, 200)
        }
        msg_seed = String()
        msg_seed.data = json.dumps(seed_data)
        self.pub_seed_event.publish(msg_seed)
        
        # Soil event
        soil_data = {
            "moisture": 40.0 + random.uniform(-10, 10)
        }
        msg_soil = String()
        msg_soil.data = json.dumps(soil_data)
        self.pub_soil_event.publish(msg_soil)
        
        self.get_logger().info(f"📊 Events: Seeds +{seed_data['count']} (Total {seed_data['totalCount']}), Soil {soil_data['moisture']:.1f}%")
    
    def generate_test_pattern(self):
        """Generate test pattern if no camera"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Animated gradient
        offset = int(time.time() * 50) % 480
        for i in range(480):
            color = int(((i + offset) % 480) * 255 / 480)
            img[i, :] = [color, 255 - color, 128]
        
        # Text
        cv2.putText(img, "TEST PATTERN", (180, 240), 
                    cv2.FONT_HERSHEY_BOLD, 1.5, (255, 255, 255), 3)
        cv2.putText(img, f"Frame: {self.frame_count}", (220, 280), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return img
    
    # ================================================================
    # SUBSCRIBERS (UI → Robot Commands)
    # ================================================================
    
    def cb_move_cmd(self, msg: String):
        """Movement command from UI"""
        self.command_count += 1
        self.get_logger().info("=" * 70)
        self.get_logger().info(f"🎮 COMMAND #{self.command_count}: MOVEMENT")
        self.get_logger().info(f"   Command: {msg.data}")
        self.get_logger().info(f"   Action: Robot moving {msg.data}")
        self.get_logger().info("=" * 70)
    
    def cb_seed_cmd(self, msg: String):
        """Seed dispense command from UI"""
        self.command_count += 1
        self.get_logger().info("=" * 70)
        self.get_logger().info(f"🌱 COMMAND #{self.command_count}: SEED DISPENSE")
        self.get_logger().info(f"   Command: {msg.data}")
        if msg.data == "start_auto":
            self.get_logger().info(f"   Action: Starting automatic seed dispensing")
        elif msg.data == "stop_auto":
            self.get_logger().info(f"   Action: Stopping automatic seed dispensing")
        elif msg.data == "dispense":
            self.get_logger().info(f"   Action: Dispensing 1 seed manually")
        self.get_logger().info("=" * 70)
    
    def cb_soil_check(self, msg: String):
        """Soil check command from UI"""
        self.command_count += 1
        self.get_logger().info("=" * 70)
        self.get_logger().info(f"💧 COMMAND #{self.command_count}: SOIL CHECK")
        self.get_logger().info(f"   Command: {msg.data}")
        self.get_logger().info(f"   Action: Checking soil moisture now...")
        self.get_logger().info("=" * 70)
        
        # Simulate response
        time.sleep(0.5)
        soil_data = {"moisture": 45.0 + random.uniform(-5, 5)}
        msg_resp = String()
        msg_resp.data = json.dumps(soil_data)
        self.pub_soil_event.publish(msg_resp)
        self.get_logger().info(f"   ✅ Result: {soil_data['moisture']:.1f}% moisture")
    
    def cb_detection_mode(self, msg: String):
        """Detection mode change from UI"""
        self.command_count += 1
        self.get_logger().info("=" * 70)
        self.get_logger().info(f"🔍 COMMAND #{self.command_count}: DETECTION MODE")
        self.get_logger().info(f"   Mode: {msg.data}")
        if msg.data == "plant":
            self.get_logger().info(f"   Action: Switching to plant disease detection")
        elif msg.data == "bird":
            self.get_logger().info(f"   Action: Switching to bird/crow detection")
        self.get_logger().info("=" * 70)
    
    def cb_seed_gap(self, msg: String):
        """Seed gap setting from UI"""
        self.command_count += 1
        self.get_logger().info("=" * 70)
        self.get_logger().info(f"⚙️  COMMAND #{self.command_count}: SEED GAP SETTING")
        self.get_logger().info(f"   New gap: {msg.data} cm")
        self.get_logger().info(f"   Action: Updated seed dispense interval")
        self.get_logger().info("=" * 70)
    
    def cb_soil_interval(self, msg: String):
        """Soil check interval setting from UI"""
        self.command_count += 1
        self.get_logger().info("=" * 70)
        self.get_logger().info(f"⚙️  COMMAND #{self.command_count}: SOIL CHECK INTERVAL")
        self.get_logger().info(f"   New interval: {msg.data} seconds")
        self.get_logger().info(f"   Action: Updated automatic soil check interval")
        self.get_logger().info("=" * 70)
    
    def cb_wifi(self, msg: String):
        """WiFi settings from UI"""
        self.command_count += 1
        try:
            data = json.loads(msg.data)
            self.get_logger().info("=" * 70)
            self.get_logger().info(f"📡 COMMAND #{self.command_count}: WIFI SETTINGS")
            self.get_logger().info(f"   SSID: {data.get('ssid', 'N/A')}")
            self.get_logger().info(f"   Password: {'*' * len(data.get('password', ''))}")
            self.get_logger().info(f"   Action: WiFi credentials updated")
            self.get_logger().info("=" * 70)
        except:
            self.get_logger().error("Failed to parse WiFi settings")
    
    def destroy_node(self):
        if self.cap:
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = BidirectionalUITest()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n" + "=" * 70)
        print(f"📊 SESSION SUMMARY")
        print("=" * 70)
        print(f"  Camera frames published: {node.frame_count}")
        print(f"  Commands received from UI: {node.command_count}")
        print("=" * 70)
        print("\n✅ Test completed successfully!\n")
        
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()