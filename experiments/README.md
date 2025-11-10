# Experiment Logging Guide

本目錄用於記錄所有訓練實驗的詳細資訊與結果。

## 📁 目錄結構

```
experiments/
├── README.md                    # 本文件
├── experiment_template.md       # 實驗記錄範本
└── logs/                        # 實驗日誌目錄
    ├── 20251110-120000-baseline/
    │   ├── config.yaml          # 使用的配置檔
    │   ├── experiment.md        # 實驗記錄（需手動填寫）
    │   ├── training.log         # 訓練日誌（自動產生）
    │   ├── environment.txt      # 環境資訊
    │   ├── git_info.txt         # Git commit 資訊
    │   ├── checkpoints/         # 模型檢查點
    │   │   ├── best_model.pth
    │   │   └── epoch_*.pth
    │   └── results/             # 評估結果
    │       └── validation_results.json
    └── 20251111-143000-large-batch/
        └── ...
```

## 🚀 使用方式

### 1. 啟動新實驗

使用訓練腳本會自動建立實驗目錄：

```bash
./scripts/run_training.sh my-experiment-name
```

這會建立：
- 帶時間戳的實驗目錄
- 複製當前配置檔
- 記錄 Git 資訊
- 產生實驗記錄範本

### 2. 填寫實驗記錄

在訓練開始前或訓練期間，編輯 `experiment.md`：

```bash
vim experiments/logs/20251110-120000-my-experiment/experiment.md
```

**必填項目：**
- 🎯 Objective: 實驗目的
- 🔧 Configuration Changes: 修改了哪些參數
- 📊 Expected Results: 預期結果

**訓練後填寫：**
- 📈 Actual Results: 實際結果與指標
- 🔍 Observations: 訓練過程觀察
- 📝 Analysis: 結果分析
- 🔄 Next Steps: 下一步行動

### 3. 監控訓練

實時查看訓練日誌：

```bash
tail -f experiments/logs/20251110-120000-my-experiment/training.log
```

使用 TensorBoard（如果有記錄）：

```bash
tensorboard --logdir experiments/logs/20251110-120000-my-experiment
```

### 4. 實驗比較

列出所有實驗：

```bash
ls -lt experiments/logs/
```

比較兩個實驗的配置：

```bash
diff experiments/logs/exp1/config.yaml experiments/logs/exp2/config.yaml
```

## 📊 實驗命名建議

使用有意義的實驗名稱，例如：

- `baseline` - 基準實驗
- `large-batch-32` - 大批次大小實驗
- `lr-schedule-cosine` - 學習率調度實驗
- `data-aug-v2` - 資料增強實驗
- `ablation-attention` - 消融實驗

格式：`<主題>-<關鍵變更>-<版本>`

## 🔍 實驗檢查清單

在開始新實驗前，確認：

- [ ] 已閱讀並理解之前類似實驗的結果
- [ ] 已明確定義實驗目的與假設
- [ ] 已記錄所有配置變更
- [ ] 已準備好評估指標
- [ ] 已確認 GPU 資源可用
- [ ] 已設定合理的訓練時間預期

訓練完成後，確認：

- [ ] 已填寫所有實驗記錄欄位
- [ ] 已儲存最佳模型檢查點
- [ ] 已備份重要結果
- [ ] 已更新實驗索引（如果有）
- [ ] 已規劃下一步實驗

## 📈 結果分析建議

### 量化指標

記錄以下關鍵指標：

- **Loss**: Training loss, validation loss
- **SI-SDR**: 訊號失真比改善
- **PESQ**: 感知評估語音品質
- **STOI**: 短時客觀可懂度
- **Training time**: 訓練總時間
- **GPU memory**: 峰值記憶體使用

### 質性觀察

記錄主觀評估：

- 輸出音訊清晰度
- 人聲與背景音分離程度
- 是否有明顯人工痕跡
- 與 ground truth 的相似度

### 性能分析

- GPU 利用率
- 資料載入速度
- 每個 epoch 時間
- 記憶體瓶頸

## 🎯 實驗最佳實踐

1. **一次改變一個變數**: 方便分析因果關係
2. **記錄詳細資訊**: 未來的你會感謝現在的你
3. **定期備份**: 重要檢查點與結果
4. **重現性**: 記錄所有隨機種子與環境
5. **版本控制**: Commit 重要的程式碼變更

## 📚 相關資源

- **TF-GridNetV2 論文**: [arxiv link]
- **訓練指南**: `../docs/TRAINING.md`
- **故障排除**: `../docs/TROUBLESHOOTING.md`
- **配置說明**: `../configs/README.md`

## 💡 提示

- 使用 Git 管理實驗記錄：將重要的 experiment.md 加入版本控制
- 建立實驗索引文件追蹤所有實驗關係
- 定期回顧實驗記錄，總結學習經驗
- 與團隊成員分享有價值的實驗結果

---

**Happy Experimenting! 🎉**
