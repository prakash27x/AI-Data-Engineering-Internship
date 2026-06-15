# Week 7: Feature Preparation and Encoding

This week focuses on preparing raw data for machine learning through cleaning, imputation, encoding, scaling, feature engineering, and model comparison.

## Task 01: Full Feature Preparation Pipeline

In this task, a student score dataset was cleaned and prepared for modeling. The pipeline dropped the high-cardinality `Name` column, used `Total` as the target, cleaned dirty numeric score values, converted `Grade` into an ordinal `grade_level`, imputed missing numeric values with the median, imputed missing categorical values with the most frequent value, one-hot encoded `Gender`, scaled numeric features with `StandardScaler`, and performed an 80/20 train-test split.

## Task 02: Feature Engineering Challenge

This task used NYC Bike Share data to create new features from timestamps and trip information. Features such as `start_hour`, `day_of_week`, `is_weekend`, age-based interaction features, `log_duration`, and age groups were added. The engineered features improved Logistic Regression accuracy from **0.9833** to **0.9874**, giving an accuracy improvement of **0.0041**.

## Task 03: Encoding Strategy Comparison

This task compares three categorical encoding approaches on the airline passenger satisfaction dataset using the same Logistic Regression model.

### Workflow

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

### Results

| Encoding | Accuracy | Training Time | Feature Count |
|---|---:|---:|---:|
| Label | 0.876116 | 0.275539 | 22 |
| One-Hot | 0.875192 | 0.353688 | 27 |
| Ordinal | 0.876116 | 0.214222 | 22 |

### Recommendation

I recommend using **Ordinal Encoding** because it gave the best overall result. It matched Label Encoding with the highest accuracy of **0.876116**, trained the fastest at **0.214222 seconds**, and used only **22 features**, while One-Hot Encoding was slower and slightly less accurate.
