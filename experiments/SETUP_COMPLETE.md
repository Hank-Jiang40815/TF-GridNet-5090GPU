# 🎉 實驗管理系統設置完成

## ✅ 已完成工作

### 1. 完整的實驗管理框架 ✅
已建立完善的實驗管理體系，包含：

#### 📚 核心文件
- **EXPERIMENT_MANAGEMENT.md** (350+ 行)
  - 兩階段策略（日常/里程碑）
  - 目錄結構規範
  - metadata.json 格式定義
  - 比較工具說明
  - 磁碟空間估算
  - 最佳實踐指南

- **QUICK_REFERENCE.md** (320+ 行)
  - 快速入門指南
  - 常用命令合集
  - 檔案追蹤系統說明
  - 儲存空間計算
  - FAQ 和疑難排解

#### 🛠️ 自動化工具
- **select_audio_samples.py**
  - 自動選擇最佳/最差樣本
  - 生成 audio_samples/ 目錄
  - 創建 README 說明
  - 預設：5 最佳 + 5 最差 (30 個 WAV，~470 KB)

- **compare_experiments.py**
  - 比較兩個實驗的評估結果
  - 統計分析（平均、標準差、百分位數等）
  - 效能分類（優秀、良好、中等、差）
  - 模型配置比較
  - 訓練資訊對比
  - 逐樣本差異分析

### 2. 基準實驗 (v1.0-baseline) ✅

#### 📁 實驗目錄結構
```
experiments/inference_results/epoch_100_best_20251111_034908/
├── README.md                     # ✅ 實驗摘要
├── metadata.json                 # ✅ 完整元資料
├── evaluation_results.csv        # ✅ 核心數據（192 樣本）
├── highlights.txt                # ✅ 最佳/最差樣本
├── visualizations/               # ✅ 20 張圖表
│   ├── 00001_waveform.png
│   ├── 00001_spectrogram.png
│   ├── ... (共 20 個 PNG)
└── audio_samples/                # ✅ 精選樣本（里程碑）
    ├── README.md
    ├── best_5/                   # 最佳 5 個樣本
    │   ├── 00057_enhanced.wav    (+43.34 dB)
    │   ├── 00057_noisy.wav
    │   ├── 00057_clean.wav
    │   ├── 00056_enhanced.wav    (+39.72 dB)
    │   ├── ... (共 15 個 WAV)
    └── worst_5/                  # 最差 5 個樣本
        ├── 00130_enhanced.wav    (-37.95 dB)
        ├── 00130_noisy.wav
        ├── 00130_clean.wav
        ├── ... (共 15 個 WAV)
```

#### 🏷️ Git 標籤
```bash
v1.0-baseline - Baseline experiment: RTX 5090 + soundfile
  Training: 1,496 epochs
  Best model: Epoch 100
  Performance: +1.10 dB (average SI-SNR improvement)
```

#### 📊 關鍵指標
- **樣本數**: 192 validation samples
- **平均改善**: +1.10 dB
- **標準差**: 12.93 dB
- **最佳樣本**: 00057 (+43.34 dB)
- **最差樣本**: 00130 (-37.95 dB)
- **效能狀態**: 低於預期（目標 >5 dB）

### 3. Git 提交記錄 ✅

#### 最近 4 次提交
```
455ce95 (HEAD -> main) docs: Add experiment management quick reference guide
7dc8836 (tag: v1.0-baseline) feat: Add milestone audio samples for baseline experiment
3c21d04 feat: Add comprehensive experiment management framework
9288867 feat: Complete RTX 5090 training experiment with soundfile + comprehensive analysis
```

#### 提交統計
- **總提交數**: 4 個（實驗管理相關）
- **新增檔案**: 
  - 2 個管理文件（EXPERIMENT_MANAGEMENT.md, QUICK_REFERENCE.md）
  - 2 個工具腳本（select_audio_samples.py, compare_experiments.py）
  - 1 個元資料檔（metadata.json）
  - 31 個音訊樣本（audio_samples/）
