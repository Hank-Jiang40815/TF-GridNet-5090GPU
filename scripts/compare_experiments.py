#!/usr/bin/env python3
"""
實驗比較腳本
比較兩個實驗的評估結果
"""

import csv
import json
from pathlib import Path
import argparse
import numpy as np

def load_experiment(exp_dir):
    """載入實驗資料"""
    exp_dir = Path(exp_dir)
    
    # 載入 CSV
    csv_path = exp_dir / 'evaluation_results.csv'
    results = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                'uttid': row['uttid'],
                'si_snr_noisy': float(row['si_snr_noisy']),
                'si_snr_enhanced': float(row['si_snr_enhanced']),
                'improvement': float(row['improvement'])
            })
    
    # 載入 metadata (如果存在)
    metadata_path = exp_dir / 'metadata.json'
    metadata = None
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    
    return {
        'dir': exp_dir,
        'name': exp_dir.name,
        'results': results,
        'metadata': metadata
    }

def compute_statistics(results):
    """計算統計資訊"""
    improvements = [r['improvement'] for r in results]
    return {
        'count': len(improvements),
        'mean': np.mean(improvements),
        'std': np.std(improvements),
        'min': np.min(improvements),
        'max': np.max(improvements),
        'median': np.median(improvements),
        'q25': np.percentile(improvements, 25),
        'q75': np.percentile(improvements, 75)
    }

