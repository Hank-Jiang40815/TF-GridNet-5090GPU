#!/usr/bin/env python3
"""
評估最佳訓練模型 - Epoch 100
實驗: rtx5090-soundfile-5000ep
日期: 2025-11-11
版本: v2 - 增加音訊保存功能
"""

import sys
import os
import torch
import numpy as np
from pathlib import Path
import soundfile as sf
import librosa
import csv
from datetime import datetime

# 添加代碼路徑
sys.path.insert(0, '/workspace/TFG-Transfer-Package/code')

from memory_optimized_tfgridnet import TFGridNetV2, AudioDataset

def calculate_si_snr(estimate, reference, eps=1e-8):
    """計算 SI-SNR (Scale-Invariant Signal-to-Noise Ratio)"""
    # 確保是一維張量
    if estimate.dim() > 1:
        estimate = estimate.squeeze()
    if reference.dim() > 1:
        reference = reference.squeeze()
    
    # 移除均值
    estimate = estimate - estimate.mean()
    reference = reference - reference.mean()
    
    # 計算投影
    reference_energy = torch.sum(reference ** 2) + eps
    projection = torch.sum(estimate * reference) * reference / reference_energy
    
    # 計算噪音
    noise = estimate - projection
    
    # 計算 SI-SNR
    si_snr = 10 * torch.log10(
        torch.sum(projection ** 2) / (torch.sum(noise ** 2) + eps) + eps
    )
    
    return si_snr.item()

