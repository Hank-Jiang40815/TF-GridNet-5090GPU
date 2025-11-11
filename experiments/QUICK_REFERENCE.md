# 實驗管理快速參考指南

## 📋 目錄結構

```
experiments/
├── EXPERIMENT_MANAGEMENT.md    # 完整管理指南
├── QUICK_REFERENCE.md          # 本檔案（快速參考）
└── inference_results/
    └── epoch_100_best_20251111_034908/  # 實驗資料夾（時間戳記）
        ├── README.md                     # 實驗摘要
        ├── metadata.json                 # 完整元資料
        ├── evaluation_results.csv        # ✅ 核心數據（檔名追蹤）
        ├── highlights.txt                # 最佳/最差樣本
        ├── visualizations/               # 20 張圖表
        │   ├── 00057_waveform.png
        │   └── 00057_spectrogram.png
        ├── audio_samples/                # 🏆 精選樣本（里程碑）
        │   ├── README.md
        │   ├── best_5/                   # 最佳 5 個樣本
        │   │   ├── 00057_enhanced.wav
        │   │   ├── 00057_noisy.wav
        │   │   └── 00057_clean.wav
        │   └── worst_5/                  # 最差 5 個樣本
        ├── enhanced/                     # ❌ 不在 Git（本地）
        ├── noisy/                        # ❌ 不在 Git（本地）
        └── clean/                        # ❌ 不在 Git（本地）
```

## 🚀 快速開始

### 1. 執行訓練
```bash
cd /home/sbplab/Hank/TF-GridNet-5090GPU
docker compose up tfgridnet-train
```

### 2. 評估最佳模型
```bash
# 找到最佳 checkpoint
ls -lh experiments/checkpoints/

# 執行評估（會生成所有音訊檔案）
docker compose run --rm tfgridnet-train \
  python scripts/evaluate_best_model.py \
  --checkpoint /workspace/experiments/checkpoints/checkpoint_epoch_100_best.pth \
  --data-dir /workspace/data \
  --output-dir /workspace/experiments/inference_results
```

### 3. 生成視覺化
```bash
# 為 10 個代表性樣本生成波形和頻譜圖
docker compose run --rm tfgridnet-train \
  python scripts/visualize_samples.py \
  --result-dir /workspace/experiments/inference_results/epoch_100_best_20251111_034908
```

### 4. 精選音訊樣本（里程碑）
```bash
# 選擇最佳和最差各 5 個樣本
docker compose run --rm tfgridnet-train \
  python scripts/select_audio_samples.py \
  --result-dir /workspace/experiments/inference_results/epoch_100_best_20251111_034908
```

### 5. 比較兩個實驗
```bash
# 比較兩個實驗的評估結果
python scripts/compare_experiments.py \
  --exp1 experiments/inference_results/epoch_100_best_20251111_034908 \
  --exp2 experiments/inference_results/epoch_200_best_20251112_120000
```

### 6. 提交到 Git

#### 日常實驗（輕量級）
```bash
git add experiments/inference_results/epoch_XXX_*/
git add experiments/inference_results/epoch_XXX_*/README.md
git add experiments/inference_results/epoch_XXX_*/metadata.json
git add experiments/inference_results/epoch_XXX_*/evaluation_results.csv
git add experiments/inference_results/epoch_XXX_*/highlights.txt
git add experiments/inference_results/epoch_XXX_*/visualizations/
git commit -m "exp: Add daily experiment epoch XXX"
```

#### 里程碑實驗（包含音訊樣本）
```bash
# 先生成精選樣本（見步驟 4）
git add -f experiments/inference_results/epoch_XXX_*/audio_samples/**/*.wav
git commit -m "milestone: Add epoch XXX with selected audio samples"
git tag -a vX.X-milestone -m "Description"
```

## 📊 檔案追蹤系統

### CSV 是核心
`evaluation_results.csv` 包含完整的檔名追蹤：
```csv
uttid,si_snr_noisy,si_snr_enhanced,improvement
00001,-38.14,-27.55,10.59
00057,-12.21,31.13,43.34
```

