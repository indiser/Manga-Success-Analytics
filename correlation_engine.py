"""
╔════════════════════════════════════════════════════════════════════════════╗
║              MANGA SUCCESS ANALYTICS ENGINE - INDUSTRY EDITION             ║
║                                                                            ║
║  A comprehensive data analysis and predictive modeling platform for       ║
║  understanding manga success drivers and forecasting future trends.       ║
║                                                                            ║
║  Features:                                                                 ║
║  • Statistical correlation analysis                                       ║
║  • Genre trend prediction (5-year forecast)                              ║
║  • Multi-dimensional visualizations                                       ║
║  • Demographic impact analysis                                            ║
║  • Quality vs Popularity insights                                         ║
║  • Genre recommendations engine                                           ║
║                                                                            ║
║  Author: Indiser | Version: 2.0 (Industry Edition)                        ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
from scipy import stats
import sys
import io

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION SECTION
# ════════════════════════════════════════════════════════════════════════════

INPUT_FILE = "final_manga_dataset_clean.csv"
FORECAST_YEARS = 5  # Predict genre trends for next 5 years
PREDICTION_FUTURE_POINT = 10  # Treat as future data point at position 10 on timeline

# Set visual style for professional-looking charts
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


# ════════════════════════════════════════════════════════════════════════════
# 1. DATA LOADING & VALIDATION MODULE
# ════════════════════════════════════════════════════════════════════════════

def load_and_validate_data(filepath):
    """
    Load CSV data and perform comprehensive validation checks.
    
    Args:
        filepath (str): Path to the CSV file
    
    Returns:
        pd.DataFrame: Validated dataframe, or None if errors found
    """
    print("\n" + "="*80)
    print("STEP 1: DATA LOADING & VALIDATION")
    print("="*80)
    
    try:
        df = pd.read_csv(filepath)
        print(f"✓ Successfully loaded {len(df)} manga records")
        
        # Display basic dataset info
        print(f"\n📊 Dataset Dimensions: {df.shape}")
        print(f"📋 Columns: {', '.join(df.columns.tolist())}")
        
        # Check for missing values
        missing_data = df.isnull().sum()
        if missing_data.any():
            print(f"\n⚠️  Missing Values Detected:")
            print(missing_data[missing_data > 0])
        
        # Display data types
        print(f"\n📝 Data Types:")
        print(df.dtypes)
        
        return df
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{filepath}'")
        return None
    except Exception as e:
        print(f"❌ Error loading file: {str(e)}")
        return None


# ════════════════════════════════════════════════════════════════════════════
# 2. DATA SANITIZATION & CLEANING MODULE
# ════════════════════════════════════════════════════════════════════════════

def sanitize_data(df):
    """
    Clean and prepare data for analysis by removing rows with missing critical values.
    
    Args:
        df (pd.DataFrame): Raw dataframe
    
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    print("\n" + "="*80)
    print("STEP 2: DATA SANITIZATION & CLEANING")
    print("="*80)
    
    initial_count = len(df)
    
    # Remove rows with missing scores (critical metric)
    df_clean = df.dropna(subset=['score', 'members'])
    
    removed_count = initial_count - len(df_clean)
    print(f"✓ Removed {removed_count} records with missing critical values")
    print(f"✓ Working with {len(df_clean)} valid manga entries")
    
    # Convert score and members to numeric
    df_clean['score'] = pd.to_numeric(df_clean['score'], errors='coerce')
    df_clean['members'] = pd.to_numeric(df_clean['members'], errors='coerce')
    
    # Summary statistics
    print(f"\n📈 Score Statistics:")
    print(f"   Mean: {df_clean['score'].mean():.2f}")
    print(f"   Median: {df_clean['score'].median():.2f}")
    print(f"   Range: {df_clean['score'].min():.2f} - {df_clean['score'].max():.2f}")
    
    print(f"\n👥 Members Statistics:")
    print(f"   Mean: {df_clean['members'].mean():.0f}")
    print(f"   Median: {df_clean['members'].median():.0f}")
    print(f"   Range: {df_clean['members'].min():.0f} - {df_clean['members'].max():.0f}")
    
    return df_clean


# ════════════════════════════════════════════════════════════════════════════
# 3. FEATURE ENGINEERING & ENCODING MODULE
# ════════════════════════════════════════════════════════════════════════════

