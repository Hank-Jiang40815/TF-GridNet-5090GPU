# 故障排除指南

本文檔列出常見問題與解決方案。

## 🔍 診斷工具

### 基本檢查

```bash
# 1. 檢查 GPU
nvidia-smi

# 2. 檢查 Docker
docker ps
docker images

# 3. 檢查容器內 GPU
docker-compose run --rm tfgridnet-train nvidia-smi

# 4. 檢查 Python 環境
docker-compose run --rm tfgridnet-train python -c "import torch; print(torch.cuda.is_available())"
```

## 🐛 常見問題

### 1. GPU 相關問題

#### 問題: nvidia-smi 找不到 GPU

**症狀**: 
```
NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver
```

**解決方案**:
```bash
# 檢查 driver 是否安裝
lsmod | grep nvidia

# 重新安裝 driver
sudo apt install nvidia-driver-580
sudo reboot

# 驗證
nvidia-smi
```

#### 問題: Docker 容器中無法使用 GPU

**症狀**:
```python
torch.cuda.is_available()  # 返回 False
```

**解決方案**:
```bash
# 1. 檢查 nvidia-container-toolkit
dpkg -l | grep nvidia-container-toolkit

# 2. 重新安裝
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# 3. 測試
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

#### 問題: CUDA Out of Memory (OOM)

**症狀**:
```
RuntimeError: CUDA out of memory
```

**解決方案**:

1. **減小批次大小**:
```yaml
training:
  batch_size: 16  # 從 32 減到 16
```

2. **啟用 gradient checkpointing**:
```yaml
model:
  architecture:
    use_gradient_checkpointing: true
```

3. **使用 gradient accumulation**:
```yaml
training:
  batch_size: 8
  gradient_accumulation:
    enabled: true
    steps: 8  # 有效批次 = 64
```

4. **清理 GPU 快取**:
```python
import torch
torch.cuda.empty_cache()
```

### 2. Docker 相關問題

#### 問題: 權限不足

**症狀**:
```
permission denied while trying to connect to the Docker daemon socket
```

**解決方案**:
```bash
sudo usermod -aG docker $USER
newgrp docker
# 或登出並重新登入
```

#### 問題: Docker build 失敗

**症狀**:
```
ERROR: failed to solve: ...
```

**解決方案**:
```bash
# 1. 清理 Docker 快取
docker system prune -a

# 2. 使用 --no-cache 重新建構
docker-compose build --no-cache

# 3. 檢查網路連線
ping google.com

# 4. 如果是網路問題，使用代理
# 編輯 Dockerfile，添加：
# ENV HTTP_PROXY=http://proxy:port
# ENV HTTPS_PROXY=http://proxy:port
```

#### 問題: Volume mount 失敗

**症狀**:
```
Error response from daemon: invalid mount config
```

**解決方案**:
```bash
# 1. 檢查路徑是否存在
ls -l /home/sbplab/Hank/ESPnet/TFG-Transfer-Package

# 2. 檢查權限
ls -ld /home/sbplab/Hank/ESPnet/TFG-Transfer-Package

# 3. 修改 docker-compose.yml 中的路徑
vim docker-compose.yml
```

### 3. 訓練相關問題

#### 問題: Loss 是 NaN

**症狀**:
```
Training loss: nan
```

**解決方案**:

1. **降低學習率**:
```yaml
training:
  learning_rate: 0.0001  # 從 0.001 降低
```

2. **啟用 gradient clipping**:
```yaml
training:
  gradient_clipping:
    enabled: true
    max_norm: 1.0  # 從 0.5 增加
```

3. **檢查資料正規化**:
```yaml
data:
  preprocessing:
    normalize_audio: true
```

4. **使用較小的模型**:
```yaml
model:
  architecture:
    emb_dim: 64  # 從 128 減小
```

#### 問題: Loss 不下降

**可能原因與解決方案**:

1. **學習率太小**:
```yaml
training:
  learning_rate: 0.001  # 嘗試增加
```

2. **學習率太大**:
```yaml
training:
  learning_rate: 0.0001  # 嘗試減小
```

3. **資料問題**:
```bash
# 檢查資料完整性
python code/data_integrity_check_stage1.py
```

4. **模型容量不足**:
```yaml
model:
  architecture:
    n_layers: 6  # 增加層數
    emb_dim: 192  # 增加維度
```

#### 問題: 訓練速度慢

**診斷**:
```bash
# 監控 GPU 利用率
nvidia-smi dmon -s u

