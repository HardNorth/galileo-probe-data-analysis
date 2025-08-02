#!/usr/bin/env python3
"""
Script to fill gaps and extrapolate data in CSV files using polynomial curve fitting.
Uses scipy's curve_fit method with parameterizable precision and polynomial order.

Usage Examples:
    # Basic usage with default parameters (precision=0, order=3)
    source ./.venv/bin/activate && python scripts/12_fill_gaps.py input.csv output.csv

    # High precision interpolation (1 decimal place) with 3rd order polynomial
    source ./.venv/bin/activate && python scripts/12_fill_gaps.py input.csv output.csv --precision 1 --order 3

    # Extrapolation beyond original data range
    source ./.venv/bin/activate && python scripts/12_fill_gaps.py input.csv output.csv \\
        --extrapolate-start -60 --extrapolate-end 80

    # Lower order polynomial for simpler curves
    source ./.venv/bin/activate && python scripts/12_fill_gaps.py input.csv output.csv --order 2
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Tuple, Union
import numpy as np
from scipy.optimize import curve_fit


def polynomial_function(x: float, *params: float) -> float:
    """Polynomial function for curve fitting."""
    return sum([p * (x**i) for i, p in enumerate(params)])


def read_csv_data(file_path: str) -> Tuple[List[str], List[List[Union[str, float]]]]:
    """
    Read CSV file and return headers and data.

    Args:
        file_path: Path to the CSV file

    Returns:
        Tuple of (headers, data_rows)
    """
    headers = []
    data_rows = []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)

        for row in reader:
            if row and row[0].strip():  # Skip empty rows
                # Convert numeric values, keep strings as-is
                processed_row = []
                for i, value in enumerate(row):
                    if i == 0:  # Index column
                        try:
                            processed_row.append(float(value))
                        except ValueError:
                            processed_row.append(value)
                    else:  # Data columns
                        try:
                            processed_row.append(float(value))
                        except ValueError:
                            processed_row.append(None)  # Handle empty/invalid values
                data_rows.append(processed_row)

    return headers, data_rows


def fit_polynomial_to_column(x_values: np.ndarray, y_values: np.ndarray, order: int) -> np.ndarray:
    """
    Fit polynomial to a data column using curve_fit.

    Args:
        x_values: Index values (x-axis)
        y_values: Data values (y-axis)
        order: Polynomial order

    Returns:
        Fitted polynomial coefficients
    """
    # Remove None values for fitting
    valid_indices = ~np.isnan(y_values)
    x_clean = x_values[valid_indices]
    y_clean = y_values[valid_indices]

    if len(x_clean) < order + 1:
        raise ValueError(f"Not enough data points ({len(x_clean)}) for polynomial order {order}")

    # Initial guess for coefficients (all ones)
    initial_guess = np.ones(order + 1)

    try:
        # Fit polynomial using curve_fit
        coefficients, _ = curve_fit(polynomial_function, x_clean, y_clean, p0=initial_guess)
        return coefficients
    except Exception as e:
        print(f"Warning: Could not fit polynomial to column. Error: {e}")
        # Fallback to simple polynomial fit
        return np.polyfit(x_clean, y_clean, order)[::-1]  # Reverse to match our polynomial convention


def generate_index_values(min_val: float, max_val: float, precision: int) -> np.ndarray:
    """
    Generate index values with specified precision.

    Args:
        min_val: Minimum index value
        max_val: Maximum index value
        precision: Number of decimal places

    Returns:
        Array of index values
    """
    step = 10 ** (-precision) if precision > 0 else 1.0
    # Generate values with proper precision
    num_points = int((max_val - min_val) / step) + 1
    return np.linspace(min_val, max_val, num_points)


def fill_gaps_and_extrapolate(
    file_path: str,
    output_path: str,
    columns: list[str],
    precision: int,
    order: int,
    extrapolate_start: float = None,
    extrapolate_end: float = None,
):
    """
    Fill gaps and extrapolate data in CSV file.

    Args:
        file_path: Input CSV file path
        output_path: Output CSV file path
        precision: Decimal precision for interpolation
        order: Polynomial order
        extrapolate_start: Start value for extrapolation (optional)
        extrapolate_end: End value for extrapolation (optional)
    """
    print(f"Reading data from {file_path}...")
    headers, data_rows = read_csv_data(file_path)

    if not data_rows:
        print("No data found in the file.")
        return

    # Extract index column (first column)
    index_values = []
    data_columns = [[] for _ in range(len(headers) - 1)]

    for row in data_rows:
        index_values.append(row[0])
        for i in range(1, len(row)):
            if i - 1 < len(data_columns):
                data_columns[i - 1].append(row[i] if len(row) > i else None)

    index_array = np.array(index_values, dtype=float)

    # Determine the range for new index values
    min_index = extrapolate_start if extrapolate_start is not None else np.min(index_array)
    max_index = extrapolate_end if extrapolate_end is not None else np.max(index_array)

    print(f"Generating new index values from {min_index} to {max_index} with precision {precision}...")
    if precision > -1:
        new_index_values = generate_index_values(min_index, max_index, precision)
    else:
        new_index_values = index_values

    # Fit polynomials and interpolate/extrapolate for each data column
    if columns:
        columns_to_process = set(columns)
    else:
        columns_to_process = set(headers[1:])

    fitted_columns = []
    for col_idx, column_data in enumerate(data_columns):
        column_name = headers[col_idx + 1]
        if column_name not in columns_to_process:
            fitted_columns.append(column_data)
            continue

        print(f"Processing column {col_idx + 1}/{len(data_columns)}: {headers[col_idx + 1]}")

        # Convert to numpy array, handling None values
        y_array = np.array([val if val is not None else np.nan for val in column_data], dtype=float)

        try:
            # Fit polynomial
            coefficients = fit_polynomial_to_column(index_array, y_array, order)

            # Generate new values using the fitted polynomial
            new_values = [polynomial_function(x, *coefficients) for x in new_index_values]
            fitted_columns.append(new_values)

            print(f"  Fitted polynomial coefficients: {coefficients}")

        except Exception as e:
            print(f"  Error processing column {headers[col_idx + 1]}: {e}")
            # Fill with zeros or interpolate linearly as fallback
            new_values = np.interp(new_index_values, index_array[~np.isnan(y_array)], y_array[~np.isnan(y_array)])
            fitted_columns.append(new_values.tolist())

    # Write results to output file
    print(f"Writing results to {output_path}...")
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write headers
        writer.writerow(headers)

        # Write data rows
        for i, index_val in enumerate(new_index_values):
            row = [index_val]
            for col_data in fitted_columns:
                row.append(col_data[i])
            writer.writerow(row)

    print(f"Successfully processed {len(new_index_values)} data points.")
    print(f"Original data points: {len(index_values)}")
    print(f"New data points: {len(new_index_values)}")


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Fill gaps and extrapolate data in CSV files using polynomial curve fitting."
    )
    parser.add_argument("input_file", help="Input CSV file path")
    parser.add_argument("output_file", help="Output CSV file path")
    parser.add_argument("columns", nargs="+", type=str, help="Columns to process (optional)")
    parser.add_argument(
        "--precision",
        "-p",
        type=int,
        default=0,
        help="Decimal precision for interpolation (default: 0). If -1, use original index values.",
    )
    parser.add_argument("--order", "-o", type=int, default=3, help="Polynomial order (default: 3)")
    parser.add_argument(
        "--extrapolate-start", type=float, default=None, help="Start value for extrapolation (optional)"
    )
    parser.add_argument("--extrapolate-end", type=float, default=None, help="End value for extrapolation (optional)")

    args = parser.parse_args()

    # Validate inputs
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)

    if args.precision < -1:
        print("Error: Precision must be -1 or greater.")
        sys.exit(1)

    if args.order < 1:
        print("Error: Polynomial order must be 1 or greater.")
        sys.exit(1)

    fill_gaps_and_extrapolate(
        args.input_file,
        args.output_file,
        args.columns,
        args.precision,
        args.order,
        args.extrapolate_start,
        args.extrapolate_end,
    )
    print("Processing completed successfully!")


if __name__ == "__main__":
    main()
