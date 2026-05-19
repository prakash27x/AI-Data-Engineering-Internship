# Week 5 - May 15

This folder contains the Week 5 EDA and visualization exercises completed on May 15. The work focuses on exploring existing internship datasets, analyzing distributions, comparing groups, and producing reusable charts and summary files.

## Tasks

### Task 1: EDA Checklist on Existing Data
Run a complete EDA checklist on one dataset built earlier in the internship. The task covers loading the data, checking shape and types, reviewing missing values, generating summary statistics, exploring categorical counts, and saving histogram and box plot outputs.

### Task 2: Distribution Deep Dive
Fetch weather data for multiple cities, store it in MySQL, and analyze temperature distributions in depth. The task includes histograms, box plots, KDE curves, and IQR-based outlier checks.

### Task 3: Correlation Analysis on Student Data
Create a synthetic student dataset and study the relationships between study time, sleep, attendance, and score. The task includes a correlation matrix, heatmap, scatter plots, and a cluster-style pairplot.

### Task 4: Full EDA Report
Build a complete EDA report on a real-world dataset. The task combines API data extraction, cleaning, summary statistics, visualizations, and written observations in comments or a text report.

## Outputs

All charts are generated inside the matching task subfolder so each notebook keeps its own images separate.

### Task 1
- [Task_1.ipynb](Task_1.ipynb)
- ![Total histogram](task_1/Total_histogram.png)
- ![Total boxplot](task_1/Total_boxplot.png)

### Task 2
- [Task_2.ipynb](Task_2.ipynb)
- ![Max temperature histogram](task_2/max_temp_histogram.png)
- ![Max temperature boxplot by city](task_2/max_temp_boxplot_by_city.png)
- ![Max temperature KDE by city](task_2/max_temp_kde_by_city.png)
- ![Rainfall by city](task_2/rainfall_by_city.png)

### Task 3
- [Task_3.ipynb](Task_3.ipynb)
- ![Study hours histogram](task_3/study_hours_histogram.png)
- ![Sleep hours histogram](task_3/sleep_hours_histogram.png)
- ![Attendance percentage histogram](task_3/attendance_pct_histogram.png)
- ![Score histogram](task_3/score_histogram.png)
- ![Study hours boxplot](task_3/study_hours_boxplot.png)
- ![Score boxplot](task_3/score_boxplot.png)
- ![Study vs score](task_3/study_vs_score.png)
- ![Attendance vs score](task_3/attendance_vs_score.png)
- ![Correlation heatmap](task_3/heatmap.png)
- ![Pairplot](task_3/pairplot.png)

### Task 4
- [Task_4.ipynb](Task_4.ipynb)
- ![Bar chart posts per user](task_4/bar_chart_posts_per_user.png)
- ![Body length boxplot](task_4/boxplot_body_length.png)
- ![Correlation heatmap](task_4/heatmap.png)
- ![Word count histogram](task_4/histogram_word_count.png)
- ![Pairplot](task_4/pairplot.png)
- ![Title vs body scatter](task_4/scatter_title_vs_body.png)

## Datasets

- [clean_posts.csv](clean_posts.csv)
- [clean_students_data.csv](clean_students_data.csv)
- [messy_students_data.csv](messy_students_data.csv)
- [students.csv](students.csv)

## Notes

- The folder is organized around notebooks and generated visuals.
- Task outputs are stored in the task subfolders to keep each analysis separate and easy to review.
- Task 4 images were regenerated so the plots in `task_4/` are now unique and no longer duplicated from Task 3.
