#!/usr/bin/env python3
"""檢查檢查點的內容"""
import torch
import sys

checkpoint_path = '/workspace/experiments/tfgridnetv2_rtx5090_baseline/checkpoint_epoch_100_best.pth'

print("=" * 80)
print("檢查點內容分析")
print("=" * 80)

checkpoint = torch.load(checkpoint_path, map_location='cpu')

print("\n📦 檢查點鍵值:")
for key in checkpoint.keys():
    print(f"  - {key}")

print("\n📊 基本信息:")
if 'epoch' in checkpoint:
    print(f"  Epoch: {checkpoint['epoch']}")
if 'train_loss' in checkpoint:
    print(f"  Train Loss: {checkpoint['train_loss']:.4f}")
if 'valid_loss' in checkpoint:
    print(f"  Valid Loss: {checkpoint['valid_loss']:.4f}")

print("\n🔑 模型參數鍵值 (前 20 個):")
state_dict = checkpoint['model_state_dict']
keys = list(state_dict.keys())[:20]
for key in keys:
    print(f"  - {key}")

print(f"\n總共 {len(state_dict)} 個參數")

# 檢查是否有 cross_attention 相關的鍵
cross_attn_keys = [k for k in state_dict.keys() if 'cross_attention' in k]
se_keys = [k for k in state_dict.keys() if 'se_block' in k]

print(f"\n✅ Cross Attention 參數: {len(cross_attn_keys)}")
print(f"✅ SE Block 參數: {len(se_keys)}")

# 檢查 base_model 前綴
base_model_keys = [k for k in state_dict.keys() if k.startswith('base_model.')]
print(f"\n🔍 base_model 前綴參數: {len(base_model_keys)}")
if base_model_keys:
    print("  前5個:")
    for key in base_model_keys[:5]:
        print(f"    - {key}")
