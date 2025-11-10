# 詳細安裝指南

本文檔提供完整的環境設定步驟。

## 📋 系統需求

### 硬體需求

- **GPU**: NVIDIA RTX 5090（32GB VRAM）或其他 CUDA 相容 GPU
  - 最低: RTX 3090 (24GB)
  - 推薦: RTX 4090 (24GB) 或 RTX 5090 (32GB)
- **CPU**: 8+ 核心（推薦 16+）
- **RAM**: 32GB+（推薦 64GB+）
- **儲存**: 100GB+ 可用空間
  - 建議使用 NVMe SSD 以加速資料載入

### 軟體需求

- **作業系統**: Linux (Ubuntu 20.04/22.04 推薦)
- **NVIDIA Driver**: 580.95+ （支援 CUDA 13.0）
- **Docker**: 24.0+
- **Docker Compose**: 2.20+
- **nvidia-container-toolkit**: latest

## 🔧 安裝步驟

### 1. 安裝 NVIDIA Driver

#### Ubuntu/Debian

```bash
# 檢查當前 driver 版本
nvidia-smi

# 如需安裝/更新（以 Ubuntu 22.04 為例）
sudo apt update
sudo apt install nvidia-driver-580

# 重新啟動
sudo reboot

# 驗證安裝
nvidia-smi
```

預期輸出應顯示：
- Driver Version: 580.95.05 或更新
- CUDA Version: 13.0

### 2. 安裝 Docker

```bash
# 移除舊版本
sudo apt-get remove docker docker-engine docker.io containerd runc

# 安裝依賴
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 設定 repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安裝 Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 驗證安裝
docker --version
docker compose version
```

### 3. 安裝 nvidia-container-toolkit

```bash
# 添加 NVIDIA Container Toolkit repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# 安裝
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 重啟 Docker daemon
sudo systemctl restart docker

# 驗證安裝
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

### 4. 配置 Docker（可選但推薦）

```bash
# 允許非 root 使用者執行 Docker
sudo usermod -aG docker $USER

# 登出並重新登入使變更生效
# 或執行
newgrp docker

# 驗證
docker run hello-world
```

### 5. Clone Repository

```bash
# 使用 SSH（需設定 SSH key）
git clone git@github.com:Hank-Jiang40815/TF-GridNet-5090GPU.git

# 或使用 HTTPS
git clone https://github.com/Hank-Jiang40815/TF-GridNet-5090GPU.git

cd TF-GridNet-5090GPU
```

### 6. 執行環境檢查

```bash
chmod +x scripts/*.sh
./scripts/setup_host.sh
```

這個腳本會檢查：
- NVIDIA GPU 與 driver
- Docker 安裝
- nvidia-docker runtime
- TFG-Transfer-Package 位置

### 7. 建構 Docker Image

```bash
# 使用 docker-compose（推薦）
docker-compose build

# 或使用 docker
docker build -t tfgridnet-rtx5090:latest .
```

建構時間約 5-10 分鐘，取決於網路速度。

### 8. 驗證安裝

```bash
# 方法 1: 執行 smoke test
./scripts/run_smoke_test.sh

# 方法 2: 手動驗證
docker-compose run --rm tfgridnet-train bash -c "
    python -c 'import torch; \
               print(\"PyTorch:\", torch.__version__); \
               print(\"CUDA available:\", torch.cuda.is_available()); \
               print(\"CUDA version:\", torch.version.cuda); \
               print(\"GPU:\", torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"); \
               print(\"GPU memory:\", torch.cuda.get_device_properties(0).total_memory // 1024**3, \"GB\")'
"
```

預期輸出：
```
PyTorch: 2.5.1+cu124
CUDA available: True
CUDA version: 12.4
GPU: NVIDIA GeForce RTX 5090
GPU memory: 32 GB
```

## 📦 資料準備

### 選項 1: 使用下載腳本

```bash
./scripts/download_data.sh
# 依照提示選擇下載來源
```

### 選項 2: 手動準備

1. 下載 TFG-Transfer-Package 資料
2. 解壓到 `/home/sbplab/Hank/ESPnet/TFG-Transfer-Package`
3. 驗證結構：

```bash
ls -l /home/sbplab/Hank/ESPnet/TFG-Transfer-Package/
# 應該看到：
# - code/
# - configs/
# - data/
#   - scp/
#   - wavs/
# - env/
# - runs/
```

### 選項 3: 自訂資料路徑

如果資料位於其他位置，修改 `docker-compose.yml`：

```yaml
volumes:
  - /your/custom/path:/workspace/TFG-Transfer-Package:ro
```

## 🎯 下一步

安裝完成後：

1. **測試環境**: 執行 smoke test 確認設定正確
2. **閱讀配置文檔**: 查看 `configs/README.md` 了解參數調整
3. **開始第一個實驗**: 參考 `docs/TRAINING.md`
4. **設定實驗記錄**: 閱讀 `experiments/README.md`

## 🔍 進階配置

### 多 GPU 訓練

修改 `configs/training_rtx5090.yaml`:

```yaml
hardware:
  use_ddp: true
  world_size: 2  # GPU 數量
  device_ids: [0, 1]
```

並修改 `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all  # 使用所有 GPU
          capabilities: [gpu]
```

### 自訂 Docker Image

如需修改 Python 套件或系統依賴：

```bash
# 編輯 Dockerfile
vim Dockerfile

# 重新建構
docker-compose build --no-cache
```

### 設定 SSH Key（用於 GitHub）

```bash
# 產生 SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 複製 public key
cat ~/.ssh/id_ed25519.pub

# 添加到 GitHub: Settings -> SSH and GPG keys -> New SSH key
```

## 🐛 安裝故障排除

### 問題 1: nvidia-smi 找不到

**解決方案**:
```bash
# 檢查 driver 是否安裝
dpkg -l | grep nvidia-driver

# 如未安裝，執行
sudo ubuntu-drivers autoinstall
sudo reboot
```

### 問題 2: Docker 權限不足

**解決方案**:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 問題 3: GPU 在 Docker 中無法使用

**解決方案**:
```bash
# 檢查 nvidia-container-toolkit
sudo systemctl restart docker
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

### 問題 4: 建構 Docker 失敗

**解決方案**:
```bash
# 清理並重試
docker system prune -a
docker-compose build --no-cache
```

## 📚 參考資源

- [NVIDIA Driver 安裝指南](https://docs.nvidia.com/datacenter/tesla/tesla-installation-notes/index.html)
- [Docker 官方文檔](https://docs.docker.com/engine/install/)
- [nvidia-container-toolkit 文檔](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

---

**需要協助？** 請查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 或開 Issue。
