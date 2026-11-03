# Final Faculty Demonstration Checklist

## Launch

```powershell
python -m streamlit run BIa\app\app.py
```

The first two commands are only needed when rebuilding generated artifacts:

```powershell
python BIa\scripts\prepare_data.py
python BIa\scripts\train_models.py
```

## Page walkthrough

1. **Executive Overview:** introduce the business problem, show the four operating
   KPIs, explain the historical-versus-predicted distinction, and point out the
   Detect → Prioritise → Govern workflow.
2. **Delivery Reliability:** change one or two order inputs, submit the form, and
   explain that the result is an estimated late-delivery likelihood.
3. **Customer Experience:** submit a pre-review order scenario and explain the
   low-review likelihood as a service-recovery signal.
4. **Orders Needing Attention:** increase the sample size, show the risk-category
   chart, search the table, and explain the recommended investigation action.
5. **Model Governance:** compare train, validation, and chronological test metrics;
   explicitly state that the delivery model is pilot-only because its test ROC-AUC
   is weak, while the customer-experience model is suitable for a controlled pilot.

## Integrity checks

- No model retraining occurs when the app starts.
- Displayed metrics come from `BIa/models/metrics.json`.
- Displayed probabilities come from the saved Joblib pipelines.
- Risk categories are policy labels based on the two model probabilities; they
  are not presented as calibrated joint-event probabilities.
- The delivery model's weak held-out ROC-AUC is visible rather than hidden.
- Logistic Regression and Random Forest candidates are compared using validation
  ROC-AUC; the test set is reserved for final reporting.
- Raw data and generated model/processed-data artifacts remain ignored by Git.
- The application does not claim autonomous action: a human operations owner
  remains responsible for investigation and service recovery.

## Faculty questions to be ready for

- **Why this problem?** It converts late reactive service handling into a
  prioritised decision-support workflow.
- **Why not call this a guaranteed prediction?** The models estimate risk and
  are evaluated on chronological held-out data; they are not certainty engines.
- **Why is the delivery result weak?** The limitation is shown openly and the
  dashboard recommends pilot-only use rather than hiding the result.
- **What is the BI contribution?** KPI reporting, segmentation, interactive
  worklist, policy-based prioritisation, and model governance are presented
  together for a management decision.
