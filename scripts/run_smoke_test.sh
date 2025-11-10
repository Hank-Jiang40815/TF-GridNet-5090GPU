#!/usr/bin/env bash
# Smoke test script - verifies environment and model forward pass

set -euo pipefail

echo "========================================"
echo "TF-GridNetV2 Smoke Test"
echo "========================================"

# Build image if not exists
if [[ "$(docker images -q tfgridnet-rtx5090:latest 2> /dev/null)" == "" ]]; then
    echo "Building Docker image..."
    docker-compose build
fi

# Run smoke test in container
echo ""
echo "Running smoke test (model forward pass)..."
docker-compose run --rm tfgridnet-train bash -c "
    cd /workspace/TFG-Transfer-Package && \
    python code/scripts/smoke_test_tfgridnet.py --sr 8000 --batch 2 --length 16000
"

EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✓ Smoke test passed!"
else
    echo "✗ Smoke test failed with exit code: $EXIT_CODE"
    exit $EXIT_CODE
fi

echo ""
echo "Environment is ready for training."
