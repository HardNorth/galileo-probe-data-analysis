0. Use `source ./.venv/bin/activate` command to activate proper venv before everything.
1. In `scripts` folder implement python script which will parse @wind.tab and @wind.lbl files and output a CSV file with column names. Parameterize tab and lbl files' paths.
2. Adjust @parse_wind_data.py script to support @ptz.tab and @ptz.lbl files: if a column in sciencific notation convert it into standart real number notation.
3. Write simple script to parse @galileo_wind_analysis.csv file, round values in the first colum (TIME FROM ENTRY (SECONDS)) to wholes, threat them as IDs, if there are 2 or more observations in the same second then drop oldest ones. Output the result CSV with "_deduplicated" suffix.
4. Update@deduplicate_wind_data.py, make it possible to input file as argument
5. Write a script to update DEGREES CELSIUS to KELVINS in @ptz_parsed.csv file
6. Implement a script to round certain column in CSV file to whole number, E.G. `TIME FROM ENTRY (SECONDS)` in @ptz_parsed.csv 
7. Implement a script to add certain value to each value in a certain column in CSV file, support negative values. E.G. -65 for each value in column `TIME FROM ENTRY (SECONDS)` in  @ptz_parsed_rounded.csv 
8. No, keep original column data type, if it's int it should stay int.
9. Implement a script to remove certain column from a CSV file: either by name, either by number.
10. Create a script which will allow to join (append) columns from one CSV to another by certain column (key). Key columns might have different names in different files. If key exists in both CSVs then each such row should be merged, if not, then the row should be just appended in the result file and missed cells should just stay empty. Sort the result CSV by key. Preserve key data type: E.G. you should not sort int as str and vice versa.
11. Update @round_csv_columns.py to be able to round till the certain number of decimal places.
12. Update @convert_celsius_to_kelvin.py file, make it accept input file path and column name.
13. Implement a script which will allow append certain column from one CSV file to another CSV file by a different column value with certain approximation.
E.G.: append `TIME (SECONDS)` column from @nep_ptz.csv file to @nep_scatter.csv file by `PRESSURE (BARS)` column, which looks like equal for both files, but if there are minor discrepancies, for instance, no more than 1 decimal number, they should be ignored. Make column names and discrepancy value configurable through arguments. Name file "06_append_column.py".
14. Implement interactive chart using HTML and JavaScript which will read all CSV files in @/output folder and draw diagram displaying all the data in files in the folder. Follow these requrements:
    1. Take "TIME" column as X axis, and other column values as Y axis.
    2. The chart should preserve X scale, but can be logarithmic at Y axis, if this is necessary.
    3. Data points should be connected with each other with edges.
    4. The chart should be interactive, means that I should be able to enable/disable display of certain columns as long as whole files.
    5. The files contain duplicate column names, this is expected, you should take it into account and provide ability to distinguish to which file a series is related.
    6. The files contain missed data: empty cells, absent lines, this is expected, you should handle it.
    The colors on series control and on charts are not fit.
    I don't see "N DEGREES (COUNTS)" columns on the chart.
    I can't display selected series from different files.
14. In `scripts` folder implement python script which will parse @tcnfdn.tab file and output a CSV file with column names. Parameterize tab file path and output CSV path. Name it "02_parse_nfr_data.py". Use `source ./.venv/bin/activate` command to activate proper venv while testing.
15. Add support of @nfr_tcnfdn.csv file to @interactive_chart.html. You also need to add more color gradient to display new columns.
16. Implement a script which will join all CSV files in @/output folder into one by a specific common column. Output CSV should:
    1. Contain file name without extension in column name, separated with colon. E.G.: "asi_descent: ALTITUDE (KM)"
    2. If a key column value is equal to another key column value in another file the result row should be merged (this should be single row in the result file)
    3. If there is no match by key column in some files then columns from these files should have empty value.
    4. The result CSV should be sorted by key column, aware of type.
    5. You should preserve column data types.
17. Implement a script which will take @joined_data.csv file and fill missed (empty) cells. Such cells should be filled with "-99999.0" if missed data is before the first or after the last value in a column. Everything in between two values should be filled with a step calculated by formula: (next value - previous value)/number of missed steps. You should preserve column data types. E.G. don't convert int columns to float. You should find integer columns "on the fly".
18. Implement a script which will allow to reduce amount of entries in a CSV file by averaging every second row values with previous line values, thus making 1 line instead of 2.
19. Update @01_parse_data.py to support 2 or more tables in LBL and TAB files like in @baseoffs.lbl and @baseoffs.tab. If there are 2 or more tables in 1 file append postfixes to result CSV file equal to table prefixes. E.G.: `OBJECT = B_TABLE` -> `nep_baseoffs_B.csv`
20. Update @09_join_csv_files.py file to accept list of CSV files in command line arguments instead of a directory, make output file also configurable.
21. Implement a script which will fill the gaps between data and extrapolation in a CSV file. File example: @nep_baseoffs_A.csv

    Take into account these requirements:
    0. Use `source ./.venv/bin/activate` command to activate proper venv before everything.
    1. Index column (X) is the first column in the specified file.
    2. Use scipy's `curve_fit` method to form polynomial function for each column, which then will be used for data interpolation and extrapolation.
    3. If a CSV contains empty values for certain columns at the beginning or the end of the table, you should extrapolate them.
    4. Parameterize specific precise for interpolation: 0 or more decimal numbers. Generate rows for each of such number based on index column. E.G. if index column contains -50 and -49, and precise is 1, then generate rows for -49.9, -49.8, etc.
    5. Parameterize specific `order` of the result polynomial as int argument, which will then will be passed to `p0` argument of `curve_fit` method as an array of 1, of `order` length.
    6. Use this function a `f` argument of `curve_fit` method:
        ```python
        def polynomial_function(x: float, *params: float) -> float:
            return sum([p*(x**i) for i, p in enumerate(params)])
        ```