- **新增行數**: ~1,400 行（文件 + 腳本）
- **音訊檔案**: 30 個 WAV (~470 KB)

### 4. 檔案追蹤系統 ✅

#### 🔗 完整追蹤鏈
```
CSV uttid "00057"
  ↓
evaluation_results.csv
  uttid,si_snr_noisy,si_snr_enhanced,improvement
  00057,-12.21,31.13,43.34
  ↓
highlights.txt
  "最佳改善: 00057 (+43.34 dB)"
  ↓
visualizations/
  00057_waveform.png
  00057_spectrogram.png
  ↓
enhanced/00057.wav       (本地，~16 KB)
noisy/00057.wav          (本地，~16 KB)
clean/00057.wav          (本地，~16 KB)
  ↓
audio_samples/best_5/
  00057_enhanced.wav      (Git 中，~16 KB)
  00057_noisy.wav         (Git 中，~16 KB)
  00057_clean.wav         (Git 中，~16 KB)
```

#### 🔄 可重現性保證
- **CSV 檔案**: 完整的 uttid 追蹤（192 個樣本）
- **Checkpoint**: 可重新生成所有音訊檔案
- **腳本**: evaluate_best_model.py 可重跑評估
- **命令**: 記錄在 metadata.json 中

### 5. .gitignore 策略 ✅

```gitignore
# Experiment management - exclude full audio but keep selected samples
experiments/inference_results/*/enhanced/      # ❌ 排除
experiments/inference_results/*/noisy/         # ❌ 排除
experiments/inference_results/*/clean/         # ❌ 排除
!experiments/inference_results/*/audio_samples/ # ✅ 保留
```

**結果**:
- 完整音訊目錄（576 WAV，~9 MB）不在 Git 中
- 精選樣本（30 WAV，~470 KB）在 Git 中
- Repo 保持輕量，但有快速驗證能力

## 📈 儲存空間統計

### 當前實驗（v1.0-baseline）
| 項目 | Git 中 | 本地 | 說明 |
|------|--------|------|------|
| CSV + 文件 | ~50 KB | ~50 KB | 核心數據 |
| 視覺化圖表 | ~1.8 MB | ~1.8 MB | 20 個 PNG |
| 精選樣本 | ~470 KB | ~470 KB | 30 個 WAV |
| 完整音訊 | ❌ | ~9 MB | 576 個 WAV |
| Checkpoint | ❌ | ~50 MB | 模型權重 |
| **總計** | **~2.3 MB** | **~61 MB** | 單一實驗 |

### 100 個實驗估算
| 項目 | Git 中 | 本地 |
|------|--------|------|
| 90 個日常實驗 | 180 MB | 8.1 GB |
| 10 個里程碑實驗 | 23 MB | 610 MB |
| **總計** | **~203 MB** | **~8.7 GB** |

**結論**: 即使 100 個實驗，Git repo 也只有 ~200 MB，非常合理！

## 🎯 使用範例

### 日常實驗流程

#### 1. 執行訓練
```bash
cd /home/sbplab/Hank/TF-GridNet-5090GPU
docker compose up tfgridnet-train
```

#### 2. 評估最佳模型
```bash
docker compose run --rm tfgridnet-train \
  python scripts/evaluate_best_model.py \
  --checkpoint /workspace/experiments/checkpoints/checkpoint_epoch_XXX_best.pth \
  --data-dir /workspace/data \
  --output-dir /workspace/experiments/inference_results
```

#### 3. 生成視覺化
```bash
docker compose run --rm tfgridnet-train \
  python scripts/visualize_samples.py \
  --result-dir /workspace/experiments/inference_results/epoch_XXX_best_TIMESTAMP
```

#### 4. 提交（日常）
```bash
git add experiments/inference_results/epoch_XXX_*/
git commit -m "exp: Add epoch XXX experiment"
git push
```

