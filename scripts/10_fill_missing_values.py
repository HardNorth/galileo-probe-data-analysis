import pandas as pd


def is_integer_column(series):
    """
    Check if all non-null values in a series are integers.
    """
    non_null = series.dropna()
    if len(non_null) == 0:
        return False
    return all(float(x).is_integer() for x in non_null)


def fill_missing_values(df):
    """
    Fill missing values in the dataframe with either -99999.0 for values before first
    or after last valid value, or with interpolated values between valid points.
    Preserves integer types for columns that contain only integer values.
    """
    # First detect which columns contain only integers
    integer_columns = [col for col in df.columns if is_integer_column(df[col])]
    print("Detected integer columns:", integer_columns)

    for column in df.columns:
        # Skip the first column (TIME) as it's our index
        if column == "TIME (SECONDS)":
            continue

        # Get indices of first and last valid values
        no_na = df[column].dropna()
        valid_indices = no_na.index[no_na != -99999.0]
        if len(valid_indices) == 0:
            continue

        first_valid_idx = valid_indices[0]
        last_valid_idx = valid_indices[-1]

        # Fill values before first valid value with -99999.0
        df.loc[:first_valid_idx, column] = df.loc[:first_valid_idx, column].fillna(-99999.0)

        # Fill values after last valid value with -99999.0
        df.loc[last_valid_idx:, column] = df.loc[last_valid_idx:, column].fillna(-99999.0)

        # For values between first and last valid value, use linear interpolation
        mask = (df.index >= first_valid_idx) & (df.index <= last_valid_idx)
        df.loc[mask, column] = df.loc[mask, column].interpolate(method="linear")

        # Convert interpolated values to integers for integer columns
        if column in integer_columns:
            # Round interpolated values and convert to int
            df[column] = df[column].round().astype("Int64")  # Using Int64 to preserve NaN values

    return df


def main():
    # Read the input CSV file
    input_file = "output/joined_data.csv"
    output_file = "output/joined_data_filled.csv"

    print(f"Reading data from {input_file}")
    df = pd.read_csv(input_file)

    # Set TIME column as index for proper interpolation
    df.set_index("TIME (SECONDS)", inplace=True)

    print("Filling missing values...")
    df = fill_missing_values(df)

    # Reset index to include TIME column in the output
    df.reset_index(inplace=True)

    print(f"Saving filled data to {output_file}")
    df.to_csv(output_file, index=False)
    print("Done!")


if __name__ == "__main__":
    main()