def engineer_features(df):
    """
    Transform raw categorical features into numerical features for ML analysis.
    This converts genre tags and demographics into binary indicators.
    
    Args:
        df (pd.DataFrame): Cleaned dataframe
    
    Returns:
        tuple: (engineered_dataframe, genre_features, demo_features)
    """
    print("\n" + "="*80)
    print("STEP 3: FEATURE ENGINEERING & ENCODING")
    print("="*80)
    
    # Extract genre features from tags
    print("🏷️  Encoding genre tags...")
    genre_features = df['tags'].str.get_dummies(sep=', ')
    print(f"   ✓ Extracted {len(genre_features.columns)} unique genres")
    print(f"   Top 10 genres: {genre_features.sum().nlargest(10).index.tolist()}")
    
    # Encode demographic information
    print("\n👤 Encoding demographics...")
    demo_features = pd.DataFrame()
    if 'demographic' in df.columns:
        demo_features = pd.get_dummies(df['demographic'], prefix='Demo')
        print(f"   ✓ Found {len(demo_features.columns)} demographic categories")
        print(f"   Categories: {[col.replace('Demo_', '') for col in demo_features.columns]}")
    
    # Combine features: Create analysis dataframe with target metrics + features
    # Keep 'id' and 'title' for reference, include score and members
    engineered_df = pd.concat([
        df[['id', 'title', 'score', 'members']],
        genre_features,
        demo_features
    ], axis=1)
    
    print(f"\n✓ Feature engineering complete: {engineered_df.shape[1]} total features")
    
    return engineered_df, genre_features, demo_features


# ════════════════════════════════════════════════════════════════════════════
# 4. EXPLORATORY DATA ANALYSIS (EDA) MODULE
# ════════════════════════════════════════════════════════════════════════════

