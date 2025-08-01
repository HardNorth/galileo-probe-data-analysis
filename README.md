# Galileo mission Jovian atmosphere probe data interactive chart

This interactive chart displays data from all CSV files in the `/output` folder, allowing you to explore the Galileo probe's atmospheric descent data.

## Quick Start

1. **Run the server:**
   ```bash
   python3 serve_chart.py
   ```

2. **Open in browser:**
   The chart will automatically open at `http://localhost:8000`

## Features

### Chart Display
- **X-axis:** TIME (SECONDS) - preserved scale across all datasets
- **Y-axis:** Various measurements from all files
- **Connected data points:** Lines connect data points within each series
- **Interactive tooltips:** Hover over points to see exact values

### Controls

#### File Controls
- **Toggle entire files:** Click file buttons (asi_descent, dwe_wind, nep_ptz, nep_scatter) to enable/disable all series from that file
- **Visual feedback:** Disabled files show with gray buttons

#### Series Controls
- **Individual series toggle:** Check/uncheck boxes to show/hide specific data columns
- **Color-coded legend:** Each series has a unique color indicator
- **File identification:** Series names are prefixed with filename to distinguish duplicate column names

#### Axis Controls
- **Manual Y-axis limits:** Set custom min/max values for the Y-axis
- **Auto-scaling:** Leave limits blank for automatic scaling

## Data Handling

### Missing Data
- Empty cells, "null", "NaN", and invalid numbers are automatically filtered out
- Missing data points don't break the line connections
- Only valid time-value pairs are plotted

### Duplicate Column Names
- Files contain duplicate column names (e.g., PRESSURE, TEMPERATURE)
- Series are labeled as "filename: column_name" to distinguish sources
- Each file's data is kept separate and independently toggleable

## Files Included

1. **asi_descent.csv** - Atmospheric Structure Instrument descent data
2. **dwe_wind.csv** - Doppler Wind Experiment wind measurements  
3. **nep_scatter.csv** - Nephelometer scattering measurements at various angles
4. **nfr_mctcnfdn.csv** - Net Flux Radiometer data on different wave lengths m-corrected, temp-corrected, correlated noise removed.

## Technical Notes

- Built with Chart.js for smooth, responsive charting
- Handles large datasets efficiently (5000+ data points)
- CORS-enabled local server for secure file access
- Responsive design works on desktop and mobile devices

## Troubleshooting

- **Port 8000 in use:** Stop other servers or modify the PORT variable in `serve_chart.py`
- **Files not loading:** Ensure all CSV files are in the `/output` folder
- **Browser compatibility:** Modern browsers (Chrome, Firefox, Safari, Edge) are supported 
