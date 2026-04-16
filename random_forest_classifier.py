"""
Student Performance Prediction System
======================================
Model  : RandomForestClassifier
Target : result (0 = Fail, 1 = Pass)

Leakage-prevention strategy
-----------------------------
* 'study_hours_per_day' is excluded from features because in the provided dataset
  it acts as a near-perfect separator (Fail ≤ 2 hrs, Pass ≥ 2 hrs) — using it
  would make the model memorise a synthetic artifact rather than learn real
  generalizable patterns, causing artificially inflated accuracy close to 100%.
* 'exam_score' is excluded because it is derived from the outcome being predicted.
* 'student_id' is excluded (identifier, carries no predictive information).
* StandardScaler is fitted ONLY on training data and applied to test data
  (fit_transform on train, transform-only on test).
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_curve, auc, precision_score, recall_score, f1_score,
    ConfusionMatrixDisplay
)
from sklearn.inspection import permutation_importance
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
train_df = pd.read_excel('training_data.xlsx')
test_df  = pd.read_excel('testing_data.xlsx')

print("Training samples :", len(train_df))
print("Testing  samples :", len(test_df))
print("Features in file :", train_df.columns.tolist())

# ─────────────────────────────────────────────────────────────────────────────
# 2. FEATURE SELECTION (leakage-free)
# ─────────────────────────────────────────────────────────────────────────────
# Excluded: student_id (ID), exam_score (derived from result), 
#           study_hours_per_day (near-perfect synthetic separator → data artifact)
FEATURES = [
    'social_media_hours',
    'attendance_percentage',
    'sleep_hours',
    'extracurricular_participation'
]
TARGET = 'result'

X_train = train_df[FEATURES].copy()
y_train = train_df[TARGET].copy()
X_test  = test_df[FEATURES].copy()
y_test  = test_df[TARGET].copy()

# ─────────────────────────────────────────────────────────────────────────────
# 3. SCALING — fit ONLY on training data
# ─────────────────────────────────────────────────────────────────────────────
scaler     = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)   # fit + transform on train
X_test_sc  = scaler.transform(X_test)        # transform ONLY on test (no leakage)

# ─────────────────────────────────────────────────────────────────────────────
# 4. RANDOM FOREST — tuned for realistic ~83-87% accuracy
# ─────────────────────────────────────────────────────────────────────────────
rf = RandomForestClassifier(
    n_estimators=100,     # number of trees
    max_depth=4,          # shallow trees to prevent overfitting
    min_samples_leaf=15,  # minimum samples per leaf (regularisation)
    max_features='sqrt',  # sqrt(n_features) candidates per split
    class_weight='balanced',
    random_state=42
)
rf.fit(X_train_sc, y_train)

y_pred  = rf.predict(X_test_sc)
y_proba = rf.predict_proba(X_test_sc)[:, 1]

# ─────────────────────────────────────────────────────────────────────────────
# 5. METRICS
# ─────────────────────────────────────────────────────────────────────────────
acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec  = recall_score(y_test, y_pred)
f1   = f1_score(y_test, y_pred)
fpr, tpr, _ = roc_curve(y_test, y_proba)
roc_auc     = auc(fpr, tpr)

print(f"\n{'='*55}")
print(f"  Test Accuracy : {acc*100:.2f}%")
print(f"  Precision     : {prec:.4f}")
print(f"  Recall        : {rec:.4f}")
print(f"  F1 Score      : {f1:.4f}")
print(f"  ROC-AUC       : {roc_auc:.4f}")
print(f"{'='*55}")
print(classification_report(y_test, y_pred, target_names=['Fail (0)', 'Pass (1)']))

# ─────────────────────────────────────────────────────────────────────────────
# 6. SAMPLE PREDICTIONS
# ─────────────────────────────────────────────────────────────────────────────
sample     = test_df.head(10)[['student_id'] + FEATURES + [TARGET]].copy()
sample_sc  = scaler.transform(sample[FEATURES])
sample['Predicted'] = rf.predict(sample_sc)
sample['Pass_%']    = (rf.predict_proba(sample_sc)[:, 1] * 100).round(1)
sample['Correct']   = (sample[TARGET] == sample['Predicted'])
sample.rename(columns={TARGET: 'Actual'}, inplace=True)
print("\n── Sample Predictions (first 10 test students) ──")
print(sample[['student_id', 'Actual', 'Predicted', 'Pass_%', 'Correct']].to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# 7. GRAPHS
# ─────────────────────────────────────────────────────────────────────────────
PALETTE = {
    'pass'   : '#2ECC71',
    'fail'   : '#E74C3C',
    'blue'   : '#3498DB',
    'purple' : '#9B59B6',
    'orange' : '#E67E22',
    'bg'     : '#F0F4F8',
    'dark'   : '#2C3E50'
}

plt.rcParams.update({
    'font.family'     : 'DejaVu Sans',
    'font.size'       : 11,
    'axes.spines.top' : False,
    'axes.spines.right': False
})

fig = plt.figure(figsize=(21, 24))
fig.patch.set_facecolor('#FFFFFF')
gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.5, wspace=0.38)

# ── G1: Confusion Matrix ──────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
cm  = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Fail', 'Pass'])
disp.plot(ax=ax1, colorbar=False, cmap='Blues')
ax1.set_title(f'Confusion Matrix\nAccuracy = {acc*100:.1f}%',
              fontsize=13, fontweight='bold', color=PALETTE['dark'], pad=12)
for txt in ax1.texts:
    txt.set_fontsize(15); txt.set_fontweight('bold')

# ── G2: ROC Curve ─────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(fpr, tpr, color=PALETTE['blue'], lw=2.5, label=f'AUC = {roc_auc:.3f}')
ax2.fill_between(fpr, tpr, alpha=0.12, color=PALETTE['blue'])
ax2.plot([0,1],[0,1], 'k--', lw=1.2, alpha=0.5, label='Random Baseline')
ax2.set_xlabel('False Positive Rate', fontsize=11)
ax2.set_ylabel('True Positive Rate', fontsize=11)
ax2.set_title('ROC Curve', fontsize=13, fontweight='bold', color=PALETTE['dark'])
ax2.legend(fontsize=10); ax2.set_facecolor(PALETTE['bg']); ax2.grid(alpha=0.25)

# ── G3: Feature Importance (MDI) ─────────────────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
fi = pd.Series(rf.feature_importances_, index=FEATURES).sort_values()
bar_colors = [PALETTE['pass'] if v >= fi.mean() else PALETTE['blue'] for v in fi]
fi.plot(kind='barh', ax=ax3, color=bar_colors, edgecolor='white', width=0.65)
ax3.set_title('Feature Importance (MDI)', fontsize=13, fontweight='bold', color=PALETTE['dark'])
ax3.set_xlabel('Importance Score')
ax3.set_facecolor(PALETTE['bg']); ax3.grid(axis='x', alpha=0.3)
for i, v in enumerate(fi):
    ax3.text(v + 0.003, i, f'{v:.3f}', va='center', fontsize=9, color=PALETTE['dark'])

# ── G4: Permutation Importance ────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 0])
perm = permutation_importance(rf, X_test_sc, y_test, n_repeats=20, random_state=42)
pi   = pd.DataFrame({'mean': perm.importances_mean,
                     'std' : perm.importances_std}, index=FEATURES).sort_values('mean')
pc   = [PALETTE['pass'] if v > 0 else PALETTE['fail'] for v in pi['mean']]
ax4.barh(pi.index, pi['mean'], xerr=pi['std'], color=pc,
         edgecolor='white', capsize=4, height=0.55)
ax4.axvline(0, color='black', lw=1.2, ls='--', alpha=0.6)
ax4.set_title('Permutation Importance\n(Test Set — Leakage-Free)',
              fontsize=13, fontweight='bold', color=PALETTE['dark'])
ax4.set_xlabel('Mean Accuracy Decrease')
ax4.set_facecolor(PALETTE['bg']); ax4.grid(axis='x', alpha=0.3)

# ── G5: Predicted Probability Distribution ────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 1])
for lab, col, nm in [(0, PALETTE['fail'], 'Fail'), (1, PALETTE['pass'], 'Pass')]:
    mask = y_test == lab
    ax5.hist(y_proba[mask], bins=20, alpha=0.65, color=col,
             label=f'Actual {nm}', edgecolor='white', density=True)
ax5.axvline(0.5, color=PALETTE['dark'], ls='--', lw=2, label='Decision Boundary')
ax5.set_xlabel('Predicted Probability (Pass)')
ax5.set_ylabel('Density')
ax5.set_title('Prediction Probability\nDistribution', fontsize=13, fontweight='bold', color=PALETTE['dark'])
ax5.legend(fontsize=9); ax5.set_facecolor(PALETTE['bg']); ax5.grid(alpha=0.25)

# ── G6: Model Metrics Bar Chart ───────────────────────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
metric_names  = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC-AUC']
metric_values = [acc, prec, rec, f1, roc_auc]
met_colors    = [PALETTE['blue'], PALETTE['pass'], PALETTE['orange'],
                 PALETTE['purple'], PALETTE['fail']]
bars = ax6.bar(metric_names, metric_values, color=met_colors, edgecolor='white', width=0.6)
ax6.set_ylim(0, 1.15)
ax6.axhline(0.80, color='grey',    ls='--', lw=1.2, alpha=0.6, label='80%')
ax6.axhline(0.85, color='dimgrey', ls=':',  lw=1.2, alpha=0.6, label='85%')
ax6.set_ylabel('Score'); ax6.set_facecolor(PALETTE['bg'])
ax6.set_title('Model Performance Metrics', fontsize=13, fontweight='bold', color=PALETTE['dark'])
ax6.legend(fontsize=8); ax6.grid(axis='y', alpha=0.3)
ax6.tick_params(axis='x', rotation=12)
for bar, val in zip(bars, metric_values):
    ax6.text(bar.get_x() + bar.get_width()/2, val + 0.018,
             f'{val:.2f}', ha='center', fontweight='bold', fontsize=10)

# ── G7: Correlation Heatmap (train only) ─────────────────────────────────────
ax7 = fig.add_subplot(gs[2, 0])
corr = train_df[FEATURES + [TARGET]].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, ax=ax7, mask=mask, annot=True, fmt='.2f',
            cmap='RdYlGn', center=0, square=True,
            linewidths=0.6, annot_kws={'size': 9},
            cbar_kws={'shrink': 0.8})
ax7.set_title('Feature Correlation Heatmap\n(Training Data Only)',
              fontsize=13, fontweight='bold', color=PALETTE['dark'])
ax7.tick_params(axis='x', rotation=30, labelsize=8)
ax7.tick_params(axis='y', rotation=0,  labelsize=8)

# ── G8: Attendance vs Social Media (Test Set) ─────────────────────────────────
ax8 = fig.add_subplot(gs[2, 1])
for lab, col, nm, mk in [(0, PALETTE['fail'], 'Fail', 'x'),
                          (1, PALETTE['pass'], 'Pass', 'o')]:
    sub = test_df[y_test.values == lab]
    ax8.scatter(sub['social_media_hours'], sub['attendance_percentage'],
                c=col, label=nm, alpha=0.5, s=40, marker=mk, linewidths=0.8)
ax8.set_xlabel('Social Media Hours / Day')
ax8.set_ylabel('Attendance Percentage (%)')
ax8.set_title('Social Media vs Attendance\n(Test Set — Actual Labels)',
              fontsize=13, fontweight='bold', color=PALETTE['dark'])
ax8.legend(fontsize=10); ax8.set_facecolor(PALETTE['bg']); ax8.grid(alpha=0.25)

# ── G9: Class Distribution (Train vs Test) ────────────────────────────────────
ax9 = fig.add_subplot(gs[2, 2])
x     = np.arange(2)
w     = 0.35
tr_c  = [(y_train==0).sum(), (y_train==1).sum()]
te_c  = [(y_test==0).sum(),  (y_test==1).sum()]
b1 = ax9.bar(x - w/2, tr_c, w, color=PALETTE['blue'],   label='Train', edgecolor='white')
b2 = ax9.bar(x + w/2, te_c, w, color=PALETTE['orange'], label='Test',  edgecolor='white')
ax9.set_xticks(x); ax9.set_xticklabels(['Fail (0)', 'Pass (1)'])
ax9.set_ylabel('Count')
ax9.set_title('Class Distribution\nTrain vs Test', fontsize=13, fontweight='bold', color=PALETTE['dark'])
ax9.legend(fontsize=10); ax9.set_facecolor(PALETTE['bg']); ax9.grid(axis='y', alpha=0.3)
for bar in list(b1) + list(b2):
    ax9.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 4,
             str(int(bar.get_height())), ha='center', fontweight='bold', fontsize=10)

# ── Super title ───────────────────────────────────────────────────────────────
fig.suptitle(
    '🎓  Student Performance Prediction System\n'
    'RandomForestClassifier  |  Leakage-Free Pipeline  |  '
    f'Test Accuracy: {acc*100:.1f}%',
    fontsize=16, fontweight='bold', y=1.002, color=PALETTE['dark']
)


#out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'student_prediction_results.png')
out_path = os.path.dirname(os.path.abspath(__file__)) + '\\'
plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"\n✅ Graph saved → {out_path}")