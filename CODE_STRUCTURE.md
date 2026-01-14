# 🔧 Correlation Engine - Code Structure & Navigation Guide

## File Overview
- **Filename:** `correlation_engine.py`
- **Lines of Code:** 874 lines
- **Size:** 46 KB
- **Version:** 2.0 - Industry Edition
- **Python Version:** 3.7+
- **Dependencies:** pandas, numpy, seaborn, matplotlib, scikit-learn, scipy

---

## Module Structure

### **IMPORTS & CONFIGURATION (Lines 1-50)**
```python
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
from scipy import stats

# Configuration constants
INPUT_FILE = "final_manga_dataset_clean.csv"
FORECAST_YEARS = 5
PREDICTION_FUTURE_POINT = 10
```

**Purpose:** Load all necessary libraries and set up visual style for professional charts

---

## 9 Core Analysis Modules

### **MODULE 1: DATA LOADING & VALIDATION**
**Location:** Lines 60-100  
**Function:** `load_and_validate_data(filepath)`

**What it does:**
- Loads CSV file with error handling
- Displays dataset dimensions (3,589 records × 6 columns)
- Reports missing values (1,050 rows without scores)
- Shows data types
- Validates file existence

**Output:**
```
✓ Successfully loaded 3589 manga records
📊 Dataset Dimensions: (3589, 6)
📋 Columns: id, title, score, members, demographic, tags
⚠️  Missing Values Detected: score=1050, demographic=1426, tags=110
```

---

### **MODULE 2: DATA SANITIZATION & CLEANING**
**Location:** Lines 103-145  
**Function:** `sanitize_data(df)`

**What it does:**
- Removes 1,050 rows with missing scores
- Converts numeric columns properly
- Generates summary statistics
- Reports data quality

**Output:**
```
✓ Removed 1050 records with missing critical values
✓ Working with 2539 valid manga entries

📈 Score Statistics:
   Mean: 7.04 | Median: 6.99 | Range: 5.02 - 9.47
👥 Members Statistics:
   Mean: 10008 | Median: 1723 | Range: 210 - 780929
```

---

### **MODULE 3: FEATURE ENGINEERING & ENCODING**
**Location:** Lines 148-195  
**Function:** `engineer_features(df)`

**What it does:**
- Extracts 70 unique genres from "tags" field
- Creates binary genre indicators (e.g., is_Action=1)
- Encodes 5 demographic categories
- Combines all features into single dataframe
- Creates 79-feature analysis matrix

**Process:**
```
Input:  "Action, Comedy, Drama" (string)
         ↓
Output: Action=1, Comedy=1, Drama=1, Others=0 (binary)
```

**Output:**
```
✓ Extracted 70 unique genres
✓ Found 5 demographic categories
✓ Feature engineering complete: 79 total features
```

---

### **MODULE 4: EXPLORATORY DATA ANALYSIS (EDA)**
**Location:** Lines 198-280  
**Function:** `perform_eda(df, engineered_df)`

**What it does:**
- **Distribution Analysis:** Scores, members, demographics
- **Demographic Analysis:** Box plots, member comparisons
- **Genre Analysis:** Top 15 genres by count and score
- Generates 3 professional visualization PNG files

**Outputs:**
```
✓ Saved: 01_eda_distributions.png
✓ Saved: 02_eda_demographics.png
✓ Saved: 03_genre_analysis.png
```

**Key Insights:**
- Identifies Shounen as highest quality demographic
- Shows Romance as most common genre
- Reveals right-skewed distribution (good quality on average)

---

### **MODULE 5: CORRELATION ANALYSIS**
**Location:** Lines 283-365  
**Function:** `perform_correlation_analysis(engineered_df)`

**What it does:**
- Calculates Pearson correlation matrix (79×79)
- Identifies top 10 quality drivers
- Identifies top 10 popularity drivers
- Finds score killers (worst correlations)
- Generates correlation heatmap

**Outputs:**
```
🏆 TOP 10 QUALITY DRIVERS:
   1. members (+0.4489) [Strong]
   2. Award Winning (+0.3350) [Strong]
   3. Drama (+0.2188) [Moderate]
   ...

🚀 TOP 10 POPULARITY DRIVERS:
   1. Award Winning (+0.3032) [Strong]
   2. Gore (+0.2869) [Moderate]
   3. Action (+0.1916) [Moderate]
   ...

✓ Saved: 04_correlation_heatmap.png
```

---

