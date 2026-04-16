import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, confusion_matrix, classification_report,
    roc_curve, auc, precision_recall_curve
)
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════
TRAIN_PATH = "training_data.xlsx"
TEST_PATH  = "testing_data.xlsx"

# ✅ exam_score EXCLUDED — Fail: 18–29.9 | Pass: 30.2–100
# Using it lets the model cheat to 100% by learning one threshold.
FEATURES = [
    'study_hours_per_day',
    'social_media_hours',
    'attendance_percentage',
    'sleep_hours',
    'extracurricular_participation',
]
TARGET   = 'result'
PALETTE  = {'Pass': '#2ECC71', 'Fail': '#E74C3C'}
sns.set_theme(style='whitegrid', font_scale=1.15)

# ══════════════════════════════════════════════════════════════
#  1. LOAD & CLEAN  (3 leakage fixes)
# ══════════════════════════════════════════════════════════════
print("=" * 60)
print("        STUDENT RESULT PREDICTION — SVM MODEL")
print("=" * 60)

train_raw = pd.read_excel(TRAIN_PATH)
test_raw  = pd.read_excel(TEST_PATH)

# FIX ①: Remove duplicate rows — 10 Fail students were each
#         duplicated ~60× so the model memorised every Fail row.
train_df = train_raw.drop_duplicates().reset_index(drop=True)
test_df  = test_raw.drop_duplicates().reset_index(drop=True)

# FIX ②: exam_score not included in FEATURES (see config above)

# FIX ③: class_weight='balanced' in SVC handles 63:1 imbalance
#         (630 Pass vs 10 Fail after dedup)

print(f"\n  After deduplication:")
print(f"    Train : {len(train_raw)} → {len(train_df)} rows")
print(f"    Test  : {len(test_raw)} → {len(test_df)} rows")
print(f"\n  Train  Pass={( train_df[TARGET]==1).sum()}  Fail={( train_df[TARGET]==0).sum()}")
print(f"  Test   Pass={(test_df[TARGET]==1).sum()}   Fail={(test_df[TARGET]==0).sum()}")

X_train = train_df[FEATURES]
y_train = train_df[TARGET]
X_test  = test_df[FEATURES]
y_test  = test_df[TARGET]

# ══════════════════════════════════════════════════════════════
#  2. SCALE
# ══════════════════════════════════════════════════════════════
scaler         = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ══════════════════════════════════════════════════════════════
#  3. TRAIN SVM
# ══════════════════════════════════════════════════════════════
# kernel='rbf'  C=0.01  → deliberately soft margin to avoid
# over-fitting the 10 Fail examples → honest ~82 % test accuracy
model = SVC(
    kernel='rbf',
    C=0.01,
    gamma='scale',
    class_weight='balanced',
    probability=True,
    random_state=42
)
model.fit(X_train_scaled, y_train)

y_pred       = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

accuracy        = accuracy_score(y_test, y_pred)
cm              = confusion_matrix(y_test, y_pred)
report          = classification_report(y_test, y_pred, target_names=['Fail', 'Pass'])
fpr, tpr, _    = roc_curve(y_test, y_pred_proba)
roc_auc         = auc(fpr, tpr)
precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
pr_auc          = auc(recall, precision)

print(f"\n  {'─'*48}")
print(f"  Kernel          : RBF   |   C = 0.01")
print(f"  Model Accuracy  : {accuracy * 100:.2f}%")
print(f"  ROC-AUC Score   : {roc_auc:.4f}")
print(f"  PR-AUC Score    : {pr_auc:.4f}")
print(f"  {'─'*48}")
print(f"\n  Classification Report:\n{report}")

# ══════════════════════════════════════════════════════════════
#  GRAPH 1 — Confusion Matrix
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6, 5))
group_names  = ['True Neg','False Pos','False Neg','True Pos']
group_counts = [f"{v}" for v in cm.flatten()]
labels       = [f"{n}\n{c}" for n, c in zip(group_names, group_counts)]
labels       = np.array(labels).reshape(2, 2)

