#!/bin/bash
# ============================================================
# DASHBOARD FIX INSTALLATION SCRIPT
# Run this after copying the 3 files above
# ============================================================

echo "🚀 Installing Dashboard Fixes..."
echo ""

# ============================================================
# 1. BACKUP OLD FILES
# ============================================================
echo "📦 Step 1: Backing up old files..."
cd ~/robot3_ws/src/robot3_dashboard/robot3_dashboard

if [ -f "dashboard_api.py" ]; then
    cp dashboard_api.py dashboard_api.py.backup
    echo "   ✅ Backed up dashboard_api.py"
fi

if [ -f "dashboard_node.py" ]; then
    cp dashboard_node.py dashboard_node.py.backup
    echo "   ✅ Backed up dashboard_node.py"
fi

if [ -f "~/Desktop/robot3_ui/src/components/Dashboard.tsx" ]; then
    cp ~/Desktop/robot3_ui/src/components/Dashboard.tsx ~/Desktop/robot3_ui/src/components/Dashboard.tsx.backup
    echo "   ✅ Backed up Dashboard.tsx"
fi

echo ""

# ============================================================
# 2. CREATE STORAGE FOLDER
# ============================================================
echo "📂 Step 2: Creating storage folder..."
mkdir -p ~/robot3_ws/src/robot3_dashboard/robot3_dashboard/storage
cd ~/robot3_ws/src/robot3_dashboard/robot3_dashboard/storage

# Initialize empty JSON files
echo "[]" > sensor_log.json
echo "[]" > seed_log.json
echo "[]" > soil_log.json

echo "   ✅ Created storage folder with 3 JSON files"
ls -lh
echo ""

# ============================================================
# 3. VERIFY FILES
# ============================================================
echo "🔍 Step 3: Verifying files..."
cd ~/robot3_ws/src/robot3_dashboard/robot3_dashboard

if [ -f "dashboard_api.py" ]; then
    echo "   ✅ dashboard_api.py exists"
else
    echo "   ❌ dashboard_api.py NOT FOUND - Copy FILE 1 first!"
    exit 1
fi

if [ -f "dashboard_node.py" ]; then
    echo "   ✅ dashboard_node.py exists"
else
    echo "   ❌ dashboard_node.py NOT FOUND - Copy FILE 2 first!"
    exit 1
fi

if [ -f "~/Desktop/robot3_ui/src/components/Dashboard.tsx" ]; then
    echo "   ✅ Dashboard.tsx exists"
else
    echo "   ⚠️  Dashboard.tsx NOT FOUND - Copy FILE 3 manually"
fi

echo ""

# ============================================================
# 4. REBUILD ROS PACKAGE
# ============================================================
echo "🔨 Step 4: Rebuilding ROS package..."
cd ~/robot3_ws
colcon build --packages-select robot3_dashboard

if [ $? -eq 0 ]; then
    echo "   ✅ ROS package built successfully"
else
    echo "   ❌ Build failed - Check errors above"
    exit 1
fi

source install/setup.bash
echo ""

# ============================================================
# 5. REBUILD REACT UI
# ============================================================
echo "⚛️  Step 5: Rebuilding React UI..."
cd ~/Desktop/robot3_ui

npm run build

if [ $? -eq 0 ]; then
    echo "   ✅ React UI built successfully"
else
    echo "   ❌ Build failed - Check errors above"
    exit 1
fi

# Copy build to ROS package
cp -r build/* ~/robot3_ws/src/robot3_ui/robot3_ui/ui_build/
echo "   ✅ Copied build to ROS package"
echo ""

# ============================================================
# 6. TEST API HEALTH
# ============================================================
echo "🏥 Step 6: Testing API health..."
echo "   Starting ROS in background..."

cd ~/robot3_ws
source install/setup.bash

# Start ROS in background
ros2 launch robot3_core core.launch.py &
ROS_PID=$!

# Wait for ROS to start
echo "   Waiting 10 seconds for ROS to start..."
sleep 10

# Test API
echo "   Testing API..."
HEALTH=$(curl -s http://127.0.0.1:5000/api/dashboard/health)

if [ $? -eq 0 ]; then
    echo "   ✅ API is responding!"
    echo "   Response: $HEALTH"
else
    echo "   ❌ API not responding - Check if ROS is running"
fi

# Stop ROS
kill $ROS_PID 2>/dev/null

echo ""

# ============================================================
# 7. FINAL INSTRUCTIONS
# ============================================================
echo "✅ Installation Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Start ROS: ros2 launch robot3_core core.launch.py"
echo "   2. Open browser: http://127.0.0.1:5000"
echo "   3. Click Dashboard tab"
echo "   4. Test Daily/Monthly/Yearly tabs - NO 500 errors!"
echo ""
echo "🔍 To generate test data:"
echo "   - Perform a soil check (generates sensor data)"
echo "   - Dispense seeds (generates seed data)"
echo "   - Wait 30 seconds, then refresh dashboard"
echo ""
echo "📊 Storage Location:"
echo "   ~/robot3_ws/src/robot3_dashboard/robot3_dashboard/storage/"
echo ""
echo "🐛 If issues occur:"
echo "   - Check logs: tail -f ~/robot3_ws/dashboard_log.txt"
echo "   - Test health: curl http://127.0.0.1:5000/api/dashboard/health"
echo ""
echo "✨ Done!"