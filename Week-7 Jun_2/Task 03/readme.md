# Task 03: Encoding Strategy Comparison

This task compares three categorical encoding approaches on the airline passenger satisfaction dataset using the same Logistic Regression model.

## Workflow

```text
Original Data
      |
Train-Test Split
      |
      +--------------------+--------------------+
      |                    |                    |
Label Encoding      One-Hot Encoding     Ordinal Encoding
      |                    |                    |
Scale                Scale                Scale
      |                    |                    |
Logistic Model       Logistic Model       Logistic Model
      |                    |                    |
      +--------------------+--------------------+
                           |
                    Compare Results
```

## Results

| Encoding | Accuracy | Training Time | Feature Count |
|---|---:|---:|---:|
| Label | 0.876116 | 0.275539 | 22 |
| One-Hot | 0.875192 | 0.353688 | 27 |
| Ordinal | 0.876116 | 0.214222 | 22 |

## Recommendation

I recommend using **Ordinal Encoding** because it gave the best overall result. It matched Label Encoding with the highest accuracy of **0.876116**, trained the fastest at **0.214222 seconds**, and used only **22 features**, while One-Hot Encoding was slower and slightly less accurate.
