import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, confusion_matrix, classification_report,
    roc_curve, auc, precision_recall_curve
)
from sklearn.inspection import permutation_importance
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
TRAIN_PATH = "training_data.xlsx"
TEST_PATH  = "testing_data.xlsx"
FEATURES   = [
    'study_hours_per_day',
    'social_media_hours',
    'attendance_percentage',
    'sleep_hours',
    'extracurricular_participation',
    'exam_score'
]
TARGET = 'result'

PALETTE = {'Pass': '#2ECC71', 'Fail': '#E74C3C'}
sns.set_theme(style='whitegrid', font_scale=1.1)

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
print("=" * 55)
print("       STUDENT RESULT PREDICTION SYSTEM")
print("          (Logistic Regression Model)")
print("=" * 55)

train_df = pd.read_excel(TRAIN_PATH)
test_df  = pd.read_excel(TEST_PATH)

X_train = train_df[FEATURES]
y_train = train_df[TARGET]
X_test  = test_df[FEATURES]
y_test  = test_df[TARGET]

print(f"\n Training samples : {len(X_train)}")
print(f" Testing  samples : {len(X_test)}")
print(f" Features         : {len(FEATURES)}")

# ─────────────────────────────────────────────
# 2. SCALE FEATURES
# ─────────────────────────────────────────────
scaler  = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ─────────────────────────────────────────────
# 3. TRAIN MODEL
# ─────────────────────────────────────────────
model = LogisticRegression(max_iter=1000, random_state=42, solver='lbfgs')
model.fit(X_train_scaled, y_train)

y_pred       = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

accuracy  = accuracy_score(y_test, y_pred)
cm        = confusion_matrix(y_test, y_pred)
report    = classification_report(y_test, y_pred, target_names=['Fail', 'Pass'])
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc   = auc(fpr, tpr)

print(f"\n {'─'*40}")
print(f"  Model Accuracy  : {accuracy * 100:.2f}%")
print(f"  ROC-AUC Score   : {roc_auc:.4f}")
print(f" {'─'*40}")
print(f"\n Classification Report:\n{report}")

