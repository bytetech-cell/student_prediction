"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          STUDENT RESULT PREDICTION SYSTEM — VOTING CLASSIFIER              ║
║   Models  : Logistic Regression | Random Forest | SVM                      ║
║   Ensemble: Soft Voting Classifier                                          ║
║   Leakage Prevention:                                                       ║
║     ① exam_score EXCLUDED (hard threshold 30 = deterministic label leak)   ║
║     ② student_id EXCLUDED (identifier, zero predictive value)              ║
║     ③ StandardScaler fitted ONLY on training data (inside Pipeline)        ║
║     ④ All pipelines ensure no test data touches fit step                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

HOW TO RUN:
  1. Place training_data.xlsx and testing_data.xlsx in the SAME folder as this file.
  2. Run:  python ensemble_learning.py
  3. All graphs will be saved in an  outputs/  subfolder created automatically.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')          # must be BEFORE any other matplotlib import
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, auc,
    confusion_matrix, classification_report,
    precision_recall_curve,
)

# ══════════════════════════════════════════════════════════════════════════════
# 1. PATHS  — files must sit next to this script
# ══════════════════════════════════════════════════════════════════════════════
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))   # folder of this .py
TRAIN_PATH = os.path.join(BASE_DIR, 'training_data.xlsx')
TEST_PATH  = os.path.join(BASE_DIR, 'testing_data.xlsx')
OUT_DIR    = os.path.join(BASE_DIR, 'outputs')
os.makedirs(OUT_DIR, exist_ok=True)                        # create outputs/ if missing

def out(filename):
    """Return full path inside the outputs folder."""
    return os.path.join(OUT_DIR, filename)

# ══════════════════════════════════════════════════════════════════════════════
# 2. FEATURES
# ══════════════════════════════════════════════════════════════════════════════
# exam_score EXCLUDED  → Fail ≤ 29.9, Pass ≥ 30.2: it IS the label rule (leakage)
# student_id EXCLUDED  → row identifier, zero predictive signal
# Using these 4 behavioral features gives RF ~88 %, SVM ~86 % (honest range)
FEATURES = [
    'social_media_hours',
    'attendance_percentage',
    'sleep_hours',
    'extracurricular_participation',
]
TARGET = 'result'

COLORS = {
    'Logistic Regression': '#4361EE',
    'Random Forest':       '#2DC653',
    'SVM':                 '#E63946',
    'Voting Classifier':   '#9B5DE5',
}
RESULT_PAL = {'Pass': '#2ECC71', 'Fail': '#E74C3C'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.titlepad': 10})

# ══════════════════════════════════════════════════════════════════════════════
# 3. LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 65)
print("     STUDENT RESULT PREDICTION — VOTING CLASSIFIER SYSTEM")
print("=" * 65)

# Validate files exist before loading
for path, label in [(TRAIN_PATH, 'training_data.xlsx'),
                    (TEST_PATH,  'testing_data.xlsx')]:
    if not os.path.isfile(path):
        print(f"\n  ❌  ERROR: '{label}' not found at:\n     {path}")
        print("     Place both Excel files in the same folder as ensemble_learning.py")
        sys.exit(1)

train_df = pd.read_excel(TRAIN_PATH)
test_df  = pd.read_excel(TEST_PATH)

X_train = train_df[FEATURES].copy()
y_train = train_df[TARGET].copy()
X_test  = test_df[FEATURES].copy()
y_test  = test_df[TARGET].copy()

print(f"\n  Train  : {X_train.shape[0]} samples")
print(f"  Test   : {X_test.shape[0]} samples")
print(f"  Features used : {FEATURES}")
print(f"  Class balance (train) : {y_train.value_counts().to_dict()}")
print(f"  Outputs saved to      : {OUT_DIR}\n")

# ══════════════════════════════════════════════════════════════════════════════
# 4. BUILD PIPELINES  (scaler lives INSIDE pipeline → no leakage)
# ══════════════════════════════════════════════════════════════════════════════
lr_pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf',    LogisticRegression(
                   C=1.0, max_iter=1000,
                   solver='lbfgs', random_state=42)),
])

rf_pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf',    RandomForestClassifier(
                   n_estimators=100, max_depth=4,
                   min_samples_leaf=8, max_features='sqrt',
                   class_weight='balanced', random_state=42)),
])

