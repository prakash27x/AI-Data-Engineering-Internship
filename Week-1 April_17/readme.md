# Week 1 - April 17: Python Fundamentals

## Overview

This folder contains basic Python scripts covering fundamental programming concepts including user input, loops, functions, and file handling. These are introductory exercises designed to practice core Python skills.

**Date:** April 17, 2026

---

## 📋 Task List

| # | Task | File | Purpose |
|---|------|------|---------|
| 1 | Find Maximum Number | `max_number_finder.py` | Find the largest number from user input list |
| 2 | Multiplication Table | `mulplication-table_generator.py` | Generate multiplication table for a given number |
| 3 | File Word Count | `file_handling.py` | Read text file and count total words |

---

## Task 1: Find Maximum Number

### Description
Program that takes a list of numbers from user input and finds the maximum value using a custom function.

### File
`max_number_finder.py`

### How to Run
```bash
python max_number_finder.py
```

### Input Example
```
Enter a list of numbers separated by spaces: 45 23 89 12 67 34
```

### Output Example
```
The maximum number in the list is: 89
```

### Implementation Details
- Takes space-separated numbers as input
- Converts input strings to integers
- Uses a custom `find_max_number()` function
- Iterates through list to find maximum value
- Returns and prints the result

---

## Task 2: Multiplication Table Generator

### Description
Program that generates a multiplication table (1-10) for any user-provided number.

### File
`mulplication-table_generator.py`

### How to Run
```bash
python mulplication-table_generator.py
```

### Input Example
```
Enter any number: 7
```

### Output Example
```
Multiplication Table Generator
7 * 1 = 7
7 * 2 = 14
7 * 3 = 21
7 * 4 = 28
7 * 5 = 35
7 * 6 = 42
7 * 7 = 49
7 * 8 = 56
7 * 9 = 63
7 * 10 = 70
The End
```

### Implementation Details
- Takes single integer input
- Uses `for` loop with `range(1, 11)` to iterate 1-10
- Uses f-string formatting for output
- Generates standard multiplication table

---

## Task 3: File Word Count

### Description
Program that reads a text file and counts the total number of words in it.

### File
`file_handling.py`

### How to Run
```bash
python file_handling.py
```

### Requirements
- Requires a file named `textfile.txt` in the same directory
- Text file should contain the content to be analyzed

### Output Example
```
The number of words in the file is: 245
```

### Implementation Details
- Opens and reads a text file named `textfile.txt`
- Splits content by whitespace to create word list
- Counts total words using `len()` function
- Uses `with` statement for safe file handling
- Automatically closes file after reading

---

## 📂 File Structure

```
Week-1 April_17/
├── max_number_finder.py              # Task 1 - Max number finder
├── mulplication-table_generator.py   # Task 2 - Multiplication table
├── file_handling.py                  # Task 3 - File word counter
├── image.png                         # Reference/documentation image
├── readme.md                         # This file
└── textfile.txt                      # (Required for Task 3)
```

---

## 🛠️ Tools & Technologies Used

| Tool/Technology | Purpose | Version |
|-----------------|---------|---------|
| Python | Programming language | 3.7+ |
| Text Editor | Code writing | Any (VS Code, PyCharm, etc.) |
| Terminal/CMD | Running scripts | Windows/Linux/Mac |
| File I/O | Text file operations | Built-in `open()` |

---

## 📦 Requirements

### Python Version
- Python 3.7 or higher

### Dependencies
- None (uses only Python standard library)

### External Files
- `textfile.txt` - Required for `file_handling.py` to work

---

## 🚀 How to Run All Tasks

### Option 1: Run Individually
```bash
# Task 1
python max_number_finder.py

# Task 2
python mulplication-table_generator.py

# Task 3
python file_handling.py
```

### Option 2: Run from Command Line
```bash
# Windows
python max_number_finder.py & python mulplication-table_generator.py & python file_handling.py

# Linux/Mac
python max_number_finder.py & python mulplication-table_generator.py & python file_handling.py
```

---

## 📝 Key Concepts Covered

### Task 1: max_number_finder.py
- User input handling with `input()`
- String to integer conversion
- List comprehension
- Function definition and calls
- Loop iteration
- Conditional statements (if)

### Task 2: mulplication-table_generator.py
- Integer input conversion
- For loops with range
- F-string formatting
- Multiplication operations
- Formatted output

### Task 3: file_handling.py
- File opening with `open()`
- Context managers (`with` statement)
- String splitting (`.split()`)
- File reading (`.read()`)
- List length operations

---

## ℹ️ Notes

1. **Input Format:** Each script expects specific input format. Follow examples for correct usage.

2. **Error Handling:** Scripts assume valid input. Invalid inputs may cause errors.

3. **File Dependencies:** Task 3 requires `textfile.txt` to be in the same directory as the script.

4. **String Formatting:** Task 2 uses f-strings (Python 3.6+). Ensure Python version compatibility.

5. **Word Definition:** In Task 3, words are defined by whitespace separation. Punctuation attached to words counts as part of the word.

---

## 📖 Usage Examples

### Example 1: Find Maximum Number
```bash
$ python max_number_finder.py
Enter a list of numbers separated by spaces: 10 20 5 30 15
The maximum number in the list is: 30
```

### Example 2: Multiplication Table
```bash
$ python mulplication-table_generator.py
Enter any number: 5
Multiplication Table Generator
5 * 1 = 5
5 * 2 = 10
...
5 * 10 = 50
The End
```

### Example 3: File Word Count
```bash
$ python file_handling.py
The number of words in the file is: 156
```

---

## 🔄 Workflow

1. Start with Task 1 (find maximum number)
2. Progress to Task 2 (multiplication table)
3. Complete Task 3 (file handling)
4. Test all scripts with sample inputs
5. Verify output against expected results

---

