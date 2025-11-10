# Configuration Files

本目錄包含不同場景的訓練配置檔案。

## 📁 檔案說明

### `training_rtx5090.yaml`
**RTX 5090 優化配置（推薦）**

針對 NVIDIA RTX 5090 (32GB VRAM) 優化的配置：
- CUDA 加速啟用
- Batch size: 32 (可調整至 64-128)
- Mixed precision 訓練
- Gradient accumulation: 4 steps
- 多 worker 資料載入

**適用場景:**
- RTX 5090 單 GPU 訓練
- 基準實驗
- 生產環境訓練

## 🔧 配置參數說明

### Hardware Section
```yaml
hardware:
  use_cuda: true          # 使用 CUDA
  use_ddp: false          # 單 GPU（多 GPU 設為 true）
  world_size: 1           # GPU 數量
  device_ids: [0]         # CUDA 裝置 ID
```

### Training Section - 關鍵參數

#### Batch Size
```yaml
batch_size: 32            # 每個 GPU 的批次大小
```

**調整建議:**
- RTX 5090 (32GB): 可用 32-128
- 監控 GPU 記憶體使用
- 配合 gradient accumulation 調整

#### Gradient Accumulation
```yaml
gradient_accumulation:
  enabled: true
  steps: 4                # 有效批次 = batch_size * steps
```

**說明:**
- 用小批次模擬大批次訓練
- 當前設定: 32 * 4 = 128 有效批次
- 可減少 steps 或停用（如果 batch_size 夠大）

#### Mixed Precision
```yaml
mixed_precision:
  enabled: true           # 自動混合精度訓練
  opt_level: O1           # FP16 + FP32 混合
```

**優點:**
- 2-3x 訓練加速
- 減少記憶體使用 ~40%
- RTX 5090 tensor cores 優化

#### Learning Rate
```yaml
learning_rate: 0.0005     # 初始學習率
```

**調整原則:**
- 批次大小增加 → 學習率線性增加
- 例如: batch 32→64, LR 0.0005→0.001
- 建議使用 warmup

#### Data Loading
```yaml
num_workers: 4            # 資料載入並行數
```

**建議值:**
- CPU 核心數的 1/2 到 1/4
- 監控 CPU 使用率
- 過多會增加記憶體使用

## 🎯 實驗配置範例

### 1. 快速實驗（小批次）
```yaml
batch_size: 16
gradient_accumulation:
  enabled: false
mixed_precision:
  enabled: true
```

### 2. 最大吞吐量（大批次）
```yaml
batch_size: 128
gradient_accumulation:
  enabled: false
mixed_precision:
  enabled: true
num_workers: 8
```

### 3. 記憶體優化（長音訊）
```yaml
batch_size: 8
max_audio_length: 32000  # 2 seconds
gradient_accumulation:
  enabled: true
  steps: 16              # 有效批次 = 128
use_gradient_checkpointing: true
```

### 4. 大模型訓練
```yaml
model:
  architecture:
    emb_dim: 256          # 增加模型容量
    lstm_hidden_units: 256
    n_layers: 6
    n_heads: 8

training:
  batch_size: 16          # 減小批次
  gradient_accumulation:
    steps: 8              # 增加累積
```

## 📊 性能調優指南

### GPU 記憶體監控
```bash
# 訓練時監控
watch -n 1 nvidia-smi

# 查看記憶體使用
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

### 批次大小尋找
1. 從小批次開始（如 16）
2. 倍增直到 OOM
3. 回退到最大可用批次的 80%

### 效能基準測試
```bash
# 測試不同批次大小的吞吐量
for bs in 16 32 64 128; do
    echo "Testing batch_size=$bs"
    # 修改 config 並測試
done
```

## 🔄 從原始配置遷移

如果從 macOS MPS 配置遷移：

```diff
hardware:
-  use_cuda: false
+  use_cuda: true
-  device_ids: [mps]
+  device_ids: [0]

training:
-  batch_size: 16
+  batch_size: 32
-  mixed_precision:
-    enabled: false
+  mixed_precision:
+    enabled: true

misc:
-  num_workers: 0
+  num_workers: 4
```

## 📝 建立新配置

1. 複製 `training_rtx5090.yaml`
2. 修改實驗名稱與描述
3. 調整目標參數
4. 記錄變更到實驗日誌

```bash
cp training_rtx5090.yaml training_my_experiment.yaml
vim training_my_experiment.yaml
```

## 🔍 配置驗證

訓練前驗證配置：

```bash
# 在容器中執行
python -c "import yaml; yaml.safe_load(open('configs/training_rtx5090.yaml'))"

# 或使用訓練腳本的 test-only 模式
./scripts/run_training.sh my-exp configs/training_rtx5090.yaml --skip-memory-test
```

## 📚 參考資源

- PyTorch Mixed Precision: https://pytorch.org/docs/stable/amp.html
- Gradient Accumulation: https://kozodoi.me/blog/20210219/gradient-accumulation
- Batch Size Tuning: https://wandb.ai/wandb_fc/tips/reports/How-to-Pick-the-Best-Batch-Size--VmlldzoyMTEzMTU

---

**需要幫助？** 查看 `../docs/TROUBLESHOOTING.md`
