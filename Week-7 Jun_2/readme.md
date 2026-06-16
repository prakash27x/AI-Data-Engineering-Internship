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

## Task 04: Scaler Sensitivity Experiment

This task studies how feature scaling affects distance-based machine learning models. The Breast Cancer Prediction dataset was used because it contains numeric features with different scales. KNN with `k=5` and SVM were trained on raw data, then retrained after applying `StandardScaler`, `MinMaxScaler`, and `RobustScaler`.

### Workflow

```text
                     Breast Cancer Dataset
                              |
                        Train-Test Split
                              |
      +----------------+----------------+----------------+
      |                |                |                |                
     Raw        StandardScaler    MinMaxScaler     RobustScaler
      |                |                |                |
   KNN + SVM       KNN + SVM       KNN + SVM       KNN + SVM
      |                |                |                |
      +----------------+----------------+----------------+
                              |
                        Compare Accuracy
                              |
                        Add 5 Outlier Rows
                              |
                        Re-run Scaled Models
                              |
                        Check Robust Scaler
```

### Results Before Outliers

| Model | Scaler | Accuracy |
|---|---|---:|
| KNN | Raw | 0.956140 |
| SVM | Raw | 0.947368 |
| KNN | StandardScaler | 0.947368 |
| SVM | StandardScaler | 0.982456 |
| KNN | MinMaxScaler | 0.964912 |
| SVM | MinMaxScaler | 0.973684 |
| KNN | RobustScaler | 0.956140 |
| SVM | RobustScaler | 0.964912 |

### Outlier Robustness

Five artificial outlier rows were added to the training data, then the scaled models were trained again.

| Model | Scaler | Before | After | Change |
|---|---|---:|---:|---:|
| KNN | StandardScaler | 0.947368 | 0.964912 | +1.75% |
| SVM | StandardScaler | 0.982456 | 0.956140 | -2.63% |
| KNN | MinMaxScaler | 0.964912 | 0.956140 | -0.88% |
| SVM | MinMaxScaler | 0.973684 | 0.956140 | -1.75% |
| KNN | RobustScaler | 0.956140 | 0.956140 | 0.00% |
| SVM | RobustScaler | 0.964912 | 0.973684 | +0.88% |

### Visualization

The results were visualized using a grouped bar chart with scaling methods on the x-axis and separate bars for KNN and SVM accuracy. The chart includes all 8 model-scaler combinations: Raw, StandardScaler, MinMaxScaler, and RobustScaler for both models.

![Task 04 grouped bar chart](Task%2004/task4_grouped_bar_chart.png)

### Conclusion

Scaling clearly affected KNN and SVM because both models depend on distances or margins in feature space. Before adding outliers, SVM with `StandardScaler` gave the highest accuracy. After adding outliers, `RobustScaler` showed the best stability because it uses the median and IQR instead of mean and standard deviation. In practical ML work, `StandardScaler` is a strong default for normally distributed data, while `RobustScaler` is a better choice when outliers are present.