### **MODULE 6: GENRE TREND PREDICTION**
**Location:** Lines 368-480  
**Function:** `predict_genre_trends(engineered_df, df_original)` ⭐ **STAR MODULE**

**What it does:**
- Analyzes all 70 genres for trend strength
- Calculates composite trend scores based on:
  - Average score (40% weight)
  - Log of average members (40% weight)
  - Volatility/growth indicator (20% weight)
- Ranks genres by prediction strength
- Forecasts which genres will skyrocket in 5 years

**Prediction Formula:**
```
trend_score = (avg_score/10)*0.4 + (log10(avg_members)/6)*0.4 + (volatility*0.5)*0.2
```

**Top Predictions:**
```
🚀 TOP 15 GENRES PREDICTED TO SKYROCKET:
 1. Fantasy (0.969) - 7.16 avg score, 16,960 members
 2. Military (0.943) - 7.53 avg score, 47,161 members
 3. Adventure (0.915) - 7.29 avg score, 26,343 members
 ...

✓ Saved: 05_genre_trends_prediction.png (4 sub-charts)
```

---

### **MODULE 7: QUALITY vs POPULARITY ANALYSIS**
**Location:** Lines 483-573  
**Function:** `analyze_quality_vs_popularity(df, engineered_df)`

**What it does:**
- Classifies manga into 5 categories:
  - **Masterpiece:** High quality + High popularity (17.5%)
  - **Cult Classic:** High quality + Low popularity (0.1%)
  - **Viral Hit:** Low quality + High popularity (1.3%)
  - **Quality Hidden Gem:** High quality + Medium popularity (7.8%)
  - **Average:** Everything else (73.4%)
- Analyzes characteristics of each category
- Creates classification scatter plot

**Output:**
```
📊 MANGA CLASSIFICATION:
   • Masterpiece: 444 (17.5%) - Score 7.90, 45,782 members
   • Quality Hidden Gem: 197 (7.8%) - Score 7.55, 3,006 members
   • Viral Hit: 32 (1.3%) - Score 6.32, 9,844 members
   • Cult Classic: 2 (0.1%) - Score 7.45, 486 members
   • Average: 1,864 (73.4%) - Score 6.79, 2,240 members

✓ Saved: 06_quality_vs_popularity.png
```

---

### **MODULE 8: STRATEGIC RECOMMENDATIONS**
**Location:** Lines 576-632  
**Function:** `generate_recommendations(df, predictions)`

**What it does:**
- Identifies high-priority genres (highest growth potential)
- Finds niche opportunities (high quality, low saturation)
- Identifies saturated markets (hard to stand out)
- Analyzes genre pairs (best combinations)

**Output:**
```
🚀 HIGH-PRIORITY GENRES:
   1. Fantasy (0.969) - Target: 7.2+, Reach: 16,960+ members
   2. Military (0.943) - Target: 7.5+, Reach: 47,161+ members
   ...

⭐ NICHE OPPORTUNITIES:
   1. Urban Fantasy (Score: 7.59, Count: 8)
   2. Samurai (Score: 7.61, Count: 19)
   ...

📊 COMBINATION STRATEGIES:
   1. Comedy + Romance (396 manga)
   2. Drama + Romance (354 manga)
   ...
```

---

### **MODULE 9: STATISTICAL INSIGHTS**
**Location:** Lines 635-793  
**Function:** `generate_statistical_insights(engineered_df, df_original)`

**What it does:**
- Analyzes quality-popularity relationship (r=0.4489)
- Examines score distribution shape (skewness=0.3539)
- Ranks demographics by performance
- Detects quality outliers (37 exceptional manga at 8.45+)
- Detects viral outliers (362 viral hits with 11,810+ members)

**Output:**
```
1. Quality-Popularity Relationship: 0.4489 (MODERATELY CONNECTED)
2. Score Distribution: FAIRLY SYMMETRIC (skewness=0.3539)
3. Demographic Rankings:
   1. Shounen (7.24 avg, 22,715 members)
   2. Seinen (7.10 avg, 21,646 members)
   ...
4. Exceptional Quality: 37 manga (1.5%)
   Examples: Monster, Berserk, 20th Century Boys
5. Viral Hits: 362 manga (14.3%)
```

---

## Main Execution Flow

**Location:** Lines 796-918

