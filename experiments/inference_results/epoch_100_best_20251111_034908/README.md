# TF-GridNetV2 Epoch 100 推理結果

**實驗**: rtx5090-soundfile-5000ep  
**檢查點**: Epoch 100 (最佳驗證損失: 32.34 dB)  
**推理日期**: 2025-11-11  
**樣本數**: 192  

## 📊 評估結果

| 指標 | 數值 |
|------|------|
| 平均改善 | +1.10 dB |
| 最佳改善 | +43.34 dB (00057) |
| 最差改善 | -37.95 dB (00130) |

## 📁 檔案說明

- evaluation_results.csv - 完整 SI-SNR 數據
- highlights.txt - 關鍵樣本
- visualizations/ - 視覺化圖表
- enhanced/, noisy/, clean/ - 音訊（不納入 Git）

詳見: ../../EXPERIMENT_ANALYSIS_20251111.md
