# Model Comparison: ⚠ SIMULATED DATA

Data: `interactions_train` (9,589 rows, 240 synthetic listeners, 43.0% yes).
Label: `memory_triggered`. 7 features. Missing popularity replaced with the average.
Validation: RapidMiner Cross Validation with **split on batch attribute** (batch = `user_id`). Each listener's rows are tested together on a model that never saw that listener (leave-one-listener-out).
The "±" is the standard deviation across listeners. The micro average pools all predictions.

Values copied from the AI Studio results screens (screenshots in results/screenshots).

| Model | AUC | Accuracy | Precision (yes) | Recall (yes) | F1 | Run date |
|---|---|---|---|---|---|---|
| Logistic Regression | 0.790 ± 0.081 | 71.87% ± 8.79% | 68.69% (micro) | 64.73% ± 25.25% (micro 63.65%) | 66.07% | 2026-09-17 |
| Random Forest (default settings) | 0.831 ± 0.073 | 74.08% ± 7.86% | 66.58% ± 16.76% (micro 66.72%) | 80.52% ± 10.81% (micro 79.35%) | 71.25% ± 11.26% (micro 72.49%) | 2026-09-17 |
| Gradient Boosted Trees (default settings) | 0.835 ± 0.073 | 73.77% ± 8.47% | 75.92% ± 16.50% (micro 76.08%) | 58.28% ± 14.98% (micro 56.96%) | 64.00% ± 11.81% (micro 65.14%) | 2026-09-17 |

Logistic Regression confusion matrix (all listeners pooled): TP 2,626 · FP 1,197 · FN 1,500 · TN 4,266.

Random Forest confusion matrix (pooled): TP 3,274 · FP 1,633 · FN 852 · TN 3,830.

Gradient Boosted Trees confusion matrix (pooled): TP 2,350 · FP 739 · FN 1,776 · TN 4,724.

Reference: always predicting "no" gives 57.0% accuracy.
Independent check (Python, scikit-learn logistic regression, 5 listener-grouped folds): accuracy 0.730, AUC 0.786.

## Final model: Random Forest (chosen 2026-09-17)
Reason: its AUC was tied with Gradient Boosted Trees (0.831 vs 0.835, well inside ±0.073), it had higher recall (80.5% vs 58.3%) which suits a reminiscence app, and it is simpler to explain.
Missing popularity is filled with a fixed value, 63.633 (the training average), so the holdout and demo data get the same treatment. Re-run cross-validation AUC: 0.831 (unchanged).

## Holdout test: 60 unseen synthetic listeners (U241–U300), ⚠ SIMULATED
- AI Studio Performance (2): **AUC 0.804** (displayed with positive class "no"; ROC AUC is identical for either class. Python check using confidence(yes): 0.804)
- Top-10 hit rate (`src/05_evaluate_ranking.py`): share of each listener's top 10 songs that were real "yes" answers, averaged over listeners:

| Ranking method | Top-10 hit rate |
|---|---|
| **RapidMiner Random Forest** | **74.2%** |
| Baseline formula | 63.2% |
| Random order | 40.2% |

Caveat: the labels were generated from rules related to these same features, so this shows the pipeline works and the model captures the simulated pattern. It is not real-world evidence.

## Demo-profile predictions (`data/processed/predictions_demo.csv`, 5 profiles × 9,840 songs)
**Finding:** when the Random Forest ranks *all* 9,840 songs on its own, 1–2 of the top 10 for some profiles are songs in the wrong language. For example, demo D1 (Malayalam) gets "The Ghost Of Al Capone" (English, popularity 19) at confidence 0.705, above many in-period Malayalam film songs at 0.685. Share of the top 10 matching the profile language: D1 80%, D2 90%, D3 80%, D4 100%, D5 100%.
**Likely cause:** in training, half of each listener's songs came from the baseline top 200, so the model saw few wrong-language, low-popularity songs in the age bump. Its guesses in that rarely seen region are unreliable (overfitting to a few examples). Many Malayalam songs also share identical feature values, so they tie at the same confidence.
**Decision for the app: a two-stage recommender.** (1) The baseline formula picks the top 200 candidates. (2) The RapidMiner Random Forest ranks those 200 by confidence(yes). This matches how the training data was collected and is a common design for recommenders. Result: 100% language match in the top 10 for all 5 demo profiles, with ages at release between 14 and 26.
