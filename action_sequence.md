Do the following actions:
0. Use `source ./.venv/bin/activate` command to activate proper venv before everything.
1. Run command: python scripts/01_parse_data.py data/nep/ptz.tab data/nep/ptz.lbl output/nep_ptz.csv
2. Run command: python scripts/03_remove_csv_columns.py output/nep_ptz.csv -c 0
3. Remove `output/nep_ptz.csv` file and rename `output/nep_ptz_columns_removed.csv` to `output/nep_ptz.csv`
4. Run command: python scripts/08_round_csv_columns.py output/nep_ptz.csv output/nep_ptz_rounded.csv 1 "TIME"
5. Remove `output/nep_ptz.csv` file and rename `output/nep_ptz_rounded.csv` to `output/nep_ptz.csv`
6. Rename column in `output/nep_ptz.csv` file with `sed`: `TIME` -> `TIME (SECONDS)`
7. Run command: python scripts/05_add_column_value.py output/nep_ptz.csv "TIME (SECONDS)" -4.7 -o output/nep_ptz_updated.csv
8. Remove `output/nep_ptz.csv` file and rename `output/nep_ptz_updated.csv` to `output/nep_ptz.csv`
9. Run command: python scripts/08_round_csv_columns.py output/nep_ptz.csv output/nep_ptz_rounded.csv 1 "TIME (SECONDS)"
10. Remove `output/nep_ptz.csv` file and rename `output/nep_ptz_rounded.csv` to `output/nep_ptz.csv`
11. Run command: python scripts/01_parse_data.py data/dwe/wind.tab data/dwe/wind.lbl output/dwe_wind.csv
12. Rename column in `output/dwe_wind.csv` file with `sed`: `TIME FROM ENTRY (SECONDS)` -> `TIME (SECONDS)`
13. Run command: python scripts/03_remove_csv_columns.py output/dwe_wind.csv -c 1
14. Remove `output/dwe_wind.csv` file and rename `output/dwe_wind_columns_removed.csv` to `output/dwe_wind.csv`
15. Run command: python scripts/08_round_csv_columns.py output/dwe_wind.csv output/dwe_wind_rounded.csv 1 "TIME (SECONDS)"
16. Remove `output/dwe_wind.csv` file and rename `output/dwe_wind_rounded.csv` to `output/dwe_wind.csv`
17. Run command: python scripts/04_convert_celsius_to_kelvin.py output/nep_ptz.csv "ATMOSPHERIC TEMPERATURE"
18. Rename column in `output/nep_ptz.csv` file with `sed`: `ATMOSPHERIC TEMPERATURE (DEGREES KELVIN)` -> `TEMPERATURE (KELVINS)`
19. Run command: python scripts/05_add_column_value.py output/dwe_wind.csv "TIME (SECONDS)" -166 -o output/dwe_wind_updated.csv
20. Run command: python scripts/08_round_csv_columns.py output/dwe_wind_updated.csv output/dwe_wind_rounded.csv 1 "TIME (SECONDS)"
21. Remove `output/dwe_wind_updated.csv` file
22. Remove `output/dwe_wind.csv` file and rename `output/dwe_wind_rounded.csv` to `output/dwe_wind.csv`
23. Rename column in `output/nep_ptz.csv` file with `sed`: `ATMOSPHERIC PRESSURE (BARS)` -> `PRESSURE (BARS)`
24. Rename column in `output/dwe_wind.csv` file with `sed`: `PRESSURE (BAR)` -> `PRESSURE (BARS)`
25. Run command: python scripts/01_parse_data.py data/asi/descent.tab data/asi/descent.lbl output/asi_descent.csv
26. Run command: python scripts/08_round_csv_columns.py output/asi_descent.csv output/asi_descent_rounded.csv 1 "TIME (SECONDS)"
27. Remove `output/asi_descent.csv` file and rename `output/asi_descent_rounded.csv` to `output/asi_descent.csv`
28. Replace all `-999.99` occurrences in `output/asi_descent.csv` file with `-99999.0`
29. Run command: python scripts/01_parse_data.py data/nep/scatter.tab data/nep/scatter.lbl output/nep_scatter.csv
30. Replace all `-9.999` occurrences in `output/nep_scatter.csv` file with `-99999.0`
31. Rename column in `output/nep_scatter.csv` file with `sed`: `ATMOSPHERIC PRESSURE (BARS)` -> `PRESSURE (BARS)`
32. Run command: python scripts/06_append_column.py output/nep_ptz.csv output/nep_scatter.csv --source-column "TIME (SECONDS)" --match-column "PRESSURE (BARS)" --tolerance 0.1 --output output/nep_scatter_time.csv
33. Remove `output/nep_scatter.csv` file and rename `output/nep_scatter_time.csv` to `output/nep_scatter.csv`
34. Run command: python scripts/07_move_column_to_left.py output/nep_scatter.csv "TIME (SECONDS)"
35. Run command: python scripts/08_round_csv_columns.py output/nep_scatter.csv output/nep_scatter_rounded.csv 0 "5.8 DEGREES (COUNTS)" "16 DEGREES (COUNTS)" "40 DEGREES (COUNTS)" "70 DEGREES (COUNTS)" "178 DEGREES (COUNTS)"
36. Remove `output/nep_scatter.csv` file and rename `output/nep_scatter_rounded.csv` to `output/nep_scatter.csv`
38. Run command: python scripts/02_parse_nfr_data.py data/nfr/fluxes/mctcnfdn.tab output/nfr_mctcnfdn.csv
39. Run command: python scripts/03_remove_csv_columns.py output/nfr_mctcnfdn.csv -c 0 1 8
40. Remove `output/nfr_mctcnfdn.csv` file and rename `output/nfr_mctcnfdn_columns_removed.csv` to `output/nfr_mctcnfdn.csv`
41. Rename column in `output/nfr_mctcnfdn.csv` file with `sed`: `TIME (seconds)` -> `TIME (SECONDS)`
42. Run command: python scripts/08_round_csv_columns.py output/nfr_mctcnfdn.csv output/nfr_mctcnfdn_rounded.csv 1 "TIME (SECONDS)"
43. Remove `output/nfr_mctcnfdn.csv` file and rename `output/nfr_mctcnfdn_rounded.csv` to `output/nfr_mctcnfdn.csv`
44. Rename columns in `output/nfr_mctcnfdn.csv` file with `sed`: `A_MCTCNFDN (W/m^2)` -> `A (broad infrared) (W/m^2)`, `B_MCTCNFDN (W/m^2)` -> `B (solar radiation) (W/m^2)`, `C_MCTCNFDN (W/m^2)` -> `C (water absorption) (W/m^2)`, `D_MCTCNFDN (W/m^2)` -> `D (water emission) (W/m^2)`, `E_MCTCNFDN (W/m^2)` -> `E (methane absorption) (W/m^2)`, `F_MCTCNFDN (W/m^2)` -> `F (blind) (W/m^2)`
45. Run command: python scripts/11_average_consecutive_rows.py output/dwe_wind.csv
46. Run command: python scripts/11_average_consecutive_rows.py output/dwe_wind_averaged.csv
47. Run command: python scripts/11_average_consecutive_rows.py output/dwe_wind_averaged_averaged.csv
48. Run command: python scripts/08_round_csv_columns.py output/dwe_wind_averaged_averaged_averaged.csv output/dwe_wind_rounded.csv 1 "TIME (SECONDS)"
49. Remove `output/dwe_wind.csv`, `output/dwe_wind_averaged.csv`, `output/dwe_wind_averaged_averaged.csv`, `output/dwe_wind_averaged_averaged_averaged.csv` and `output/dwe_wind_rounded.csv` files and rename `output/dwe_wind_rounded2.csv` to `output/dwe_wind.csv`
50. Run command: python scripts/09_join_csv_files.py output/asi_descent.csv output/dwe_wind.csv output/nep_scatter.csv output/nfr_mctcnfdn.csv -o output/joined_data.csv -k "TIME (SECONDS)"
51. Run command: python scripts/10_fill_missing_values.py
52. Run command: python scripts/08_round_csv_columns.py output/joined_data_filled.csv output/data.csv 4 "nep_scatter: PRESSURE (BARS)" "asi_descent: ALTITUDE (KM)" "asi_descent: PRESSURE (BARS)" "asi_descent: DENSITY (KG/M^3)" "asi_descent: GRAVITY (M/S^2)" "asi_descent: dz/dt (M/S)" "asi_descent: dT/dz (KELVINS/KILOMETER)" "nfr_mctcnfdn: A (broad infrared) (W/m^2)" "nfr_mctcnfdn: B (solar radiation) (W/m^2)" "nfr_mctcnfdn: C (water absorption) (W/m^2)" "nfr_mctcnfdn: D (water emission) (W/m^2)" "nfr_mctcnfdn: E (methane absorption) (W/m^2)" "dwe_wind: TEMPERATURE (KELVINS)" "dwe_wind: PRESSURE (BARS)" "dwe_wind: WIND (METER SECOND^-1)"
53. Run command: python scripts/01_parse_data.py data/nep/tempvolt.tab data/nep/tempvolt.lbl output/nep_tempvolt.csv
54. Rename column in `output/nep_tempvolt.csv` file with `sed`: `ATMOSPHERIC PRESSURE (BARS)` -> `PRESSURE (BARS)`
55. Run command: python scripts/06_append_column.py output/nep_tempvolt.csv output/nep_ptz.csv --source-column "FORWARD CHANNEL (DEGREES CELSIUS)" --match-column "PRESSURE (BARS)" --tolerance 0.1 --output output/nep_calibration_forward.csv
56. Run command: python scripts/06_append_column.py output/nep_tempvolt.csv output/nep_calibration_forward.csv --source-column "BACKWARD CHANNEL (DEGREES CELSIUS)" --match-column "PRESSURE (BARS)" --tolerance 0.1 --output output/nep_calibration_forward_backward.csv
57. Remove `output/nep_calibration_forward.csv` file and rename `output/nep_calibration_forward_backward.csv` to `output/nep_calibration.csv`
58. Run command: python scripts/12_fill_gaps.py output/nep_baseoffs_A.csv output/nep_baseoffs_A_extrapolated.csv --extrapolate-end 120 -p 2 -o 3
59. Run command: python scripts/12_fill_gaps.py output/nep_baseoffs_B.csv output/nep_baseoffs_B_extrapolated.csv --extrapolate-end 120 -p 2 -o 3
60. Run command: python scripts/08_round_csv_columns.py output/nep_baseoffs_A_extrapolated.csv output/nep_baseoffs_A_extrapolated_rounded.csv 2 "INSTRUMENT TEMPERATURE, FORWARD (DEGREES CELSIUS)"
61. Run command: python scripts/08_round_csv_columns.py output/nep_baseoffs_A_extrapolated_rounded.csv output/nep_baseoffs_A_extrapolated_rounded2.csv 0 "5.8 DEGREES (COUNTS)" "16 DEGREES (COUNTS)" "40 DEGREES (COUNTS)" "70 DEGREES (COUNTS)"
62. Remove `output/nep_baseoffs_A_extrapolated.csv` and `output/nep_baseoffs_A_extrapolated_rounded.csv` files and rename `output/nep_baseoffs_A_extrapolated_rounded2.csv` to `output/nep_baseoffs_A_extrapolated.csv`
63. Run command: python scripts/08_round_csv_columns.py output/nep_baseoffs_B_extrapolated.csv output/nep_baseoffs_B_extrapolated_rounded.csv 2 "INSTRUMENT TEMPERATURE, BACKWARD (DEGREES CELSIUS)"
64. Run command: python scripts/08_round_csv_columns.py output/nep_baseoffs_B_extrapolated_rounded.csv output/nep_baseoffs_B_extrapolated_rounded2.csv 0 "178 DEGREES (COUNTS)"
65. Remove `output/nep_baseoffs_B_extrapolated.csv` and `output/nep_baseoffs_B_extrapolated_rounded.csv` files and rename `output/nep_baseoffs_B_extrapolated_rounded2.csv` to `output/output/nep_baseoffs_B_extrapolated.csv`
66. Run command: python scripts/12_fill_gaps.py output/nep_calibration.csv output/nep_calibration_extrapolated.csv "FORWARD CHANNEL (DEGREES CELSIUS)" "BACKWARD CHANNEL (DEGREES CELSIUS)" -p -1 -o 4
67. Run command: python scripts/08_round_csv_columns.py output/nep_calibration_extrapolated.csv output/nep_calibration_extrapolated_rounded.csv 2 "FORWARD CHANNEL (DEGREES CELSIUS)" "BACKWARD CHANNEL (DEGREES CELSIUS)"
68. Remove `output/nep_calibration_extrapolated.csv` file and rename `output/nep_calibration_extrapolated_rounded.csv` to `output/nep_calibration_extrapolated.csv`
69. Rename column in `output/nep_baseoffs_A_extrapolated.csv` file with `sed`: `"INSTRUMENT TEMPERATURE, FORWARD (DEGREES CELSIUS)"` -> `FORWARD CHANNEL (DEGREES CELSIUS)`
70. Rename column in `output/nep_baseoffs_B_extrapolated.csv` file with `sed`: `"INSTRUMENT TEMPERATURE, BACKWARD (DEGREES CELSIUS)"` -> `BACKWARD CHANNEL (DEGREES CELSIUS)`
71. Run command: python scripts/06_append_column.py output/nep_baseoffs_A_extrapolated.csv output/nep_calibration_extrapolated.csv --source-column "5.8 DEGREES (COUNTS)" --match-column "FORWARD CHANNEL (DEGREES CELSIUS)" --tolerance 0.01 --output output/nep_calibration_baseoffs_extrapolated.csv
72. Run command: python scripts/06_append_column.py output/nep_baseoffs_A_extrapolated.csv output/nep_calibration_baseoffs_extrapolated.csv --source-column "16 DEGREES (COUNTS)" --match-column "FORWARD CHANNEL (DEGREES CELSIUS)" --tolerance 0.01 --output output/nep_calibration_baseoffs_extrapolated2.csv
73. Run command: python scripts/06_append_column.py output/nep_baseoffs_A_extrapolated.csv output/nep_calibration_baseoffs_extrapolated2.csv --source-column "40 DEGREES (COUNTS)" --match-column "FORWARD CHANNEL (DEGREES CELSIUS)" --tolerance 0.01 --output output/nep_calibration_baseoffs_extrapolated3.csv
74. Run command: python scripts/06_append_column.py output/nep_baseoffs_A_extrapolated.csv output/nep_calibration_baseoffs_extrapolated3.csv --source-column "70 DEGREES (COUNTS)" --match-column "FORWARD CHANNEL (DEGREES CELSIUS)" --tolerance 0.01 --output output/nep_calibration_baseoffs_extrapolated4.csv
75. Run command: python scripts/06_append_column.py output/nep_baseoffs_B_extrapolated.csv output/nep_calibration_baseoffs_extrapolated4.csv --source-column "178 DEGREES (COUNTS)" --match-column "BACKWARD CHANNEL (DEGREES CELSIUS)" --tolerance 0.01 --output output/nep_calibration_baseoffs_extrapolated5.csv
76. Remove `output/nep_calibration_baseoffs_extrapolated.csv`, `output/nep_calibration_baseoffs_extrapolated2.csv`, `output/nep_calibration_baseoffs_extrapolated3.csv` and `output/nep_calibration_baseoffs_extrapolated4.csv` files and rename `output/nep_calibration_baseoffs_extrapolated5.csv` to `output/nep_calibration_baseoffs_extrapolated.csv`
77. Run command: python scripts/13_arithmetic_csv_columns.py output/nep_scatter.csv output/nep_calibration_baseoffs_extrapolated.csv output/nep_scatter_corrected.csv --index-column "TIME (SECONDS)" --target-column "5.8 DEGREES (COUNTS)" --operation divide --source-file file2
78. Run command: python scripts/13_arithmetic_csv_columns.py output/nep_scatter_corrected.csv output/nep_calibration_baseoffs_extrapolated.csv output/nep_scatter_corrected2.csv --index-column "TIME (SECONDS)" --target-column "16 DEGREES (COUNTS)" --operation divide --source-file file2
79. Run command: python scripts/13_arithmetic_csv_columns.py output/nep_scatter_corrected2.csv output/nep_calibration_baseoffs_extrapolated.csv output/nep_scatter_corrected3.csv --index-column "TIME (SECONDS)" --target-column "40 DEGREES (COUNTS)" --operation divide --source-file file2
80. Run command: python scripts/13_arithmetic_csv_columns.py output/nep_scatter_corrected3.csv output/nep_calibration_baseoffs_extrapolated.csv output/nep_scatter_corrected4.csv --index-column "TIME (SECONDS)" --target-column "70 DEGREES (COUNTS)" --operation divide --source-file file2
81. Run command: python scripts/13_arithmetic_csv_columns.py output/nep_scatter_corrected4.csv output/nep_calibration_baseoffs_extrapolated.csv output/nep_scatter_corrected5.csv --index-column "TIME (SECONDS)" --target-column "178 DEGREES (COUNTS)" --operation divide --source-file file2
82. Remove `output/nep_scatter_corrected.csv`, `output/nep_scatter_corrected2.csv`, `output/nep_scatter_corrected3.csv` and `output/nep_scatter_corrected4.csv` files and rename `output/nep_scatter_corrected5.csv` to `output/nep_scatter_corrected.csv`
83. Run command: python scripts/08_round_csv_columns.py output/nep_scatter_corrected.csv output/nep_scatter_corrected_rounded.csv 5 "5.8 DEGREES (COUNTS)" "16 DEGREES (COUNTS)" "40 DEGREES (COUNTS)" "70 DEGREES (COUNTS)" "178 DEGREES (COUNTS)"
84. Remove `output/nep_scatter_corrected.csv` file and rename `output/nep_scatter_corrected_rounded.csv` to `output/nep_scatter_corrected.csv`