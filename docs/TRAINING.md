# 訓練流程說明

本文檔說明如何使用本專案進行 TF-GridNetV2 模型訓練。

## 🎯 訓練流程概覽

```
準備資料 → 配置調整 → 執行訓練 → 監控進度 → 記錄結果 → 評估模型
```

## 📋 訓練前檢查清單

- [ ] 環境已正確安裝（執行過 `./scripts/setup_host.sh`）
- [ ] Docker image 已建構（`docker-compose build`）
- [ ] Smoke test 通過（`./scripts/run_smoke_test.sh`）
- [ ] 資料已準備好（`/home/sbplab/Hank/ESPnet/TFG-Transfer-Package/data`）
- [ ] 配置檔已調整（`configs/training_rtx5090.yaml`）
- [ ] GPU 可用且記憶體充足（`nvidia-smi`）

## 🚀 開始訓練

### 基本訓練命令

```bash
./scripts/run_training.sh <experiment_name> [config_file] [skip_memory_test]
```

**參數說明**:
- `experiment_name`: 實驗名稱（必填）
- `config_file`: 配置檔路徑（選填，預設: `/workspace/configs/training_rtx5090.yaml`）
- `skip_memory_test`: 跳過記憶體測試（選填，`true`/`false`，預設: `false`）

### 範例

```bash
# 1. 基準實驗
./scripts/run_training.sh baseline

# 2. 使用自訂配置
./scripts/run_training.sh my-experiment /workspace/configs/my_config.yaml

# 3. 快速啟動（跳過記憶體測試）
./scripts/run_training.sh quick-test /workspace/configs/training_rtx5090.yaml true
```

## 📊 監控訓練

### 實時日誌

```bash
# 查看最新實驗的訓練日誌
tail -f experiments/logs/$(ls -t experiments/logs | head -1)/training.log
```

### GPU 監控

```bash
# 實時監控 GPU
watch -n 1 nvidia-smi

# 查看記憶體使用
nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv -l 1
```

### TensorBoard（如果啟用）

```bash
# 啟動 TensorBoard 服務
docker-compose --profile tensorboard up tensorboard

# 訪問 http://localhost:6006
```

## 📝 實驗記錄

### 自動記錄

訓練腳本會自動產生實驗目錄：

```
experiments/logs/YYYYMMDD-HHMMSS-<experiment_name>/
├── config.yaml          # 配置備份
├── training.log         # 訓練日誌
├── environment.txt      # 環境資訊
├── git_info.txt         # Git commit
├── experiment.md        # 實驗記錄範本
├── checkpoints/
└── results/
```

### 手動填寫實驗記錄

訓練開始後，編輯 `experiment.md`:

```bash
# 找到最新實驗目錄
EXP_DIR=$(ls -td experiments/logs/* | head -1)

# 編輯實驗記錄
vim $EXP_DIR/experiment.md
```

**必填項目**:
- 實驗目的
- 配置變更
- 預期結果

**訓練後填寫**:
- 實際結果
- 觀察與分析
- 下一步計劃

詳細指南請參閱 [`../experiments/README.md`](../experiments/README.md)。

## ⚙️ 配置調整

### 批次大小調整

根據 GPU 記憶體調整 `configs/training_rtx5090.yaml`:

```yaml
training:
  batch_size: 32  # 調整此值
  
  # 如果 OOM，啟用 gradient accumulation
  gradient_accumulation:
    enabled: true
    steps: 4  # 有效批次 = batch_size * steps
```

**推薦值**（RTX 5090 32GB）:
- 保守: 32
- 平衡: 64
- 激進: 128（可能需要 gradient checkpointing）

### 學習率調整

```yaml
training:
  learning_rate: 0.0005  # 基準值
  
  # 批次大小翻倍時，學習率也應調整
  # batch_size: 32 → 64, learning_rate: 0.0005 → 0.001
```

### 模型容量調整

