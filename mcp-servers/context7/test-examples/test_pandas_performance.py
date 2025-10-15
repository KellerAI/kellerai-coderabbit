"""
Test file for Context7 integration - Pandas performance patterns
This file demonstrates performance issues that Context7 should detect
"""

import pandas as pd
import numpy as np
from typing import List


# ISSUE 1: Reading large file without chunking
# Context7 should suggest using chunksize parameter
def load_large_csv():
    """Load large CSV file - may cause memory issues"""
    df = pd.read_csv("large_file.csv")  # No chunking
    return df[df['value'] > 100]


# ISSUE 2: Iterating with iterrows (slow)
# Context7 should suggest vectorized operations or itertuples
def process_rows_slow(df: pd.DataFrame):
    """Process dataframe rows inefficiently"""
    results = []
    for index, row in df.iterrows():  # Very slow!
        results.append(row['value'] * 2)
    return results


# ISSUE 3: Appending in a loop
# Context7 should suggest collecting data then concat
def append_in_loop(data_list: List[dict]):
    """Append data in loop - creates many copies"""
    df = pd.DataFrame()
    for item in data_list:
        df = df.append(item, ignore_index=True)  # Also deprecated!
    return df


# ISSUE 4: Using deprecated append method
# Context7 should suggest using pd.concat
def use_deprecated_append(df1: pd.DataFrame, df2: pd.DataFrame):
    """Use deprecated append method"""
    return df1.append(df2)  # Deprecated in pandas 2.0


# ISSUE 5: Not using vectorized operations
# Context7 should suggest vectorization
def calculate_non_vectorized(df: pd.DataFrame):
    """Calculate values without vectorization"""
    results = []
    for val in df['price']:
        if val > 100:
            results.append(val * 1.1)
        else:
            results.append(val)
    return results


# ISSUE 6: Inefficient filtering
# Context7 should suggest boolean indexing
def filter_inefficiently(df: pd.DataFrame):
    """Filter dataframe inefficiently"""
    filtered = df[df.apply(lambda row: row['value'] > 100, axis=1)]
    return filtered


# GOOD PATTERN: Chunked reading for large files
# Context7 should recognize this as best practice
def load_large_csv_chunked(filename: str, chunk_size: int = 10000):
    """Load large CSV with chunking to manage memory"""
    chunks = []
    for chunk in pd.read_csv(filename, chunksize=chunk_size):
        # Filter each chunk before combining
        filtered_chunk = chunk[chunk['value'] > 100]
        chunks.append(filtered_chunk)
    
    return pd.concat(chunks, ignore_index=True)


# GOOD PATTERN: Using itertuples instead of iterrows
# Context7 should recognize this as performance improvement
def process_rows_fast(df: pd.DataFrame):
    """Process dataframe rows efficiently"""
    results = []
    for row in df.itertuples(index=False):
        results.append(row.value * 2)
    return results


# GOOD PATTERN: Vectorized operations
# Context7 should recognize this as optimal
def calculate_vectorized(df: pd.DataFrame):
    """Calculate values with vectorization"""
    return np.where(df['price'] > 100, df['price'] * 1.1, df['price'])


# GOOD PATTERN: Using pd.concat instead of append
# Context7 should recognize this as modern pattern
def combine_dataframes(dfs: List[pd.DataFrame]):
    """Combine multiple dataframes efficiently"""
    return pd.concat(dfs, ignore_index=True)


# GOOD PATTERN: Efficient filtering with boolean indexing
# Context7 should recognize this as correct
def filter_efficiently(df: pd.DataFrame):
    """Filter dataframe efficiently"""
    return df[df['value'] > 100]


# GOOD PATTERN: Using query for complex filters
# Context7 should recognize this as good practice
def filter_with_query(df: pd.DataFrame):
    """Filter with query method for readability"""
    return df.query('value > 100 and category == "active"')


# ISSUE 7: Not specifying dtypes on read
# Context7 should suggest dtype specification
def read_without_dtypes():
    """Read CSV without specifying dtypes - slower and more memory"""
    return pd.read_csv("data.csv")


# GOOD PATTERN: Specifying dtypes
# Context7 should recognize memory efficiency
def read_with_dtypes():
    """Read CSV with specified dtypes for efficiency"""
    dtypes = {
        'id': 'int32',
        'category': 'category',
        'value': 'float32',
        'timestamp': 'string'
    }
    
    return pd.read_csv(
        "data.csv",
        dtype=dtypes,
        parse_dates=['timestamp']
    )


# ISSUE 8: Not using categorical for repeated strings
# Context7 should suggest categorical dtype
def inefficient_string_columns(df: pd.DataFrame):
    """Keep repeated strings as object dtype - wastes memory"""
    # df['category'] stays as object dtype
    return df


# GOOD PATTERN: Using categorical for repeated values
# Context7 should recognize memory optimization
def optimize_categorical(df: pd.DataFrame):
    """Convert repeated strings to categorical"""
    df['category'] = df['category'].astype('category')
    df['status'] = df['status'].astype('category')
    return df


# GOOD PATTERN: Using eval for complex expressions
# Context7 should recognize performance benefit
def calculate_with_eval(df: pd.DataFrame):
    """Use eval for complex calculations (faster for large DataFrames)"""
    return df.eval('result = (price * quantity) - discount')
