"""
train_model_window_1h.py
Train model WINDOW-BASED dự đoán UP/DOWN/NEUTRAL cho 1H tiếp theo
(Dùng label_1h từ CSV window-based)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    accuracy_score,
    precision_recall_fscore_support
)
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
from datetime import datetime

# ============================================
# 1. LOAD DATA
# ============================================

print("=" * 70)
print("TRAIN MODEL WINDOW 1H: PREDICT UP/DOWN/NEUTRAL")
print("=" * 70)

# Load window-based CSV
df = pd.read_csv('aligned_news_price_window_1h_2025-12-01_to_2026-01-22.csv')

# Parse datetime
df['window_start'] = pd.to_datetime(df['window_start'])
df['window_end'] = pd.to_datetime(df['window_end'])

# Filter out UNKNOWN labels
df = df[df['label_1h'].notna()].copy()
df = df[df['label_1h'] != 'UNKNOWN'].copy()

print(f"✓ Loaded {len(df)} windows")
print(f"  Date range: {df['window_start'].min()} to {df['window_end'].max()}")

# ============================================
# 2. FEATURE ENGINEERING
# ============================================

print("\n" + "=" * 70)
print("2. FEATURE SELECTION (WINDOW-BASED)")
print("=" * 70)

feature_cols = [
    # NEWS FEATURES (13)
    'news_count',
    'avg_sentiment',
    'max_sentiment',
    'min_sentiment',
    'sentiment_std',
    'breaking_count',
    'avg_breaking_score',
    'has_sec',
    'has_fed',
    'has_blackrock',
    'has_major_entity',
    'positive_keyword_count',
    'negative_keyword_count',
    
    # PRICE FEATURES (6)
    'vol_pre_24h',
    'volume_pre_24h',
    'rsi_24h',
    'price_change_24h',
    'high_low_range_24h',
    'volume_ma_ratio',
    
    # MARKET CONTEXT (3)
    'market_cap_rank',
    'time_of_day',
    'day_of_week',
]

# Add baseline if exists
if 'baseline_ret_1h' in df.columns:
    feature_cols.append('baseline_ret_1h')

target_col = 'label_1h'

# Drop rows có missing features
df_clean = df.dropna(subset=feature_cols + [target_col])

print(f"✓ Features: {len(feature_cols)}")
print(f"  News: 13, Price: 6, Context: 3")
print(f"✓ Target: {target_col}")
print(f"✓ Clean dataset: {len(df_clean)} windows")
print(f"\nLabel distribution:\n{df_clean[target_col].value_counts()}")

# ============================================
# 3. TRAIN/VAL/TEST SPLIT (STRATIFIED)
# ============================================

print("\n" + "=" * 70)
print("3. TRAIN/VAL/TEST SPLIT (STRATIFIED)")
print("=" * 70)

X = df_clean[feature_cols]
y = df_clean[target_col]

# Stratified split
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.15, stratify=y, random_state=42
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.176, stratify=y_temp, random_state=42
)

print(f"Train: {len(X_train)} windows")
print(f"Val:   {len(X_val)} windows")
print(f"Test:  {len(X_test)} windows")

print(f"\nLabel distribution:")
print(f"  Train: {dict(y_train.value_counts())}")
print(f"  Val:   {dict(y_val.value_counts())}")
print(f"  Test:  {dict(y_test.value_counts())}")

# ============================================
# 4. TRAIN MODELS
# ============================================

print("\n" + "=" * 70)
print("4. TRAINING MODELS (WINDOW-BASED 1H)")
print("=" * 70)

# Model 1: Random Forest
model_rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)

model_rf.fit(X_train, y_train)
print("✓ Random Forest trained")

# Model 2: Gradient Boosting
model_gb = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)

model_gb.fit(X_train, y_train)
print("✓ Gradient Boosting trained")



# ============================================
# 5. EVALUATE ON VALIDATION SET
# ============================================

print("\n" + "=" * 70)
print("5. VALIDATION SET PERFORMANCE")
print("=" * 70)

# Random Forest
y_val_pred_rf = model_rf.predict(X_val)
acc_val_rf = accuracy_score(y_val, y_val_pred_rf)
print(f"\nRandom Forest - Val Acc: {acc_val_rf:.4f}")

# Gradient Boosting
y_val_pred_gb = model_gb.predict(X_val)
acc_val_gb = accuracy_score(y_val, y_val_pred_gb)
print(f"Gradient Boosting - Val Acc: {acc_val_gb:.4f}")


# Chọn model tốt nhất
best_scores = {
    'Random Forest': acc_val_rf,
    'Gradient Boosting': acc_val_gb,
}

best_model_name = max(best_scores, key=best_scores.get)
best_acc = best_scores[best_model_name]


if best_model_name == 'Random Forest':
    best_model = model_rf
else:  # Gradient Boosting
    best_model = model_gb
print(f"\n✅ Selected: {best_model_name} (acc: {best_acc:.4f})")

# ============================================
# 6. EVALUATE ON TEST SET
# ============================================

print("\n" + "=" * 70)
print("6. TEST SET PERFORMANCE")
print("=" * 70)


y_test_pred = best_model.predict(X_test)
y_test_proba = best_model.predict_proba(X_test)

acc_test = accuracy_score(y_test, y_test_pred)

print(f"\n{best_model_name} - Test Accuracy: {acc_test:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_test_pred, zero_division=0))

# Confusion Matrix
cm = confusion_matrix(y_test, y_test_pred, labels=['DOWN', 'UP'])

print("\nConfusion Matrix:")
print("              Predicted")
print("               DOWN  UP")
print(f"Actual DOWN    {cm[0,0]:4d}  {cm[0,1]:4d}")
print(f"       UP      {cm[1,0]:4d}  {cm[1,1]:4d}")

# ============================================
# 7. FEATURE IMPORTANCE
# ============================================

print("\n" + "=" * 70)
print("7. FEATURE IMPORTANCE")
print("=" * 70)

feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=False)

print(feature_importance.head(10).to_string(index=False))

# ============================================
# 8. VISUALIZATIONS
# ============================================

print("\n" + "=" * 70)
print("8. CREATING VISUALIZATIONS...")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Confusion Matrix
# SAU (BINARY)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['DOWN', 'UP'],
            yticklabels=['DOWN', 'UP'],
            ax=axes[0, 0])
axes[0, 0].set_title(f'Confusion Matrix (Window 1H)\nAccuracy: {acc_test:.2%}')
axes[0, 0].set_ylabel('Actual')
axes[0, 0].set_xlabel('Predicted')

# Plot 2: Feature Importance (top 15)
top_features = feature_importance.head(15)
axes[0, 1].barh(top_features['feature'], top_features['importance'])
axes[0, 1].set_xlabel('Importance')
axes[0, 1].set_title('Top 15 Features (Window 1H)')
axes[0, 1].invert_yaxis()
axes[0, 1].grid(alpha=0.3)

# Plot 3: Prediction distribution
test_label_dist = pd.Series(y_test_pred).value_counts()
axes[1, 0].bar(test_label_dist.index, test_label_dist.values, alpha=0.7, edgecolor='black')
axes[1, 0].set_xlabel('Predicted Label')
axes[1, 0].set_ylabel('Count')
axes[1, 0].set_title('Prediction Distribution (Window 1H)')
axes[1, 0].grid(alpha=0.3)

# Plot 4: News count effect
df_test = df_clean.loc[X_test.index].copy()
df_test['predicted'] = y_test_pred
df_test['correct'] = (df_test['predicted'] == df_test[target_col])

news_bins = [0, 1, 3, 5, 100]
df_test['news_bin'] = pd.cut(df_test['news_count'], bins=news_bins, labels=['0', '1-2', '3-4', '5+'])
news_acc = df_test.groupby('news_bin', observed=True)['correct'].mean()

axes[1, 1].bar(range(len(news_acc)), news_acc.values, alpha=0.7, edgecolor='black')
axes[1, 1].set_xticks(range(len(news_acc)))
axes[1, 1].set_xticklabels(news_acc.index)
axes[1, 1].set_ylabel('Accuracy')
axes[1, 1].set_xlabel('News Count in Window')
axes[1, 1].set_title('Accuracy by News Count (Window 1H)')
axes[1, 1].grid(alpha=0.3)
axes[1, 1].axhline(acc_test, color='red', linestyle='--', label=f'Overall: {acc_test:.2%}')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('model_evaluation_window_1h.png', dpi=300, bbox_inches='tight')
print("✓ Saved: model_evaluation_window_1h.png")

# ============================================
# 9. SAVE MODEL
# ============================================

print("\n" + "=" * 70)
print("9. SAVING MODEL (WINDOW 1H)...")
print("=" * 70)

model_filename = f'model_window_1h.pkl'
joblib.dump(best_model, model_filename)
print(f"✓ Model saved: {model_filename}")

# Save metadata
feature_info = {
    'feature_cols': feature_cols,
    'model_name': best_model_name,
    'approach': 'window-based',
    'window_hours': 1,
    'target': 'label_1h',
    'test_accuracy': float(acc_test),
    'trained_date': datetime.now().isoformat(),
    'threshold': 0.0,  # ← SỬA: 0.0 cho binary
    'horizon': '1h',
    'num_features': len(feature_cols),
    'classes': ['DOWN', 'UP'],  # ← SỬA: chỉ 2 classes
    'is_binary': True  # ← THÊM
}

with open('model_info_window_1h.json', 'w') as f:
    json.dump(feature_info, f, indent=2)
print("✓ Metadata saved: model_info_window_1h.json")
# ============================================
# 10. SUMMARY
# ============================================

print("\n" + "=" * 70)
print("📊 WINDOW-BASED MODEL 1H SUMMARY")
print("=" * 70)

# SAU (BINARY)
precision, recall, f1, support = precision_recall_fscore_support(
    y_test, y_test_pred, average=None, labels=['DOWN', 'UP'], zero_division=0
)

print(f"""
MODEL DETAILS:
--------------
Approach: Window-based (aggregate news in 1h windows)
Model: {best_model_name}
Target: label_1h (BINARY: UP/DOWN only, threshold 0.0)
Features: {len(feature_cols)} (13 news + 6 price + 3 context)
Training windows: {len(X_train)}
Test windows: {len(X_test)}

TEST PERFORMANCE:
-----------------
Overall Accuracy: {acc_test:.2%}

Per-class (BINARY):
  DOWN: Precision {precision[0]:.2%}, Recall {recall[0]:.2%}, F1 {f1[0]:.2%}, Support {support[0]}
  UP:   Precision {precision[1]:.2%}, Recall {recall[1]:.2%}, F1 {f1[1]:.2%}, Support {support[1]}

TOP 5 FEATURES:
---------------
""")

for i, (idx, row) in enumerate(feature_importance.head(5).iterrows(), 1):
    print(f"{i}. {row['feature']}: {row['importance']:.4f}")

print(f"""
SAVED FILES:
------------
- Model: {model_filename}
- Metadata: model_info_window_1h.json
- Visualization: model_evaluation_window_1h.png
""")


print("\nCONCLUSION:")
print("-----------")
if acc_test >= 0.70:
    print("✅ Model achieves ≥70% accuracy → GOOD")
elif acc_test >= 0.60:
    print("⚠️ Model achieves 60-70% accuracy → ACCEPTABLE")
else:
    print("❌ Model achieves <60% accuracy → NEEDS TUNING")

print("\n✅ Window-based model 1H training DONE!")
print("=" * 70)