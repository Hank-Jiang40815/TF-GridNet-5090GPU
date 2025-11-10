# 訓練資料 Release 資訊

## Release 位置

**GitHub Release**: https://github.com/Hank-Jiang40815/TF-GridNet-5090GPU/releases/tag/v1.0-training-data

## 檔案資訊

- **檔名**: `tfgridnet_training_data_v1.0.tar.gz`
- **大小**: 388 MB (壓縮後) / 947 MB (解壓後)
- **MD5**: `d706a420f28adbd6c7177d9aad025aee`
- **發布日期**: 2025-11-10

## 快速下載

```bash
# 方法 1: 使用專案下載腳本（推薦）
cd /home/sbplab/Hank/TF-GridNet-5090GPU
./scripts/download_data.sh

# 方法 2: 手動下載
wget https://github.com/Hank-Jiang40815/TF-GridNet-5090GPU/releases/download/v1.0-training-data/tfgridnet_training_data_v1.0.tar.gz

# 驗證 MD5
md5sum tfgridnet_training_data_v1.0.tar.gz
# 應該顯示: d706a420f28adbd6c7177d9aad025aee

# 解壓縮
tar -xzf tfgridnet_training_data_v1.0.tar.gz -C /path/to/TFG-Transfer-Package/data/
```

## 資料內容

```
wavs/
├── train/
│   ├── clean/     # 3,456 個 WAV 檔案 (453MB)
│   └── noisy/     # 3,456 個 WAV 檔案 (453MB)
└── valid/
    ├── clean/     # 192 個 WAV 檔案 (25MB)
    └── noisy/     # 192 個 WAV 檔案 (17MB)

總計: 7,296 個 WAV 檔案
```

## 注意事項

- 此資料已上傳至 GitHub Release，**不需要**包含在 git repository 中
- 下載腳本會自動驗證 MD5 校驗和，確保資料完整性
- 資料會自動解壓到 `/home/sbplab/Hank/ESPnet/TFG-Transfer-Package/data/wavs/`

## 更新資料

如需更新訓練資料，請：

1. 準備新的資料壓縮檔
2. 計算新的 MD5 校驗和
3. 創建新的 Release tag（例如 `v1.1-training-data`）
4. 更新 `scripts/download_data.sh` 中的 `RELEASE_TAG` 和 `EXPECTED_MD5`
5. 更新此文件

## 相關腳本

- `scripts/download_data.sh` - 自動下載和解壓腳本
- `scripts/create_github_release.sh` - Release 創建腳本（一次性使用，可選擇保留或刪除）