# ─────────────────────────────────────────────
# GRAPH 1 — Confusion Matrix
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(
    cm, annot=True, fmt='d', cmap='Blues',
    xticklabels=['Fail', 'Pass'],
    yticklabels=['Fail', 'Pass'],
    linewidths=1, linecolor='white',
    annot_kws={'size': 16, 'weight': 'bold'}, ax=ax
)
ax.set_xlabel('Predicted Label', fontsize=13, labelpad=10)
ax.set_ylabel('True Label', fontsize=13, labelpad=10)
ax.set_title('Confusion Matrix', fontsize=15, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('graph1_confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.show()
print(" Graph 1 saved: graph1_confusion_matrix.png")

# ─────────────────────────────────────────────
# GRAPH 2 — ROC Curve
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(fpr, tpr, color='#2980B9', lw=2.5, label=f'ROC Curve (AUC = {roc_auc:.3f})')
ax.plot([0, 1], [0, 1], color='#7F8C8D', lw=1.5, linestyle='--', label='Random Classifier')
ax.fill_between(fpr, tpr, alpha=0.1, color='#2980B9')
ax.set_xlim([0.0, 1.0])
ax.set_ylim([0.0, 1.05])
ax.set_xlabel('False Positive Rate', fontsize=13)
ax.set_ylabel('True Positive Rate', fontsize=13)
ax.set_title('ROC Curve — Logistic Regression', fontsize=15, fontweight='bold')
ax.legend(loc='lower right', fontsize=11)
plt.tight_layout()
plt.savefig('graph2_roc_curve.png', dpi=150, bbox_inches='tight')
plt.show()
print(" Graph 2 saved: graph2_roc_curve.png")

# ─────────────────────────────────────────────
# GRAPH 3 — Feature Importance (Coefficients)
# ─────────────────────────────────────────────
coef_df = pd.DataFrame({
    'Feature': FEATURES,
    'Coefficient': model.coef_[0]
}).sort_values('Coefficient', ascending=True)

colors = ['#E74C3C' if c < 0 else '#2ECC71' for c in coef_df['Coefficient']]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(coef_df['Feature'], coef_df['Coefficient'], color=colors, edgecolor='white', height=0.6)
ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
ax.set_xlabel('Coefficient Value', fontsize=13)
ax.set_title('Feature Importance (Logistic Regression Coefficients)', fontsize=14, fontweight='bold')
for bar, val in zip(bars, coef_df['Coefficient']):
    ax.text(val + (0.02 if val >= 0 else -0.02), bar.get_y() + bar.get_height() / 2,
            f'{val:.3f}', va='center', ha='left' if val >= 0 else 'right', fontsize=10)
plt.tight_layout()
plt.savefig('graph3_feature_importance.png', dpi=150, bbox_inches='tight')
plt.show()
print(" Graph 3 saved: graph3_feature_importance.png")

# ─────────────────────────────────────────────
# GRAPH 4 — Predicted Probability Distribution
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
labels = ['Fail' if y == 0 else 'Pass' for y in y_test]
prob_df = pd.DataFrame({'Probability': y_pred_proba, 'Actual': labels})

for label, color in PALETTE.items():
    subset = prob_df[prob_df['Actual'] == label]['Probability']
    ax.hist(subset, bins=25, alpha=0.7, color=color, label=label, edgecolor='white')

ax.axvline(0.5, color='black', linestyle='--', lw=1.5, label='Decision Threshold (0.5)')
ax.set_xlabel('Predicted Probability of Pass', fontsize=13)
ax.set_ylabel('Count', fontsize=13)
ax.set_title('Predicted Probability Distribution', fontsize=15, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig('graph4_probability_distribution.png', dpi=150, bbox_inches='tight')
plt.show()
print(" Graph 4 saved: graph4_probability_distribution.png")

# ─────────────────────────────────────────────
# GRAPH 5 — Precision-Recall Curve
# ─────────────────────────────────────────────
precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
pr_auc = auc(recall, precision)

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(recall, precision, color='#8E44AD', lw=2.5, label=f'PR Curve (AUC = {pr_auc:.3f})')
ax.fill_between(recall, precision, alpha=0.1, color='#8E44AD')
ax.set_xlabel('Recall', fontsize=13)
ax.set_ylabel('Precision', fontsize=13)
ax.set_title('Precision-Recall Curve', fontsize=15, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig('graph5_precision_recall.png', dpi=150, bbox_inches='tight')
plt.show()
print(" Graph 5 saved: graph5_precision_recall.png")

# ─────────────────────────────────────────────
# GRAPH 6 — Correlation Heatmap
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
corr = train_df[FEATURES + [TARGET]].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
    center=0, linewidths=0.5, ax=ax,
    annot_kws={'size': 9}
)
ax.set_title('Feature Correlation Heatmap', fontsize=15, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('graph6_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
print(" Graph 6 saved: graph6_correlation_heatmap.png")

# ─────────────────────────────────────────────
# GRAPH 7 — Feature Distributions by Result
# ─────────────────────────────────────────────
train_plot = train_df.copy()
train_plot['Result'] = train_plot[TARGET].map({1: 'Pass', 0: 'Fail'})

fig, axes = plt.subplots(2, 3, figsize=(15, 9))
axes = axes.flatten()

for i, feat in enumerate(FEATURES):
    sns.violinplot(
        data=train_plot, x='Result', y=feat,
        palette=PALETTE, ax=axes[i], inner='box', cut=0
    )
    axes[i].set_title(feat.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    axes[i].set_xlabel('')
    axes[i].set_ylabel('')

fig.suptitle('Feature Distributions by Result (Pass / Fail)', fontsize=15, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('graph7_feature_distributions.png', dpi=150, bbox_inches='tight')
plt.show()
print(" Graph 7 saved: graph7_feature_distributions.png")

# ─────────────────────────────────────────────
# GRAPH 8 — Actual vs Predicted Bar Chart
# ─────────────────────────────────────────────
actual_counts    = pd.Series(y_test).map({1: 'Pass', 0: 'Fail'}).value_counts()
predicted_counts = pd.Series(y_pred).map({1: 'Pass', 0: 'Fail'}).value_counts()
compare_df = pd.DataFrame({'Actual': actual_counts, 'Predicted': predicted_counts})

fig, ax = plt.subplots(figsize=(7, 5))
compare_df.plot(kind='bar', ax=ax, color=['#2980B9', '#E67E22'], edgecolor='white', width=0.6)
ax.set_xticklabels(['Fail', 'Pass'], rotation=0, fontsize=12)
ax.set_ylabel('Count', fontsize=13)
ax.set_title('Actual vs Predicted Results', fontsize=15, fontweight='bold')
ax.legend(fontsize=11)
for container in ax.containers:
    ax.bar_label(container, fontsize=11, fontweight='bold', padding=3)
plt.tight_layout()
plt.savefig('graph8_actual_vs_predicted.png', dpi=150, bbox_inches='tight')
plt.show()
print(" Graph 8 saved: graph8_actual_vs_predicted.png")

# ─────────────────────────────────────────────
# PREDICT NEW STUDENT
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("         PREDICT A NEW STUDENT")
print("=" * 55)

new_student = pd.DataFrame([{
    'study_hours_per_day':         5.0,
    'social_media_hours':          2.0,
    'attendance_percentage':       85.0,
    'sleep_hours':                 7.0,
    'extracurricular_participation': 1,
    'exam_score':                  72.0
}])

new_scaled   = scaler.transform(new_student)
prediction   = model.predict(new_scaled)[0]
probability  = model.predict_proba(new_scaled)[0]

print(f"\n  Study Hours/Day          : {new_student['study_hours_per_day'].values[0]}")
print(f"  Social Media Hours       : {new_student['social_media_hours'].values[0]}")
print(f"  Attendance %             : {new_student['attendance_percentage'].values[0]}")
print(f"  Sleep Hours              : {new_student['sleep_hours'].values[0]}")
print(f"  Extracurricular          : {'Yes' if new_student['extracurricular_participation'].values[0] else 'No'}")
print(f"  Exam Score               : {new_student['exam_score'].values[0]}")
print(f"\n  ► Prediction             : {'✅ PASS' if prediction == 1 else '❌ FAIL'}")
print(f"  ► Pass Probability       : {probability[1] * 100:.2f}%")
print(f"  ► Fail Probability       : {probability[0] * 100:.2f}%")
print("\n" + "=" * 55)
print(" All graphs saved successfully!")
print("=" * 55)