#!/usr/bin/env python3
"""
Script to append a column from one CSV file to another CSV file based on
approximate matching of a common column.

Usage:
    python 06_append_column.py source.csv target.csv --source-column "COLUMN_NAME"
                               --match-column "MATCH_COLUMN" --tolerance 0.1
                               --output output.csv
"""

import pandas as pd
import argparse
import sys
import numpy as np
from typing import Optional


def find_closest_match(target_value: float, source_values: pd.Series, tolerance: float) -> Optional[int]:
    """
    Find the index of the closest matching value within tolerance.

    Args:
        target_value: Value to match against
        source_values: Series of values to search in
        tolerance: Maximum allowed difference

    Returns:
        Index of the closest match within tolerance, or None if no match found
    """
    # Calculate absolute differences
    differences = np.abs(source_values - target_value)

    # Find the minimum difference
    min_diff_idx = differences.idxmin()
    min_diff = differences.iloc[min_diff_idx]

    # Return index if within tolerance, otherwise None
    if min_diff <= tolerance:
        return min_diff_idx
    return None


def append_column_with_matching(
    source_file: str, target_file: str, source_column: str, match_column: str, tolerance: float, output_file: str
):
    """
    Append a column from source CSV to target CSV based on approximate matching.

    Args:
        source_file: Path to source CSV file
        target_file: Path to target CSV file
        source_column: Name of column to append from source
        match_column: Name of column to match on (should exist in both files)
        tolerance: Maximum allowed difference for matching
        output_file: Path to output CSV file
    """
    try:
        # Read CSV files
        print(f"Reading source file: {source_file}")
        source_df = pd.read_csv(source_file)

        print(f"Reading target file: {target_file}")
        target_df = pd.read_csv(target_file)

        # Check if required columns exist
        if source_column not in source_df.columns:
            raise ValueError(f"Source column '{source_column}' not found in {source_file}")

        if match_column not in source_df.columns:
            raise ValueError(f"Match column '{match_column}' not found in {source_file}")

        if match_column not in target_df.columns:
            raise ValueError(f"Match column '{match_column}' not found in {target_file}")

        print(f"Matching on column: {match_column}")
        print(f"Appending column: {source_column}")
        print(f"Tolerance: {tolerance}")

        # Create a copy of target dataframe for output
        result_df = target_df.copy()

        # Initialize the new column with NaN values
        result_df[source_column] = np.nan

        # Statistics
        matches_found = 0
        no_matches = 0

        # For each row in target, find matching row in source
        for idx, target_row in target_df.iterrows():
            target_match_value = target_row[match_column]

            # Skip if target match value is NaN
            if pd.isna(target_match_value):
                no_matches += 1
                continue

            # Find closest match in source
            match_idx = find_closest_match(target_match_value, source_df[match_column], tolerance)

            if match_idx is not None:
                # Copy the value from source to result
                result_df.iloc[idx, result_df.columns.get_loc(source_column)] = source_df.iloc[match_idx][
                    source_column
                ]
                matches_found += 1
            else:
                no_matches += 1

        # Save result
        print(f"Writing output to: {output_file}")
        result_df.to_csv(output_file, index=False)

        # Print statistics
        total_rows = len(target_df)
        print("\nResults:")
        print(f"Total rows processed: {total_rows}")
        print(f"Matches found: {matches_found} ({matches_found / total_rows * 100:.1f}%)")
        print(f"No matches: {no_matches} ({no_matches / total_rows * 100:.1f}%)")

        if no_matches > 0:
            print(f"\nWarning: {no_matches} rows could not be matched within tolerance {tolerance}")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Append a column from one CSV file to another based on approximate matching",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Append TIME column from nep_ptz.csv to nep_scatter.csv matching on PRESSURE
  python 06_append_column.py nep_ptz.csv nep_scatter.csv \\
    --source-column "TIME (SECONDS)" \\
    --match-column "PRESSURE (BARS)" \\
    --tolerance 0.1 \\
    --output result.csv
        """,
    )

    parser.add_argument("source_file", help="Source CSV file (to get column from)")
    parser.add_argument("target_file", help="Target CSV file (to append column to)")
    parser.add_argument("--source-column", "-s", required=True, help="Name of column to append from source file")
    parser.add_argument(
        "--match-column", "-m", required=True, help="Name of column to match on (must exist in both files)"
    )
    parser.add_argument(
        "--tolerance", "-t", type=float, default=0.1, help="Maximum allowed difference for matching (default: 0.1)"
    )
    parser.add_argument("--output", "-o", required=True, help="Output CSV file path")

    args = parser.parse_args()

    # Validate tolerance
    if args.tolerance < 0:
        print("Error: Tolerance must be non-negative")
        sys.exit(1)

    append_column_with_matching(
        args.source_file, args.target_file, args.source_column, args.match_column, args.tolerance, args.output
    )


if __name__ == "__main__":
    main()