```yaml
model:
  architecture:
    emb_dim: 128          # 可增加到 192 或 256
    lstm_hidden_units: 128  # 可增加到 192 或 256
    n_layers: 4           # 可增加到 6 或 8
    n_heads: 4            # 可增加到 8
```

更多配置說明請參閱 [`../configs/README.md`](../configs/README.md)。

## 🔄 訓練策略

### 從頭訓練

```bash
./scripts/run_training.sh baseline
```

### 從檢查點繼續訓練

修改配置檔：

```yaml
training:
  resume_from_checkpoint: /workspace/experiments/logs/YYYYMMDD-HHMMSS-baseline/checkpoints/epoch_50.pth
```

### 遷移學習

```yaml
model:
  pretrained_weights: /path/to/pretrained_model.pth
  freeze_encoder: false  # 是否凍結編碼器
```

## 📈 訓練技巧

### 1. 批次大小尋找

逐步增加批次大小直到 OOM，然後回退：

```bash
# 測試不同批次大小
for bs in 16 32 64 128 256; do
    # 修改 config batch_size=$bs
    # 執行短訓練看是否 OOM
done
```

### 2. 學習率尋找

使用學習率 finder 找到最佳學習率：

```python
# 在訓練腳本中添加
from torch.optim.lr_scheduler import LRFinder
# ... 實作 LR finder
```

### 3. 梯度累積

當受限於記憶體時：

```yaml
training:
  batch_size: 16
  gradient_accumulation:
    enabled: true
    steps: 8  # 有效批次 = 128
```

### 4. 混合精度訓練

啟用以加速 2-3x：

```yaml
training:
  mixed_precision:
    enabled: true  # RTX 5090 支援
    opt_level: O1
```

### 5. 資料增強

考慮添加：
- 時域增強（time stretching, pitch shifting）
- 頻域增強（SpecAugment）
- 混合增強（mixup, cutmix）

## ⏹️ 停止與恢復

### 正常停止

訓練會在每個 epoch 結束時儲存檢查點。按 `Ctrl+C` 正常停止。

### 從檢查點恢復

```bash
# 找到最新檢查點
ls -lh experiments/logs/<experiment>/checkpoints/

# 修改配置檔指向檢查點
# 重新啟動訓練
./scripts/run_training.sh continue-experiment
```

## 🎓 最佳實踐

1. **小規模測試**: 先用少量資料與少數 epoch 測試配置
2. **記錄詳細**: 填寫完整的實驗記錄
3. **定期備份**: 重要檢查點複製到安全位置
4. **監控指標**: 關注 loss 曲線與 GPU 使用率
5. **對比實驗**: 一次只改變一個變數
6. **版本控制**: 重要的配置變更提交到 Git

## 📊 評估結果

訓練完成後：

```bash
# 查看訓練日誌
cat experiments/logs/<experiment>/training.log | grep "Validation"

# 查看最佳模型
ls -lh experiments/logs/<experiment>/checkpoints/best_model.pth

# 執行評估（如有評估腳本）
# ./scripts/run_evaluation.sh <experiment>
```

## 🔧 故障排除

### 訓練很慢

1. 檢查 GPU 利用率：`nvidia-smi`
2. 增加 `num_workers`
3. 啟用混合精度
4. 檢查資料載入瓶頸

### Out of Memory

1. 減小 batch_size
2. 啟用 gradient_checkpointing
3. 使用 gradient accumulation
4. 減小模型大小

### Loss 不下降

1. 檢查學習率（太大或太小）
2. 檢查資料預處理
3. 檢查 loss function
4. 增加模型容量

### 梯度爆炸

1. 啟用 gradient clipping
2. 降低學習率
3. 檢查資料正規化

完整故障排除請參閱 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)。

## 📚 延伸閱讀

- [配置說明](../configs/README.md)
- [實驗記錄指南](../experiments/README.md)
- [故障排除](TROUBLESHOOTING.md)

---

**祝訓練順利！🚀**
