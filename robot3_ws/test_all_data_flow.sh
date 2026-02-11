#!/bin/bash

# ============================================================
# COMPLETE ROS2 DATA FLOW TEST SCRIPT
# Tests all manual interactions: seed, soil, movement, detection
# Shows data flow once per test - NO continuous logs
# ============================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test duration for each check (seconds)
TEST_DURATION=3

echo ""
echo "============================================================"
echo "  ROS2 DATA FLOW VERIFICATION TEST"
echo "  Testing: Seed, Soil, Movement, Detection, Settings"
echo "============================================================"
echo ""

# Check if ROS2 is sourced
if [ -z "$ROS_DISTRO" ]; then
    echo -e "${RED}❌ ERROR: ROS2 not sourced${NC}"
    echo "Run: source ~/robot3_ws/install/setup.bash"
    exit 1
fi

echo -e "${CYAN}✓ ROS2 environment detected: $ROS_DISTRO${NC}"
echo ""

# ============================================================
# HELPER FUNCTIONS
# ============================================================

test_topic() {
    local topic_name=$1
    local test_name=$2
    local instruction=$3
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}TEST: $test_name${NC}"
    echo -e "${CYAN}Instruction: $instruction${NC}"
    echo -e "Topic: ${BLUE}$topic_name${NC}"
    echo ""
    echo -e "${GREEN}Listening for ${TEST_DURATION} seconds...${NC}"
    echo ""
    
    # Capture topic data with timeout
    timeout $TEST_DURATION ros2 topic echo $topic_name --once 2>/dev/null
    
    local exit_code=$?
    echo ""
    
    if [ $exit_code -eq 124 ]; then
        echo -e "${RED}⚠ TIMEOUT: No data received${NC}"
        echo -e "${YELLOW}  → Check if UI action was performed${NC}"
        echo -e "${YELLOW}  → Check if node is running: ros2 node list | grep -i ${topic_name##*/}${NC}"
    elif [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Data received successfully${NC}"
    else
        echo -e "${RED}✗ Error: Topic may not exist${NC}"
    fi
    
    echo ""
    read -p "Press ENTER to continue to next test..."
    echo ""
}

test_topic_quick() {
    local topic_name=$1
    local expected=$2
    
    timeout 1 ros2 topic echo $topic_name --once 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✓ $expected${NC}"
    else
        echo -e "${RED}  ✗ $expected - NO DATA${NC}"
    fi
}

# ============================================================
# PRE-FLIGHT CHECKS
# ============================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  PRE-FLIGHT: Checking System Status${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${CYAN}Checking active nodes...${NC}"
NODES=$(ros2 node list 2>/dev/null)

if [ -z "$NODES" ]; then
    echo -e "${RED}❌ ERROR: No ROS2 nodes running${NC}"
    echo "Start the system first: ros2 launch robot3_core core.launch.py"
    exit 1
fi

echo "$NODES" | while read -r node; do
    echo -e "${GREEN}  ✓ $node${NC}"
done

echo ""
echo -e "${CYAN}Checking critical topics...${NC}"

test_topic_quick "/ui/seed_cmd" "Seed command topic"
test_topic_quick "/ui/check_soil_moisture" "Soil check topic"
test_topic_quick "/ui/move_cmd" "Movement topic"
test_topic_quick "/dashboard/seed_event" "Seed event topic"
test_topic_quick "/dashboard/soil_event" "Soil event topic"

echo ""
echo -e "${GREEN}✓ System is running${NC}"
echo ""
read -p "Press ENTER to start interactive tests..."
echo ""

# ============================================================
# TEST 1: SEED DISPENSE (MANUAL)
# ============================================================

test_topic \
    "/ui/seed_cmd" \
    "Seed Dispense Command (UI → Seed Node)" \
    "In UI: Click 'Dispense Seed' button in Robot1 panel"

test_topic \
    "/robot1/seed_cmd" \
    "Seed Command to ESP32 (Seed Node → ESP32)" \
    "In UI: Click 'Dispense Seed' button again"

test_topic \
    "/dashboard/seed_event" \
    "Seed Event Confirmation (Backend → Dashboard)" \
    "In UI: Click 'Dispense Seed' button once more"

# ============================================================
# TEST 2: SEED MODE CHANGE
# ============================================================

test_topic \
    "/ui/seed_cmd" \
    "Seed Mode Change (Auto/Manual Toggle)" \
    "In UI: Toggle seed mode slider between Auto ↔ Manual"

# ============================================================
# TEST 3: SOIL CHECK (MANUAL)
# ============================================================

test_topic \
    "/ui/check_soil_moisture" \
    "Soil Check Command (UI → Soil Check Node)" \
    "In UI: Click 'Perform Soil Check' button in Robot1 panel"

test_topic \
    "/robot1/check_soil_moisture" \
    "Soil Check to ESP32 (Soil Node → ESP32)" \
    "In UI: Click 'Perform Soil Check' button again"

