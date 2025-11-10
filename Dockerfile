# TF-GridNetV2 Training Environment for RTX 5090
# Base: PyTorch 2.5.1 with CUDA 12.4 (compatible with CUDA 13.0 driver)

FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

LABEL maintainer="Hank-Jiang40815"
LABEL description="TF-GridNetV2 audio enhancement training on RTX 5090"

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libsndfile1 \
    vim \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip

# Install Python dependencies
# Note: PyTorch is already installed in base image
RUN pip install --no-cache-dir \
    soundfile==0.12.1 \
    numpy==1.24.3 \
    PyYAML==6.0.1 \
    tqdm \
    tensorboard \
    matplotlib \
    scipy

# Create directories for mounting
RUN mkdir -p /workspace/TFG-Transfer-Package \
             /workspace/experiments \
             /workspace/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Default command
CMD ["/bin/bash"]