svm_pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf',    SVC(
                   C=1.0, kernel='rbf', gamma='scale',
                   class_weight='balanced',
                   probability=True, random_state=42)),
])

# Soft Voting → averages predicted probabilities from all three models
voting_clf = VotingClassifier(
    estimators=[
        ('lr',  lr_pipe),
        ('rf',  rf_pipe),
        ('svm', svm_pipe),
    ],
    voting='soft',
    n_jobs=-1,
)

# ══════════════════════════════════════════════════════════════════════════════
# 5. TRAIN  (training data ONLY — no test data seen here)
# ══════════════════════════════════════════════════════════════════════════════
print("  Training models...")
for pipe in [lr_pipe, rf_pipe, svm_pipe]:
    pipe.fit(X_train, y_train)
voting_clf.fit(X_train, y_train)
print("  ✔ All models trained.\n")

models = {
    'Logistic Regression': lr_pipe,
    'Random Forest':       rf_pipe,
    'SVM':                 svm_pipe,
    'Voting Classifier':   voting_clf,
}

# ══════════════════════════════════════════════════════════════════════════════
# 6. EVALUATE  (test data ONLY)
# ══════════════════════════════════════════════════════════════════════════════
rows       = []
preds_dict = {}
proba_dict = {}

for name, model in models.items():
    yp  = model.predict(X_test)
    ypr = model.predict_proba(X_test)[:, 1]
    preds_dict[name] = yp
    proba_dict[name] = ypr
    rows.append({
        'Model':     name,
        'Accuracy':  round(accuracy_score(y_test, yp)  * 100, 2),
        'Precision': round(precision_score(y_test, yp) * 100, 2),
        'Recall':    round(recall_score(y_test, yp)    * 100, 2),
        'F1 Score':  round(f1_score(y_test, yp)        * 100, 2),
        'ROC AUC':   round(roc_auc_score(y_test, ypr)  * 100, 2),
    })

metrics_df  = pd.DataFrame(rows).set_index('Model')
METRIC_COLS = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC']
model_names = list(metrics_df.index)
file_ids = {
    'Logistic Regression': 'logistic_regression',
    'Random Forest':       'random_forest',
    'SVM':                 'svm',
    'Voting Classifier':   'voting_classifier',
}

print("=" * 65)
print("  METRICS TABLE  (all values in %,  evaluated on TEST set only)")
print("=" * 65)
print(metrics_df.to_string())
print()

for name in model_names:
    print(f"  ── {name} ──")
    print(classification_report(y_test, preds_dict[name],
                                target_names=['Fail (0)', 'Pass (1)'], digits=4))

# ══════════════════════════════════════════════════════════════════════════════
# GRAPH 1 — All Models: Grouped Metrics Bar Chart
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(15, 7))
fig.patch.set_facecolor('#F8F9FA')
ax.set_facecolor('#F4F6F8')

x     = np.arange(len(METRIC_COLS))
width = 0.19

for i, mname in enumerate(model_names):
    vals = [metrics_df.loc[mname, m] for m in METRIC_COLS]
    bars = ax.bar(x + (i - 1.5) * width, vals, width,
                  label=mname, color=COLORS[mname],
                  edgecolor='white', linewidth=0.8, alpha=0.92, zorder=3)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                f'{v:.1f}', ha='center', va='bottom',
                fontsize=7.5, fontweight='bold', color='#333')

ax.set_xticks(x)
ax.set_xticklabels(METRIC_COLS, fontsize=12, fontweight='bold')
ax.set_ylim(40, 112)
ax.set_ylabel('Score (%)', fontsize=12)
ax.set_title('All Models – Performance Metrics Comparison\n'
             'Logistic Regression | Random Forest | SVM | Voting Classifier',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=10, loc='lower right', framealpha=0.9)
ax.grid(axis='y', alpha=0.35, zorder=0)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig(out('graph1_all_models_comparison.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✔  Graph 1  — All Models Comparison")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPH 2 — ROC Curves: All Models
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 7))
fig.patch.set_facecolor('#F8F9FA'); ax.set_facecolor('#F4F6F8')
ax.plot([0, 1], [0, 1], 'k--', lw=1.2, alpha=0.4, label='Random (AUC = 50%)')

