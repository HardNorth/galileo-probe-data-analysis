#!/usr/bin/env python3
"""
Script to perform arithmetic operations (add/subtract/multiply/divide) between columns of two CSV files
based on a common index column.

Usage:
    python scripts/13_arithmetic_csv_columns.py file1.csv file2.csv output.csv \
        --index-column "TIME (SECONDS)" \
        --target-column "5.8 DEGREES (COUNTS)" \
        --operation subtract \
        --source-file file2

Example:
    # Subtract values from nep_calibration_baseoffs_extrapolated.csv from nep_scatter.csv
    python scripts/13_arithmetic_csv_columns.py \
        output/nep_scatter.csv \
        output/nep_calibration_baseoffs_extrapolated.csv \
        output/nep_scatter_corrected.csv \
        --index-column "TIME (SECONDS)" \
        --target-column "5.8 DEGREES (COUNTS)" \
        --operation subtract \
        --source-file file2
"""

import pandas as pd
import argparse
import sys
from pathlib import Path
import numpy as np


def load_csv_with_dtypes(file_path):
    """Load CSV file and preserve original data types."""
    df = pd.read_csv(file_path)

    # Store original dtypes for numeric columns
    original_dtypes = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # Check if it's integer type
            if pd.api.types.is_integer_dtype(df[col]):
                original_dtypes[col] = "int"
            else:
                original_dtypes[col] = "float"
        else:
            original_dtypes[col] = "str"

    return df, original_dtypes


def arithmetic_operation(df1, df2, index_column, target_column, operation="subtract", source_file="file2"):
    """
    Perform arithmetic operation between columns of two dataframes.

    Parameters:
    - df1, df2: Input dataframes
    - index_column: Column to match rows on
    - target_column: Column to perform operation on
    - operation: 'add', 'subtract', 'multiply', or 'divide'
    - source_file: 'file1' or 'file2' - which file's values to use as operand

    Returns:
    - Modified copy of df1 with operation performed
    """
    # Make a copy of df1 to avoid modifying original
    result_df = df1.copy()

    # Check if required columns exist
    if index_column not in df1.columns:
        raise ValueError(f"Index column '{index_column}' not found in first file")
    if index_column not in df2.columns:
        raise ValueError(f"Index column '{index_column}' not found in second file")
    if target_column not in df1.columns:
        raise ValueError(f"Target column '{target_column}' not found in first file")
    if target_column not in df2.columns:
        raise ValueError(f"Target column '{target_column}' not found in second file")

    # Merge dataframes on index column to align rows
    merged = pd.merge(df1, df2, on=index_column, how="left", suffixes=("_file1", "_file2"))

    # Get the column names after merge
    target_col_1 = f"{target_column}_file1"
    target_col_2 = f"{target_column}_file2"

    if target_col_1 not in merged.columns or target_col_2 not in merged.columns:
        # If no suffix was added, it means the column name was unique or identical
        target_col_1 = target_column
        target_col_2 = target_column
        if target_column in merged.columns:
            # This shouldn't happen with suffixes, but handle it
            print(f"Warning: Column '{target_column}' exists without suffix")

    # Determine which values to use as operands
    if source_file == "file2":
        base_values = merged[target_col_1]
        operand_values = merged[target_col_2]
    else:  # source_file == 'file1'
        base_values = merged[target_col_2]
        operand_values = merged[target_col_1]

    # Perform the operation
    if operation == "subtract":
        new_values = base_values - operand_values
    elif operation == "add":
        new_values = base_values + operand_values
    elif operation == "multiply":
        new_values = base_values * operand_values
    elif operation == "divide":
        # Handle division by zero
        with np.errstate(divide="ignore", invalid="ignore"):
            new_values = base_values / operand_values
            # Replace inf and -inf with NaN for consistency
            new_values = new_values.replace([np.inf, -np.inf], np.nan)
    else:
        raise ValueError(f"Unknown operation: {operation}. Use 'add', 'subtract', 'multiply', or 'divide'")

    # Update the result dataframe
    result_df[target_column] = new_values

    return result_df


def preserve_dtypes(df, original_dtypes):
    """Convert columns back to their original data types where possible."""
    for col, dtype in original_dtypes.items():
        if col in df.columns:
            try:
                if dtype == "int":
                    # Check if values are actually integers (no decimals)
                    if df[col].notna().all() and (df[col] == df[col].astype(int)).all():
                        df[col] = df[col].astype(int)
                    else:
                        # Keep as float if there are decimals or NaN values
                        df[col] = df[col].astype(float)
                elif dtype == "float":
                    df[col] = df[col].astype(float)
                # For string columns, pandas usually handles them correctly
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not convert column '{col}' to {dtype}: {e}")

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Perform arithmetic operations between columns of two CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("file1", help="First CSV file (target file that will be modified)")
    parser.add_argument("file2", help="Second CSV file (source of operand values)")
    parser.add_argument("output", help="Output CSV file")
    parser.add_argument("--index-column", required=True, help="Column name to use for matching rows between files")
    parser.add_argument("--target-column", required=True, help="Column name to perform operation on")
    parser.add_argument(
        "--operation",
        choices=["add", "subtract", "multiply", "divide"],
        default="subtract",
        help="Operation to perform (default: subtract)",
    )
    parser.add_argument(
        "--source-file",
        choices=["file1", "file2"],
        default="file2",
        help="Which file's values to use as operand (default: file2)",
    )

    args = parser.parse_args()

    # Check if input files exist
    if not Path(args.file1).exists():
        print(f"Error: File '{args.file1}' not found")
        sys.exit(1)
    if not Path(args.file2).exists():
        print(f"Error: File '{args.file2}' not found")
        sys.exit(1)

    try:
        # Load CSV files
        print(f"Loading {args.file1}...")
        df1, dtypes1 = load_csv_with_dtypes(args.file1)
        print(f"Loading {args.file2}...")
        df2, dtypes2 = load_csv_with_dtypes(args.file2)

        print(f"File 1 shape: {df1.shape}")
        print(f"File 2 shape: {df2.shape}")

        # Perform arithmetic operation
        operation_desc = f"{args.operation} {args.file2 if args.source_file == 'file2' else args.file1} values"
        if args.source_file == "file2":
            operation_desc = f"{args.operation} values from {args.file2}"
        else:
            operation_desc = f"{args.operation} values from {args.file1}"

        print(f"Performing operation: {operation_desc}")
        print(f"Target column: '{args.target_column}'")
        print(f"Index column: '{args.index_column}'")

        result_df = arithmetic_operation(
            df1, df2, args.index_column, args.target_column, args.operation, args.source_file
        )

        # Preserve original data types
        result_df = preserve_dtypes(result_df, dtypes1)

        # Create output directory if it doesn't exist
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save result
        result_df.to_csv(args.output, index=False)
        print(f"Result saved to: {args.output}")
        print(f"Output shape: {result_df.shape}")

        # Show some statistics
        if args.target_column in result_df.columns:
            col_data = result_df[args.target_column].dropna()
            if len(col_data) > 0:
                print(f"\nColumn '{args.target_column}' statistics after operation:")
                print(f"  Min: {col_data.min()}")
                print(f"  Max: {col_data.max()}")
                print(f"  Mean: {col_data.mean():.2f}")
                print(f"  Data type: {col_data.dtype}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