### 追蹤鏈
```
uttid "00057" in CSV
  ↓
highlights.txt: "最佳改善: 00057 (+43.34 dB)"
  ↓
visualizations/00057_waveform.png
visualizations/00057_spectrogram.png
  ↓
enhanced/00057.wav  (本地，可重新生成)
noisy/00057.wav
clean/00057.wav
  ↓
audio_samples/best_5/00057_enhanced.wav  (精選，在 Git 中)
```

### 重新生成音訊檔案
如果本地音訊檔案丟失，可以從 checkpoint 重新生成：
```bash
docker compose run --rm tfgridnet-train \
  python scripts/evaluate_best_model.py \
  --checkpoint /workspace/experiments/checkpoints/checkpoint_epoch_100_best.pth \
  --data-dir /workspace/data \
  --output-dir /workspace/experiments/inference_results
```

## 🎯 兩階段策略

### 日常實驗（Daily）
- **提交內容**: CSV + docs + visualizations (~2 MB)
- **音訊檔案**: 不提交（本地保存，~9 MB）
- **用途**: 快速迭代，保持 repo 輕量
- **可重現性**: ✅ 透過 checkpoint 重新生成

### 里程碑實驗（Milestone）
- **提交內容**: 日常 + 精選樣本 (~2.5 MB)
- **音訊樣本**: 10 個最佳 + 10 個最差 (30 個 WAV，~470 KB)
- **用途**: 重要基準，快速驗證
- **標籤**: 使用 Git tag 標記版本

## 📈 儲存空間估算

### 單一實驗
- **在 Git 中**:
  - 日常: ~2 MB (CSV + docs + visualizations)
  - 里程碑: ~2.5 MB (日常 + 精選樣本 ~470 KB)
- **本地**:
  - 完整音訊: ~9 MB (576 個 WAV)
  - Checkpoint: ~50-100 MB
  - 訓練日誌: ~1-5 MB

### 100 個實驗
- **在 Git 中**:
  - 90 個日常: 180 MB
  - 10 個里程碑: 25 MB
  - **總計**: ~205 MB
- **本地**:
  - 完整音訊: ~900 MB
  - Checkpoints: ~5-10 GB
  - 訓練日誌: ~100-500 MB

## 🔍 查詢實驗資訊

### 查看所有實驗
```bash
ls -lh experiments/inference_results/
```

### 查看特定實驗摘要
```bash
cat experiments/inference_results/epoch_100_best_20251111_034908/README.md
```

### 查看元資料
```bash
cat experiments/inference_results/epoch_100_best_20251111_034908/metadata.json | jq
```

### 查看最佳/最差樣本
```bash
cat experiments/inference_results/epoch_100_best_20251111_034908/highlights.txt
```

### 查看評估結果（前 10 個）
```bash
head -11 experiments/inference_results/epoch_100_best_20251111_034908/evaluation_results.csv
```

### 查看所有 Git 標籤
```bash
git tag -l
git show v1.0-baseline
```

## 🛠️ 常用命令

### 檢查磁碟使用量
```bash
# 單一實驗（在 Git 中）
du -sh experiments/inference_results/epoch_100_best_20251111_034908/

# 單一實驗（本地音訊）
du -sh experiments/inference_results/epoch_100_best_20251111_034908/*/*.wav

# 所有實驗
du -sh experiments/inference_results/
```

### 清理本地音訊檔案
```bash
# 刪除特定實驗的音訊檔案（保留 CSV 和文件）
rm -rf experiments/inference_results/epoch_100_best_20251111_034908/enhanced/
rm -rf experiments/inference_results/epoch_100_best_20251111_034908/noisy/
rm -rf experiments/inference_results/epoch_100_best_20251111_034908/clean/
# 保留 audio_samples/ 不刪除
```

### 檢查檔案數量
```bash
# CSV 中的樣本數
wc -l experiments/inference_results/epoch_100_best_20251111_034908/evaluation_results.csv

# 視覺化圖表數
ls experiments/inference_results/epoch_100_best_20251111_034908/visualizations/*.png | wc -l

# 精選樣本數
find experiments/inference_results/epoch_100_best_20251111_034908/audio_samples/ -name "*.wav" | wc -l
```

