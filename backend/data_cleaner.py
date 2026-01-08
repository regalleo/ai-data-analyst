"""
Data Cleaning Module - Advanced Edition
Handles missing values, duplicates, outliers, standardization, and data quality issues
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import re
from datetime import datetime


class DataCleaningReport:
    """Report of cleaning operations performed."""
    def __init__(self):
        self.issues_found = []
        self.actions_taken = []
        self.rows_before = 0
        self.rows_after = 0
        self.columns_before = 0
        self.columns_after = 0
        self.missing_values_summary = {}
        self.duplicates_removed = 0
        self.outliers_fixed = 0
        self.values_standardized = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary with native Python types."""
        def clean_value(val):
            """Convert numpy types to native Python."""
            if isinstance(val, (np.integer, np.int64, np.int32)):
                return int(val)
            elif isinstance(val, (np.floating, np.float64, np.float32)):
                return float(val)
            elif isinstance(val, (np.bool_, bool)):
                return bool(val)
            elif isinstance(val, dict):
                return {k: clean_value(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [clean_value(item) for item in val]
            elif pd.isna(val):
                return None
            return val
        
        return {
            "issues_found": self.issues_found,
            "actions_taken": self.actions_taken,
            "rows_before": int(self.rows_before),
            "rows_after": int(self.rows_after),
            "columns_before": int(self.columns_before),
            "columns_after": int(self.columns_after),
            "missing_values": clean_value(self.missing_values_summary),
            "duplicates_removed": int(self.duplicates_removed),
            "outliers_fixed": int(self.outliers_fixed),
            "values_standardized": int(self.values_standardized),
        }



def parse_text_to_number(value):
    """Convert text numbers like 'twenty-one' to numeric."""
    if pd.isna(value):
        return np.nan
    
    if isinstance(value, (int, float)):
        return value
    
    # Dictionary of word to number mappings
    word_to_num = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
        'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
        'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
        'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
        'eighty': 80, 'ninety': 90, 'hundred': 100
    }
    
    value_str = str(value).lower().strip()
    
    # Check if it's already a number
    try:
        return float(value_str)
    except ValueError:
        pass
    
    # Handle text numbers like 'twenty-one'
    if '-' in value_str:
        parts = value_str.split('-')
        total = 0
        for part in parts:
            if part in word_to_num:
                total += word_to_num[part]
        return total if total > 0 else np.nan
    
    # Single word number
    if value_str in word_to_num:
        return word_to_num[value_str]
    
    return np.nan


def fix_email(email):
    """Fix and validate email addresses."""
    if pd.isna(email):
        return np.nan
    
    email_str = str(email).strip()
    
    # Check if email has @ and domain
    if '@' not in email_str:
        # Try to add .com if it ends with @gmail
        if email_str.endswith('@gmail'):
            return email_str + '.com'
        return np.nan
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email_str):
        return email_str.lower()
    
    return np.nan


