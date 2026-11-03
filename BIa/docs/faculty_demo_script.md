# Faculty Demo Script

## Opening statement

> This project is **Service Recovery Intelligence**, a Business Intelligence and
> Analytics decision-support system. It helps operations teams identify orders
> that deserve attention before a late delivery or poor customer experience is
> confirmed. It combines historical reporting, predictive risk signals,
> transparent prioritisation, and model governance in one workspace.

## Five-minute flow

### 1. Executive Overview — 60 seconds

Point out:

- 96,476 eligible orders analysed;
- confirmed historical delay and dissatisfaction rates;
- the difference between observed outcomes and estimated risk;
- the Detect → Prioritise → Govern operating workflow.

Say: “This is not only a prediction page. It is a management decision-support
view that connects evidence, prioritisation, and responsible use.”

### 2. Delivery Reliability — 45 seconds

Change total item price or freight value, then submit. Explain that the output is
the estimated likelihood of missing the expected delivery commitment. Do not call
it a confirmed result.

### 3. Customer Experience — 45 seconds

Submit a scenario using order information available before a review. Explain
that a high score indicates a reason to consider service recovery or review—not
that the customer has already complained.

### 4. Orders Needing Attention — 90 seconds

Increase the sample size and show:

- the number of orders carrying both risk signals;
- the category distribution;
- the searchable worklist;
- the recommended investigation action.

Explain that the table is a human review queue, not an automated action engine.

### 5. Model Governance — 60 seconds

Show the chronological train, validation, and test comparison, then show the
candidate model comparison. Explain that Logistic Regression and Random Forest
were compared using validation ROC-AUC and that the test split was held back for
final reporting. State the
limitation directly:

> The customer-experience model is suitable for a controlled pilot based on its
> held-out discrimination, while the delivery model is pilot-only and requires
> additional operational features before automated use.

## Closing statement

> The contribution is the integrated decision process: historical BI describes
> what happened, predictive analytics estimates where attention may be needed,
> multi-criteria policy ranks the worklist, and governance prevents the model
> from being presented as more certain than the evidence supports.