## 📝 最佳實踐

### 1. 命名規範
- 實驗資料夾: `epoch_{N}_best_{TIMESTAMP}/`
- 音訊檔案: `{uttid}_{type}.wav` (e.g., `00057_enhanced.wav`)
- Git 標籤: `vX.X-{type}` (e.g., `v1.0-baseline`, `v1.1-improved`)

### 2. 提交訊息
- 日常: `exp: Add epoch XXX experiment`
- 里程碑: `milestone: Epoch XXX achieves Y dB improvement`
- 功能: `feat: Add new feature`
- 修復: `fix: Fix bug in X`
- 文件: `docs: Update documentation`

### 3. 定期清理
- 每 10 個實驗: 審查並保留重要的里程碑
- 每月: 刪除不需要的本地音訊檔案
- 每季: 標記重要實驗為 Git tag

### 4. 備份策略
- **在 Git 中**: CSV + docs + visualizations + 精選樣本
- **本地備份**: Checkpoints + 完整音訊（外部硬碟）
- **雲端備份**: Git repo + 重要 checkpoints

## 🎯 基準實驗參考

### v1.0-baseline (當前)
- **時間**: 2025-01-11 03:49:08
- **模型**: Epoch 100 (最佳)
- **效能**: Average SI-SNR +1.10 dB
- **狀態**: 低於預期 (目標 >5 dB)
- **查看**: `git show v1.0-baseline`

## 📚 相關文件

- [完整管理指南](./EXPERIMENT_MANAGEMENT.md) - 詳細的實驗管理策略
- [實驗分析](./EXPERIMENT_ANALYSIS_20251111.md) - 訓練過程完整分析
- [評估腳本](../scripts/evaluate_best_model.py) - 模型評估工具
- [視覺化腳本](../scripts/visualize_samples.py) - 圖表生成工具
- [樣本選擇腳本](../scripts/select_audio_samples.py) - 精選樣本工具
- [比較腳本](../scripts/compare_experiments.py) - 實驗比較工具

## ❓ 常見問題

### Q: 音訊檔案為什麼不在 Git 中？
A: 為了保持 repo 輕量（單一實驗 ~9 MB 音訊）。CSV 已包含完整檔名追蹤，可從 checkpoint 重新生成。

### Q: 如何選擇哪些實驗做為里程碑？
A: 建議選擇：
- 首次達到預期效能的實驗
- 顯著改善的實驗（例如 >5 dB 改善）
- 模型架構變更的實驗
- 最終提交前的實驗

### Q: audio_samples/ 中應該包含多少樣本？
A: 預設 10 個（5 最佳 + 5 最差），每個包含 3 個檔案（enhanced, noisy, clean），總共 30 個 WAV (~470 KB)。可根據需求調整。

### Q: 如果我想要更多樣本在 Git 中怎麼辦？
A: 使用 `select_audio_samples.py` 的參數：
```bash
python scripts/select_audio_samples.py \
  --result-dir experiments/inference_results/epoch_XXX_*/ \
  --best 10 \
  --worst 10
```

### Q: 如何查看兩個實驗的差異？
A: 使用比較腳本：
```bash
python scripts/compare_experiments.py \
  --exp1 experiments/inference_results/epoch_100_best_20251111_034908 \
  --exp2 experiments/inference_results/epoch_200_best_20251112_120000
```

## 🎓 學習路徑

1. **基礎**: 閱讀本檔案（快速參考）
2. **進階**: 閱讀 [EXPERIMENT_MANAGEMENT.md](./EXPERIMENT_MANAGEMENT.md)
3. **實踐**: 執行一個完整的實驗流程（訓練 → 評估 → 視覺化 → 提交）
4. **精通**: 建立自己的實驗比較和分析流程

---

**更新日期**: 2025-01-11  
**版本**: 1.0  
**維護者**: sbplab@sbplab
