# Week 4 (May 8) - Advanced ETL & Data Engineering

## Overview
This week focuses on building complete **ETL (Extract, Transform, Load) pipelines** using Pandas and databases. All tasks emphasize data cleaning, API integration, and production-ready code patterns with proper error handling and logging.

---

## Files & Deliverables

### Task 01 - Clean Messy CSV
**File:** `Task_1.ipynb`

**Goal:** Practice comprehensive data cleaning techniques on messy student data.

**Deliverables:**
- `messy_students_data.csv` - Original messy data with intentional problems
- `clean_students_data.csv` - Cleaned output data
- Grade column added: A (≥90), B (≥75), C (≥50), F (<50)

---

### Task 02 - API → Clean → Save ✅
**File:** `Task_2.ipynb`

**Goal:** Build a complete ETL pipeline from real API data.

**Deliverables:**
- `clean_posts.csv` - Filtered posts with 4+ words
- Statistics: posts fetched, posts after filter, top 3 users

---

### Task 03 - Multi-Source ETL ✅
**File:** `Task_3.ipynb`

**Goal:** Merge data from two API sources and store in MySQL.

**Deliverables:**
- `merged_data.csv` - Combined users + posts data
- MySQL database storage (`etl_db.users`)
- Top 3 most active users printed

**Features:**
- Extract from 2 endpoints: `/users` and `/posts`
- Use `pd.json_normalize()` for nested data (address.city)
- Merge on user id with post count aggregation
- Data cleaning: lowercase emails, strip whitespace
- MySQL connector for database storage
- Results: user profiles with post counts

---

### Task 04 - Transform & Enrich ✅
**File:** `Task_4.ipynb`
**Output:** `enriched_students.csv`

**Goal:** Advanced column engineering with Pandas.

**Deliverables:**
- `enriched_students.csv` - Student data with 5 new columns
- GroupBy summary printed
- Top 5 ranked students displayed
- **Bonus:** Pivot table (grade vs subject vs average score)

**Enriched Columns:**
- `grade` - Letter grades (A/B/C/D/F)
- `passed` - Boolean (score ≥ 50)
- `score_category` - High/Medium/Low
- `rank` - Rank by score (1 = highest)

**Screenshots:**

![Task 4 - Enriched Data](outputs/task4.png)

![Task 4 - Pivot Table](outputs/task4_1.png)

---

### Task 05 - Full ETL System (Capstone) ✅
**File:** `Task_5.ipynb`
**Output:** `etl_data_run1.csv`, `etl_data_run2.csv`

**Goal:** Production-ready ETL pipeline with reusable functions.

**Deliverables:**
- `etl_data_run1.csv` - First pipeline execution
- `etl_data_run2.csv` - Second execution (duplicate-free)
- Full logging with timestamps

**Architecture:**
- `extract()` - Fetch from API with error handling
- `transform()` - Clean and enrich data
- `load()` - Save to CSV and MySQL

**Features:**
- Reusable modular functions
- Comprehensive logging at each step
- Error handling for API calls
- 2 enriched columns: word_count, body_length
- MySQL integration with duplicate prevention
- **Bonus:** Run pipeline twice without creating duplicates

**Screenshots:**

![Task 5 - Pipeline Run 1](outputs/task5.png)

![Task 5 - Pipeline Run 2 (Duplicate Prevention)](outputs/task5_1.png)

![Task 5 - Final Summary](outputs/task5_2.png)

---


*Completed: May 11, 2026*