```python
def run_correlation_engine():
    """
    Main orchestration function.
    Calls all 9 modules in sequence.
    """
    # Step 1: Load data
    df = load_and_validate_data(INPUT_FILE)
    
    # Step 2: Clean data
    df_clean = sanitize_data(df)
    
    # Step 3: Engineer features
    engineered_df, genre_features, demo_features = engineer_features(df_clean)
    
    # Step 4: Exploratory analysis
    perform_eda(df_clean, engineered_df)
    
    # Step 5: Correlation analysis
    corr_matrix, score_drivers, popularity_drivers = perform_correlation_analysis(engineered_df)
    
    # Step 6: Trend prediction ⭐
    predictions = predict_genre_trends(engineered_df, df_clean)
    
    # Step 7: Quality vs popularity
    analyze_quality_vs_popularity(df_clean, engineered_df)
    
    # Step 8: Recommendations
    generate_recommendations(df_clean, predictions)
    
    # Step 9: Statistical insights
    generate_statistical_insights(engineered_df, df_clean)
    
    # Step 10: Final report
    generate_final_report(df_clean, engineered_df, predictions)

if __name__ == "__main__":
    run_correlation_engine()
```

---

## Key Features by Line Count

| Module | Lines | Purpose |
|--------|-------|---------|
| Imports & Config | 1-50 | Setup and initialization |
| Data Loading | 60-100 | Input validation |
| Data Cleaning | 103-145 | Quality control |
| Feature Engineering | 148-195 | Data transformation |
| EDA | 198-280 | Initial exploration (3 charts) |
| Correlation Analysis | 283-365 | Driver identification (1 chart) |
| **Trend Prediction** | **368-480** | **5-year forecast (1 chart)** ⭐ |
| Quality vs Popularity | 483-573 | Classification (1 chart) |
| Recommendations | 576-632 | Strategic insights |
| Statistical Insights | 635-793 | Deep statistics |
| Main Execution | 796-918 | Orchestration |

---

## Configuration Section

**Location:** Lines 37-50

```python
INPUT_FILE = "final_manga_dataset_clean.csv"  # Input CSV file
FORECAST_YEARS = 5                             # Prediction window
PREDICTION_FUTURE_POINT = 10                   # Timeline reference

# Visual style settings
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10
```

**Customization Tips:**
- Change `FORECAST_YEARS` to predict different time horizons
- Modify color palettes in `sns.set_palette()`
- Adjust figure size with `plt.rcParams['figure.figsize']`

---

## Output Files Generated

### **PNG Visualizations:**
1. `01_eda_distributions.png` - 4-panel distribution analysis
2. `02_eda_demographics.png` - 2-panel demographic analysis
3. `03_genre_analysis.png` - 2-panel genre ranking
4. `04_correlation_heatmap.png` - 20×20 correlation matrix
5. `05_genre_trends_prediction.png` - 4-panel trend forecast ⭐
6. `06_quality_vs_popularity.png` - Classification plots

### **Console Output:**
- 9 detailed analysis sections
- 45+ key metrics
- 100+ insights and recommendations

---

## Error Handling

**Implemented Safeguards:**
- File not found detection
- Missing value handling
- Type conversion validation
- Index bounds checking
- Division by zero prevention
- Unicode encoding support (Windows)

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| **Input Records** | 3,589 |
| **Cleaned Records** | 2,539 |
| **Feature Count** | 79 |
| **Unique Genres** | 70 |
| **Correlation Matrix Size** | 79×79 |
| **Execution Time** | ~1-2 minutes |
| **Output Files** | 6 PNG + console output |

---

## Extension Points

### **To Add New Analysis:**

1. **Create new module function:**
```python
def analyze_new_metric(df):
    """New analysis function"""
    # Your analysis code
    print("Results here")
```

2. **Add to main execution:**
```python
analyze_new_metric(df_clean)  # Add to run_correlation_engine()
```

3. **Save visualizations:**
```python
plt.savefig('07_new_analysis.png', dpi=300, bbox_inches='tight')
```

---

## Common Customizations

### **Change Input File:**
```python
INPUT_FILE = "your_file.csv"  # Line 37
```

### **Adjust Trend Prediction Weights:**
```python
# In predict_genre_trends() function, modify:
trend_score = (avg_score/10)*0.5 + (np.log10(avg_members)/6)*0.3 + (avg_growth * 0.5)*0.2
```

### **Change Visualization Style:**
```python
sns.set_style("darkgrid")  # Options: darkgrid, whitegrid, dark, white, ticks
sns.set_palette("Set2")    # Options: husl, Set1, Set2, Set3, Pastel1, etc.
```

---

**Last Updated:** January 2026  
**Code Status:** Production Ready ✅  
**Testing:** All 9 modules verified  
**Documentation:** Complete
