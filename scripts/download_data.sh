#!/usr/bin/env bash
# Data download script
# Modify this script to download your dataset from your preferred source

set -euo pipefail

echo "========================================"
echo "TF-GridNetV2 Data Download"
echo "========================================"

DATA_DIR="/home/sbplab/Hank/ESPnet/TFG-Transfer-Package/data"
DOWNLOAD_METHOD="${1:-prompt}"

echo ""
echo "Target directory: $DATA_DIR"
echo ""

# Function to download from GitHub Release
download_from_github_release() {
    echo "Downloading from GitHub Release..."
    REPO="Hank-Jiang40815/TF-GridNet-5090GPU"
    RELEASE_TAG="v1.0.0-data"
    ASSET_NAME="tfgridnet-data.tar.gz"
    
    echo "Repository: $REPO"
    echo "Release tag: $RELEASE_TAG"
    echo "Asset: $ASSET_NAME"
    echo ""
    
    # Download using curl or wget
    if command -v curl &> /dev/null; then
        curl -L "https://github.com/$REPO/releases/download/$RELEASE_TAG/$ASSET_NAME" -o /tmp/$ASSET_NAME
    elif command -v wget &> /dev/null; then
        wget "https://github.com/$REPO/releases/download/$RELEASE_TAG/$ASSET_NAME" -O /tmp/$ASSET_NAME
    else
        echo "Error: Neither curl nor wget found"
        exit 1
    fi
    
    echo "Extracting..."
    mkdir -p "$DATA_DIR"
    tar -xzf /tmp/$ASSET_NAME -C "$DATA_DIR"
    rm /tmp/$ASSET_NAME
    
    echo "✓ Download completed!"
}

# Function to download from Google Drive
download_from_google_drive() {
    echo "Downloading from Google Drive..."
    FILE_ID="YOUR_GOOGLE_DRIVE_FILE_ID"
    OUTPUT="/tmp/tfgridnet-data.tar.gz"
    
    echo "File ID: $FILE_ID"
    echo ""
    
    # Use gdown if available, otherwise provide manual instructions
    if command -v gdown &> /dev/null; then
        gdown "https://drive.google.com/uc?id=$FILE_ID" -O "$OUTPUT"
    else
        echo "Error: gdown not installed"
        echo "Install with: pip install gdown"
        echo ""
        echo "Or download manually from:"
        echo "https://drive.google.com/file/d/$FILE_ID/view"
        exit 1
    fi
    
    echo "Extracting..."
    mkdir -p "$DATA_DIR"
    tar -xzf "$OUTPUT" -C "$DATA_DIR"
    rm "$OUTPUT"
    
    echo "✓ Download completed!"
}

# Function to download from Hugging Face
download_from_huggingface() {
    echo "Downloading from Hugging Face..."
    REPO_ID="YOUR_HF_USERNAME/tfgridnet-data"
    
    echo "Repository: $REPO_ID"
    echo ""
    
    if command -v huggingface-cli &> /dev/null; then
        huggingface-cli download "$REPO_ID" --repo-type dataset --local-dir "$DATA_DIR"
    else
        echo "Error: huggingface-cli not installed"
        echo "Install with: pip install huggingface_hub"
        exit 1
    fi
    
    echo "✓ Download completed!"
}

# Main logic
case "$DOWNLOAD_METHOD" in
    github)
        download_from_github_release
        ;;
    gdrive)
        download_from_google_drive
        ;;
    huggingface|hf)
        download_from_huggingface
        ;;
    prompt|*)
        echo "Please select download method:"
        echo "  1) GitHub Release (recommended)"
        echo "  2) Google Drive"
        echo "  3) Hugging Face"
        echo "  4) Manual (I'll download manually)"
        echo ""
        read -p "Enter choice (1-4): " choice
        
        case $choice in
            1) download_from_github_release ;;
            2) download_from_google_drive ;;
            3) download_from_huggingface ;;
            4)
                echo ""
                echo "Manual download instructions:"
                echo "1. Download the dataset archive from your source"
                echo "2. Extract to: $DATA_DIR"
                echo "3. Verify structure:"
                echo "   $DATA_DIR/"
                echo "   ├── scp/"
                echo "   │   ├── train_clean.scp"
                echo "   │   ├── train_noisy.scp"
                echo "   │   ├── valid_clean.scp"
                echo "   │   └── valid_noisy.scp"
                echo "   └── wavs/"
                echo "       ├── clean/"
                echo "       └── noisy/"
                echo ""
                exit 0
                ;;
            *)
                echo "Invalid choice"
                exit 1
                ;;
        esac
        ;;
esac

# Verify data
echo ""
echo "Verifying data..."
if [ -d "$DATA_DIR/wavs" ] && [ -d "$DATA_DIR/scp" ]; then
    WAV_COUNT=$(find "$DATA_DIR/wavs" -name "*.wav" | wc -l)
    echo "✓ Found $WAV_COUNT WAV files"
    echo "✓ Data verification passed"
else
    echo "✗ Data verification failed"
    echo "Expected directories not found: $DATA_DIR/wavs and $DATA_DIR/scp"
    exit 1
fi

echo ""
echo "========================================"
echo "Data download completed!"
echo "========================================"
