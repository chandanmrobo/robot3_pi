#!/usr/bin/env python3
"""
Test script to publish to all UI topics ONCE
Verify that everything displays correctly in the UI
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
from robot3_msgs.msg import BatteryStatus, DHT11, SoilMoisture
import json
import time
import cv2
import numpy as np


class UITestPublisher(Node):
    def __init__(self):
        super().__init__("ui_test_publisher")
        
        # Create all publishers
        self.pub_r1_batt = self.create_publisher(BatteryStatus, "/robot1/battery_status", 10)
        self.pub_r2_batt = self.create_publisher(BatteryStatus, "/robot2/battery_status", 10)
        self.pub_dht = self.create_publisher(DHT11, "/robot1/dht11_status", 10)
        self.pub_soil = self.create_publisher(SoilMoisture, "/robot1/soil_status", 10)
        self.pub_plant = self.create_publisher(String, "/ui/plant_detection", 10)
        self.pub_bird = self.create_publisher(String, "/ui/bird_detection", 10)
        self.pub_seed_event = self.create_publisher(String, "/dashboard/seed_event", 10)
        self.pub_soil_event = self.create_publisher(String, "/dashboard/soil_event", 10)
        self.pub_camera = self.create_publisher(CompressedImage, "/robot2/camera/image_raw/compressed", 10)
        
        self.get_logger().info("=" * 60)
        self.get_logger().info("🧪 UI Test Publisher - Publishing to all topics")
        self.get_logger().info("=" * 60)
        
        # Wait for subscribers
        time.sleep(1.0)
        
        # Publish test data
        self.publish_all()
        
        self.get_logger().info("✅ All test messages published!")
        self.get_logger().info("Check the UI at http://127.0.0.1:5000")
        
    def publish_all(self):
        """Publish test data to all topics"""
        
        # 1. Robot 1 Battery
        self.get_logger().info("📊 Publishing Robot 1 Battery (75%)")
        msg_batt1 = BatteryStatus()
        msg_batt1.voltage = 7.8
        msg_batt1.percent = 75.0
        msg_batt1.low_flag = False
        self.pub_r1_batt.publish(msg_batt1)
        
        # 2. Robot 2 Battery
        self.get_logger().info("📊 Publishing Robot 2 Battery (45%)")
        msg_batt2 = BatteryStatus()
        msg_batt2.voltage = 7.2
        msg_batt2.percent = 45.0
        msg_batt2.low_flag = False
        self.pub_r2_batt.publish(msg_batt2)
        
        # 3. DHT11 Sensor (Temperature + Humidity)
        self.get_logger().info("🌡️  Publishing DHT11 (28°C, 65% humidity)")
        msg_dht = DHT11()
        msg_dht.temperature = 28.5
        msg_dht.humidity = 65.0
        self.pub_dht.publish(msg_dht)
        
        # 4. Soil Moisture
        self.get_logger().info("💧 Publishing Soil Moisture (42%)")
        msg_soil = SoilMoisture()
        msg_soil.moisture = 42.0
        self.pub_soil.publish(msg_soil)
        
        # 5. Plant Detection
        self.get_logger().info("🌿 Publishing Plant Detection (Corn Leaf Blight)")
        msg_plant = String()
        msg_plant.data = "Corn Leaf Blight"
        self.pub_plant.publish(msg_plant)
        
        # 6. Bird Detection
        self.get_logger().info("🐦 Publishing Bird Detection (Crow)")
        msg_bird = String()
        msg_bird.data = "Crow"
        self.pub_bird.publish(msg_bird)
        
        # 7. Seed Dispense Event
        self.get_logger().info("🌱 Publishing Seed Event (3 seeds, total 127)")
        seed_data = {
            "count": 3,
            "totalCount": 127
        }
        msg_seed = String()
        msg_seed.data = json.dumps(seed_data)
        self.pub_seed_event.publish(msg_seed)
        
        # 8. Soil Check Event
        self.get_logger().info("🔍 Publishing Soil Check Event (55% moisture)")
        soil_data = {
            "moisture": 55.0
        }
        msg_soil_evt = String()
        msg_soil_evt.data = json.dumps(soil_data)
        self.pub_soil_event.publish(msg_soil_evt)
        
        # 9. Camera Image (Test Pattern)
        self.get_logger().info("📹 Publishing Test Camera Image")
        self.publish_test_image()
        
    def publish_test_image(self):
        """Publish a test pattern image"""
        # Create test image with text
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Gradient background
        for i in range(480):
            img[i, :] = [int(i * 255 / 480), int((480 - i) * 255 / 480), 128]
        
        # Add text
        cv2.putText(img, "ROBOT 2 CAMERA TEST", (120, 200), 
                    cv2.FONT_HERSHEY_BOLD, 1.2, (255, 255, 255), 3)
        cv2.putText(img, "UI Test Pattern", (200, 280), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Draw some shapes
        cv2.circle(img, (320, 350), 50, (0, 255, 0), 3)
        cv2.rectangle(img, (100, 100), (200, 150), (255, 0, 0), 2)
        cv2.line(img, (450, 100), (550, 150), (0, 0, 255), 2)
        
        # Encode as JPEG
        ok, jpeg = cv2.imencode(".jpg", img)
        if not ok:
            self.get_logger().error("Failed to encode test image")
            return
        
        # Publish
        msg = CompressedImage()
        msg.format = "jpeg"
        msg.data = jpeg.tobytes()
        self.pub_camera.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = UITestPublisher()
    
    # Keep alive for a moment to ensure delivery
    time.sleep(2.0)
    
    node.destroy_node()
    rclpy.shutdown()
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)
    print("\n📋 Expected UI Updates:")
    print("  ✓ Robot 1 Battery: 75%")
    print("  ✓ Robot 2 Battery: 45%")
    print("  ✓ Temperature: 28.5°C")
    print("  ✓ Humidity: 65%")
    print("  ✓ Soil Moisture: 42%")
    print("  ✓ Plant Detection: 'Corn Leaf Blight'")
    print("  ✓ Bird Detection: 'Crow'")
    print("  ✓ Seed Event: +3 seeds (Total: 127)")
    print("  ✓ Soil Check: 55% moisture")
    print("  ✓ Camera: Test pattern image")
    print("\n🌐 Check UI at: http://127.0.0.1:5000")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()