def compare_experiments(exp1_dir, exp2_dir):
    """比較兩個實驗"""
    print("=" * 80)
    print("實驗比較報告")
    print("=" * 80)
    print()
    
    # 載入實驗
    exp1 = load_experiment(exp1_dir)
    exp2 = load_experiment(exp2_dir)
    
    print(f"📊 實驗 1: {exp1['name']}")
    print(f"📊 實驗 2: {exp2['name']}")
    print()
    
    # 計算統計
    stats1 = compute_statistics(exp1['results'])
    stats2 = compute_statistics(exp2['results'])
    
    # 顯示基本資訊
    print("=" * 80)
    print("基本資訊")
    print("=" * 80)
    print(f"{'指標':<20} {'實驗 1':>15} {'實驗 2':>15} {'差異':>15}")
    print("-" * 80)
    print(f"{'樣本數':<20} {stats1['count']:>15} {stats2['count']:>15} {stats2['count']-stats1['count']:>15}")
    print()
    
    # 顯示 SI-SNR 改善統計
    print("=" * 80)
    print("SI-SNR 改善統計 (dB)")
    print("=" * 80)
    print(f"{'指標':<20} {'實驗 1':>15} {'實驗 2':>15} {'差異':>15}")
    print("-" * 80)
    
    for key, label in [
        ('mean', '平均'),
        ('std', '標準差'),
        ('median', '中位數'),
        ('min', '最小'),
        ('max', '最大'),
        ('q25', '第25百分位'),
        ('q75', '第75百分位')
    ]:
        val1 = stats1[key]
        val2 = stats2[key]
        diff = val2 - val1
        sign = '↑' if diff > 0 else '↓' if diff < 0 else '='
        print(f"{label:<20} {val1:>15.2f} {val2:>15.2f} {diff:>14.2f}{sign}")
    
    print()
    
    # 效能分類
    print("=" * 80)
    print("效能分類")
    print("=" * 80)
    
    def classify_performance(results):
        excellent = sum(1 for r in results if r['improvement'] > 10)
        good = sum(1 for r in results if 5 < r['improvement'] <= 10)
        moderate = sum(1 for r in results if 0 < r['improvement'] <= 5)
        poor = sum(1 for r in results if r['improvement'] <= 0)
        return excellent, good, moderate, poor
    
    e1_exc, e1_good, e1_mod, e1_poor = classify_performance(exp1['results'])
    e2_exc, e2_good, e2_mod, e2_poor = classify_performance(exp2['results'])
    
    print(f"{'類別':<20} {'實驗 1':>15} {'實驗 2':>15} {'差異':>15}")
    print("-" * 80)
    print(f"{'優秀 (>10 dB)':<20} {e1_exc:>15} {e2_exc:>15} {e2_exc-e1_exc:>+15}")
    print(f"{'良好 (5-10 dB)':<20} {e1_good:>15} {e2_good:>15} {e2_good-e1_good:>+15}")
    print(f"{'中等 (0-5 dB)':<20} {e1_mod:>15} {e2_mod:>15} {e2_mod-e1_mod:>+15}")
    print(f"{'差 (≤0 dB)':<20} {e1_poor:>15} {e2_poor:>15} {e2_poor-e1_poor:>+15}")
    print()
    
    # 如果有 metadata，顯示模型資訊
    if exp1['metadata'] and exp2['metadata']:
        print("=" * 80)
        print("模型配置")
        print("=" * 80)
        
        m1 = exp1['metadata'].get('model', {})
        m2 = exp2['metadata'].get('model', {})
        
        print(f"{'參數':<20} {'實驗 1':>15} {'實驗 2':>15}")
        print("-" * 80)
        
        for key, label in [
            ('n_layers', '層數'),
            ('lstm_hidden_units', 'LSTM隱藏單元'),
            ('attn_n_head', '注意力頭數'),
            ('emb_dim', '嵌入維度')
        ]:
            v1 = m1.get(key, 'N/A')
            v2 = m2.get(key, 'N/A')
            print(f"{label:<20} {str(v1):>15} {str(v2):>15}")
        
        print()
        
        # 訓練資訊
        print("=" * 80)
        print("訓練配置")
        print("=" * 80)
        
        t1 = exp1['metadata'].get('training', {})
        t2 = exp2['metadata'].get('training', {})
        
        print(f"{'參數':<20} {'實驗 1':>25} {'實驗 2':>25}")
        print("-" * 80)
        
        for key, label in [
            ('total_epochs', '總訓練輪數'),
            ('best_epoch', '最佳輪數'),
            ('gpu', 'GPU'),
            ('pytorch_version', 'PyTorch版本')
        ]:
            v1 = t1.get(key, 'N/A')
            v2 = t2.get(key, 'N/A')
            print(f"{label:<20} {str(v1):>25} {str(v2):>25}")
        
        print()
    
    # 逐樣本比較
    print("=" * 80)
    print("逐樣本改善差異 (實驗2 - 實驗1)")
    print("=" * 80)
    
    # 確保兩個實驗有相同的樣本
    uttids1 = {r['uttid'] for r in exp1['results']}
    uttids2 = {r['uttid'] for r in exp2['results']}
    common_uttids = uttids1 & uttids2
    
    if len(common_uttids) == 0:
        print("⚠️ 兩個實驗沒有共同樣本")
    else:
        print(f"共同樣本數: {len(common_uttids)}")
        print()
        
        # 計算差異
        diffs = []
        for uttid in sorted(common_uttids):
            r1 = next(r for r in exp1['results'] if r['uttid'] == uttid)
            r2 = next(r for r in exp2['results'] if r['uttid'] == uttid)
            diff = r2['improvement'] - r1['improvement']
            diffs.append((uttid, r1['improvement'], r2['improvement'], diff))
        
        # 排序找出最大改善和退步
        diffs.sort(key=lambda x: x[3])
        
        print("📉 最大退步 (Top 5):")
        for i, (uttid, imp1, imp2, diff) in enumerate(diffs[:5], 1):
            print(f"  {i}. {uttid}: {imp1:+.2f} dB → {imp2:+.2f} dB ({diff:+.2f} dB)")
        
        print()
        print("📈 最大改善 (Top 5):")
        for i, (uttid, imp1, imp2, diff) in enumerate(diffs[-5:][::-1], 1):
            print(f"  {i}. {uttid}: {imp1:+.2f} dB → {imp2:+.2f} dB ({diff:+.2f} dB)")
        
        print()
        
        # 統計差異分布
        diff_values = [d[3] for d in diffs]
        better = sum(1 for d in diff_values if d > 0)
        worse = sum(1 for d in diff_values if d < 0)
        same = sum(1 for d in diff_values if d == 0)
        
        print(f"實驗 2 相對於實驗 1:")
        print(f"  更好: {better} 個樣本 ({better/len(diff_values)*100:.1f}%)")
        print(f"  更差: {worse} 個樣本 ({worse/len(diff_values)*100:.1f}%)")
        print(f"  相同: {same} 個樣本 ({same/len(diff_values)*100:.1f}%)")
        print(f"  平均差異: {np.mean(diff_values):+.2f} dB")
    
    print()
    print("=" * 80)
    
    # 結論
    print("\n✅ 比較完成！")
    
    # 判斷哪個實驗更好
    if stats2['mean'] > stats1['mean']:
        print(f"🏆 實驗 2 表現較佳 (平均改善 {stats2['mean'] - stats1['mean']:+.2f} dB)")
    elif stats1['mean'] > stats2['mean']:
        print(f"🏆 實驗 1 表現較佳 (平均改善 {stats1['mean'] - stats2['mean']:+.2f} dB)")
    else:
        print("⚖️ 兩個實驗表現相當")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='比較兩個實驗的評估結果')
    parser.add_argument('--exp1', type=str, required=True,
                       help='實驗1的結果目錄路徑')
    parser.add_argument('--exp2', type=str, required=True,
                       help='實驗2的結果目錄路徑')
    
    args = parser.parse_args()
    
    compare_experiments(args.exp1, args.exp2)