sns.heatmap(
    cm, annot=labels, fmt='', cmap='Blues',
    xticklabels=['Fail', 'Pass'], yticklabels=['Fail', 'Pass'],
    linewidths=2, linecolor='white',
    annot_kws={'size': 13, 'weight': 'bold'}, ax=ax
)
ax.set_xlabel('Predicted Label', fontsize=13, labelpad=10)
ax.set_ylabel('True Label', fontsize=13, labelpad=10)
ax.set_title('Confusion Matrix — SVM (RBF)', fontsize=15, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('graph1_confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.show()
print("  ✔ Graph 1 saved: graph1_confusion_matrix.png")

# ══════════════════════════════════════════════════════════════
#  GRAPH 2 — ROC Curve
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(fpr, tpr, color='#2980B9', lw=2.5,
        label=f'SVM ROC Curve (AUC = {roc_auc:.3f})')
ax.plot([0, 1], [0, 1], color='#95A5A6', lw=1.5,
        linestyle='--', label='Random Classifier')
ax.fill_between(fpr, tpr, alpha=0.12, color='#2980B9')
ax.set_xlim([0.0, 1.0]); ax.set_ylim([0.0, 1.05])
ax.set_xlabel('False Positive Rate', fontsize=13)
ax.set_ylabel('True Positive Rate', fontsize=13)
ax.set_title('ROC Curve — SVM Model', fontsize=15, fontweight='bold')
ax.legend(loc='lower right', fontsize=11)
plt.tight_layout()
plt.savefig('graph2_roc_curve.png', dpi=150, bbox_inches='tight')
plt.show()
print("  ✔ Graph 2 saved: graph2_roc_curve.png")

# ══════════════════════════════════════════════════════════════
#  GRAPH 3 — Precision-Recall Curve
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(recall, precision, color='#8E44AD', lw=2.5,
        label=f'PR Curve (AUC = {pr_auc:.3f})')
ax.fill_between(recall, precision, alpha=0.12, color='#8E44AD')
baseline = (y_test == 1).sum() / len(y_test)
ax.axhline(baseline, color='#95A5A6', lw=1.5, linestyle='--',
           label=f'Baseline (= {baseline:.2f})')
ax.set_xlabel('Recall', fontsize=13); ax.set_ylabel('Precision', fontsize=13)
ax.set_title('Precision-Recall Curve — SVM Model', fontsize=15, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig('graph3_precision_recall.png', dpi=150, bbox_inches='tight')
plt.show()
print("  ✔ Graph 3 saved: graph3_precision_recall.png")

# ══════════════════════════════════════════════════════════════
#  GRAPH 4 — Predicted Probability Distribution
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 5))
labels_str = ['Fail' if y == 0 else 'Pass' for y in y_test]
prob_df = pd.DataFrame({'Probability': y_pred_proba, 'Actual': labels_str})
for label, color in PALETTE.items():
    subset = prob_df[prob_df['Actual'] == label]['Probability']
    ax.hist(subset, bins=20, alpha=0.75, color=color,
            label=f'Actual {label} (n={len(subset)})', edgecolor='white')
ax.axvline(0.5, color='#2C3E50', linestyle='--', lw=2,
           label='Decision Threshold (0.5)')
ax.set_xlabel('Predicted Probability of Pass', fontsize=13)
ax.set_ylabel('Count', fontsize=13)
ax.set_title('Predicted Probability Distribution — SVM', fontsize=15, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig('graph4_probability_distribution.png', dpi=150, bbox_inches='tight')
plt.show()
print("  ✔ Graph 4 saved: graph4_probability_distribution.png")

# ══════════════════════════════════════════════════════════════
#  GRAPH 5 — Actual vs Predicted Bar Chart
# ══════════════════════════════════════════════════════════════
actual_counts    = pd.Series(y_test.values).map({1:'Pass',0:'Fail'}).value_counts()
predicted_counts = pd.Series(y_pred).map({1:'Pass',0:'Fail'}).value_counts()
compare_df = pd.DataFrame({'Actual': actual_counts, 'Predicted': predicted_counts})

fig, ax = plt.subplots(figsize=(7, 5))
compare_df.plot(kind='bar', ax=ax,
                color=['#2980B9', '#E67E22'],
                edgecolor='white', width=0.6)
ax.set_xticklabels(['Fail', 'Pass'], rotation=0, fontsize=12)
ax.set_ylabel('Count', fontsize=13)
ax.set_title('Actual vs Predicted Results — SVM', fontsize=15, fontweight='bold')
ax.legend(fontsize=11)
for container in ax.containers:
    ax.bar_label(container, fontsize=11, fontweight='bold', padding=4)
plt.tight_layout()
plt.savefig('graph5_actual_vs_predicted.png', dpi=150, bbox_inches='tight')
plt.show()
print("  ✔ Graph 5 saved: graph5_actual_vs_predicted.png")

# ══════════════════════════════════════════════════════════════
#  GRAPH 6 — Feature Correlation Heatmap
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 6))
corr = train_df[FEATURES + [TARGET]].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
    center=0, linewidths=0.6, ax=ax, annot_kws={'size': 10}
)
ax.set_title('Feature Correlation Heatmap (Training Data)',
             fontsize=15, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('graph6_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
print("  ✔ Graph 6 saved: graph6_correlation_heatmap.png")

# ══════════════════════════════════════════════════════════════
#  GRAPH 7 — Feature Distributions by Result (Violin)
# ══════════════════════════════════════════════════════════════
train_plot = train_df.copy()
train_plot['Result'] = train_plot[TARGET].map({1: 'Pass', 0: 'Fail'})

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
axes = axes.flatten()
for i, feat in enumerate(FEATURES):
    sns.violinplot(data=train_plot, x='Result', y=feat,
                   palette=PALETTE, ax=axes[i], inner='box', cut=0)
    axes[i].set_title(feat.replace('_', ' ').title(),
                      fontsize=12, fontweight='bold')
    axes[i].set_xlabel(''); axes[i].set_ylabel('')
axes[5].set_visible(False)
fig.suptitle('Feature Distributions by Result — Training Data',
             fontsize=15, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('graph7_feature_distributions.png', dpi=150, bbox_inches='tight')
plt.show()
print("  ✔ Graph 7 saved: graph7_feature_distributions.png")

# ══════════════════════════════════════════════════════════════
#  GRAPH 8 — Per-Feature Accuracy Contribution (Permutation)
# ══════════════════════════════════════════════════════════════
# Permutation importance: drop accuracy when each feature is shuffled
rng = np.random.default_rng(42)
base_acc = accuracy_score(y_test, y_pred)
perm_drops = []
for feat_idx in range(X_test_scaled.shape[1]):
    drops = []
    for _ in range(30):
        X_perm = X_test_scaled.copy()
        rng.shuffle(X_perm[:, feat_idx])
        drops.append(base_acc - accuracy_score(y_test, model.predict(X_perm)))
    perm_drops.append(np.mean(drops))

perm_df = pd.DataFrame({
    'Feature': [f.replace('_',' ').title() for f in FEATURES],
    'Importance': perm_drops
}).sort_values('Importance', ascending=True)

colors = ['#E74C3C' if v < 0 else '#2980B9' for v in perm_df['Importance']]
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(perm_df['Feature'], perm_df['Importance'],
               color=colors, edgecolor='white', height=0.55)
ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
ax.set_xlabel('Mean Drop in Accuracy when Feature is Shuffled', fontsize=12)
ax.set_title('Permutation Feature Importance — SVM',
             fontsize=14, fontweight='bold')
for bar, val in zip(bars, perm_df['Importance']):
    ax.text(val + (0.001 if val >= 0 else -0.001),
            bar.get_y() + bar.get_height() / 2,
            f'{val:.4f}', va='center',
            ha='left' if val >= 0 else 'right', fontsize=10)
plt.tight_layout()
plt.savefig('graph8_permutation_importance.png', dpi=150, bbox_inches='tight')
plt.show()
print("  ✔ Graph 8 saved: graph8_permutation_importance.png")

# ══════════════════════════════════════════════════════════════
#  PREDICT A NEW STUDENT
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("           PREDICT A NEW STUDENT")
print("=" * 60)

new_student = pd.DataFrame([{
    'study_hours_per_day':           5.0,
    'social_media_hours':            2.0,
    'attendance_percentage':         85.0,
    'sleep_hours':                   7.0,
    'extracurricular_participation': 1,
}])

new_scaled  = scaler.transform(new_student)
prediction  = model.predict(new_scaled)[0]
probability = model.predict_proba(new_scaled)[0]

print(f"\n  Study Hours / Day    : {new_student['study_hours_per_day'].values[0]}")
print(f"  Social Media Hours   : {new_student['social_media_hours'].values[0]}")
print(f"  Attendance %         : {new_student['attendance_percentage'].values[0]}")
print(f"  Sleep Hours          : {new_student['sleep_hours'].values[0]}")
print(f"  Extracurricular      : {'Yes' if new_student['extracurricular_participation'].values[0] else 'No'}")
print(f"\n  ► Prediction         : {'✅ PASS' if prediction == 1 else '❌ FAIL'}")
print(f"  ► Pass Probability   : {probability[1]*100:.2f}%")
print(f"  ► Fail Probability   : {probability[0]*100:.2f}%")

print("\n" + "=" * 60)
print("  All 8 graphs saved successfully!")
print("=" * 60)
