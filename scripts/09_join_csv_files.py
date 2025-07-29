import pandas as pd
from pathlib import Path


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


def join_csv_files(input_dir: str, output_file: str, key_column: str = "TIME (SECONDS)"):
    """
    Join all CSV files in the input directory based on a key column.
    Prefixes column names with the file name (without extension).
    Preserves original column data types.

    Args:
        input_dir (str): Directory containing CSV files
        output_file (str): Path to save the joined CSV file
        key_column (str): Column name to join on
    """
    # Get all CSV files in the input directory
    csv_files = list(Path(input_dir).glob("*.csv"))

    if not csv_files:
        raise ValueError(f"No CSV files found in {input_dir}")

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
    # Define input and output paths relative to the project root
    input_dir = "output"
    output_file = "output/joined_data.csv"

    # Join the CSV files
    join_csv_files(input_dir, output_file)
