Do the following actions:
0. Use `source ./.venv/bin/activate` command to activate proper venv before everything.
1. Run command: python scripts/01_parse_data.py data/nep/ptz.tab data/nep/ptz.lbl output/nep_ptz.csv
2. Run command: python scripts/03_remove_csv_columns.py output/nep_ptz.csv -c 0
3. Remove `output/nep_ptz.csv` file and rename `output/nep_ptz_columns_removed.csv` to `output/nep_ptz.csv`
4. Run command: python scripts/08_round_csv_columns.py output/nep_ptz.csv output/nep_ptz_rounded.csv 1 "TIME"
5. Remove `output/nep_ptz.csv` file and rename `output/nep_ptz_rounded.csv` to `output/nep_ptz.csv`
6. Rename column in `output/nep_ptz.csv` file `TIME` -> `TIME (SECONDS)`
7. Run command: python scripts/05_add_column_value.py output/nep_ptz.csv "TIME (SECONDS)" -4.7 -o output/nep_ptz_updated.csv
8. Remove `output/nep_ptz.csv` file and rename `output/nep_ptz_updated.csv` to `output/nep_ptz.csv`
9. Run command: python scripts/08_round_csv_columns.py output/nep_ptz.csv output/nep_ptz_rounded.csv 1 "TIME (SECONDS)"
10. Remove `output/nep_ptz.csv` file and rename `output/nep_ptz_rounded.csv` to `output/nep_ptz.csv`
11. Run command: python scripts/01_parse_data.py data/dwe/wind.tab data/dwe/wind.lbl output/dwe_wind.csv
12. Rename column in `output/dwe_wind.csv` file `TIME FROM ENTRY (SECONDS)` -> `TIME (SECONDS)`
13. Run command: python scripts/03_remove_csv_columns.py output/dwe_wind.csv -c 1
14. Remove `output/dwe_wind.csv` file and rename `output/dwe_wind_columns_removed.csv` to `output/dwe_wind.csv`
15. Run command: python scripts/08_round_csv_columns.py output/dwe_wind.csv output/dwe_wind_rounded.csv 1 "TIME (SECONDS)"
16. Remove `output/dwe_wind.csv` file and rename `output/dwe_wind_rounded.csv` to `output/dwe_wind.csv`
17. Run command: python scripts/04_convert_celsius_to_kelvin.py output/nep_ptz.csv "ATMOSPHERIC TEMPERATURE"
18. Rename column in `output/nep_ptz.csv` file `ATMOSPHERIC TEMPERATURE (DEGREES KELVIN)` -> `TEMPERATURE (KELVINS)`
19. Run command: python scripts/05_add_column_value.py output/dwe_wind.csv "TIME (SECONDS)" -166 -o output/dwe_wind_updated.csv
20. Run command: python scripts/08_round_csv_columns.py output/dwe_wind_updated.csv output/dwe_wind_rounded.csv 1 "TIME (SECONDS)"
21. Remove `output/dwe_wind_updated.csv` file
22. Remove `output/dwe_wind.csv` file and rename `output/dwe_wind_rounded.csv` to `output/dwe_wind.csv`
23. Rename column in `output/nep_ptz.csv` file `ATMOSPHERIC PRESSURE (BARS)` -> `PRESSURE (BARS)`
24. Rename column in `output/dwe_wind.csv` file `PRESSURE (BAR)` -> `PRESSURE (BARS)`
25. Run command: python scripts/01_parse_data.py data/asi/descent.tab data/asi/descent.lbl output/asi_descent.csv
26. Run command: python scripts/08_round_csv_columns.py output/asi_descent.csv output/asi_descent_rounded.csv 1 "TIME (SECONDS)"
27. Remove `output/asi_descent.csv` file and rename `output/asi_descent_rounded.csv` to `output/asi_descent.csv`
28. Replace all `-999.99` occurrences in `output/asi_descent.csv` file with `-99999.0`
29. Run command: python scripts/01_parse_data.py data/nep/scatter.tab data/nep/scatter.lbl output/nep_scatter.csv
30. Replace all `-9.999` occurrences in `output/nep_scatter.csv` file with `-99999.0`
31. Rename column in `output/nep_scatter.csv` file `ATMOSPHERIC PRESSURE (BARS)` -> `PRESSURE (BARS)`
32. Run command: python scripts/06_append_column.py output/nep_ptz.csv output/nep_scatter.csv --source-column "TIME (SECONDS)" --match-column "PRESSURE (BARS)" --tolerance 0.1 --output output/nep_scatter_time.csv
33. Remove `output/nep_scatter.csv` file and rename `output/nep_scatter_time.csv` to `output/nep_scatter.csv`
34. Run command: python scripts/07_move_column_to_left.py output/nep_scatter.csv "TIME (SECONDS)"
35. Run command: python scripts/08_round_csv_columns.py output/nep_scatter.csv output/nep_scatter_rounded.csv 0 "5.8 DEGREES (COUNTS)" "16 DEGREES (COUNTS)" "40 DEGREES (COUNTS)" "70 DEGREES (COUNTS)" "178 DEGREES (COUNTS)"
36. Remove `output/nep_scatter.csv` file and rename `output/nep_scatter_rounded.csv` to `output/nep_scatter.csv`
38. Run command: python scripts/02_parse_nfr_data.py data/nfr/fluxes/mctcnfdn.tab output/nfr_mctcnfdn.csv
39. Run command: python scripts/03_remove_csv_columns.py output/nfr_mctcnfdn.csv -c 0 1
40. Remove `output/nfr_mctcnfdn.csv` file and rename `output/nfr_mctcnfdn_columns_removed.csv` to `output/nfr_mctcnfdn.csv`
41. Rename column in `output/nfr_mctcnfdn.csv` file `TIME (seconds)` -> `TIME (SECONDS)`
42. Run command: python scripts/08_round_csv_columns.py output/nfr_mctcnfdn.csv output/nfr_mctcnfdn_rounded.csv 1 "TIME (SECONDS)"
43. Remove `output/nfr_mctcnfdn.csv` file and rename `output/nfr_mctcnfdn_rounded.csv` to `output/nfr_mctcnfdn.csv`
44. Run command: python scripts/09_join_csv_files.py
45. Run command: python scripts/10_fill_missing_values.py
45. Run command: python scripts/08_round_csv_columns.py output/joined_data_filled.csv output/data.csv 4 "nep_scatter: PRESSURE (BARS)" "asi_descent: ALTITUDE (KM)" "asi_descent: PRESSURE (BARS)" "asi_descent: DENSITY (KG/M^3)" "asi_descent: GRAVITY (M/S^2)" "asi_descent: dz/dt (M/S)" "asi_descent: dT/dz (KELVINS/KILOMETER)" "nfr_mctcnfdn: A_MCTCNFDN (W/m^2)" "nfr_mctcnfdn: B_MCTCNFDN (W/m^2)" "nfr_mctcnfdn: C_MCTCNFDN (W/m^2)" "nfr_mctcnfdn: D_MCTCNFDN (W/m^2)" "nfr_mctcnfdn: E_MCTCNFDN (W/m^2)" "nfr_mctcnfdn: F_MCTCNFDN (W/m^2)" "nep_ptz: PRESSURE (BARS)" "nep_ptz: TEMPERATURE (KELVINS)" "nep_ptz: ALTITUDE (KILOMETERS)" "dwe_wind: TEMPERATURE (KELVINS)" "dwe_wind: PRESSURE (BARS)" "dwe_wind: WIND (METER SECOND^-1)"