### 里程碑實驗流程

#### 1-3. 同日常實驗

#### 4. 精選樣本
```bash
docker compose run --rm tfgridnet-train \
  python scripts/select_audio_samples.py \
  --result-dir /workspace/experiments/inference_results/epoch_XXX_best_TIMESTAMP
```

#### 5. 提交（里程碑）
```bash
git add experiments/inference_results/epoch_XXX_*/
git add -f experiments/inference_results/epoch_XXX_*/audio_samples/**/*.wav
git commit -m "milestone: Epoch XXX achieves Y dB improvement"
git tag -a vX.X-milestone -m "Description"
git push origin main
git push origin vX.X-milestone
```

### 實驗比較
```bash
python scripts/compare_experiments.py \
  --exp1 experiments/inference_results/epoch_100_best_20251111_034908 \
  --exp2 experiments/inference_results/epoch_200_best_20251112_120000
```

## 🔍 查詢實驗

### 查看所有實驗
```bash
ls -lh experiments/inference_results/
```

### 查看特定實驗
```bash
# 摘要
cat experiments/inference_results/epoch_100_best_20251111_034908/README.md

# 元資料
cat experiments/inference_results/epoch_100_best_20251111_034908/metadata.json | jq

# 最佳/最差樣本
cat experiments/inference_results/epoch_100_best_20251111_034908/highlights.txt

# 評估結果（前 10 個）
head -11 experiments/inference_results/epoch_100_best_20251111_034908/evaluation_results.csv
```

### 查看 Git 標籤
```bash
git tag -l
git show v1.0-baseline
```

## 📚 文件導覽

### 入門
1. **[QUICK_REFERENCE.md](experiments/QUICK_REFERENCE.md)** - 從這裡開始！
   - 快速入門指南
   - 常用命令
   - FAQ

### 詳細指南
2. **[EXPERIMENT_MANAGEMENT.md](experiments/EXPERIMENT_MANAGEMENT.md)** - 完整管理策略
   - 兩階段策略詳解
   - 目錄結構規範
   - metadata.json 格式
   - 最佳實踐

### 實驗分析
3. **[EXPERIMENT_ANALYSIS_20251111.md](experiments/EXPERIMENT_ANALYSIS_20251111.md)** - 訓練過程分析
   - 訓練曲線
   - 效能分析
   - 問題診斷

### 工具腳本
4. **scripts/evaluate_best_model.py** - 模型評估
5. **scripts/visualize_samples.py** - 視覺化生成
6. **scripts/select_audio_samples.py** - 精選樣本
7. **scripts/compare_experiments.py** - 實驗比較

## 🚀 下一步建議

### 立即可做
1. ✅ **實驗管理系統已完成** - 可以開始新實驗了！
2. 📖 **閱讀快速參考** - 熟悉常用命令
3. 🔬 **診斷效能問題** - 為什麼只有 +1.10 dB？

### 效能改善方向
根據 metadata.json 中的調查筆記：

#### 可能問題
1. **資料前處理**
   - 驗證音訊載入和重採樣
   - 檢查 STFT 參數
   - 確認正規化方法

2. **損失函數**
   - SI-SNR 計算是否正確
   - 訓練/評估一致性
   - 參考音訊對齊

3. **模型輸出**
   - 輸出範圍檢查
   - Mask 應用驗證
   - 相位重建

4. **訓練配置**
   - 學習率可能太高或太低
   - Batch size 影響
   - 混合精度問題

#### 建議實驗
1. **診斷實驗**
   ```bash
   # 創建診斷腳本驗證每個環節
   python scripts/diagnose_data_pipeline.py
   python scripts/diagnose_loss_calculation.py
   python scripts/diagnose_model_output.py
   ```

2. **對照實驗**
   - 使用原始 torchaudio（如果可行）
   - 不同學習率
   - 不同模型大小

