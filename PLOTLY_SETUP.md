# Plotly.js Setup Instructions

## Overview

The visualization feature requires the Plotly.js library to be downloaded and placed in the `static/lib/` directory.

## Download Plotly.js

### Option 1: Manual Download (Recommended)

1. Visit https://cdn.plotly.com/plotly-2.27.0.min.js
2. Save the file to `static/lib/plotly.min.js`

### Option 2: Using wget (Linux/Mac)

```bash
cd static/lib
wget https://cdn.plotly.com/plotly-2.27.0.min.js -O plotly.min.js
```

### Option 3: Using curl

```bash
cd static/lib
curl -o plotly.min.js https://cdn.plotly.com/plotly-2.27.0.min.js
```

### Option 4: Using PowerShell (Windows)

```powershell
Invoke-WebRequest -Uri "https://cdn.plotly.com/plotly-2.27.0.min.js" -OutFile "static\lib\plotly.min.js"
```

## Verify Installation

After downloading, verify the file exists:

```bash
# Unix/Linux/Mac
ls -lh static/lib/plotly.min.js

# Windows PowerShell
Get-Item static\lib\plotly.min.js | Format-List
```

The file should be approximately 3.1 MB in size.

## Alternative: CDN Usage

If you prefer to use a CDN instead of local hosting:

1. Open `static/app.js`
2. Find the `loadPlotly()` function
3. Change the script source from:
   ```javascript
   script.src = 'lib/plotly.min.js';
   ```
   to:
   ```javascript
   script.src = 'https://cdn.plotly.com/plotly-2.27.0.min.js';
   ```

**Note:** CDN usage requires internet connectivity and may have privacy/security implications.

## Testing

After setup, test the visualization feature:

1. Start the application
2. Execute a query that returns numeric data
3. Click the "Visualizations" tab
4. Select a chart type and configure axes
5. Verify the chart renders correctly

## Troubleshooting

### Library Not Loading

- **Error:** "Failed to load Plotly.js library"
- **Solution:** Verify the file path is correct and the file exists

### 404 Error

- **Error:** GET /lib/plotly.min.js 404
- **Solution:** Ensure the file is in `static/lib/` directory, not just `lib/`

### File Size Issues

- **Error:** Chart rendering is slow
- **Solution:** This is normal for the first load. Plotly.js is ~3MB. Consider using CDN for production.

## License

Plotly.js is released under the MIT License, which is compatible with this project.