def standardize_date(date_val):
    """Standardize various date formats to YYYY-MM-DD."""
    if pd.isna(date_val):
        return np.nan
    
    date_str = str(date_val).strip()
    
    # Common date formats to try
    date_formats = [
        '%Y-%m-%d',      # 2023-01-15
        '%d/%m/%Y',      # 15/01/2023
        '%Y/%m/%d',      # 2023/01/15
        '%m-%d-%Y',      # 01-20-2023
        '%d-%m-%Y',      # 25-01-2023
        '%Y.%m.%d',      # 2023.01.21
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return date_str  # Return as-is if can't parse


def standardize_gender(gender):
    """Standardize gender values to 'Male', 'Female', or 'Other'."""
    if pd.isna(gender):
        return np.nan
    
    gender_str = str(gender).strip().lower()
    
    if gender_str in ['male', 'm', 'man', 'boy']:
        return 'Male'
    elif gender_str in ['female', 'f', 'woman', 'girl']:
        return 'Female'
    elif gender_str in ['other', 'non-binary', 'nb']:
        return 'Other'
    
    return 'Other'


def fix_outliers(series, column_name):
    """Fix outliers using IQR method for numeric columns."""
    if not pd.api.types.is_numeric_dtype(series):
        return series, 0
    
    fixed_count = 0
    fixed_series = series.copy()
    
    # Age-specific rules
    if 'age' in column_name.lower():
        # Age should be between 0 and 120
        mask_negative = fixed_series < 0
        mask_toolarge = fixed_series > 120
        
        # Fix negative ages by taking absolute value
        fixed_series.loc[mask_negative] = fixed_series.loc[mask_negative].abs()
        fixed_count += mask_negative.sum()
        
        # Fix unrealistic ages (e.g., 200) with median
        if mask_toolarge.any():
            median_age = fixed_series[~mask_toolarge].median()
            fixed_series.loc[mask_toolarge] = median_age
            fixed_count += mask_toolarge.sum()
        
        return fixed_series, fixed_count
    
    # Marks/scores specific rules
    if 'mark' in column_name.lower() or 'score' in column_name.lower():
        # Marks should be between 0 and 100
        mask_negative = fixed_series < 0
        mask_toolarge = fixed_series > 100
        
        # Clip to valid range
        fixed_series = fixed_series.clip(0, 100)
        fixed_count = (mask_negative | mask_toolarge).sum()
        
        return fixed_series, fixed_count
    
    # General outlier detection using IQR
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 3 * IQR
    upper_bound = Q3 + 3 * IQR
    
    outlier_mask = (series < lower_bound) | (series > upper_bound)
    
    if outlier_mask.any():
        # Replace outliers with median
        median_val = series[~outlier_mask].median()
        fixed_series.loc[outlier_mask] = median_val
        fixed_count = outlier_mask.sum()
    
    return fixed_series, fixed_count


def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive data quality analysis.
    """
    quality_report = {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "missing_values": {},
        "duplicate_rows": 0,
        "column_types": {},
        "outliers": {},
        "issues": [],
        "needs_cleaning": False,
    }
    
    # Check for missing values
    for col in df.columns:
        missing_count = int(df[col].isna().sum())  # Convert to int
        # Also check for placeholder values
        placeholder_count = 0
        if df[col].dtype == 'object':
            placeholder_values = ['-', '', ' ', 'nan', 'null', 'none', 'unknown']
            placeholder_count = int(df[col].astype(str).str.strip().str.lower().isin(placeholder_values).sum())
        
        total_missing = missing_count + placeholder_count
        missing_pct = (total_missing / len(df)) * 100 if len(df) > 0 else 0
        
        if total_missing > 0:
            quality_report["missing_values"][col] = {
                "count": int(total_missing),
                "percentage": float(round(missing_pct, 2))
            }
            quality_report["issues"].append(
                f"Column '{col}' has {total_missing} missing/placeholder values ({missing_pct:.1f}%)"
            )
            quality_report["needs_cleaning"] = True
    
    # Check for duplicates
    duplicate_count = int(df.duplicated().sum())  # Convert to int
    if duplicate_count > 0:
        quality_report["duplicate_rows"] = duplicate_count
        quality_report["issues"].append(f"Found {duplicate_count} duplicate rows")
        quality_report["needs_cleaning"] = True
    
    # Check for outliers in numeric columns
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if 'age' in col.lower():
                outliers = int(((df[col] < 0) | (df[col] > 120)).sum())
                if outliers > 0:
                    quality_report["outliers"][col] = outliers
                    quality_report["issues"].append(f"Column '{col}' has {outliers} outlier values")
                    quality_report["needs_cleaning"] = True
    
    # Check column types
    for col in df.columns:
        quality_report["column_types"][col] = str(df[col].dtype)
    
    return quality_report



def clean_dataset(
    df: pd.DataFrame,
    strategy: str = "auto"
) -> Tuple[pd.DataFrame, DataCleaningReport]:
    """
    Comprehensive dataset cleaning with intelligent strategies.
    """
    report = DataCleaningReport()
    report.rows_before = len(df)
    report.columns_before = len(df.columns)
    
    cleaned_df = df.copy()
    
    # === STEP 1: Remove exact duplicates ===
    duplicate_count = cleaned_df.duplicated().sum()
    if duplicate_count > 0:
        cleaned_df = cleaned_df.drop_duplicates()
        report.duplicates_removed = int(duplicate_count)
        report.actions_taken.append(f"✓ Removed {duplicate_count} duplicate rows")
        report.issues_found.append(f"Found {duplicate_count} duplicate rows")
    
    # === STEP 2: Clean column names ===
    cleaned_df.columns = [col.strip().lower().replace(' ', '_') for col in cleaned_df.columns]
    
    # === STEP 3: Handle each column intelligently ===
    for col in cleaned_df.columns:
        original_missing = cleaned_df[col].isna().sum()
        
        # Replace placeholder values with NaN
        if cleaned_df[col].dtype == 'object':
            placeholder_values = ['-', '', ' ', 'nan', 'null', 'none']
            cleaned_df[col] = cleaned_df[col].replace(placeholder_values, np.nan)
            cleaned_df[col] = cleaned_df[col].replace('', np.nan)
            # Strip whitespace
            cleaned_df[col] = cleaned_df[col].str.strip() if cleaned_df[col].dtype == 'object' else cleaned_df[col]
        
        # Column-specific cleaning
        if 'age' in col:
            # Convert text numbers to numeric
            cleaned_df[col] = cleaned_df[col].apply(parse_text_to_number)
            # Fix outliers
            cleaned_df[col], outliers_fixed = fix_outliers(cleaned_df[col], col)
            if outliers_fixed > 0:
                report.outliers_fixed += outliers_fixed
                report.actions_taken.append(f"✓ Fixed {outliers_fixed} outlier values in '{col}'")
            # Fill remaining missing with median
            if cleaned_df[col].isna().any():
                median_age = cleaned_df[col].median()
                cleaned_df[col] = cleaned_df[col].fillna(median_age)
                report.actions_taken.append(f"✓ Filled missing '{col}' values with median ({median_age:.0f})")
        
        elif 'email' in col:
            # Fix email formats
            cleaned_df[col] = cleaned_df[col].apply(fix_email)
            # For missing emails, create generic ones based on name if available
            if 'name' in cleaned_df.columns and cleaned_df[col].isna().any():
                for idx in cleaned_df[cleaned_df[col].isna()].index:
                    if pd.notna(cleaned_df.loc[idx, 'name']):
                        name = cleaned_df.loc[idx, 'name'].lower().replace(' ', '.')
                        cleaned_df.loc[idx, col] = f"{name}@example.com"
                report.actions_taken.append(f"✓ Generated email addresses for missing values")
        
        elif 'gender' in col:
            # Standardize gender values
            original_values = cleaned_df[col].copy()
            cleaned_df[col] = cleaned_df[col].apply(standardize_gender)
            standardized = (cleaned_df[col] != original_values).sum()
            if standardized > 0:
                report.values_standardized += standardized
                report.actions_taken.append(f"✓ Standardized {standardized} gender values")
            # Fill missing with mode
            if cleaned_df[col].isna().any():
                mode_val = cleaned_df[col].mode()[0] if len(cleaned_df[col].mode()) > 0 else 'Other'
                cleaned_df[col] = cleaned_df[col].fillna(mode_val)
                report.actions_taken.append(f"✓ Filled missing '{col}' with mode ('{mode_val}')")
        
        elif 'date' in col:
            # Standardize date formats
            cleaned_df[col] = cleaned_df[col].apply(standardize_date)
            report.actions_taken.append(f"✓ Standardized date format in '{col}'")
            # Fill missing dates with mode or forward fill
            if cleaned_df[col].isna().any():
                mode_date = cleaned_df[col].mode()[0] if len(cleaned_df[col].mode()) > 0 else None
                if mode_date:
                    cleaned_df[col] = cleaned_df[col].fillna(mode_date)
                    report.actions_taken.append(f"✓ Filled missing '{col}' with mode")
        
        elif 'mark' in col or 'score' in col or 'grade' in col:
            # Handle numeric scores
            if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                cleaned_df[col], outliers_fixed = fix_outliers(cleaned_df[col], col)
                if outliers_fixed > 0:
                    report.outliers_fixed += outliers_fixed
                    report.actions_taken.append(f"✓ Fixed {outliers_fixed} outlier values in '{col}'")
                # Fill missing with median
                if cleaned_df[col].isna().any():
                    median_val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)
                    report.actions_taken.append(f"✓ Filled missing '{col}' with median ({median_val:.1f})")
            else:
                # Categorical grades - fill with mode
                if cleaned_df[col].isna().any():
                    mode_val = cleaned_df[col].mode()[0] if len(cleaned_df[col].mode()) > 0 else 'B'
                    cleaned_df[col] = cleaned_df[col].fillna(mode_val)
                    report.actions_taken.append(f"✓ Filled missing '{col}' with mode ('{mode_val}')")
        
        elif 'name' in col:
            # Clean name formatting
            if cleaned_df[col].dtype == 'object':
                # Remove extra spaces, title case
                cleaned_df[col] = cleaned_df[col].str.strip()
                cleaned_df[col] = cleaned_df[col].str.title()
                # Fill missing names
                if cleaned_df[col].isna().any():
                    cleaned_df[col] = cleaned_df[col].fillna('Unknown')
                    report.actions_taken.append(f"✓ Filled missing '{col}' with 'Unknown'")
        
        else:
            # General handling for other columns
            if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                # Numeric column - fill with median
                if cleaned_df[col].isna().any():
                    median_val = cleaned_df[col].median()
                    if pd.notna(median_val):
                        cleaned_df[col] = cleaned_df[col].fillna(median_val)
                        report.actions_taken.append(f"✓ Filled missing '{col}' with median")
            else:
                # Categorical column - fill with mode
                if cleaned_df[col].isna().any():
                    mode_series = cleaned_df[col].mode()
                    if len(mode_series) > 0:
                        mode_val = mode_series[0]
                        cleaned_df[col] = cleaned_df[col].fillna(mode_val)
                        report.actions_taken.append(f"✓ Filled missing '{col}' with mode")
                    else:
                        cleaned_df[col] = cleaned_df[col].fillna('Unknown')
                        report.actions_taken.append(f"✓ Filled missing '{col}' with 'Unknown'")
    
    # === STEP 4: Convert data types where appropriate ===
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == 'object':
            # Try to convert to numeric
            try:
                numeric_col = pd.to_numeric(cleaned_df[col], errors='coerce')
                # Only convert if most values are numeric
                if numeric_col.notna().sum() / len(cleaned_df) > 0.8:
                    cleaned_df[col] = numeric_col
                    report.actions_taken.append(f"✓ Converted '{col}' to numeric type")
            except:
                pass
    
    # === STEP 5: Remove columns that are still >70% missing ===
    for col in cleaned_df.columns:
        missing_pct = cleaned_df[col].isna().sum() / len(cleaned_df) * 100
        if missing_pct > 70:
            cleaned_df = cleaned_df.drop(columns=[col])
            report.actions_taken.append(f"✓ Dropped column '{col}' ({missing_pct:.1f}% missing)")
    
    report.rows_after = len(cleaned_df)
    report.columns_after = len(cleaned_df.columns)
    
    # Summary
    if report.duplicates_removed == 0 and report.outliers_fixed == 0 and len(report.actions_taken) == 0:
        report.actions_taken.append("✓ Dataset is already clean - no changes needed")
    
    return cleaned_df, report


def get_cleaning_preview(df: pd.DataFrame, max_rows: int = 10) -> Dict[str, Any]:
    """
    Generate a detailed preview of cleaning operations.
    """
    quality = analyze_data_quality(df)
    
    # Get cleaned version
    cleaned_df, report = clean_dataset(df)
    
    # Convert numpy/pandas types to native Python types for JSON serialization
    def convert_to_native(obj):
        """Convert numpy/pandas types to native Python types."""
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (pd.Series, pd.DataFrame)):
            return obj.to_dict()
        elif pd.isna(obj):
            return None
        elif isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(item) for item in obj]
        else:
            return obj
    
    # Convert dataframes to records with proper type conversion
    def df_to_records(dataframe, n_rows):
        """Convert DataFrame to list of dicts with native Python types."""
        records = []
        for _, row in dataframe.head(n_rows).iterrows():
            record = {}
            for col in dataframe.columns:
                val = row[col]
                if pd.isna(val):
                    record[col] = None
                elif isinstance(val, (np.integer, np.int64, np.int32)):
                    record[col] = int(val)
                elif isinstance(val, (np.floating, np.float64, np.float32)):
                    record[col] = float(val)
                elif isinstance(val, (np.bool_, bool)):
                    record[col] = bool(val)
                else:
                    record[col] = str(val)
            records.append(record)
        return records
    
    preview = {
        "needs_cleaning": bool(quality["needs_cleaning"]),
        "issues": quality["issues"],
        "original_shape": {
            "rows": int(quality["total_rows"]),
            "columns": int(quality["total_columns"])
        },
        "estimated_changes": {
            "duplicates_to_remove": int(quality["duplicate_rows"]),
            "columns_with_missing_data": int(len(quality["missing_values"])),
            "outliers_to_fix": int(sum(quality.get("outliers", {}).values())),
        },
        "sample_data_before": df_to_records(df, max_rows),
        "sample_data_after": df_to_records(cleaned_df, max_rows),
        "columns_before": [str(col) for col in df.columns.tolist()],
        "columns_after": [str(col) for col in cleaned_df.columns.tolist()],
        "estimated_cleaned_shape": {
            "rows": int(len(cleaned_df)),
            "columns": int(len(cleaned_df.columns))
        },
        "cleaning_actions": report.actions_taken
    }
    
    return preview



def export_cleaned_data(df: pd.DataFrame) -> bytes:
    """
    Export cleaned dataset as CSV bytes.
    """
    return df.to_csv(index=False).encode('utf-8')
