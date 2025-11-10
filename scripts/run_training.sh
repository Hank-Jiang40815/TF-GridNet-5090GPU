#!/usr/bin/env bash
# Training script with automated experiment logging

set -euo pipefail

# Default values
EXPERIMENT_NAME="${1:-rtx5090-baseline}"
CONFIG_FILE="${2:-/workspace/configs/training_rtx5090.yaml}"
SKIP_MEMORY_TEST="${3:-false}"

echo "========================================"
echo "TF-GridNetV2 Training"
echo "========================================"
echo "Experiment: $EXPERIMENT_NAME"
echo "Config: $CONFIG_FILE"
echo "========================================"

# Create experiment directory with timestamp
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
EXP_DIR="/workspace/experiments/logs/${TIMESTAMP}-${EXPERIMENT_NAME}"

echo ""
echo "Creating experiment directory: $EXP_DIR"

# Run training in container with experiment logging
docker-compose run --rm tfgridnet-train bash -c "
    set -e
    
    # Create experiment directory
    mkdir -p '$EXP_DIR'/{checkpoints,results}
    
    # Copy config file
    cp '$CONFIG_FILE' '$EXP_DIR/config.yaml'
    
    # Save git info (if available)
    if cd /workspace/TFG-Transfer-Package && git rev-parse --git-dir > /dev/null 2>&1; then
        echo 'Git commit:' \$(git rev-parse HEAD) > '$EXP_DIR/git_info.txt'
        echo 'Git branch:' \$(git rev-parse --abbrev-ref HEAD) >> '$EXP_DIR/git_info.txt'
        git diff > '$EXP_DIR/git_diff.patch' || true
    fi
    
    # Save environment info
    echo 'Python: '\$(python --version) > '$EXP_DIR/environment.txt'
    echo 'PyTorch: '\$(python -c 'import torch; print(torch.__version__)') >> '$EXP_DIR/environment.txt'
    echo 'CUDA: '\$(python -c 'import torch; print(torch.version.cuda)') >> '$EXP_DIR/environment.txt'
    echo 'GPU: '\$(nvidia-smi --query-gpu=name --format=csv,noheader) >> '$EXP_DIR/environment.txt'
    
    # Copy experiment template
    if [ -f '/workspace/experiments/experiment_template.md' ]; then
        cp /workspace/experiments/experiment_template.md '$EXP_DIR/experiment.md'
        # Update template with experiment info
        sed -i 's/{{EXPERIMENT_NAME}}/$EXPERIMENT_NAME/g' '$EXP_DIR/experiment.md'
        sed -i 's|{{CONFIG_FILE}}|$CONFIG_FILE|g' '$EXP_DIR/experiment.md'
        sed -i 's/{{TIMESTAMP}}/$TIMESTAMP/g' '$EXP_DIR/experiment.md'
    fi
    
    echo ''
    echo '========================================'
    echo 'Starting training...'
    echo 'Experiment directory: $EXP_DIR'
    echo '========================================'
    echo ''
    
    # Run training with output logging
    cd /workspace/TFG-Transfer-Package
    
    TRAIN_CMD=\"python -u code/train_complete_tfgridnetv2_fixed.py --config $CONFIG_FILE\"
    
    if [ '$SKIP_MEMORY_TEST' = 'true' ]; then
        TRAIN_CMD=\"\$TRAIN_CMD --skip-memory-test\"
    fi
    
    # Run and capture output
    \$TRAIN_CMD 2>&1 | tee '$EXP_DIR/training.log'
    
    EXIT_CODE=\${PIPESTATUS[0]}
    
    echo ''
    echo 'Training completed with exit code: '\$EXIT_CODE
    echo 'Experiment directory: $EXP_DIR'
    echo ''
    
    exit \$EXIT_CODE
"

EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
    echo ""
    echo "✓ Training completed successfully!"
    echo ""
    echo "Experiment directory: ./experiments/logs/${TIMESTAMP}-${EXPERIMENT_NAME}"
    echo ""
    echo "Next steps:"
    echo "  1. Review results: ls -lh ./experiments/logs/${TIMESTAMP}-${EXPERIMENT_NAME}/"
    echo "  2. Edit experiment log: vim ./experiments/logs/${TIMESTAMP}-${EXPERIMENT_NAME}/experiment.md"
    echo "  3. Run evaluation: ./scripts/run_evaluation.sh ${TIMESTAMP}-${EXPERIMENT_NAME}"
else
    echo ""
    echo "✗ Training failed with exit code: $EXIT_CODE"
    echo "Check logs: ./experiments/logs/${TIMESTAMP}-${EXPERIMENT_NAME}/training.log"
    exit $EXIT_CODE
fi
