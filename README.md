# TF-GridNet-5090GPU

> TF-GridNetV2 音訊增強模型訓練環境 - 針對 NVIDIA RTX 5090 優化

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![CUDA](https://img.shields.io/badge/CUDA-13.0-green.svg)](https://developer.nvidia.com/cuda-toolkit)

## 📖 簡介

本專案提供完整的 Docker 化訓練環境，用於在 NVIDIA RTX 5090 GPU 上訓練 **TF-GridNetV2** 音訊增強模型。包含：

- 🐳 **Docker 容器化環境**：確保可重現性與一致性
- ⚡ **RTX 5090 優化**：充分利用 32GB VRAM 與 CUDA 13.0
- 📊 **實驗記錄系統**：自動化實驗追蹤與結果記錄
- 🚀 **自動化腳本**：簡化訓練流程與部署
- 📝 **完整文檔**：詳細的設定與使用指南

## 🎯 特色功能

- ✅ 針對 RTX 5090 優化的配置（32GB VRAM）
- ✅ Mixed precision 訓練（FP16/BF16）
- ✅ Gradient accumulation 支援
- ✅ 自動實驗日誌與檢查點管理
- ✅ TensorBoard 整合
- ✅ CI/CD workflow 範本
- ✅ 資料下載與管理腳本

## 🚀 快速開始

### 前置需求

- NVIDIA RTX 5090 GPU（或其他 CUDA 相容 GPU）
- NVIDIA Driver 580+ （支援 CUDA 13.0）
- Docker 與 Docker Compose
- nvidia-container-toolkit

### 安裝步驟

```bash
# 1. Clone repository
git clone git@github.com:Hank-Jiang40815/TF-GridNet-5090GPU.git
cd TF-GridNet-5090GPU

# 2. 檢查系統環境
./scripts/setup_host.sh

# 3. 建構 Docker image
docker-compose build

# 4. 下載資料（選擇一種方式）
./scripts/download_data.sh
# 或手動將 TFG-Transfer-Package 放置到指定位置

# 5. 執行 smoke test 驗證環境
./scripts/run_smoke_test.sh

# 6. 開始訓練
./scripts/run_training.sh my-first-experiment
```

### 五分鐘測試

```bash
# 快速驗證環境是否正常
docker-compose run --rm tfgridnet-train bash -c "
    python -c 'import torch; print(f\"PyTorch: {torch.__version__}\"); \
               print(f\"CUDA: {torch.cuda.is_available()}\"); \
               print(f\"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

## 📂 專案結構

```
TF-GridNet-5090GPU/
├── Dockerfile                    # Docker 環境定義
├── docker-compose.yml            # 容器編排配置
├── LICENSE                       # MIT 授權
├── README.md                     # 本文件
│
├── scripts/                      # 執行腳本
│   ├── setup_host.sh            # 環境檢查與設定
│   ├── run_smoke_test.sh        # 快速驗證
│   ├── run_training.sh          # 訓練啟動（含實驗記錄）
│   └── download_data.sh         # 資料下載
│
├── configs/                      # 訓練配置
│   ├── training_rtx5090.yaml    # RTX 5090 優化配置
│   └── README.md                # 配置說明文檔
│
├── experiments/                  # 實驗記錄
│   ├── README.md                # 實驗記錄指南
│   ├── experiment_template.md   # 實驗記錄範本
│   └── logs/                    # 實驗結果目錄
│
├── docs/                         # 詳細文檔
│   ├── SETUP.md                 # 詳細安裝指南
│   ├── TRAINING.md              # 訓練流程說明
│   └── TROUBLESHOOTING.md       # 故障排除
│
└── .github/                      # CI/CD
    └── workflows/
        └── ci.yml               # GitHub Actions workflow
```

## 💻 使用方式

### 基本訓練

```bash
# 使用預設配置訓練
./scripts/run_training.sh baseline

# 使用自訂配置
./scripts/run_training.sh my-experiment /workspace/configs/my_config.yaml

# 跳過記憶體測試（加速啟動）
./scripts/run_training.sh baseline /workspace/configs/training_rtx5090.yaml true
```

### 監控訓練

```bash
# 實時查看訓練日誌
tail -f experiments/logs/<timestamp>-<experiment-name>/training.log

# GPU 監控
watch -n 1 nvidia-smi

# 啟動 TensorBoard（如果有記錄）
docker-compose --profile tensorboard up tensorboard
# 訪問 http://localhost:6006
```

### 進入容器互動模式

```bash
# 啟動容器 shell
docker-compose run --rm tfgridnet-train bash

# 在容器內執行命令
cd /workspace/TFG-Transfer-Package
python code/scripts/smoke_test_tfgridnet.py --sr 8000 --batch 2 --length 16000
```

## 📊 實驗記錄

每次訓練會自動建立實驗目錄：

```
experiments/logs/20251110-120000-my-experiment/
├── config.yaml              # 使用的配置
├── experiment.md            # 實驗記錄（手動編輯）
├── training.log             # 訓練日誌
├── environment.txt          # 環境資訊
├── git_info.txt             # Git commit 資訊
├── checkpoints/             # 模型檢查點
│   ├── best_model.pth
│   └── epoch_*.pth
└── results/                 # 評估結果
```

詳細說明請參閱 [`experiments/README.md`](experiments/README.md)。

## 🔧 配置調整

### RTX 5090 效能優化建議

```yaml
# configs/training_rtx5090.yaml

# 1. 增加批次大小（充分利用 32GB VRAM）
training:
  batch_size: 64  # 從 32 增加到 64

# 2. 啟用混合精度（2-3x 加速）
training:
  mixed_precision:
    enabled: true

# 3. 調整資料載入
misc:
  num_workers: 8  # 根據 CPU 核心數調整

# 4. 增加模型容量
model:
  architecture:
    emb_dim: 192  # 從 128 增加
    n_layers: 6   # 從 4 增加
```

更多配置選項請參閱 [`configs/README.md`](configs/README.md)。

## 📦 資料準備

### 資料結構

```
/home/sbplab/Hank/ESPnet/TFG-Transfer-Package/
└── data/
    ├── scp/
    │   ├── train_clean.scp
    │   ├── train_noisy.scp
    │   ├── valid_clean.scp
    │   └── valid_noisy.scp
    └── wavs/
        ├── clean/
        │   └── *.wav
        └── noisy/
            └── *.wav
```

### 下載資料

```bash
# 方法 1: 使用下載腳本
./scripts/download_data.sh github  # 從 GitHub Release
./scripts/download_data.sh gdrive  # 從 Google Drive

# 方法 2: 手動下載
# 請參考 scripts/download_data.sh 中的說明
```

**注意**：資料檔案不包含在 Git repository 中。請從以下來源下載：
- GitHub Release: [連結待更新]
- Google Drive: [連結待更新]
- Hugging Face: [連結待更新]

## 🔬 實驗範例

### 基準實驗

```bash
./scripts/run_training.sh baseline
```

### 大批次實驗

```bash
# 修改配置中的 batch_size
./scripts/run_training.sh large-batch-64
```

### 長音訊實驗

```bash
# 修改 max_audio_length 到 32000（2秒）
./scripts/run_training.sh long-audio-2s
```

## 📈 效能基準

在 RTX 5090 上的參考效能：

| 配置 | Batch Size | Mixed Precision | 訓練速度 | GPU 記憶體 |
|------|-----------|----------------|---------|-----------|
| 基準 | 32 | FP32 | ~X samples/s | ~18 GB |
| 優化 | 64 | FP16 | ~X samples/s | ~24 GB |
| 最大 | 128 | FP16 | ~X samples/s | ~30 GB |

*實際效能會根據資料與模型配置而異*

## 🐛 故障排除

### 常見問題

1. **Out of Memory (OOM)**
   ```bash
   # 減小 batch size 或啟用 gradient checkpointing
   ```

2. **GPU 未被偵測**
   ```bash
   # 檢查 nvidia-container-toolkit
   docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
   ```

3. **資料載入緩慢**
   ```bash
   # 增加 num_workers 或使用 SSD
   ```

完整故障排除指南請參閱 [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)。

## 📚 文檔

- [詳細安裝指南](docs/SETUP.md)
- [訓練流程說明](docs/TRAINING.md)
- [故障排除](docs/TROUBLESHOOTING.md)
- [實驗記錄指南](experiments/README.md)
- [配置說明](configs/README.md)

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

## 📄 授權

本專案採用 [MIT 授權](LICENSE)。

## 🙏 致謝

- [TF-GridNet](https://github.com/YOUR_REFERENCE) - 原始模型實現
- PyTorch 與 NVIDIA - 深度學習框架與 CUDA 支援

## 📧 聯絡

- GitHub: [@Hank-Jiang40815](https://github.com/Hank-Jiang40815)
- Email: [您的 Email]

---

**⭐ 如果這個專案對你有幫助，請給個星星！**
