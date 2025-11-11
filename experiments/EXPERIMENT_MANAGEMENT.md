# 實驗管理指南

## 📁 目錄結構

```
experiments/
├── EXPERIMENT_MANAGEMENT.md           # 本文檔
├── tfgridnetv2_rtx5090_baseline/      # 訓練輸出（本地保存）
│   ├── checkpoint_epoch_*.pth         # 模型檢查點
│   └── train_*.log                    # 訓練日誌
└── inference_results/
    └── epoch_{N}_best_{TIMESTAMP}/    # 一個實驗一個資料夾
        ├── README.md                   # 實驗摘要
        ├── metadata.json               # 實驗元數據
        ├── evaluation_results.csv      # 完整評估數據（含檔名）
        ├── highlights.txt              # 關鍵樣本標註
        ├── visualizations/             # 視覺化圖表
        │   ├── *_waveform.png
        │   ├── *_spectrogram.png
        │   └── VISUALIZATION_INDEX.md
        ├── enhanced/                   # 全部增強音訊（本地）
        ├── noisy/                      # 全部噪音音訊（本地）
        ├── clean/                      # 全部乾淨音訊（本地）
        └── audio_samples/              # 精選樣本（可選提交）
            ├── best_5/
            └── worst_5/
```

---

## 🎯 管理策略

### 1. 日常實驗（輕量級）

**提交到 Git**:
- ✅ `README.md` - 實驗摘要
- ✅ `metadata.json` - 完整配置記錄
- ✅ `evaluation_results.csv` - 含所有檔名和指標
- ✅ `highlights.txt` - 關鍵樣本標註
- ✅ `visualizations/` - 波形圖和頻譜圖

**不提交（本地保存）**:
- ❌ `enhanced/`, `noisy/`, `clean/` - 全部音訊檔案
- ❌ 模型檢查點 - 太大
- ❌ 訓練日誌 - 太冗長

**重新生成方法**:
```bash
# 從檢查點重新推理
docker compose run --rm tfgridnet-train \
  python /workspace/scripts/evaluate_best_model.py \
  --checkpoint /workspace/experiments/tfgridnetv2_rtx5090_baseline/checkpoint_epoch_100_best.pth
```

---

### 2. 重要里程碑（完整快照）

當達到以下情況時，額外提交精選音訊：
- 🎯 發表論文
- 🎯 重大性能突破
- 🎯 基準模型建立
- 🎯 需要長期保存的結果

**額外提交**:
- ✅ `audio_samples/best_5/` - 5 個最佳樣本（3 × 5 = 15 個 WAV）
- ✅ `audio_samples/worst_5/` - 5 個最差樣本（3 × 5 = 15 個 WAV）
- ✅ Git tag: `git tag -a v1.0-baseline -m "Baseline model"`

**預期大小**: 約 500KB（30 個 WAV 檔案）

---

## 📊 檔名追溯系統

### CSV 記錄格式
```csv
uttid,si_snr_noisy,si_snr_enhanced,improvement
00001,-38.14,-27.55,10.59
00057,-64.03,-20.69,43.34
```

### 音訊檔案命名規則
```
enhanced/00057.wav   → evaluation_results.csv 中的 uttid=00057
noisy/00057.wav
clean/00057.wav
```

### 完整追溯鏈
```
uttid "00057"
  → evaluation_results.csv (SI-SNR 數據)
  → highlights.txt (標註為最佳樣本)
  → visualizations/00057_waveform.png (波形圖)
  → visualizations/00057_spectrogram.png (頻譜圖)
  → enhanced/00057.wav (音訊檔案 - 本地)
  → 原始 SCP: valid_clean_relative.scp (源頭追溯)
```

---

## 🔍 實驗比較範例

### 比較兩個實驗
```bash
# 實驗 A: Epoch 100
experiments/inference_results/epoch_100_best_20251111_034908/

# 實驗 B: Epoch 500 (未來)
experiments/inference_results/epoch_500_best_20251112_102030/

# 快速比較 CSV
diff -u \
  experiments/inference_results/epoch_100_best_20251111_034908/evaluation_results.csv \
  experiments/inference_results/epoch_500_best_20251112_102030/evaluation_results.csv

# 或使用 Python
python scripts/compare_experiments.py \
  --exp1 epoch_100_best_20251111_034908 \
  --exp2 epoch_500_best_20251112_102030
```