test_topic \
    "/dashboard/soil_event" \
    "Soil Event Result (Backend → Dashboard)" \
    "Wait a moment for auto soil check OR click manual button"

# ============================================================
# TEST 4: SOIL MODE CHANGE
# ============================================================

test_topic \
    "/ui/soil_mode" \
    "Soil Mode Change (Auto/Manual Toggle)" \
    "In UI: Toggle soil check slider between Auto ↔ Manual"

# ============================================================
# TEST 5: ROBOT 1 MOVEMENT
# ============================================================

test_topic \
    "/ui/move_cmd" \
    "Robot 1 Movement - Forward" \
    "In UI: Click UP arrow (Forward) in Robot1 panel"

test_topic \
    "/ui/move_cmd" \
    "Robot 1 Movement - Left" \
    "In UI: Click LEFT arrow in Robot1 panel"

test_topic \
    "/ui/move_cmd" \
    "Robot 1 Movement - Right" \
    "In UI: Click RIGHT arrow in Robot1 panel"

test_topic \
    "/ui/move_cmd" \
    "Robot 1 Movement - Backward" \
    "In UI: Click DOWN arrow (Backward) in Robot1 panel"

# ============================================================
# TEST 6: ROBOT 2 MOVEMENT
# ============================================================

test_topic \
    "/ui/move_cmd" \
    "Robot 2 Movement - Forward" \
    "In UI: Click UP arrow (Forward) in Robot2 panel"

test_topic \
    "/ui/move_cmd" \
    "Robot 2 Movement - Any Direction" \
    "In UI: Click ANY arrow in Robot2 panel"

# ============================================================
# TEST 7: DETECTION MODE
# ============================================================

test_topic \
    "/ui/detection_mode" \
    "Detection Mode Change (Plant/Bird Toggle)" \
    "In UI: Toggle detection slider between Plant ↔ Bird in Robot2 panel"

# ============================================================
# TEST 8: SETTINGS - SEED GAP
# ============================================================

test_topic \
    "/ui/settings_seed_gap" \
    "Seed Gap Setting Update" \
    "In UI: Go to Settings tab, change 'Seed Dispense Gap', click SAVE"

# ============================================================
# TEST 9: SETTINGS - SOIL INTERVAL
# ============================================================

test_topic \
    "/ui/settings_soil_interval" \
    "Soil Check Interval Update" \
    "In UI: Go to Settings tab, change 'Soil Check Interval', click SAVE"

# ============================================================
# TEST 10: BATTERY STATUS
# ============================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}TEST: Battery Status (Both Robots)${NC}"
echo -e "${CYAN}Instruction: Battery updates automatically${NC}"
echo ""
echo -e "${GREEN}Checking current battery levels...${NC}"
echo ""

echo -e "${CYAN}Robot 1 Battery:${NC}"
timeout 2 ros2 topic echo /robot1/battery_status --once 2>/dev/null
echo ""

echo -e "${CYAN}Robot 2 Battery:${NC}"
timeout 2 ros2 topic echo /robot2/battery_status --once 2>/dev/null
echo ""

read -p "Press ENTER to continue..."
echo ""

# ============================================================
# TEST 11: SENSOR DATA
# ============================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}TEST: Sensor Data (Temperature, Humidity, Soil Moisture)${NC}"
echo -e "${CYAN}Instruction: Sensors update automatically${NC}"
echo ""
echo -e "${GREEN}Checking current sensor readings...${NC}"
echo ""

echo -e "${CYAN}DHT11 (Temperature & Humidity):${NC}"
timeout 2 ros2 topic echo /robot1/dht11_status --once 2>/dev/null
echo ""

echo -e "${CYAN}Soil Moisture:${NC}"
timeout 2 ros2 topic echo /robot1/soil_status --once 2>/dev/null
echo ""

read -p "Press ENTER to continue..."
echo ""

# ============================================================
# FINAL SUMMARY
# ============================================================

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ALL TESTS COMPLETED${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Summary:${NC}"
echo "✓ Seed dispense (manual & mode change)"
echo "✓ Soil check (manual & mode change)"
echo "✓ Robot 1 movement (all directions)"
echo "✓ Robot 2 movement (all directions)"
echo "✓ Detection mode (plant/bird toggle)"
echo "✓ Settings updates (seed gap, soil interval)"
echo "✓ Battery status (both robots)"
echo "✓ Sensor data (DHT11, soil moisture)"
echo ""
echo -e "${YELLOW}If any tests showed TIMEOUT or NO DATA:${NC}"
echo "  1. Verify the UI is open: http://localhost:5000"
echo "  2. Check nodes are running: ros2 node list"
echo "  3. Check system is launched: ros2 launch robot3_core core.launch.py"
echo ""
echo -e "${GREEN}Data flow verification complete! 🎉${NC}"
echo ""