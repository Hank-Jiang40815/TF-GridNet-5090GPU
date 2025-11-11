#!/usr/bin/env python3
"""
精選音訊樣本腳本
從評估結果中選擇最佳和最差的樣本，用於 Git 提交
"""

import csv
import shutil
from pathlib import Path
import argparse

def select_samples(result_dir, output_dir='audio_samples', best_n=5, worst_n=5):
    """
    從評估結果中精選樣本
    
    Args:
        result_dir: 推理結果目錄
        output_dir: 輸出目錄名稱
        best_n: 選擇最佳樣本數量
        worst_n: 選擇最差樣本數量
    """
    result_dir = Path(result_dir)
    csv_path = result_dir / 'evaluation_results.csv'
    
    if not csv_path.exists():
        print(f"❌ 找不到 CSV 檔案: {csv_path}")
        return
    
    # 讀取評估結果
    results = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                'uttid': row['uttid'],
                'improvement': float(row['improvement'])
            })
    
    # 排序
    sorted_results = sorted(results, key=lambda x: x['improvement'])
    
    # 選擇最佳和最差
    worst_samples = sorted_results[:worst_n]
    best_samples = sorted_results[-best_n:]
    best_samples.reverse()  # 從高到低排列
    
    # 創建輸出目錄
    output_base = result_dir / output_dir
    best_dir = output_base / 'best_5'
    worst_dir = output_base / 'worst_5'
    
    for d in [best_dir, worst_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 創建精選樣本目錄: {output_base}")
    print(f"   最佳樣本: {best_dir}")
    print(f"   最差樣本: {worst_dir}")
    print()
    
    # 複製最佳樣本
    print("🏆 複製最佳樣本:")
    for i, sample in enumerate(best_samples, 1):
        uttid = sample['uttid']
        imp = sample['improvement']
        print(f"  {i}. {uttid}: {imp:+.2f} dB")
        
        for audio_type in ['enhanced', 'noisy', 'clean']:
            src = result_dir / audio_type / f'{uttid}.wav'
            dst = best_dir / f'{uttid}_{audio_type}.wav'
            if src.exists():
                shutil.copy2(src, dst)
    
    # 複製最差樣本
    print("\n⚠️ 複製最差樣本:")
    for i, sample in enumerate(worst_samples, 1):
        uttid = sample['uttid']
        imp = sample['improvement']
        print(f"  {i}. {uttid}: {imp:+.2f} dB")
        
        for audio_type in ['enhanced', 'noisy', 'clean']:
            src = result_dir / audio_type / f'{uttid}.wav'
            dst = worst_dir / f'{uttid}_{audio_type}.wav'
            if src.exists():
                shutil.copy2(src, dst)
    
    # 創建 README
    readme_path = output_base / 'README.md'
    with open(readme_path, 'w') as f:
        f.write("# 精選音訊樣本\n\n")
        f.write("此目錄包含從評估結果中精選的代表性音訊樣本，用於快速驗證和 Git 提交。\n\n")
        f.write("## 🏆 最佳改善樣本 (Top 5)\n\n")
        for i, sample in enumerate(best_samples, 1):
            uttid = sample['uttid']
            imp = sample['improvement']
            f.write(f"{i}. **{uttid}**: {imp:+.2f} dB\n")
            f.write(f"   - `{uttid}_noisy.wav` - 原始噪音音訊\n")
            f.write(f"   - `{uttid}_enhanced.wav` - 增強後音訊\n")
            f.write(f"   - `{uttid}_clean.wav` - 乾淨參考音訊\n\n")
        
        f.write("\n## ⚠️ 最差改善樣本 (Bottom 5)\n\n")
        for i, sample in enumerate(worst_samples, 1):
            uttid = sample['uttid']
            imp = sample['improvement']
            f.write(f"{i}. **{uttid}**: {imp:+.2f} dB\n")
            f.write(f"   - `{uttid}_noisy.wav` - 原始噪音音訊\n")
            f.write(f"   - `{uttid}_enhanced.wav` - 增強後音訊\n")
            f.write(f"   - `{uttid}_clean.wav` - 乾淨參考音訊\n\n")
        
        f.write("\n## 📊 統計\n\n")
        f.write(f"- 總樣本數: {len(results)}\n")
        f.write(f"- 精選樣本: {best_n + worst_n} 個\n")
        f.write(f"- 音訊檔案數: {(best_n + worst_n) * 3} 個 WAV\n")
        f.write(f"- 來源實驗: {result_dir.name}\n")
    
    # 統計資訊
    total_files = (best_n + worst_n) * 3
    print(f"\n✅ 完成！")
    print(f"   精選樣本數: {best_n + worst_n}")
    print(f"   總檔案數: {total_files} 個 WAV")
    print(f"   輸出位置: {output_base}")
    
    # 計算大小
    total_size = sum(f.stat().st_size for f in output_base.rglob('*.wav'))
    print(f"   總大小: {total_size / 1024:.1f} KB")
    
    return output_base

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='精選音訊樣本用於 Git 提交')
    parser.add_argument('--result-dir', type=str, required=True,
                       help='推理結果目錄路徑')
    parser.add_argument('--output-dir', type=str, default='audio_samples',
                       help='輸出目錄名稱 (default: audio_samples)')
    parser.add_argument('--best', type=int, default=5,
                       help='選擇最佳樣本數量 (default: 5)')
    parser.add_argument('--worst', type=int, default=5,
                       help='選擇最差樣本數量 (default: 5)')
    
    args = parser.parse_args()
    
    select_samples(
        result_dir=args.result_dir,
        output_dir=args.output_dir,
        best_n=args.best,
        worst_n=args.worst
    )