def evaluate_model(checkpoint_path, config_path='/workspace/configs/training_rtx5090.yaml', 
                   save_audio=True, output_dir='/workspace/experiments/inference_results'):
    """評估模型性能並保存增強音訊"""
    import yaml
    
    print("=" * 80)
    print("🎯 TF-GridNetV2 模型評估")
    print("=" * 80)
    print(f"檢查點: {checkpoint_path}")
    print(f"配置文件: {config_path}")
    if save_audio:
        print(f"輸出目錄: {output_dir}")
    print()
    
    # 載入配置
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # 設置設備
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print(f"使用設備: {device}")
    
    # 創建模型
    model_config = config['model']['architecture']
    stft_config = config['model']['stft']
    
    model = TFGridNetV2(
        n_srcs=model_config['n_srcs'],
        n_fft=stft_config['n_fft'],
        hop_length=stft_config['hop_length'],
        win_length=stft_config['win_length'],
        n_layers=model_config['n_layers'],
        lstm_hidden_units=model_config['lstm_hidden_units'],
        attn_n_head=model_config['n_heads'],
        emb_dim=model_config['emb_dim'],
        emb_ks=model_config['emb_ks'],
        emb_hs=model_config['emb_hs'],
        activation=model_config['activation'],
        eps=model_config['eps'],
        use_attn=model_config.get('use_multi_head_attention', True),
        use_gradient_checkpointing=False,  # 評估時不需要
        use_cross_attn=model_config.get('use_cross_attention', False),
        use_se=model_config.get('use_squeeze_excitation', False),
    ).to(device)
    
    # 載入檢查點
    print(f"\n📦 載入檢查點...")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # 處理 state_dict 中的 base_model 前綴
    state_dict = checkpoint['model_state_dict']
    new_state_dict = {}
    for key, value in state_dict.items():
        if key.startswith('base_model.'):
            new_key = key.replace('base_model.', '')
            new_state_dict[new_key] = value
        else:
            new_state_dict[key] = value
    
    # 使用 strict=False 因為模型可能有未使用的組件（如 cross_attention）
    missing_keys, unexpected_keys = model.load_state_dict(new_state_dict, strict=False)
    if missing_keys:
        print(f"   ⚠️ 未載入的鍵值 ({len(missing_keys)}): 這些是未使用的組件")
    if unexpected_keys:
        print(f"   ⚠️ 意外的鍵值 ({len(unexpected_keys)})")
    
    model.eval()
    print(f"✅ 模型已載入 (Epoch {checkpoint['epoch']})")
    if 'train_loss' in checkpoint and checkpoint['train_loss'] != 'N/A':
        print(f"   訓練損失: {checkpoint['train_loss']:.4f}")
    if 'valid_loss' in checkpoint and checkpoint['valid_loss'] != 'N/A':
        print(f"   驗證損失: {checkpoint['valid_loss']:.4f}")
    if 'loss' in checkpoint:
        print(f"   損失: {checkpoint['loss']:.4f}")
    
    # 創建驗證集
    print(f"\n📊 載入驗證集...")
    valid_dataset = AudioDataset(
        clean_scp_path='/workspace/TFG-Transfer-Package/data/scp/valid_clean_relative.scp',
        noisy_scp_path='/workspace/TFG-Transfer-Package/data/scp/valid_noisy_relative.scp',
        config=config
    )
    print(f"   驗證樣本數: {len(valid_dataset)}")
    
    # 創建輸出目錄
    if save_audio:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        epoch_num = checkpoint['epoch']
        result_dir = Path(output_dir) / f'epoch_{epoch_num}_best_{timestamp}'
        enhanced_dir = result_dir / 'enhanced'
        noisy_dir = result_dir / 'noisy'
        clean_dir = result_dir / 'clean'
        
        for d in [enhanced_dir, noisy_dir, clean_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        print(f"\n💾 音訊輸出目錄:")
        print(f"   {result_dir}")
        print()
    
    # 評估
    print(f"\n🔬 開始評估...")
    si_snr_improvements = []
    si_snr_noisy_list = []
    si_snr_enhanced_list = []
    audio_results = []  # 保存每個檔案的詳細結果
    
    with torch.no_grad():
        for i in range(len(valid_dataset)):
            try:
                noisy_audio, clean_audio, uttid = valid_dataset[i]
                
                # 移動到設備
                noisy_audio = noisy_audio.unsqueeze(0).to(device)
                clean_audio = clean_audio.to(device)
                
                # 模型推理
                enhanced_audio = model(noisy_audio)
                enhanced_audio = enhanced_audio.squeeze(0).squeeze(0)
                
                # 確保長度一致
                min_len = min(enhanced_audio.shape[0], clean_audio.shape[0])
                enhanced_audio = enhanced_audio[:min_len]
                clean_audio = clean_audio[:min_len]
                noisy_for_calc = noisy_audio.squeeze(0).squeeze(0)[:min_len]
                
                # 計算 SI-SNR
                si_snr_noisy = calculate_si_snr(noisy_for_calc, clean_audio)
                si_snr_enhanced = calculate_si_snr(enhanced_audio, clean_audio)
                improvement = si_snr_enhanced - si_snr_noisy
                
                si_snr_noisy_list.append(si_snr_noisy)
                si_snr_enhanced_list.append(si_snr_enhanced)
                si_snr_improvements.append(improvement)
                
                # 保存音訊檔案
                if save_audio:
                    # 保存增強後的音訊
                    enhanced_path = enhanced_dir / f"{uttid}.wav"
                    sf.write(enhanced_path, enhanced_audio.cpu().numpy(), config['data']['preprocessing']['target_sample_rate'])
                    
                    # 保存噪音音訊（參考）
                    noisy_path = noisy_dir / f"{uttid}.wav"
                    sf.write(noisy_path, noisy_for_calc.cpu().numpy(), config['data']['preprocessing']['target_sample_rate'])
                    
                    # 保存乾淨音訊（ground truth）
                    clean_path = clean_dir / f"{uttid}.wav"
                    sf.write(clean_path, clean_audio.cpu().numpy(), config['data']['preprocessing']['target_sample_rate'])
                
                # 記錄結果
                audio_results.append({
                    'uttid': uttid,
                    'si_snr_noisy': si_snr_noisy,
                    'si_snr_enhanced': si_snr_enhanced,
                    'improvement': improvement
                })
                
                if (i + 1) % 50 == 0:
                    print(f"   處理進度: {i+1}/{len(valid_dataset)} "
                          f"(平均改善: {np.mean(si_snr_improvements):.2f} dB)")
                
            except Exception as e:
                print(f"   ⚠️  樣本 {i} ({uttid if 'uttid' in locals() else 'unknown'}) 評估失敗: {e}")
                continue
    
    # 計算統計
    print("\n" + "=" * 80)
    print("📊 評估結果")
    print("=" * 80)
    print(f"成功評估樣本數: {len(si_snr_improvements)}/{len(valid_dataset)}")
    print()
    print("SI-SNR 統計:")
    print(f"  噪音音訊平均 SI-SNR:    {np.mean(si_snr_noisy_list):>8.2f} dB")
    print(f"  增強音訊平均 SI-SNR:    {np.mean(si_snr_enhanced_list):>8.2f} dB")
    print(f"  平均改善:               {np.mean(si_snr_improvements):>8.2f} dB")
    print(f"  標準差:                 {np.std(si_snr_improvements):>8.2f} dB")
    print(f"  最佳改善:               {np.max(si_snr_improvements):>8.2f} dB")
    print(f"  最差改善:               {np.min(si_snr_improvements):>8.2f} dB")
    print("=" * 80)
    
    # 保存結果到 CSV
    if save_audio and len(audio_results) > 0:
        csv_path = result_dir / 'evaluation_results.csv'
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['uttid', 'si_snr_noisy', 'si_snr_enhanced', 'improvement'])
            writer.writeheader()
            writer.writerows(audio_results)
        
        print(f"\n💾 結果已保存:")
        print(f"   CSV 報告: {csv_path}")
        print(f"   增強音訊: {enhanced_dir} ({len(list(enhanced_dir.glob('*.wav')))} 個檔案)")
        
        # 標註關鍵樣本
        if len(audio_results) > 0:
            sorted_results = sorted(audio_results, key=lambda x: x['improvement'])
            best_samples = sorted_results[-5:]  # 最佳5個
            worst_samples = sorted_results[:5]  # 最差5個
            
            highlights_path = result_dir / 'highlights.txt'
            with open(highlights_path, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("關鍵樣本標註\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("🏆 最佳改善 Top 5:\n")
                for r in reversed(best_samples):
                    f.write(f"  {r['uttid']}: {r['improvement']:+.2f} dB "
                           f"({r['si_snr_noisy']:.2f} → {r['si_snr_enhanced']:.2f})\n")
                
                f.write("\n⚠️ 最差改善 Top 5:\n")
                for r in worst_samples:
                    f.write(f"  {r['uttid']}: {r['improvement']:+.2f} dB "
                           f"({r['si_snr_noisy']:.2f} → {r['si_snr_enhanced']:.2f})\n")
            
            print(f"   關鍵樣本: {highlights_path}")
    
    # 保存結果字典
    results = {
        'checkpoint': checkpoint_path,
        'epoch': checkpoint['epoch'],
        'num_samples': len(si_snr_improvements),
        'si_snr_noisy_mean': float(np.mean(si_snr_noisy_list)),
        'si_snr_enhanced_mean': float(np.mean(si_snr_enhanced_list)),
        'si_snr_improvement_mean': float(np.mean(si_snr_improvements)),
        'si_snr_improvement_std': float(np.std(si_snr_improvements)),
        'si_snr_improvement_max': float(np.max(si_snr_improvements)),
        'si_snr_improvement_min': float(np.min(si_snr_improvements)),
    }
    
    if save_audio:
        results['output_dir'] = str(result_dir)
    
    return results, si_snr_improvements

if __name__ == '__main__':
    checkpoint_path = '/workspace/experiments/tfgridnetv2_rtx5090_baseline/checkpoint_epoch_100_best.pth'
    
    if not os.path.exists(checkpoint_path):
        print(f"❌ 找不到檢查點: {checkpoint_path}")
        sys.exit(1)
    
    results, improvements = evaluate_model(checkpoint_path)
    
    print("\n✅ 評估完成！")