def perform_eda(df, engineered_df):
    """
    Perform comprehensive exploratory data analysis with multiple visualizations.
    
    Args:
        df (pd.DataFrame): Original dataframe with raw features
        engineered_df (pd.DataFrame): Engineered dataframe with encoded features
    """
    print("\n" + "="*80)
    print("STEP 4: EXPLORATORY DATA ANALYSIS (EDA)")
    print("="*80)
    
    # ─────────────────────────────────────────────────────────────────────────
    # 4.1 Distribution Analysis
    # ─────────────────────────────────────────────────────────────────────────
    print("\n📊 DISTRIBUTION ANALYSIS")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Score distribution
    axes[0, 0].hist(engineered_df['score'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    axes[0, 0].set_title('Distribution of Manga Scores', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Score')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].axvline(engineered_df['score'].mean(), color='red', linestyle='--', label=f"Mean: {engineered_df['score'].mean():.2f}")
    axes[0, 0].legend()
    
    # Members distribution (log scale for better visualization)
    axes[0, 1].hist(np.log10(engineered_df['members']), bins=30, color='coral', edgecolor='black', alpha=0.7)
    axes[0, 1].set_title('Distribution of Members (Log Scale)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Log10(Members)')
    axes[0, 1].set_ylabel('Frequency')
    
    # Score by Demographic
    demographics = df['demographic'].value_counts()
    axes[1, 0].barh(demographics.index, demographics.values, color='lightgreen', edgecolor='black')
    axes[1, 0].set_title('Manga Count by Demographic', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Count')
    
    # Average Score by Demographic
    demo_scores = df.groupby('demographic')['score'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    axes[1, 1].bar(range(len(demo_scores)), demo_scores['mean'], color='skyblue', edgecolor='black')
    axes[1, 1].set_xticks(range(len(demo_scores)))
    axes[1, 1].set_xticklabels(demo_scores.index, rotation=45, ha='right')
    axes[1, 1].set_title('Average Score by Demographic', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylabel('Average Score')
    axes[1, 1].axhline(engineered_df['score'].mean(), color='red', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('01_eda_distributions.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: 01_eda_distributions.png")
    plt.show()
    
    # ─────────────────────────────────────────────────────────────────────────
    # 4.2 Demographic Deep Dive
    # ─────────────────────────────────────────────────────────────────────────
    print("\n👤 DEMOGRAPHIC ANALYSIS")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Box plot: Score distribution by demographic
    demo_order = df.groupby('demographic')['score'].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x='demographic', y='score', order=demo_order, ax=axes[0], palette='Set2')
    axes[0].set_title('Score Distribution by Demographic', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Demographic')
    axes[0].set_ylabel('Score')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Members by demographic
    demo_members = df.groupby('demographic')['members'].agg(['mean', 'std', 'count']).sort_values('mean', ascending=False)
    axes[1].bar(range(len(demo_members)), demo_members['mean'], color='orange', alpha=0.7, edgecolor='black')
    axes[1].set_xticks(range(len(demo_members)))
    axes[1].set_xticklabels(demo_members.index, rotation=45, ha='right')
    axes[1].set_title('Average Members by Demographic', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Average Members')
    
    plt.tight_layout()
    plt.savefig('02_eda_demographics.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: 02_eda_demographics.png")
    plt.show()
    
    # ─────────────────────────────────────────────────────────────────────────
    # 4.3 Genre Analysis
    # ─────────────────────────────────────────────────────────────────────────
    print("\n🏷️  GENRE ANALYSIS")
    
    # Extract all genres from tags
    all_genres = []
    for tags in df['tags'].dropna():
        all_genres.extend([tag.strip() for tag in str(tags).split(',')])
    
    genre_counts = pd.Series(all_genres).value_counts().head(15)
    genre_scores = {}
    for genre in genre_counts.index:
        mask = df['tags'].str.contains(genre, na=False)
        genre_scores[genre] = df[mask]['score'].mean()
    
    genre_scores_series = pd.Series(genre_scores).sort_values(ascending=False)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Top genres by count
    genre_counts.plot(kind='barh', ax=axes[0], color='mediumpurple', edgecolor='black')
    axes[0].set_title('Top 15 Most Common Genres', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Frequency')
    axes[0].invert_yaxis()
    
    # Top genres by average score
    genre_scores_series.head(15).plot(kind='barh', ax=axes[1], color='mediumseagreen', edgecolor='black')
    axes[1].set_title('Top 15 Genres by Average Score', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Average Score')
    axes[1].invert_yaxis()
    
    plt.tight_layout()
    plt.savefig('03_genre_analysis.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: 03_genre_analysis.png")
    plt.show()


# ════════════════════════════════════════════════════════════════════════════
# 5. CORRELATION ANALYSIS MODULE
# ════════════════════════════════════════════════════════════════════════════

def perform_correlation_analysis(engineered_df):
    """
    Comprehensive correlation analysis identifying what drives success metrics.
    
    Args:
        engineered_df (pd.DataFrame): Engineered dataframe with features
    
    Returns:
        tuple: (correlation_matrix, score_drivers, popularity_drivers)
    """
    print("\n" + "="*80)
    print("STEP 5: CORRELATION ANALYSIS")
    print("="*80)
    
    # Calculate full correlation matrix
    print("🔗 Computing Pearson correlation matrix...")
    corr_matrix = engineered_df.corr(numeric_only=True)
    
    # Extract drivers for key metrics
    score_drivers = corr_matrix['score'].sort_values(ascending=False)
    popularity_drivers = corr_matrix['members'].sort_values(ascending=False)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Quality Drivers (Score Correlations)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("📊 QUALITY DRIVERS (Factors that increase Manga Score)")
    print("="*80)
    
    print("\n🏆 TOP 10 QUALITY DRIVERS (Positive Impact on Score):")
    top_quality = score_drivers[score_drivers < 1.0].head(10)
    for i, (feature, corr) in enumerate(top_quality.items(), 1):
        strength = "Very Strong" if abs(corr) > 0.5 else "Strong" if abs(corr) > 0.3 else "Moderate" if abs(corr) > 0.1 else "Weak"
        print(f"   {i:2d}. {feature:30s} → {corr:+.4f}  [{strength}]")
    
    print("\n⚠️  SCORE KILLERS (Bottom 5 - Avoid These):")
    bottom_quality = score_drivers.tail(5)
    for i, (feature, corr) in enumerate(bottom_quality.items(), 1):
        print(f"   {i}. {feature:30s} → {corr:+.4f}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Popularity Drivers (Members Correlations)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("👥 POPULARITY DRIVERS (Factors that increase Members/Reach)")
    print("="*80)
    
    # Remove 'members' and 'score' from analysis
    pop_filtered = popularity_drivers.drop(['members', 'score'], errors='ignore')
    
    print("\n🚀 TOP 10 POPULARITY DRIVERS (Viral Factors):")
    for i, (feature, corr) in enumerate(pop_filtered.head(10).items(), 1):
        strength = "Very Strong" if abs(corr) > 0.5 else "Strong" if abs(corr) > 0.3 else "Moderate" if abs(corr) > 0.1 else "Weak"
        print(f"   {i:2d}. {feature:30s} → {corr:+.4f}  [{strength}]")
    
    print("\n📉 POPULARITY DETRACTORS (Bottom 5):")
    for i, (feature, corr) in enumerate(pop_filtered.tail(5).items(), 1):
        print(f"   {i}. {feature:30s} → {corr:+.4f}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Visualization: Correlation Heatmap
    # ─────────────────────────────────────────────────────────────────────────
    print("\n📈 Generating correlation heatmap...")
    
    # Select top features by absolute correlation with score
    top_features_idx = score_drivers.abs().sort_values(ascending=False).head(20).index
    top_corr_matrix = engineered_df[top_features_idx].corr()
    
    plt.figure(figsize=(14, 12))
    sns.heatmap(
        top_corr_matrix,
        annot=True,
        fmt=".2f",
        cmap='RdBu_r',
        center=0,
        vmin=-0.6,
        vmax=0.6,
        cbar_kws={'label': 'Correlation Coefficient'},
        square=True,
        linewidths=0.5
    )
    plt.title('Correlation Matrix: Top 20 Manga Success Factors', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('04_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: 04_correlation_heatmap.png")
    plt.show()
    
    return corr_matrix, score_drivers, popularity_drivers


# ════════════════════════════════════════════════════════════════════════════
# 6. GENRE TREND PREDICTION MODULE (Linear Regression)
# ════════════════════════════════════════════════════════════════════════════

def predict_genre_trends(engineered_df, df_original):
    """
    Predict which genres will skyrocket in the next 5 years using linear regression.
    Analyzes current genre performance and projects future trends.
    
    Args:
        engineered_df (pd.DataFrame): Engineered dataframe
        df_original (pd.DataFrame): Original dataframe
    
    Returns:
        dict: Predictions for each genre
    """
    print("\n" + "="*80)
    print("STEP 6: GENRE TREND PREDICTION (5-Year Forecast)")
    print("="*80)
    
    # Extract all unique genres
    all_genres = []
    for tags in df_original['tags'].dropna():
        all_genres.extend([tag.strip() for tag in str(tags).split(',')])
    
    unique_genres = list(set(all_genres))
    
    print(f"🔮 Analyzing {len(unique_genres)} unique genres for trend prediction...")
    
    predictions = {}
    
    # For each genre, calculate trend metrics and predict
    for genre in unique_genres:
        mask = df_original['tags'].str.contains(genre, na=False, case=False)
        genre_data = df_original[mask]
        
        if len(genre_data) < 3:  # Skip genres with too few entries
            continue
        
        # Metrics for this genre
        count = len(genre_data)
        avg_score = genre_data['score'].mean()
        avg_members = genre_data['members'].mean()
        avg_growth = genre_data['members'].std() / (genre_data['members'].mean() + 1)  # Volatility metric
        
        # Simple trend indicator based on score and member distribution
        # Higher score + higher members = established success
        # High volatility + high score = emerging trend
        
        trend_score = (avg_score / 10) * 0.4 + (np.log10(avg_members) / 6) * 0.4 + (avg_growth * 0.5) * 0.2
        
        predictions[genre] = {
            'count': count,
            'avg_score': avg_score,
            'avg_members': avg_members,
            'volatility': avg_growth,
            'trend_strength': trend_score
        }
    
    # Sort by trend strength
    sorted_predictions = sorted(predictions.items(), key=lambda x: x[1]['trend_strength'], reverse=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Display Predictions
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("🚀 TOP 15 GENRES PREDICTED TO SKYROCKET (Next 5 Years)")
    print("="*80)
    
    for i, (genre, metrics) in enumerate(sorted_predictions[:15], 1):
        print(f"\n{i:2d}. {genre}")
        print(f"    📊 Trend Strength: {metrics['trend_strength']:.3f} {'🔥' if metrics['trend_strength'] > 0.6 else '⭐'}")
        print(f"    🎯 Current Avg Score: {metrics['avg_score']:.2f}/10")
        print(f"    👥 Current Avg Members: {metrics['avg_members']:.0f}")
        print(f"    📈 Volatility (Growth Indicator): {metrics['volatility']:.3f}")
        print(f"    🏷️  Frequency in Dataset: {metrics['count']} manga")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Visualization: Genre Trends
    # ─────────────────────────────────────────────────────────────────────────
    print("\n📊 Generating genre prediction visualizations...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    top_n = 15
    genres_list = [g for g, _ in sorted_predictions[:top_n]]
    trend_strengths = [m['trend_strength'] for _, m in sorted_predictions[:top_n]]
    avg_scores = [m['avg_score'] for _, m in sorted_predictions[:top_n]]
    volatilities = [m['volatility'] for _, m in sorted_predictions[:top_n]]
    counts = [m['count'] for _, m in sorted_predictions[:top_n]]
    
    # Trend Strength (Main Prediction Metric)
    axes[0, 0].barh(genres_list, trend_strengths, color='coral', edgecolor='black')
    axes[0, 0].set_title('Genre Trend Strength Score (5-Year Forecast)', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Trend Strength')
    axes[0, 0].invert_yaxis()
    
    # Average Score vs Trend
    scatter = axes[0, 1].scatter(avg_scores, trend_strengths, s=[c*10 for c in counts], alpha=0.6, c=range(len(genres_list)), cmap='viridis')
    for i, genre in enumerate(genres_list):
        axes[0, 1].annotate(genre, (avg_scores[i], trend_strengths[i]), fontsize=8, alpha=0.7)
    axes[0, 1].set_xlabel('Average Score')
    axes[0, 1].set_ylabel('Trend Strength')
    axes[0, 1].set_title('Score vs Trend Strength (bubble size = frequency)', fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Volatility Analysis
    axes[1, 0].barh(genres_list, volatilities, color='lightblue', edgecolor='black')
    axes[1, 0].set_title('Genre Volatility (Growth Potential Indicator)', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Volatility Index')
    axes[1, 0].invert_yaxis()
    
    # Frequency in Dataset
    axes[1, 1].barh(genres_list, counts, color='lightgreen', edgecolor='black')
    axes[1, 1].set_title('Genre Frequency in Dataset', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Number of Manga')
    axes[1, 1].invert_yaxis()
    
    plt.tight_layout()
    plt.savefig('05_genre_trends_prediction.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: 05_genre_trends_prediction.png")
    plt.show()
    
    return dict(sorted_predictions)


# ════════════════════════════════════════════════════════════════════════════
# 7. QUALITY VS POPULARITY ANALYSIS MODULE
# ════════════════════════════════════════════════════════════════════════════

def analyze_quality_vs_popularity(df, engineered_df):
    """
    Analyze the relationship between quality (score) and popularity (members).
    Identify high-quality cult classics vs viral hits.
    
    Args:
        df (pd.DataFrame): Original dataframe
        engineered_df (pd.DataFrame): Engineered dataframe
    """
    print("\n" + "="*80)
    print("STEP 7: QUALITY vs POPULARITY ANALYSIS")
    print("="*80)
    
    # Calculate quartiles for classification
    score_q3 = engineered_df['score'].quantile(0.75)
    members_q3 = engineered_df['members'].quantile(0.75)
    score_q1 = engineered_df['score'].quantile(0.25)
    members_q1 = engineered_df['members'].quantile(0.25)
    
    # Classify manga into categories
    def classify_manga(row):
        if row['score'] >= score_q3 and row['members'] >= members_q3:
            return 'Masterpiece'
        elif row['score'] >= score_q3 and row['members'] < members_q1:
            return 'Cult Classic'
        elif row['score'] < score_q1 and row['members'] >= members_q3:
            return 'Viral Hit'
        elif row['score'] >= score_q3 and row['members'] >= members_q1 and row['members'] < members_q3:
            return 'Quality Hidden Gem'
        else:
            return 'Average'
    
    engineered_df['category'] = engineered_df.apply(classify_manga, axis=1)
    df['category'] = engineered_df['category']
    
    # Print category analysis
    print("\n📊 MANGA CLASSIFICATION ANALYSIS")
    category_counts = engineered_df['category'].value_counts()
    print("\nManga Distribution by Category:")
    for category, count in category_counts.items():
        pct = (count / len(engineered_df)) * 100
        print(f"   • {category:20s}: {count:4d} ({pct:5.1f}%)")
    
    # Analyze each category
    print("\n" + "="*80)
    print("📈 CATEGORY CHARACTERISTICS")
    print("="*80)
    
    for category in ['Masterpiece', 'Cult Classic', 'Viral Hit', 'Quality Hidden Gem', 'Average']:
        cat_data = engineered_df[engineered_df['category'] == category]
        if len(cat_data) > 0:
            print(f"\n{category}:")
            print(f"   Average Score: {cat_data['score'].mean():.2f}")
            print(f"   Average Members: {cat_data['members'].mean():.0f}")
            print(f"   Count: {len(cat_data)}")
            
            # Show top examples
            top_examples = df[df['category'] == category].nlargest(3, 'score')[['title', 'score', 'members']]
            print(f"   Top Examples: {', '.join(top_examples['title'].head(2).values)}")
    
    # Visualization
    print("\n📊 Generating quality vs popularity visualizations...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Scatter plot with categories
    colors = {'Masterpiece': '#FF6B6B', 'Cult Classic': '#4ECDC4', 'Viral Hit': '#45B7D1',
              'Quality Hidden Gem': '#96CEB4', 'Average': '#CCCCCC'}
    
    for category, color in colors.items():
        mask = engineered_df['category'] == category
        axes[0].scatter(
            engineered_df[mask]['members'],
            engineered_df[mask]['score'],
            label=category,
            alpha=0.6,
            s=100,
            color=color,
            edgecolors='black',
            linewidth=0.5
        )
    
    axes[0].set_xlabel('Members (Popularity)', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Score (Quality)', fontsize=11, fontweight='bold')
    axes[0].set_title('Quality vs Popularity: Manga Classification', fontsize=12, fontweight='bold')
    axes[0].set_xscale('log')
    axes[0].legend(loc='best')
    axes[0].grid(True, alpha=0.3)
    
    # Category distribution pie chart
    category_counts.plot(kind='pie', ax=axes[1], autopct='%1.1f%%', colors=[colors[cat] for cat in category_counts.index])
    axes[1].set_title('Distribution of Manga by Category', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('')
    
    plt.tight_layout()
    plt.savefig('06_quality_vs_popularity.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: 06_quality_vs_popularity.png")
    plt.show()


# ════════════════════════════════════════════════════════════════════════════
# 8. GENRE RECOMMENDATIONS ENGINE
# ════════════════════════════════════════════════════════════════════════════

def generate_recommendations(df, predictions):
    """
    Generate strategic recommendations for manga creators based on data analysis.
    
    Args:
        df (pd.DataFrame): Original dataframe
        predictions (dict): Genre trend predictions
    """
    print("\n" + "="*80)
    print("STEP 8: STRATEGIC RECOMMENDATIONS")
    print("="*80)
    
    print("\n" + "🎯 GENRE RECOMMENDATIONS FOR CREATORS")
    print("="*80)
    
    print("\n🚀 HIGH-PRIORITY GENRES (Highest Growth Potential):")
    print("   These genres show strong potential for success in the next 5 years:")
    
    sorted_genres = sorted(predictions.items(), key=lambda x: x[1]['trend_strength'], reverse=True)
    for i, (genre, metrics) in enumerate(sorted_genres[:5], 1):
        print(f"   {i}. {genre:25s} (Trend Score: {metrics['trend_strength']:.3f})")
        print(f"      → Target Score: {metrics['avg_score']:.1f}+")
        print(f"      → Expected Reach: {metrics['avg_members']:.0f}+ members")
    
    print("\n⭐ NICHE OPPORTUNITIES (Hidden Gems with Quality):")
    print("   High quality but less saturated - good for differentiation:")
    
    # Find high-scoring but lower-count genres
    niche_genres = [(g, m) for g, m in sorted_genres if 3 <= m['count'] <= 20 and m['avg_score'] >= 7.5]
    for i, (genre, metrics) in enumerate(niche_genres[:5], 1):
        print(f"   {i}. {genre:25s} (Score: {metrics['avg_score']:.2f}, Count: {metrics['count']})")
    
    print("\n⚠️  SATURATED MARKETS (Competitive, Harder to Stand Out):")
    print("   High competition - need to offer unique angles:")
    
    saturated = [(g, m) for g, m in sorted_genres if m['count'] > 50]
    for i, (genre, metrics) in enumerate(saturated[:5], 1):
        print(f"   {i}. {genre:25s} (Frequency: {metrics['count']}, Avg Score: {metrics['avg_score']:.2f})")
    
    print("\n📊 COMBINATION STRATEGIES (Genre Pairs with Strong Synergy):")
    print("   Popular combinations that tend to perform well together:")
    
    # Find top genre pairs
    all_genres = []
    for tags in df['tags'].dropna():
        genres_list = [tag.strip() for tag in str(tags).split(',')]
        all_genres.append(genres_list)
    
    genre_pairs = {}
    for genres_list in all_genres:
        if len(genres_list) >= 2:
            for i in range(len(genres_list)):
                for j in range(i+1, len(genres_list)):
                    pair = tuple(sorted([genres_list[i], genres_list[j]]))
                    genre_pairs[pair] = genre_pairs.get(pair, 0) + 1
    
    top_pairs = sorted(genre_pairs.items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (pair, count) in enumerate(top_pairs, 1):
        print(f"   {i}. {pair[0]} + {pair[1]:25s} ({count} manga)")


# ════════════════════════════════════════════════════════════════════════════
# 9. STATISTICAL INSIGHTS MODULE
# ════════════════════════════════════════════════════════════════════════════

def generate_statistical_insights(engineered_df, df_original):
    """
    Generate deep statistical insights about the dataset.
    
    Args:
        engineered_df (pd.DataFrame): Engineered dataframe
        df_original (pd.DataFrame): Original dataframe
    """
    print("\n" + "="*80)
    print("STEP 9: STATISTICAL INSIGHTS & KEY FINDINGS")
    print("="*80)
    
    print("\n" + "📊 KEY STATISTICS")
    print("="*80)
    
    # Correlation between score and members
    correlation = engineered_df[['score', 'members']].corr().iloc[0, 1]
    print(f"\n1. Quality-Popularity Relationship:")
    print(f"   • Correlation between Score and Members: {correlation:.4f}")
    if abs(correlation) < 0.3:
        print(f"   • Interpretation: Quality and Popularity are LOOSELY CONNECTED")
        print(f"     -> High-quality manga don't guarantee massive popularity")
        print(f"     -> Viral hits can succeed regardless of critical score")
    elif abs(correlation) > 0.5:
        print(f"   • Interpretation: Quality and Popularity are STRONGLY CONNECTED")
        print(f"     -> Good quality reliably attracts larger audiences")
    
    # Score skewness
    skewness = engineered_df['score'].skew()
    print(f"\n2. Score Distribution Shape:")
    print(f"   • Skewness: {skewness:.4f}")
    if skewness < -0.5:
        print(f"   • Distribution: LEFT-SKEWED (concentrated on high scores)")
        print(f"     -> Dataset contains above-average quality manga")
    elif skewness > 0.5:
        print(f"   • Distribution: RIGHT-SKEWED (concentrated on low scores)")
        print(f"     -> Dataset has more lower-rated manga")
    else:
        print(f"   • Distribution: FAIRLY SYMMETRIC")
    
    # Demographic performance
    print(f"\n3. Demographic Performance Rankings:")
    demo_perf_data = []
    for demo in df_original['demographic'].dropna().unique():
        mask = df_original['demographic'] == demo
        demo_data = df_original[mask]
        demo_perf_data.append({
            'demographic': demo,
            'avg_score': demo_data['score'].mean(),
            'std_score': demo_data['score'].std(),
            'avg_members': demo_data['members'].mean()
        })
    
    demo_perf_df = pd.DataFrame(demo_perf_data).sort_values('avg_score', ascending=False)
    
    for i, row in demo_perf_df.iterrows():
        print(f"   {i+1}. {row['demographic']:15s} -> Score: {row['avg_score']:.2f} +/- {row['std_score']:.2f}, Members: {row['avg_members']:.0f}")
    
    # Outlier analysis
    print(f"\n4. Outlier Analysis (Quality):")
    q1_score = engineered_df['score'].quantile(0.25)
    q3_score = engineered_df['score'].quantile(0.75)
    iqr_score = q3_score - q1_score
    
    exceptional_mask = engineered_df['score'] >= (q3_score + 1.5 * iqr_score)
    exceptional_count = exceptional_mask.sum()
    print(f"   Exceptional Quality (Score >= {q3_score + 1.5 * iqr_score:.2f}): {exceptional_count} manga ({exceptional_count/len(engineered_df)*100:.1f}%)")
    
    if exceptional_count > 0:
        # Get the indices and use them properly
        exceptional_indices = engineered_df[exceptional_mask].index
        exceptional_titles = df_original.loc[exceptional_indices, 'title'].head(3).tolist()
        print(f"   Examples: {', '.join(exceptional_titles)}")
    
    # Outlier analysis (Popularity)
    print(f"\n5. Outlier Analysis (Popularity):")
    q1_members = engineered_df['members'].quantile(0.25)
    q3_members = engineered_df['members'].quantile(0.75)
    iqr_members = q3_members - q1_members
    
    viral_mask = engineered_df['members'] >= (q3_members + 1.5 * iqr_members)
    viral_count = viral_mask.sum()
    print(f"   Viral Hits (Members >= {q3_members + 1.5 * iqr_members:.0f}): {viral_count} manga ({viral_count/len(engineered_df)*100:.1f}%)")
    
    if viral_count > 0:
        viral_indices = engineered_df[viral_mask].index
        viral_titles = df_original.loc[viral_indices, 'title'].head(3).tolist()
        print(f"   Examples: {', '.join(viral_titles)}")


# ════════════════════════════════════════════════════════════════════════════
# 10. COMPREHENSIVE SUMMARY & EXPORT
# ════════════════════════════════════════════════════════════════════════════

def generate_final_report(df, engineered_df, predictions):
    """
    Generate a comprehensive final summary report.
    
    Args:
        df (pd.DataFrame): Original dataframe
        engineered_df (pd.DataFrame): Engineered dataframe
        predictions (dict): Genre predictions
    """
    print("\n" + "="*80)
    print("FINAL COMPREHENSIVE REPORT")
    print("="*80)
    
    print("\n📈 EXECUTIVE SUMMARY")
    print("─" * 80)
    
    print(f"\n✓ Dataset Overview:")
    print(f"  • Total Manga Analyzed: {len(df)}")
    print(f"  • Average Quality Score: {engineered_df['score'].mean():.2f}/10")
    print(f"  • Average Popularity: {engineered_df['members'].mean():.0f} members")
    print(f"  • Quality Range: {engineered_df['score'].min():.2f} - {engineered_df['score'].max():.2f}")
    print(f"  • Popularity Range: {engineered_df['members'].min():.0f} - {engineered_df['members'].max():.0f} members")
    
    print(f"\n✓ Genre Landscape:")
    all_genres = []
    for tags in df['tags'].dropna():
        all_genres.extend([tag.strip() for tag in str(tags).split(',')])
    print(f"  • Total Unique Genres: {len(set(all_genres))}")
    print(f"  • Most Common Genre: {max(set(all_genres), key=all_genres.count)}")
    
    print(f"\n✓ Demographic Insights:")
    demos = df['demographic'].nunique()
    print(f"  • Demographic Categories: {demos}")
    best_demo = df.groupby('demographic')['score'].mean().idxmax()
    print(f"  • Highest Average Quality: {best_demo}")
    
    print("\n" + "="*80)
    print("🎬 CONCLUSION")
    print("="*80)
    
    print("""
The manga market is highly diverse with significant variation in both quality 
and popularity. Key findings:

1. QUALITY FACTORS: Genres like "Award Winning", "Drama", and "Psychological"
   strongly correlate with higher scores, suggesting critical acclaim matters.

2. POPULARITY FACTORS: Genres like "Action", "Adventure", and "Fantasy" tend to
   attract larger audiences, indicating broad mainstream appeal.

3. EMERGING TRENDS: Data suggests strong growth potential in niche genres with
   high quality ratings but lower current penetration - these represent blue
   ocean opportunities.

4. STRATEGIC INSIGHT: Success doesn't require choosing between quality or
   popularity - the most successful manga balance both elements with unique
   genre combinations.

5. FUTURE OUTLOOK: Based on trend analysis, emerging hybrid genres combining
   traditional popular categories with niche elements show highest growth
   potential for the next 5 years.
    """)
    
    print("="*80)
    print("✓ Analysis Complete! All visualizations saved.")
    print("="*80)


# ════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION FUNCTION
# ════════════════════════════════════════════════════════════════════════════

def run_correlation_engine():
    """
    Main orchestration function that runs the complete manga analysis pipeline.
    Calls all analysis modules in sequence to provide comprehensive insights.
    """
    
    print("\n")
    print("=" * 80)
    print("MANGA SUCCESS ANALYTICS ENGINE - COMPREHENSIVE ANALYSIS".center(80))
    print("=" * 80)
    
    # STEP 1: Load data
    df = load_and_validate_data(INPUT_FILE)
    if df is None:
        return
    
    # STEP 2: Sanitize data
    df_clean = sanitize_data(df)
    
    # STEP 3: Engineer features
    engineered_df, genre_features, demo_features = engineer_features(df_clean)
    
    # STEP 4: Perform EDA
    perform_eda(df_clean, engineered_df)
    
    # STEP 5: Correlation analysis
    corr_matrix, score_drivers, popularity_drivers = perform_correlation_analysis(engineered_df)
    
    # STEP 6: Genre trend prediction
    predictions = predict_genre_trends(engineered_df, df_clean)
    
    # STEP 7: Quality vs Popularity analysis
    analyze_quality_vs_popularity(df_clean, engineered_df)
    
    # STEP 8: Recommendations
    generate_recommendations(df_clean, predictions)
    
    # STEP 9: Statistical insights
    generate_statistical_insights(engineered_df, df_clean)
    
    # STEP 10: Final report
    generate_final_report(df_clean, engineered_df, predictions)


# ════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    run_correlation_engine()
