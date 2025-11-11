"""
視覺化代表性音訊樣本
為 10 個關鍵樣本生成波形圖和頻譜圖比較
"""

import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from pathlib import Path

# 樣本清單
BEST_SAMPLES = ['00057', '00056', '00086', '00128', '00180']
WORST_SAMPLES = ['00130', '00144', '00067', '00068', '00039']

def load_audio(file_path):
    """載入音訊檔案"""
    audio, sr = sf.read(file_path)
    return audio, sr

def plot_waveform_comparison(noisy, enhanced, clean, sr, uttid, improvement, output_path):
    """
    繪製三個音訊的波形比較
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 8))
    
    time_noisy = np.arange(len(noisy)) / sr
    time_enhanced = np.arange(len(enhanced)) / sr
    time_clean = np.arange(len(clean)) / sr
    
    # Noisy waveform
    axes[0].plot(time_noisy, noisy, linewidth=0.5, color='#d62728')
    axes[0].set_title(f'Noisy Audio (uttid: {uttid})', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_ylim(-1, 1)
    axes[0].grid(True, alpha=0.3)
    
    # Enhanced waveform
    axes[1].plot(time_enhanced, enhanced, linewidth=0.5, color='#2ca02c')
    axes[1].set_title(f'Enhanced Audio (Improvement: {improvement:.2f} dB)', 
                     fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Amplitude')
    axes[1].set_ylim(-1, 1)
    axes[1].grid(True, alpha=0.3)
    
    # Clean waveform
    axes[2].plot(time_clean, clean, linewidth=0.5, color='#1f77b4')
    axes[2].set_title('Clean Reference', fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Time (seconds)')
    axes[2].set_ylabel('Amplitude')
    axes[2].set_ylim(-1, 1)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ 已儲存波形圖: {output_path.name}")

def plot_spectrogram_comparison(noisy, enhanced, clean, sr, uttid, improvement, output_path):
    """
    繪製三個音訊的頻譜圖比較
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # 計算頻譜圖 (STFT)
    n_fft = 512
    hop_length = 256
    
    # Noisy spectrogram
    D_noisy = librosa.stft(noisy, n_fft=n_fft, hop_length=hop_length)
    D_noisy_db = librosa.amplitude_to_db(np.abs(D_noisy), ref=np.max)
    img1 = librosa.display.specshow(D_noisy_db, sr=sr, hop_length=hop_length, 
                                     x_axis='time', y_axis='hz', ax=axes[0], 
                                     cmap='viridis')
    axes[0].set_title(f'Noisy Spectrogram (uttid: {uttid})', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Frequency (Hz)')
    fig.colorbar(img1, ax=axes[0], format='%+2.0f dB')
    
    # Enhanced spectrogram
    D_enhanced = librosa.stft(enhanced, n_fft=n_fft, hop_length=hop_length)
    D_enhanced_db = librosa.amplitude_to_db(np.abs(D_enhanced), ref=np.max)
    img2 = librosa.display.specshow(D_enhanced_db, sr=sr, hop_length=hop_length, 
                                     x_axis='time', y_axis='hz', ax=axes[1], 
                                     cmap='viridis')
    axes[1].set_title(f'Enhanced Spectrogram (Improvement: {improvement:.2f} dB)', 
                     fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Frequency (Hz)')
    fig.colorbar(img2, ax=axes[1], format='%+2.0f dB')
    
    # Clean spectrogram
    D_clean = librosa.stft(clean, n_fft=n_fft, hop_length=hop_length)
    D_clean_db = librosa.amplitude_to_db(np.abs(D_clean), ref=np.max)
    img3 = librosa.display.specshow(D_clean_db, sr=sr, hop_length=hop_length, 
                                     x_axis='time', y_axis='hz', ax=axes[2], 
                                     cmap='viridis')
    axes[2].set_title('Clean Reference Spectrogram', fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Time (seconds)')
    axes[2].set_ylabel('Frequency (Hz)')
    fig.colorbar(img3, ax=axes[2], format='%+2.0f dB')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ 已儲存頻譜圖: {output_path.name}")

def process_sample(base_dir, uttid, improvement, output_dir):
    """
    處理單一樣本：生成波形圖和頻譜圖
    """
    print(f"\n🔍 處理樣本: {uttid} (改善: {improvement:.2f} dB)")
    
    # 載入音訊
    noisy_path = base_dir / 'noisy' / f'{uttid}.wav'
    enhanced_path = base_dir / 'enhanced' / f'{uttid}.wav'
    clean_path = base_dir / 'clean' / f'{uttid}.wav'
    
    noisy, sr = load_audio(noisy_path)
    enhanced, _ = load_audio(enhanced_path)
    clean, _ = load_audio(clean_path)
    
    # 生成波形圖
    waveform_output = output_dir / f'{uttid}_waveform.png'
    plot_waveform_comparison(noisy, enhanced, clean, sr, uttid, improvement, waveform_output)
    
    # 生成頻譜圖
    spectrogram_output = output_dir / f'{uttid}_spectrogram.png'
    plot_spectrogram_comparison(noisy, enhanced, clean, sr, uttid, improvement, spectrogram_output)

def main():
    # 設定路徑
    base_dir = Path('/workspace/experiments/inference_results/epoch_100_best_20251111_034908')
    output_dir = base_dir / 'visualizations'
    output_dir.mkdir(exist_ok=True)
    
    print(f"📊 開始生成視覺化圖表...")
    print(f"輸出目錄: {output_dir}")
    
    # 讀取 CSV 取得改善量
    import csv
    csv_path = base_dir / 'evaluation_results.csv'
    improvements = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            improvements[row['uttid']] = float(row['improvement'])
    
    # 處理最佳樣本
    print("\n" + "="*60)
    print("🏆 處理最佳改善樣本 (Top 5)")
    print("="*60)
    for uttid in BEST_SAMPLES:
        process_sample(base_dir, uttid, improvements[uttid], output_dir)
    
    # 處理最差樣本
    print("\n" + "="*60)
    print("⚠️ 處理最差改善樣本 (Bottom 5)")
    print("="*60)
    for uttid in WORST_SAMPLES:
        process_sample(base_dir, uttid, improvements[uttid], output_dir)
    
    print("\n" + "="*60)
    print("✅ 完成！共生成 20 張圖表 (10 波形圖 + 10 頻譜圖)")
    print(f"📁 儲存位置: {output_dir}")
    print("="*60)
    
    # 生成索引頁
    create_visualization_index(output_dir, BEST_SAMPLES, WORST_SAMPLES, improvements)

def create_visualization_index(output_dir, best_samples, worst_samples, improvements):
    """
    生成視覺化索引 Markdown 檔案
    """
    index_path = output_dir / 'VISUALIZATION_INDEX.md'
    
    with open(index_path, 'w') as f:
        f.write("# 視覺化圖表索引\n\n")
        f.write("**實驗**: rtx5090-soundfile-5000ep (Epoch 100)\n")
        f.write("**生成日期**: 2025-11-11\n\n")
        f.write("---\n\n")
        
        # 最佳樣本
        f.write("## 🏆 最佳改善樣本\n\n")
        for uttid in best_samples:
            imp = improvements[uttid]
            f.write(f"### {uttid} (改善: {imp:+.2f} dB)\n\n")
            f.write(f"**波形比較**:\n")
            f.write(f"![{uttid} Waveform](./{uttid}_waveform.png)\n\n")
            f.write(f"**頻譜圖比較**:\n")
            f.write(f"![{uttid} Spectrogram](./{uttid}_spectrogram.png)\n\n")
            f.write("---\n\n")
        
        # 最差樣本
        f.write("## ⚠️ 最差改善樣本\n\n")
        for uttid in worst_samples:
            imp = improvements[uttid]
            f.write(f"### {uttid} (改善: {imp:+.2f} dB)\n\n")
            f.write(f"**波形比較**:\n")
            f.write(f"![{uttid} Waveform](./{uttid}_waveform.png)\n\n")
            f.write(f"**頻譜圖比較**:\n")
            f.write(f"![{uttid} Spectrogram](./{uttid}_spectrogram.png)\n\n")
            f.write("---\n\n")
    
    print(f"✅ 已生成索引檔案: {index_path.name}")

if __name__ == '__main__':
    main()
