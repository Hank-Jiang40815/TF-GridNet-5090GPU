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
    RELEASE_TAG="v1.0-training-data"
    ASSET_NAME="tfgridnet_training_data_v1.0.tar.gz"
    
    echo "Repository: $REPO"
    echo "Release tag: $RELEASE_TAG"
    echo "Asset: $ASSET_NAME"
    echo "Target directory: $DATA_DIR"
    echo ""
    
    # 檢查資料是否已存在
    if [ -d "$DATA_DIR/wavs" ] && [ "$(find $DATA_DIR/wavs -name '*.wav' | wc -l)" -ge 7000 ]; then
        echo "✓ Training data already exists ($(find $DATA_DIR/wavs -name '*.wav' | wc -l) WAV files)"
        echo "Skipping download."
        return 0
    fi
    
    # Download using curl or wget
    DOWNLOAD_PATH="/tmp/$ASSET_NAME"
    echo "Downloading to $DOWNLOAD_PATH (388MB)..."
    echo "This may take several minutes depending on your network speed..."
    echo ""
    
    if command -v curl &> /dev/null; then
        curl -L --progress-bar "https://github.com/$REPO/releases/download/$RELEASE_TAG/$ASSET_NAME" -o "$DOWNLOAD_PATH"
    elif command -v wget &> /dev/null; then
        wget --show-progress "https://github.com/$REPO/releases/download/$RELEASE_TAG/$ASSET_NAME" -O "$DOWNLOAD_PATH"
    elif command -v gh &> /dev/null; then
        gh release download "$RELEASE_TAG" --repo "$REPO" --pattern "$ASSET_NAME" --dir /tmp
    else
        echo "Error: No download tool found (curl, wget, or gh)"
        echo "Please install one of them:"
        echo "  sudo apt install curl"
        echo "  sudo apt install wget"
        echo "  sudo apt install gh"
        exit 1
    fi
    
    echo ""
    echo "Verifying download integrity..."
    EXPECTED_MD5="d706a420f28adbd6c7177d9aad025aee"
    ACTUAL_MD5=$(md5sum "$DOWNLOAD_PATH" | cut -d' ' -f1)
    
    if [ "$ACTUAL_MD5" != "$EXPECTED_MD5" ]; then
        echo "✗ Error: MD5 checksum mismatch!"
        echo "  Expected: $EXPECTED_MD5"
        echo "  Actual:   $ACTUAL_MD5"
        echo "  Please try downloading again."
        rm "$DOWNLOAD_PATH"
        exit 1
    fi
    echo "✓ MD5 checksum verified"
    
    echo ""
    echo "Extracting to $DATA_DIR..."
    mkdir -p "$DATA_DIR"
    tar -xzf "$DOWNLOAD_PATH" -C "$DATA_DIR"
    rm "$DOWNLOAD_PATH"
    
    # 驗證資料完整性
    WAV_COUNT=$(find "$DATA_DIR/wavs" -name "*.wav" | wc -l)
    echo ""
    echo "✓ Download completed!"
    echo "✓ Extracted $WAV_COUNT WAV files"
    
    if [ "$WAV_COUNT" -ne 7296 ]; then
        echo "⚠ Warning: Expected 7296 files, found $WAV_COUNT"
        echo "Please verify data integrity"
    else
        echo "✓ All files extracted successfully"
    fi
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
