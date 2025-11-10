#!/usr/bin/env bash
# Setup script for host environment
# Run this on the host machine before using Docker

set -euo pipefail

echo "========================================"
echo "TF-GridNetV2 Host Environment Setup"
echo "========================================"

# Check if running on Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo "Warning: This script is designed for Linux. Continue? (y/n)"
    read -r response
    if [[ "$response" != "y" ]]; then
        exit 1
    fi
fi

# Check NVIDIA driver
echo ""
echo "Checking NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
else
    echo "Error: nvidia-smi not found. Please install NVIDIA drivers."
    exit 1
fi

# Check Docker
echo ""
echo "Checking Docker..."
if command -v docker &> /dev/null; then
    docker --version
else
    echo "Error: Docker not found. Please install Docker."
    exit 1
fi

# Check nvidia-docker runtime
echo ""
echo "Checking nvidia-docker runtime..."
if docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo "✓ nvidia-docker runtime is working"
else
    echo "Error: nvidia-docker runtime not working properly."
    echo "Please install nvidia-container-toolkit:"
    echo "  https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi

# Check if TFG-Transfer-Package exists
echo ""
echo "Checking TFG-Transfer-Package..."
TFG_PATH="/home/sbplab/Hank/ESPnet/TFG-Transfer-Package"
if [[ -d "$TFG_PATH" ]]; then
    echo "✓ Found TFG-Transfer-Package at: $TFG_PATH"
    echo "  - code/: $(ls -1 $TFG_PATH/code/*.py 2>/dev/null | wc -l) Python files"
    echo "  - data/wavs/: $(find $TFG_PATH/data/wavs -name '*.wav' 2>/dev/null | wc -l) WAV files"
else
    echo "Warning: TFG-Transfer-Package not found at: $TFG_PATH"
    echo "Please extract the transfer package or update docker-compose.yml with correct path."
fi

# Create local experiment directory if not exists
echo ""
echo "Setting up experiment directory..."
mkdir -p experiments/logs
echo "✓ Created experiments/logs/"

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Build Docker image: docker-compose build"
echo "  2. Run smoke test: ./scripts/run_smoke_test.sh"
echo "  3. Start training: ./scripts/run_training.sh <experiment_name>"
echo ""
