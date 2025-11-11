# TF-GridNetV2 Training Environment for RTX 5090
# Base: PyTorch 2.9.0 official image with CUDA 12.8
# Using the latest PyTorch version which may have better RTX 5090 support

FROM pytorch/pytorch:2.9.0-cuda12.8-cudnn9-devel

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
RUN pip install --no-cache-dir --upgrade pip

# PyTorch is already installed from base image  
# Skip torchaudio to avoid version conflicts, use soundfile instead

# Install other Python dependencies (including soundfile as torchaudio alternative)
RUN pip install --no-cache-dir \
    soundfile==0.12.1 \
    numpy==1.24.3 \
    PyYAML==6.0.1 \
    tqdm \
    tensorboard \
    matplotlib \
    scipy \
    librosa

# Create directories for mounting
RUN mkdir -p /workspace/TFG-Transfer-Package \
             /workspace/experiments \
             /workspace/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Default command
CMD ["/bin/bash"]
