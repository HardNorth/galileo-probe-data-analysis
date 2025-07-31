import pandas as pd
from pathlib import Path
import argparse


def infer_dtype(series):
    """
    Infer the most appropriate dtype for a series.
    Converts float columns back to int if they contain only whole numbers.
    """
    if pd.api.types.is_float_dtype(series):
        # Check if all non-NA values are integers
        non_na = series.dropna()
        if len(non_na) > 0 and all(non_na.astype(int) == non_na):
            return pd.Int64Dtype()  # Use nullable integer type to handle NaN values
    return series.dtype


def join_csv_files(csv_file_paths: list, output_file: str, key_column: str = "TIME (SECONDS)"):
    """
    Join specified CSV files based on a key column.
    Prefixes column names with the file name (without extension).
    Preserves original column data types.

    Args:
        csv_file_paths (list): List of CSV file paths to join
        output_file (str): Path to save the joined CSV file
        key_column (str): Column name to join on
    """
    # Convert string paths to Path objects
    csv_files = [Path(path) for path in csv_file_paths]

    if not csv_files:
        raise ValueError("No CSV files provided")

    # Initialize an empty list to store DataFrames
    dfs = []

    # Read each CSV file and prepare it for joining
    for csv_file in csv_files:
        # Read the CSV file with automatic dtype inference
        df = pd.read_csv(csv_file)

        # Get file name without extension
        file_prefix = csv_file.stem

        # Store original dtypes before renaming columns
        original_dtypes = {col: df[col].dtype for col in df.columns if col != key_column}

        # Rename columns to include file prefix, except for the key column
        new_columns = {col: f"{file_prefix}: {col}" for col in df.columns if col != key_column}
        df = df.rename(columns=new_columns)

        # Update dtypes dictionary with new column names
        dtypes = {new_columns[col]: dtype for col, dtype in original_dtypes.items()}

        # Store dtypes with the DataFrame for later use
        df.attrs["original_dtypes"] = dtypes

        dfs.append(df)

    # Merge all DataFrames on the key column
    result = dfs[0]
    for df in dfs[1:]:
        result = pd.merge(result, df, on=key_column, how="outer")

    # Sort by the key column
    # First, convert the key column to numeric, handling any non-numeric values
    result[key_column] = pd.to_numeric(result[key_column], errors="coerce")
    result = result.sort_values(by=key_column)

    # Restore original data types for all columns
    for df in dfs:
        for col, dtype in df.attrs["original_dtypes"].items():
            if col in result.columns:
                # For integer columns, use nullable integer type to handle NaN values
                if pd.api.types.is_integer_dtype(dtype):
                    result[col] = result[col].astype(pd.Int64Dtype())
                else:
                    result[col] = result[col].astype(dtype)

    # Convert float columns back to integer if possible
    for col in result.columns:
        if col != key_column:
            result[col] = result[col].astype(infer_dtype(result[col]))

    # Save the result
    result.to_csv(output_file, index=False)
    print("Joined CSV saved to: {}".format(output_file))

    # Print some statistics
    print("\nStatistics:")
    print("Number of files joined: {}".format(len(csv_files)))
    print("Total rows in result: {}".format(len(result)))
    print("Total columns in result: {}".format(len(result.columns)))
    print("\nFiles joined:")
    for csv_file in csv_files:
        print("- {}".format(csv_file.name))

    # Print column data types
    print("\nColumn data types:")
    for col, dtype in result.dtypes.items():
        print("- {}: {}".format(col, dtype))


if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Join multiple CSV files based on a common key column.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 09_join_csv_files.py file1.csv file2.csv file3.csv -o joined.csv
  python 09_join_csv_files.py output/*.csv -o output/joined_data.csv
  python 09_join_csv_files.py file1.csv file2.csv -o result.csv -k "TIMESTAMP"
        """,
    )

    parser.add_argument("csv_files", nargs="+", help="CSV files to join (at least one file required)")

    parser.add_argument("-o", "--output", required=True, help="Output CSV file path")

    parser.add_argument(
        "-k", "--key-column", default="TIME (SECONDS)", help="Column name to join on (default: 'TIME (SECONDS)')"
    )

    # Parse command line arguments
    args = parser.parse_args()

    # Validate that all input files exist
    for csv_file in args.csv_files:
        if not Path(csv_file).exists():
            print(f"Error: File '{csv_file}' does not exist")
            exit(1)

    # Join the CSV files
    try:
        join_csv_files(args.csv_files, args.output, args.key_column)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