# 如果 GPU 利用率低（<50%），可能是：
```

**解決方案**:

1. **增加 num_workers**:
```yaml
misc:
  num_workers: 8  # 增加資料載入並行
```

2. **啟用混合精度**:
```yaml
training:
  mixed_precision:
    enabled: true
```

3. **增加批次大小**:
```yaml
training:
  batch_size: 64  # 增加以充分利用 GPU
```

4. **使用更快的儲存**:
```bash
# 將資料移到 SSD
# 或使用記憶體快取
```

### 4. 資料相關問題

#### 問題: 找不到資料檔案

**症狀**:
```
FileNotFoundError: [Errno 2] No such file or directory: './data/scp/train_clean.scp'
```

**解決方案**:
```bash
# 1. 檢查資料路徑
ls -l /home/sbplab/Hank/ESPnet/TFG-Transfer-Package/data

# 2. 檢查 SCP 檔案
cat /home/sbplab/Hank/ESPnet/TFG-Transfer-Package/data/scp/train_clean.scp | head

# 3. 檢查相對路徑設定
# 確保在 TFG-Transfer-Package 目錄下執行

# 4. 如果使用絕對路徑，確保路徑正確
```

#### 問題: 音訊檔案損壞

**症狀**:
```
soundfile.LibsndfileError: Error opening ...
```

**解決方案**:
```bash
# 1. 檢查單個檔案
ffprobe /path/to/audio.wav

# 2. 批次檢查
find /path/to/wavs -name "*.wav" -exec ffprobe -v error {} \; 2>&1 | grep -i error

# 3. 移除損壞的檔案
# 或從備份恢復
```

### 5. 配置相關問題

#### 問題: YAML 語法錯誤

**症狀**:
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**解決方案**:
```bash
# 檢查 YAML 語法
python -c "import yaml; yaml.safe_load(open('configs/training_rtx5090.yaml'))"

# 常見錯誤：
# - 縮排不一致（使用空格，不要用 tab）
# - 冒號後缺少空格
# - 字串包含特殊字元未加引號
```

#### 問題: 配置參數未生效

**解決方案**:
```bash
# 1. 確認使用正確的配置檔
ls -l /workspace/configs/

# 2. 檢查配置是否被複製到實驗目錄
cat experiments/logs/<experiment>/config.yaml

# 3. 確認參數名稱正確（區分大小寫）
```

## 🔧 進階診斷

### 記憶體洩漏

**症狀**: 記憶體使用持續增加

**診斷**:
```python
import torch
import gc

# 在訓練循環中
gc.collect()
torch.cuda.empty_cache()

# 監控張量數量
print(len(list(gc.get_objects())))
```

### 性能剖析

```python
import torch.profiler as profiler

with profiler.profile(
    activities=[
        profiler.ProfilerActivity.CPU,
        profiler.ProfilerActivity.CUDA,
    ]
) as prof:
    # 訓練程式碼
    ...

print(prof.key_averages().table(sort_by="cuda_time_total"))
```

### 檢查點損壞

**症狀**: 無法載入檢查點

**解決方案**:
```python
import torch

# 嘗試載入
try:
    checkpoint = torch.load('checkpoint.pth')
    print("Checkpoint keys:", checkpoint.keys())
except Exception as e:
    print(f"Error: {e}")
    # 使用較早的檢查點
```

## 📚 獲取幫助

如果上述方案都無法解決問題：

1. **檢查日誌**:
```bash
# 查看完整訓練日誌
cat experiments/logs/<experiment>/training.log

# 查看 Docker 日誌
docker-compose logs
```

2. **建立最小可重現範例**:
```bash
# 使用最小配置與少量資料測試
```

3. **提交 Issue**:
   - 包含錯誤訊息
   - 系統資訊（`nvidia-smi`, `docker version`）
   - 配置檔案
   - 重現步驟

4. **參考資源**:
   - [PyTorch 論壇](https://discuss.pytorch.org/)
   - [NVIDIA Developer 論壇](https://forums.developer.nvidia.com/)
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/pytorch)

## 🛡️ 預防措施

1. **定期備份**: 重要檢查點與實驗記錄
2. **版本控制**: 配置檔與程式碼變更
3. **監控日誌**: 設定自動化監控
4. **漸進測試**: 大規模訓練前先小規模測試
5. **文檔記錄**: 詳細記錄實驗設定與結果

---

**還有問題？** 歡迎開 [Issue](https://github.com/Hank-Jiang40815/TF-GridNet-5090GPU/issues)！
