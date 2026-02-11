to add
“Add battery icon”
“Add charge animation”
“Add audio alert when battery critical”

This document contains all commands required to:
Check it out simple making the process work

cd ~/robot3_ws
colcon build --symlink-install

source /opt/ros/humble/setup.bash
source ~/robot3_ws/install/setup.bash

ros2 launch robot3_core core.launch.py

ros2 topic pub /robot1/battery_voltage std_msgs/Float32 "data: 15.4" -r 1
ros2 topic pub /robot2/battery_voltage std_msgs/Float32 "data: 15.0" -r 1

ros2 topic pub /robot1/dht11_temperature std_msgs/Float32 "data: 30.5" -r 1
ros2 topic pub /robot1/dht11_humidity std_msgs/Float32 "data: 55.2" -r 1
ros2 topic pub /robot1/soil_moisture std_msgs/Float32 "data: 61.0" -r 1

ros2 topic pub /ui/move_cmd std_msgs/String "data: 'r1_up'" -1
ros2 topic pub /ui/move_cmd std_msgs/String "data: 'r2_left'" -1
ros2 topic pub /ui/move_cmd std_msgs/String "data: 'r1_stop'" -1

ros2 topic pub /ui/seed_cmd std_msgs/String "data: 'seed_power_on'" -1
ros2 topic pub /ui/seed_cmd std_msgs/String "data: 'seed_mode_auto'" -1
ros2 topic pub /ui/seed_cmd std_msgs/String "data: 'seed_dispense_once'" -1

ros2 topic pub /ui/check_soil_moisture std_msgs/String "data: 'check'" -1

ros2 topic pub /r2/camera std_msgs/String "data: 'on'" -1
ros2 topic pub /r2/camera std_msgs/String "data: 'off'" -1
ros2 topic pub /r2/mode std_msgs/String "data: 'plant'" -1
ros2 topic pub /r2/mode std_msgs/String "data: 'bird'" -1

ros2 topic pub /robot1/battery_status robot3_msgs/BatteryStatus "{voltage: 14.2, percent: 20.0, low_flag: true}" -1

http://<RPI-IP>:5000


chandan@chandan-Legion-5-15ACH6:~$ sudo lsof -i :5000
[sudo] password for chandan: 
COMMAND    PID    USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
ui_server 1464 chandan   13u  IPv4  20632      0t0  TCP *:5000 (LISTEN)
chandan@chandan-Legion-5-15ACH6:~$ kill -9 1464
chandan@chandan-Legion-5-15ACH6:~$ 


To Do Later 🔧

GPS (waypoint processing from Robot 2)
FieldMap (UI editor for corners/rows)
AutoNav (movement commands generation)
Ultrasonic (row centering bridge - optional)
WiFi (settings consumer/forwarder)

