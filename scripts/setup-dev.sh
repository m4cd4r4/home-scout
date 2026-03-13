#!/bin/bash
# Home Scout - Development Environment Setup
# Run this on a fresh Ubuntu 24.04 machine

set -e

echo "=== Home Scout Development Setup ==="

# Check Ubuntu version
if ! grep -q "24.04" /etc/lsb-release 2>/dev/null; then
    echo "Warning: This script is tested on Ubuntu 24.04"
fi

# Install ROS 2 Jazzy
echo "Installing ROS 2 Jazzy..."
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo apt update
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install -y ros-jazzy-desktop python3-colcon-common-extensions python3-rosdep

# Initialize rosdep
sudo rosdep init 2>/dev/null || true
rosdep update

# Install PlatformIO for firmware
echo "Installing PlatformIO..."
pip install platformio

# Install Python tools
echo "Installing Python tools..."
pip install ruff mypy pytest pytest-cov

# Build ROS 2 workspace
echo "Building ROS 2 workspace..."
cd "$(dirname "$0")/../ros2_ws"
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install

echo ""
echo "=== Setup complete ==="
echo "Run: source /opt/ros/jazzy/setup.bash"
echo "Run: source ros2_ws/install/setup.bash"
echo "Then: ros2 launch scout_bringup scout_voice_only.launch.py"