3. **消融研究**
   - 移除混合精度
   - 移除梯度 checkpointing
   - 不同損失函數

### 組織管理
1. **定期審查**
   - 每 10 個實驗審查一次
   - 保留重要里程碑
   - 刪除不必要的本地音訊

2. **備份策略**
   - Git: CSV + docs + visualizations + 精選樣本
   - 本地: Checkpoints + 完整音訊
   - 雲端: 重要 checkpoints

3. **團隊協作**
   - 所有實驗都有清晰文件
   - metadata.json 包含所有配置
   - 可重現的評估流程

## ✨ 系統亮點

### 1. 完整追蹤 ✅
- CSV uttid 欄位追蹤所有 192 個樣本
- 每個樣本對應 3 個音訊檔案
- metadata.json 記錄所有配置
- 可重現的評估命令

### 2. 輕量級 Git ✅
- 日常實驗: ~2 MB/個
- 里程碑實驗: ~2.5 MB/個
- 100 個實驗: ~200 MB
- 音訊檔案不佔 repo 空間

### 3. 快速驗證 ✅
- 精選樣本在 Git 中 (~470 KB)
- 最佳和最差各 5 個
- 可以快速聽音訊確認效能
- 不需要重新生成

### 4. 自動化工具 ✅
- evaluate_best_model.py: 自動評估
- visualize_samples.py: 自動視覺化
- select_audio_samples.py: 自動精選
- compare_experiments.py: 自動比較

### 5. 可擴展性 ✅
- 支援 10-100+ 個實驗
- 清晰的目錄結構
- 標準化的檔案格式
- 一致的命名規範

### 6. 可重現性 ✅
- Checkpoint 保存完整模型
- 腳本記錄評估流程
- metadata.json 包含所有參數
- CSV 追蹤所有樣本

## 🎓 學習資源

### 第一次使用？
1. 閱讀 [QUICK_REFERENCE.md](experiments/QUICK_REFERENCE.md)
2. 執行一次完整流程
3. 比較兩個實驗
4. 創建自己的里程碑

### 進階使用？
1. 閱讀 [EXPERIMENT_MANAGEMENT.md](experiments/EXPERIMENT_MANAGEMENT.md)
2. 自訂 select_audio_samples.py 參數
3. 建立自己的分析腳本
4. 整合到 CI/CD pipeline

## 📞 需要幫助？

### 常見問題
查看 [QUICK_REFERENCE.md](experiments/QUICK_REFERENCE.md) 的 FAQ 區段

### 問題追蹤
- 音訊檔案追蹤: CSV uttid 欄位
- 實驗配置: metadata.json
- 效能分析: highlights.txt
- 視覺驗證: visualizations/

### 除錯流程
1. 檢查 metadata.json 中的配置
2. 查看 evaluation_results.csv 的數據
3. 比較 visualizations/ 中的圖表
4. 聆聽 audio_samples/ 中的音訊
5. 使用 compare_experiments.py 比較

---

## 🎉 總結

你現在擁有一個**完整、輕量級、可擴展的實驗管理系統**！

### ✅ 已建立
- 📚 完整文件（2 個指南，~670 行）
- 🛠️ 自動化工具（2 個腳本，~400 行）
- 🏷️ 基準實驗（v1.0-baseline）
- 📊 精選樣本（30 個 WAV，~470 KB）
- 🔗 完整追蹤鏈（uttid → CSV → audio）

### ✅ 已驗證
- Git repo 輕量（~2.3 MB/實驗）
- 完整可重現（checkpoint + scripts）
- 快速驗證（audio_samples/）
- 標準化流程（兩階段策略）

### 🚀 可以開始
- 執行新實驗
- 診斷效能問題
- 比較不同配置
- 建立實驗歷史

**祝實驗順利！** 🎊

---

**創建日期**: 2025-01-11  
**版本**: 1.0  
**狀態**: ✅ 完成