for name in model_names:
    fpr, tpr, _ = roc_curve(y_test, proba_dict[name])
    a = metrics_df.loc[name, 'ROC AUC']
    ax.plot(fpr, tpr, label=f'{name}  (AUC = {a:.1f}%)',
            color=COLORS[name], lw=2.3)

ax.set_xlabel('False Positive Rate', fontsize=12)
ax.set_ylabel('True Positive Rate', fontsize=12)
ax.set_title('ROC Curves – All Models', fontsize=14, fontweight='bold')
ax.legend(fontsize=10, loc='lower right', framealpha=0.9)
ax.grid(alpha=0.3); ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig(out('graph2_roc_curves_all.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✔  Graph 2  — ROC Curves All Models")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPHS 3–6 — Individual Model 3-Panel Reports
# ══════════════════════════════════════════════════════════════════════════════
for idx, (name, model) in enumerate(models.items(), start=3):
    clr = COLORS[name]
    yp  = preds_dict[name]
    ypr = proba_dict[name]
    cm  = confusion_matrix(y_test, yp)
    cm_n = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    fpr, tpr, _ = roc_curve(y_test, ypr)
    auc_v = metrics_df.loc[name, 'ROC AUC']

    fig = plt.figure(figsize=(17, 5.5))
    fig.patch.set_facecolor('#F8F9FA')
    fig.suptitle(f'{name}  –  Detailed Performance Report',
                 fontsize=15, fontweight='bold', x=0.5, ha='center')
    gs = fig.add_gridspec(1, 3, wspace=0.40,
                          left=0.06, right=0.97, top=0.84, bottom=0.13)

    # Panel A: Confusion Matrix
    ax1 = fig.add_subplot(gs[0]); ax1.set_facecolor('#F4F6F8')
    cpal = sns.light_palette(clr, as_cmap=True)
    sns.heatmap(cm_n, annot=False, ax=ax1, cmap=cpal, cbar=False,
                linewidths=2, linecolor='white',
                xticklabels=['Fail (0)', 'Pass (1)'],
                yticklabels=['Fail (0)', 'Pass (1)'])
    for i in range(2):
        for j in range(2):
            ax1.text(j + 0.5, i + 0.5, f'{cm[i,j]}\n({cm_n[i,j]*100:.1f}%)',
                     ha='center', va='center', fontsize=13, fontweight='bold',
                     color='white' if cm_n[i, j] > 0.55 else '#333')
    ax1.set_xlabel('Predicted', fontsize=11, labelpad=7)
    ax1.set_ylabel('Actual',    fontsize=11, labelpad=7)
    ax1.set_title('Confusion Matrix', fontsize=12, fontweight='bold')

    # Panel B: Metrics Bar
    ax2 = fig.add_subplot(gs[1]); ax2.set_facecolor('#F4F6F8')
    vals = [metrics_df.loc[name, m] for m in METRIC_COLS]
    pal  = sns.light_palette(clr, n_colors=8)[3:]
    bars = ax2.bar(METRIC_COLS, vals,
                   color=[pal[i] for i in range(len(METRIC_COLS))],
                   edgecolor='white', linewidth=0.8, zorder=3)
    for bar, v in zip(bars, vals):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f'{v:.1f}%', ha='center', va='bottom',
                 fontsize=10, fontweight='bold', color='#333')
    ax2.set_ylim(40, 113); ax2.set_ylabel('Score (%)', fontsize=11)
    ax2.set_title('Metrics Overview', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='x', labelsize=9.5)
    ax2.grid(axis='y', alpha=0.35, zorder=0)
    ax2.spines[['top', 'right']].set_visible(False)

    # Panel C: ROC Curve
    ax3 = fig.add_subplot(gs[2]); ax3.set_facecolor('#F4F6F8')
    ax3.plot([0, 1], [0, 1], 'k--', lw=1.2, alpha=0.4)
    ax3.fill_between(fpr, tpr, alpha=0.15, color=clr)
    ax3.plot(fpr, tpr, color=clr, lw=2.6, label=f'AUC = {auc_v:.1f}%')
    ax3.set_xlabel('False Positive Rate', fontsize=11, labelpad=6)
    ax3.set_ylabel('True Positive Rate',  fontsize=11, labelpad=6)
    ax3.set_title('ROC Curve', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=11, loc='lower right', framealpha=0.9)
    ax3.grid(alpha=0.3); ax3.spines[['top', 'right']].set_visible(False)

    plt.savefig(out(f'graph{idx}_{file_ids[name]}.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✔  Graph {idx}  — {name}")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPH 7 — Predicted Probability Distribution (All Models, 2×2)
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.patch.set_facecolor('#F8F9FA'); axes = axes.flatten()

for i, name in enumerate(model_names):
    ax  = axes[i]; ax.set_facecolor('#F4F6F8')
    ypr = proba_dict[name]
    lab = pd.Series(y_test.values).map({0: 'Fail', 1: 'Pass'})
    for lbl, col in RESULT_PAL.items():
        mask = lab == lbl
        ax.hist(ypr[mask], bins=22, alpha=0.72, color=col,
                label=f'Actual {lbl} (n={mask.sum()})', edgecolor='white')
    ax.axvline(0.5, color='#2C3E50', ls='--', lw=1.8, label='Threshold = 0.5')
    ax.set_xlabel('Predicted Probability of Pass', fontsize=10)
    ax.set_ylabel('Count', fontsize=10)
    ax.set_title(name, fontsize=12, fontweight='bold', color=COLORS[name])
    ax.legend(fontsize=8.5); ax.grid(alpha=0.25)
    ax.spines[['top', 'right']].set_visible(False)

fig.suptitle('Predicted Probability Distribution — All Models',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(out('graph7_probability_distributions.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✔  Graph 7  — Probability Distributions")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPH 8 — Feature Importance: MDI + Permutation (Random Forest)
# ══════════════════════════════════════════════════════════════════════════════
rf_clf  = rf_pipe.named_steps['clf']
mdi     = rf_clf.feature_importances_
X_te_sc = rf_pipe.named_steps['scaler'].transform(X_test)
perm    = permutation_importance(rf_clf, X_te_sc, y_test,
                                 n_repeats=30, random_state=42)

feat_labels = [f.replace('_', ' ').title() for f in FEATURES]
mdi_df  = pd.DataFrame({'Feature': feat_labels, 'MDI': mdi}).sort_values('MDI')
perm_df = pd.DataFrame({'Feature': feat_labels,
                        'Perm': perm.importances_mean,
                        'Std':  perm.importances_std}).sort_values('Perm')

fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor('#F8F9FA')

pal_mdi = sns.light_palette(COLORS['Random Forest'], n_colors=len(mdi_df) + 3)[3:]
ax_l.set_facecolor('#F4F6F8')
bars = ax_l.barh(mdi_df['Feature'], mdi_df['MDI'], color=pal_mdi,
                 edgecolor='white', height=0.55)
for bar, v in zip(bars, mdi_df['MDI']):
    ax_l.text(v + 0.005, bar.get_y() + bar.get_height() / 2,
              f'{v:.4f}', va='center', fontsize=10, fontweight='bold')
ax_l.set_xlabel('Mean Decrease in Impurity', fontsize=11)
ax_l.set_title('Feature Importance (MDI)\nRandom Forest', fontsize=12, fontweight='bold')
ax_l.grid(axis='x', alpha=0.3); ax_l.spines[['top', 'right']].set_visible(False)

pc = [COLORS['Random Forest'] if v > 0 else COLORS['SVM'] for v in perm_df['Perm']]
ax_r.set_facecolor('#F4F6F8')
ax_r.barh(perm_df['Feature'], perm_df['Perm'], xerr=perm_df['Std'],
          color=pc, edgecolor='white', capsize=4, height=0.55)
ax_r.axvline(0, color='black', lw=1, ls='--', alpha=0.5)
ax_r.set_xlabel('Mean Accuracy Drop when Shuffled', fontsize=11)
ax_r.set_title('Permutation Feature Importance\n(Leakage-Free — Test Set)',
               fontsize=12, fontweight='bold')
ax_r.grid(axis='x', alpha=0.3); ax_r.spines[['top', 'right']].set_visible(False)

plt.tight_layout()
plt.savefig(out('graph8_feature_importance.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✔  Graph 8  — Feature Importance")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPH 9 — Correlation Heatmap (Training Data Only)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 6)); fig.patch.set_facecolor('#F8F9FA')
corr = train_df[FEATURES + [TARGET]].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
            center=0, linewidths=0.7, ax=ax, annot_kws={'size': 10},
            square=True, cbar_kws={'shrink': 0.8})
ax.set_title('Feature Correlation Heatmap — Training Data Only',
             fontsize=13, fontweight='bold', pad=14)
ax.tick_params(axis='x', rotation=20, labelsize=9)
ax.tick_params(axis='y', rotation=0,  labelsize=9)
plt.tight_layout()
plt.savefig(out('graph9_correlation_heatmap.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✔  Graph 9  — Correlation Heatmap")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPH 10 — Violin: Feature Distributions by Result
# ══════════════════════════════════════════════════════════════════════════════
train_plot = train_df.copy()
train_plot['Result'] = train_plot[TARGET].map({1: 'Pass', 0: 'Fail'})

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.patch.set_facecolor('#F8F9FA'); axes = axes.flatten()

for i, feat in enumerate(FEATURES):
    ax = axes[i]; ax.set_facecolor('#F4F6F8')
    sns.violinplot(data=train_plot, x='Result', y=feat,
                   palette=RESULT_PAL, ax=ax, inner='box', cut=0)
    ax.set_title(feat.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    ax.set_xlabel(''); ax.grid(axis='y', alpha=0.3)
    ax.spines[['top', 'right']].set_visible(False)

fig.suptitle('Feature Distributions by Result — Training Data',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(out('graph10_violin_distributions.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✔  Graph 10 — Violin Distributions")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPH 11 — Radar / Spider Chart
# ══════════════════════════════════════════════════════════════════════════════
N      = len(METRIC_COLS)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
fig.patch.set_facecolor('#F8F9FA'); ax.set_facecolor('#F4F6F8')
ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
ax.set_thetagrids(np.degrees(angles[:-1]), METRIC_COLS, fontsize=11.5, fontweight='bold')

for name in model_names:
    vals = [metrics_df.loc[name, m] for m in METRIC_COLS] + \
           [metrics_df.loc[name, METRIC_COLS[0]]]
    ax.plot(angles, vals, lw=2.3, color=COLORS[name], label=name)
    ax.fill(angles, vals, alpha=0.09, color=COLORS[name])

ax.set_ylim(40, 105)
ax.set_yticks([50, 60, 70, 80, 90, 100])
ax.set_yticklabels(['50', '60', '70', '80', '90', '100'], fontsize=8.5, color='#666')
ax.set_title('Radar Chart — Model Comparison Across All Metrics',
             fontsize=13, fontweight='bold', pad=22)
ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.12), fontsize=10.5)
plt.tight_layout()
plt.savefig(out('graph11_radar_chart.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✔  Graph 11 — Radar Chart")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPH 12 — Actual vs Predicted (All Models, side by side)
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 4, figsize=(16, 5), sharey=True)
fig.patch.set_facecolor('#F8F9FA')

for i, name in enumerate(model_names):
    ax  = axes[i]; ax.set_facecolor('#F4F6F8')
    act = pd.Series(y_test.values).map({0: 'Fail', 1: 'Pass'}).value_counts().reindex(['Fail', 'Pass'])
    pre = pd.Series(preds_dict[name]).map({0: 'Fail', 1: 'Pass'}).value_counts().reindex(['Fail', 'Pass'])
    xp  = np.arange(2)
    b1  = ax.bar(xp - 0.2, act.values, 0.38, label='Actual',
                 color='#4A90D9', edgecolor='white', alpha=0.9)
    b2  = ax.bar(xp + 0.2, pre.values, 0.38, label='Predicted',
                 color=COLORS[name], edgecolor='white', alpha=0.9)
    ax.set_xticks(xp); ax.set_xticklabels(['Fail', 'Pass'], fontsize=11)
    ax.set_title(name, fontsize=11, fontweight='bold', color=COLORS[name])
    ax.grid(axis='y', alpha=0.3); ax.spines[['top', 'right']].set_visible(False)
    if i == 0:
        ax.set_ylabel('Count', fontsize=11)
        ax.legend(fontsize=9, loc='upper right')
    for container in [b1, b2]:
        ax.bar_label(container, fontsize=9, fontweight='bold', padding=2)

fig.suptitle('Actual vs Predicted Results — All Models', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(out('graph12_actual_vs_predicted.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✔  Graph 12 — Actual vs Predicted")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPH 13 — Precision-Recall Curves (All Models)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 6)); fig.patch.set_facecolor('#F8F9FA')
ax.set_facecolor('#F4F6F8')
base = (y_test == 1).sum() / len(y_test)
ax.axhline(base, color='grey', ls='--', lw=1.5, alpha=0.6,
           label=f'Baseline = {base:.2f}')

for name in model_names:
    prec_c, rec_c, _ = precision_recall_curve(y_test, proba_dict[name])
    pr_a = auc(rec_c, prec_c)
    ax.plot(rec_c, prec_c, lw=2.2, color=COLORS[name],
            label=f'{name}  (PR-AUC={pr_a:.3f})')

ax.set_xlabel('Recall', fontsize=12); ax.set_ylabel('Precision', fontsize=12)
ax.set_title('Precision-Recall Curves — All Models', fontsize=14, fontweight='bold')
ax.legend(fontsize=9.5, loc='lower left', framealpha=0.9)
ax.grid(alpha=0.3); ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig(out('graph13_precision_recall_curves.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✔  Graph 13 — Precision-Recall Curves")

# ══════════════════════════════════════════════════════════════════════════════
# GRAPH 14 — Scatter: Social Media vs Attendance (Test Set, Actual Labels)
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 4, figsize=(18, 5)); fig.patch.set_facecolor('#F8F9FA')

for i, name in enumerate(model_names):
    ax = axes[i]; ax.set_facecolor('#F4F6F8')
    for lab, col, mk in [(0, '#E74C3C', 'x'), (1, '#2ECC71', 'o')]:
        mask = y_test.values == lab
        ax.scatter(test_df['social_media_hours'].values[mask],
                   test_df['attendance_percentage'].values[mask],
                   c=col, marker=mk, alpha=0.55, s=45, linewidths=0.8,
                   label='Fail' if lab == 0 else 'Pass')
    acc_v = metrics_df.loc[name, 'Accuracy']
    ax.set_title(f'{name}\n(Acc={acc_v:.1f}%)', fontsize=10.5,
                 fontweight='bold', color=COLORS[name])
    ax.set_xlabel('Social Media Hours', fontsize=9)
    if i == 0:
        ax.set_ylabel('Attendance %', fontsize=9)
        ax.legend(fontsize=8.5)
    ax.grid(alpha=0.25); ax.spines[['top', 'right']].set_visible(False)

fig.suptitle('Social Media Hours vs Attendance % — Test Set (Actual Labels)',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(out('graph14_scatter_social_attendance.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✔  Graph 14 — Scatter Plot")

# ══════════════════════════════════════════════════════════════════════════════
# PREDICT A NEW STUDENT
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("              PREDICT A NEW STUDENT")
print("=" * 65)

new_student = pd.DataFrame([{
    'social_media_hours':            2.5,
    'attendance_percentage':         80.0,
    'sleep_hours':                   6.5,
    'extracurricular_participation':  1,
}])

print(f"\n  Social Media Hours   : {new_student['social_media_hours'].values[0]}")
print(f"  Attendance %         : {new_student['attendance_percentage'].values[0]}")
print(f"  Sleep Hours          : {new_student['sleep_hours'].values[0]}")
print(f"  Extracurricular      : {'Yes' if new_student['extracurricular_participation'].values[0] else 'No'}")
print()

for name, model in models.items():
    pred = model.predict(new_student)[0]
    prob = model.predict_proba(new_student)[0]
    icon = '✅ PASS' if pred == 1 else '❌ FAIL'
    print(f"  {name:<22} → {icon}  "
          f"(Pass: {prob[1]*100:.1f}%  |  Fail: {prob[0]*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  FINAL METRICS SUMMARY  (% — evaluated on held-out TEST set)")
print("=" * 65)
print(metrics_df.to_string())
print("=" * 65)
print("\n  Leakage Prevention Applied:")
print("  ①  exam_score EXCLUDED  (threshold 30 = deterministic target leak)")
print("  ②  student_id EXCLUDED  (non-predictive row identifier)")
print("  ③  StandardScaler inside Pipeline — fitted on TRAIN data only")
print("  ④  VotingClassifier uses SOFT voting (probability averaging)")
print(f"\n  Features : {FEATURES}")
print(f"\n✅  All 14 graphs saved to → {OUT_DIR}")