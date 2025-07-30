#!/usr/bin/env python3
"""
Script to reduce CSV entries by averaging every pair of consecutive rows.
This reduces the dataset size by half while preserving the general trends.
"""

import pandas as pd
import argparse
import sys
from pathlib import Path


def average_consecutive_rows(input_file, output_file=None):
    """
    Average every pair of consecutive rows in a CSV file.

    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file (optional)

    Returns:
        str: Path to the output file
    """
    # Read the CSV file
    try:
        df = pd.read_csv(input_file)
        print(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

    # If we have an odd number of rows, we'll process pairs and keep the last row as-is
    num_pairs = len(df) // 2
    remaining_rows = len(df) % 2

    print(f"Processing {num_pairs} pairs of rows...")
    if remaining_rows:
        print(f"Note: {remaining_rows} row(s) will be kept as-is (odd number of total rows)")

    # Create a new dataframe for averaged results
    averaged_rows = []

    # Process pairs of rows
    for i in range(0, num_pairs * 2, 2):
        row1 = df.iloc[i]
        row2 = df.iloc[i + 1]

        # Average numerical columns, keep string columns from first row
        averaged_row = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Average numerical values
                averaged_row[col] = (row1[col] + row2[col]) / 2
            else:
                # For non-numerical columns, take the first row's value
                averaged_row[col] = row1[col]

        averaged_rows.append(averaged_row)

    # Add any remaining rows (in case of odd number of rows)
    if remaining_rows:
        for i in range(num_pairs * 2, len(df)):
            averaged_rows.append(df.iloc[i].to_dict())

    # Create new dataframe
    result_df = pd.DataFrame(averaged_rows)

    # Determine output file path
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_averaged{input_path.suffix}"

    # Save the result
    try:
        result_df.to_csv(output_file, index=False)
        print(f"Saved averaged data to: {output_file}")
        print(f"Reduced from {len(df)} rows to {len(result_df)} rows")
        print(f"Reduction: {len(df) - len(result_df)} rows ({(len(df) - len(result_df)) / len(df) * 100:.1f}%)")
        return str(output_file)
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Average consecutive rows in a CSV file to reduce dataset size")
    parser.add_argument("input_file", help="Path to input CSV file")
    parser.add_argument("-o", "--output", help="Path to output CSV file (default: input_file_averaged.csv)")

    args = parser.parse_args()

    # Check if input file exists
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist")
        sys.exit(1)

    # Process the file
    result = average_consecutive_rows(args.input_file, args.output)

    if result:
        print(f"Successfully created averaged CSV: {result}")
    else:
        print("Failed to process the CSV file")
        sys.exit(1)


if __name__ == "__main__":
    main()