---

## 🗂️ 元數據記錄

### metadata.json 範例
```json
{
  "experiment_name": "rtx5090-soundfile-5000ep",
  "checkpoint": "checkpoint_epoch_100_best.pth",
  "timestamp": "2025-11-11T03:49:00",
  "model": {
    "name": "TFGridNetV2",
    "n_layers": 4,
    "lstm_hidden_units": 128,
    "n_heads": 4,
    "emb_dim": 128
  },
  "training": {
    "total_epochs": 1496,
    "best_epoch": 100,
    "best_valid_loss": 32.34,
    "gpu": "NVIDIA RTX 5090",
    "pytorch_version": "2.9.0+cu128"
  },
  "evaluation": {
    "num_samples": 192,
    "avg_improvement": 1.10,
    "std_improvement": 12.93,
    "best_improvement": 43.34,
    "worst_improvement": -37.95
  },
  "audio_files": {
    "total_count": 576,
    "format": "WAV",
    "sample_rate": 16000,
    "local_path": "/workspace/experiments/inference_results/epoch_100_best_20251111_034908/",
    "in_git": false,
    "regenerate_command": "python scripts/evaluate_best_model.py"
  }
}
```

---

## 📝 實驗清單

| 實驗 ID | 日期 | Epoch | 平均改善 | 狀態 | 說明 |
|---------|------|-------|----------|------|------|
| epoch_100_best_20251111 | 2025-11-11 | 100 | +1.10 dB | ⚠️ 待改進 | 基準實驗 |
| epoch_500_best_20251112 | TBD | 500 | TBD | 🔄 計劃中 | 繼續訓練 |

---

## 🛠️ 工具腳本

### 創建實驗記錄
```bash
python scripts/create_experiment_record.py \
  --checkpoint checkpoint_epoch_100_best.pth \
  --name "baseline-epoch100"
```

### 精選音訊樣本
```bash
python scripts/select_audio_samples.py \
  --input experiments/inference_results/epoch_100_best_20251111_034908/ \
  --output audio_samples/ \
  --best 5 \
  --worst 5
```

### 比較實驗
```bash
python scripts/compare_experiments.py \
  --experiments epoch_100_best_20251111_034908 epoch_500_best_20251112_102030 \
  --output comparison_report.md
```

---

## 💡 最佳實踐

1. **每個實驗創建獨立資料夾** ✅
   - 使用時間戳避免衝突
   - 完整記錄所有元數據

2. **CSV 是實驗的核心** ✅
   - 包含所有檔名和指標
   - 可追溯、可比較、可視覺化

3. **音訊檔案分層管理** ✅
   - 日常：本地保存，Git 只存記錄
   - 里程碑：精選樣本可提交

4. **使用 Git tag 標記重要版本** ✅
   ```bash
   git tag -a v1.0-baseline -m "Baseline: Epoch 100, +1.10 dB"
   git push origin v1.0-baseline
   ```

5. **定期備份本地音訊** ✅
   ```bash
   # 壓縮保存到備份位置
   tar -czf experiments_backup_20251111.tar.gz \
     experiments/inference_results/*/enhanced/ \
     experiments/inference_results/*/noisy/ \
     experiments/inference_results/*/clean/
   ```

---

## 📊 磁碟空間估算

| 內容 | 單個實驗 | 10 個實驗 | 100 個實驗 |
|------|----------|-----------|------------|
| Git (無音訊) | ~2 MB | ~20 MB | ~200 MB |
| 全部音訊 (本地) | ~9 MB | ~90 MB | ~900 MB |
| 精選樣本 (Git) | ~0.5 MB | ~5 MB | ~50 MB |

**建議**:
- < 10 個實驗：可考慮提交精選樣本
- > 10 個實驗：只提交記錄，音訊本地管理
- 重要里程碑：使用 Git LFS 或單獨存儲

---

## 🔄 實驗生命週期

```
1. 訓練 → 產生 checkpoint
2. 評估 → 產生 CSV + 音訊
3. 分析 → 產生視覺化 + 文檔
4. 提交 → Git 記錄核心數據
5. 保存 → 本地備份音訊檔案
6. 比較 → 使用 CSV 對比實驗
```

---

**更新日期**: 2025-11-11  
**維護者**: Hank Jiang
