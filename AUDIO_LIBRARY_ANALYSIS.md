# torchaudio vs soundfile 分析報告

## 問題診斷

### 為什麼 torchaudio 不行？

**根本原因：** torchaudio 2.9.0 版本的 `load()` 函數內部默認調用了 `load_with_torchcodec()`，但這需要額外安裝 `torchcodec` 套件。

**錯誤訊息：**
```
ImportError: TorchCodec is required for load_with_torchcodec. 
Please install torchcodec to use this function.
```

**為什麼會這樣？**
1. **PyTorch 2.9.0 是新版本**，引入了新的音訊後端架構
2. **torchaudio 2.9.0 重構了載入機制**，優先使用 TorchCodec（一個新的編解碼器）
3. **TorchCodec 是可選依賴**，但新版 torchaudio.load() 會嘗試使用它

**測試結果：**
- ✗ `torchaudio.load()` → 失敗（需要 TorchCodec）
- ✓ `soundfile.read()` → 成功
- 音訊格式：22050 Hz, 單聲道 WAV

---

## 當前訓練程式碼使用情況

### 實際使用的函式庫

**好消息：** 訓練程式碼 **已經在使用 soundfile**！

```python
# train_tfgridnetv2.py, line 27
import soundfile as sf

# train_tfgridnetv2.py, line 87-88
clean_audio, sr_clean = sf.read(clean_file_path)
noisy_audio, sr_noisy = sf.read(noisy_file_path)
```

### BUT... 程式碼也使用了 torchaudio！

**問題點：**
```python
# train_tfgridnetv2.py, line 24
import torchaudio

# train_tfgridnetv2.py, line 51
self.resampler = torchaudio.transforms.Resample(orig_freq=22050, new_freq=self.target_sample_rate)

# train_tfgridnetv2.py, line 94-97
if sr_clean != self.target_sample_rate:
    clean_audio = self.resampler(torch.from_numpy(clean_audio).float()).numpy()
if sr_noisy != self.target_sample_rate:
    noisy_audio = self.resampler(torch.from_numpy(noisy_audio).float()).numpy()
```

**所以問題出在：**
- 載入音訊用 `soundfile` ✓（不會出錯）
- 重取樣用 `torchaudio.transforms.Resample` ✓（這個功能可以用）
- 但 `import torchaudio` 時可能觸發初始化檢查導致錯誤 ✗

---

## 解決方案比較

### 方案 1：安裝 torchcodec（推薦但可能困難）

**優點：**
- 完整支援 torchaudio 2.9.0 的所有功能
- 未來相容性最好
- 可能有更好的效能

**缺點：**
- torchcodec 是新套件，可能不穩定
- 安裝可能需要編譯或特定版本
- 增加依賴複雜度

**執行：**
```bash
pip install torchcodec
```

---

### 方案 2：降級 torchaudio 到穩定版本

**優點：**
- 使用經過測試的穩定版本
- 不需要額外依賴
- torchaudio.transforms.Resample 功能完整

**缺點：**
- 可能不支援 RTX 5090（需要測試）
- 版本相容性需要驗證

**執行：**
```dockerfile
RUN pip install --no-cache-dir torchaudio==2.5.1
```

---

### 方案 3：用 librosa 取代 torchaudio 重取樣（最簡單）

**優點：**
- **不需要 torchaudio**，移除依賴
- librosa 是成熟穩定的音訊處理庫
- 已經在 Dockerfile 中安裝了
- 重取樣功能完整且經過廣泛測試

**缺點：**
- 需要修改程式碼
- librosa 重取樣可能比 torchaudio 稍慢（但差異不大）
- 需要轉換 numpy array

**影響分析：**
1. **功能完整性**：librosa.resample() 提供高品質重取樣 ✓
2. **效能**：對於訓練來說，重取樣只做一次，影響微乎其微 ✓
3. **準確性**：librosa 使用 scipy 的 resampy，品質與 torchaudio 相當 ✓

**程式碼修改：**
```python
# 移除
import torchaudio

# 改為
import librosa

# 移除
self.resampler = torchaudio.transforms.Resample(orig_freq=22050, new_freq=self.target_sample_rate)

# 重取樣改為
if sr_clean != self.target_sample_rate:
    clean_audio = librosa.resample(clean_audio, orig_sr=sr_clean, target_sr=self.target_sample_rate)
if sr_noisy != self.target_sample_rate:
    noisy_audio = librosa.resample(noisy_audio, orig_sr=sr_noisy, target_sr=self.target_sample_rate)
```

---

## 使用 soundfile 的影響分析

### ✓ 正面影響

1. **已經在使用中** - 程式碼本來就用 soundfile 載入
2. **穩定可靠** - soundfile 是 Python 音訊處理的標準庫
3. **格式支援廣** - 支援 WAV, FLAC, OGG 等
4. **無額外依賴** - 只需要 libsndfile（已安裝）
5. **效能優秀** - C library 後端，速度快

### ⚠️ 潛在考慮

1. **重取樣功能** - soundfile 本身不提供重取樣
   - **解決**：用 librosa.resample() 或 scipy.signal.resample()
   
2. **張量轉換** - soundfile 返回 numpy array，需要轉 torch tensor
   - **影響**：微小，只是一行 `torch.from_numpy()`
   
3. **批次處理** - 如果需要在 GPU 上批次載入和預處理
   - **影響**：無，因為音訊載入本來就在 CPU 上做

---

## 建議

### 🎯 推薦方案：方案 3（用 librosa 取代 torchaudio）

**理由：**
1. ✅ **最簡單** - 只需修改幾行程式碼
2. ✅ **最穩定** - 移除問題源頭（torchaudio 2.9.0）
3. ✅ **功能完整** - librosa 已經安裝且功能齊全
4. ✅ **不影響訓練** - 重取樣品質相同，效能影響可忽略
5. ✅ **減少依賴** - 簡化環境，降低未來出錯機率

### 實施步驟：

1. **修改訓練程式碼** - 用 librosa 取代 torchaudio 重取樣
2. **移除 Dockerfile 中的 torchaudio 安裝** - 已經做了
3. **測試訓練** - 確認音訊載入和重取樣正常
4. **開始正式訓練** - RTX 5090 準備就緒！

---

## 效能比較

| 操作 | torchaudio | librosa | soundfile |
|-----|-----------|---------|-----------|
| 載入 WAV | ✗ (需要 torchcodec) | ✓ (較慢) | ✓✓ (最快) |
| 重取樣 | ✓✓ (GPU 加速) | ✓ (CPU, 高品質) | ✗ (不支援) |
| 格式支援 | ✓✓ (廣泛) | ✓✓ (廣泛) | ✓✓✓ (最廣) |
| GPU 整合 | ✓✓✓ (原生) | ✗ (僅 CPU) | ✗ (僅 CPU) |
| 穩定性 | ⚠️ (2.9.0 有問題) | ✓✓✓ (非常穩定) | ✓✓✓ (非常穩定) |

**結論：** 對於訓練任務，使用 `soundfile` + `librosa` 的組合是最佳選擇。

---

## 附註：實際測試結果

```bash
測試載入檔案: data/wavs/train/clean/00001.wav
------------------------------------------------------------
✗ torchaudio.load() 失敗: ImportError: TorchCodec is required
✓ soundfile.read() 成功
  Shape: (58652,), Sample rate: 22050
```

**音訊檔案資訊：**
- 格式：WAV
- 採樣率：22050 Hz
- 長度：58652 samples ≈ 2.66 秒
- 聲道：單聲道

**配置需求：**
- 目標採樣率：8000 Hz（根據 training_rtx5090.yaml）
- 需要重取樣：是（22050 Hz → 8000 Hz）
- 重取樣比率：0.363
