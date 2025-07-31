const CSV_FILE = 'output/data.csv'
const COMMON_PREFIX = 'common'

class InteractiveChart {
    constructor() {
        this.allData = {};
        this.chart = null;
        this.enabledFiles = new Set();
        this.enabledSeries = new Set();
        this.colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#E7E9ED', '#71B37C', '#FFA1B5', '#D63031',
            '#74B9FF', '#FDCB6E', '#6C5CE7', '#00B894', '#FD79A8',
            '#FF7043', '#8BC34A', '#03DAC6', '#FF5722', '#607D8B',
            '#795548', '#9C27B0', '#FF9800', '#4CAF50', '#E91E63',
            '#2196F3', '#FFEB3B', '#673AB7', '#009688', '#F44336',
            '#3F51B5', '#FFC107', '#8E24AA', '#26A69A', '#EF5350'
        ];
        this.seriesColorMap = new Map(); // Map series IDs to colors
        this.init().then(_ => console.log("InteractiveChart initialized"));
    }

    async init() {
        try {
            this.allData = await this.loadAllData();
            Object.keys(this.allData).forEach(key => this.enabledFiles.add(key));
            this.setupControls();
            this.createChart();
            document.getElementById('loadingMessage').style.display = 'none';
        } catch (error) {
            this.showError(`Failed to load data: ${error.message}\n${error.stack}`);
            document.getElementById('loadingMessage').style.display = 'none';
        }
    }

    async loadAllData() {
        const file = CSV_FILE;
        const response = await fetch(file);
        if (!response.ok) {
            console.error(`Failed to load ${file}: ${response.statusText}`);
        }
        const csvText = await response.text();
        return this.parseCSV(csvText);
    }

    parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        const rawHeaders = lines[0].split(',').map(h => h.trim());
        const xAxisColumn = rawHeaders[0];
        const prefixes = rawHeaders.reduce((acc, h) => {
            const prefixColumn = h.split(':');
            let prefix = null;
            if (prefixColumn.length < 2) {
                if (h === xAxisColumn) {
                    return acc;
                }
                prefix = COMMON_PREFIX;
            } else {
                prefix = prefixColumn[0].trim();
            }
            acc.add(prefix);
            return acc;
        }, new Set());
        const data = {};
        prefixes.forEach(prefix => {
            let headers = [];
            if (prefix === COMMON_PREFIX) {
                headers = rawHeaders.filter(h => !h.includes(':') || h === xAxisColumn).map(h => h.trim());
            } else {
                headers = rawHeaders.filter(h => h.startsWith(prefix + ':') || h === xAxisColumn).map(h => h === xAxisColumn ? h.trim() : h.split(':')[1].trim());
            }
            data[prefix] = {
                xAxisColumn,
                headers,
                data: {},
                filename: prefix
            };
        });

        // Parse data rows
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',');
            prefixes.forEach(prefix => {
                const prefixData = data[prefix].data;
                rawHeaders.forEach((h, index) => {
                    if (!h.startsWith(prefix + ':') && h.includes(':')) {
                        return;
                    }
                    let value = values[index] ? values[index].trim() : '';
                    const header = h.includes(':') ? h.split(':')[1].trim() : h;
                    if (!(header in prefixData)) {
                        prefixData[header] = [];
                    }
                    // Handle missing data
                    if (value === '' || value === 'null' || value === 'NaN') {
                        value = null;
                    } else {
                        const numValue = parseFloat(value);
                        value = isNaN(numValue) ? null : numValue;
                    }
                    prefixData[header].push(value);
                });
            });
        }
        return data;
    }

    setupControls() {
        this.setupFileControls();
        this.setupSeriesControls();
        this.setupAxisControls();
    }

    setupFileControls() {
        const container = document.getElementById('fileControls');

        Object.keys(this.allData).forEach(file => {
            const button = document.createElement('button');
            button.className = 'file-toggle';
            button.textContent = file;
            button.onclick = () => this.toggleFile(file, button);
            container.appendChild(button);
        });
    }

    setupSeriesControls() {
        const container = document.getElementById('seriesControls');
        let colorIndex = 0;

        Object.keys(this.allData).forEach(file => {
            const fileData = this.allData[file];
            const basename = fileData.filename;

            fileData.headers.forEach(header => {
                if (header === fileData.xAxisColumn) return; // Skip time columns

                const seriesId = `${basename}_${header}`;
                this.enabledSeries.add(seriesId);

                // Assign color to this series
                const seriesColor = this.colors[colorIndex % this.colors.length];
                this.seriesColorMap.set(seriesId, seriesColor);

                const div = document.createElement('div');
                div.className = 'checkbox-item';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = seriesId;
                checkbox.checked = true;
                checkbox.onchange = () => this.toggleSeries(seriesId);

                const label = document.createElement('label');
                label.htmlFor = seriesId;

                const colorSpan = document.createElement('span');
                colorSpan.className = 'legend-color';
                colorSpan.style.backgroundColor = seriesColor;

                label.appendChild(colorSpan);
                label.appendChild(document.createTextNode(`${basename}: ${header}`));

                div.appendChild(checkbox);
                div.appendChild(label);
                container.appendChild(div);

                colorIndex++;
            });
        });
    }

    setupAxisControls() {
        document.getElementById('xAxisMin').onchange = () => this.updateChart();
        document.getElementById('xAxisMax').onchange = () => this.updateChart();
        document.getElementById('yAxisMin').onchange = () => this.updateChart();
        document.getElementById('yAxisMax').onchange = () => this.updateChart();
        document.getElementById('resetAxesButton').onclick = () => this.resetAxes();
    }


    toggleFile(file, button) {
        if (this.enabledFiles.has(file)) {
            this.enabledFiles.delete(file);
            button.classList.add('disabled');

            // Disable all series from this file
            const fileData = this.allData[file];
            fileData.headers.forEach(header => {
                if (header !== fileData.xAxisColumn) {
                    const seriesId = `${file}_${header}`;
                    this.enabledSeries.delete(seriesId);
                    const checkbox = document.getElementById(seriesId);
                    if (checkbox) checkbox.checked = false;
                }
            });
        } else {
            this.enabledFiles.add(file);
            button.classList.remove('disabled');

            // Enable all series from this file
            const fileData = this.allData[file];
            fileData.headers.forEach(header => {
                if (header !== fileData.xAxisColumn) {
                    const seriesId = `${file}_${header}`;
                    this.enabledSeries.add(seriesId);
                    const checkbox = document.getElementById(seriesId);
                    if (checkbox) checkbox.checked = true;
                }
            });
        }

        this.updateChart();
    }

    toggleSeries(seriesId) {
        if (this.enabledSeries.has(seriesId)) {
            this.enabledSeries.delete(seriesId);
        } else {
            this.enabledSeries.add(seriesId);
        }
        this.updateChart();
    }

    checkScaleMismatch() {
        if (!this.chart || this.chart.data.datasets.length === 0) return;

        let allValues = [];
        this.chart.data.datasets.forEach(dataset => {
            dataset.data.forEach(point => {
                if (point.y !== null && !isNaN(point.y) && point.y > -99999) {
                    allValues.push(Math.abs(point.y));
                }
            });
        });

        if (allValues.length === 0) return;
        allValues.sort((a, b) => a - b);

        const min = allValues[0];
        const max = allValues[allValues.length - 1];

        // If the range spans more than 3 orders of magnitude, show the hint
        if (max / min > 1000) {
            document.getElementById('scaleHint').style.display = 'block';
        }
    }

    autoFit() {
        let allYValues = [];
        let allXValues = [];
        this.chart.data.datasets.forEach(dataset => {
            dataset.data.forEach(point => {
                if (point.y !== null && !isNaN(point.y) && point.y > -99999) {
                    allYValues.push(point.y);
                }
                if (point.x !== null && !isNaN(point.x)) {
                    allXValues.push(point.x);
                }
            });
        });

        if (allYValues.length === 0) return;
        allYValues.sort((a, b) => a - b);
        allXValues.sort((a, b) => a - b);

        // Auto-fit Y-axis
        const yMin = allYValues[0];
        const yMax = allYValues[allYValues.length - 1];
        const yRange = yMax - yMin;
        const yPadding = yRange * 0.01; // 1% padding

        document.getElementById('yAxisMin').value = Math.floor(yMin - yPadding);
        document.getElementById('yAxisMax').value = Math.ceil(yMax + yPadding);

        // Auto-fit X-axis
        if (allXValues.length === 0) return;

        const xMin = allXValues[0];
        const xMax = allXValues[allXValues.length - 1];
        const xRange = xMax - xMin;
        const xPadding = xRange * 0.01; // 1% padding for X-axis

        const newXMin = Math.max(0, xMin - xPadding);
        const newXMax = xMax + xPadding;

        document.getElementById('xAxisMin').value = newXMin.toFixed(1);
        document.getElementById('xAxisMax').value = newXMax.toFixed(1);
    }

    autoScaleAxes() {
        if (!this.chart || this.chart.data.datasets.length === 0) return;

        // Only auto-scale Y-axis if user hasn't set manual values
        const yMinInput = document.getElementById('yAxisMin').value;
        const yMaxInput = document.getElementById('yAxisMax').value;
        const xMinInput = document.getElementById('xAxisMin').value;
        const xMaxInput = document.getElementById('xAxisMax').value;

        if (yMinInput === '' && yMaxInput === '' && xMinInput === '' && xMaxInput === '') {
            this.autoFit();
        }
    }

    generateDatasets() {
        const datasets = [];

        Object.keys(this.allData).forEach(file => {
            if (!this.enabledFiles.has(file)) return;

            const fileData = this.allData[file];
            const basename = fileData.filename;

            fileData.headers.forEach(header => {
                if (header === fileData.xAxisColumn) return;

                const seriesId = `${basename}_${header}`;
                if (!this.enabledSeries.has(seriesId)) return;

                const data = [];
                const timeData = fileData.data[fileData.xAxisColumn];
                const valueData = fileData.data[header];

                for (let i = 0; i < timeData.length; i++) {
                    const time = timeData[i];
                    const value = valueData[i];

                    // Skip missing data points
                    if (time !== null && value !== null && !isNaN(time) && !isNaN(value)) {
                        data.push({ x: time, y: value });
                    }
                }

                if (data.length > 0) {
                    // Use the assigned color from the color map
                    const seriesColor = this.seriesColorMap.get(seriesId) || '#999999';
                    datasets.push({
                        label: `${basename}: ${header}`,
                        data: data,
                        borderColor: seriesColor,
                        backgroundColor: seriesColor + '20',
                        fill: false,
                        tension: 0.1
                    });
                }
            });
        });

        return datasets;
    }

    updateChart() {
        if (!this.chart) return;

        this.chart.data.datasets = this.generateDatasets();
        this.autoScaleAxes();

        // Update X-axis limits
        const xMin = document.getElementById('xAxisMin').value;
        const xMax = document.getElementById('xAxisMax').value;

        if (xMin !== '') {
            this.chart.options.scales.x.min = parseFloat(xMin);
        } else {
            delete this.chart.options.scales.x.min;
        }

        if (xMax !== '') {
            this.chart.options.scales.x.max = parseFloat(xMax);
        } else {
            delete this.chart.options.scales.x.max;
        }

        // Update Y-axis limits
        const yMin = document.getElementById('yAxisMin').value;
        const yMax = document.getElementById('yAxisMax').value;


        if (yMin !== '') {
            this.chart.options.scales.y.min = parseFloat(yMin);
        } else {
            delete this.chart.options.scales.y.min;
        }

        if (yMax !== '') {
            this.chart.options.scales.y.max = parseFloat(yMax);
        } else {
            delete this.chart.options.scales.y.max;
        }

        this.checkScaleMismatch();
        this.chart.update();
    }

    createChart() {
        const ctx = document.getElementById('dataChart').getContext('2d');

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: this.generateDatasets()
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: false // We have our own legend
                    },
                    tooltip: {
                        callbacks: {
                            title: function (context) {
                                return `Time: ${context[0].parsed.x} seconds`;
                            },
                            label: function (context) {
                                return `${context.dataset.label}: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Time (Seconds)'
                        }
                    },
                    y: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Values'
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 1,
                        hoverRadius: 3
                    },
                    line: {
                        borderWidth: 1
                    }
                }
            }
        });

        this.updateChart();
    }

    resetAxes() {
        // Clear all manual axis settings
        document.getElementById('xAxisMin').value = '';
        document.getElementById('xAxisMax').value = '';
        document.getElementById('yAxisMin').value = '';
        document.getElementById('yAxisMax').value = '';

        // Reset chart axis options
        delete this.chart.options.scales.x.min;
        delete this.chart.options.scales.x.max;
        delete this.chart.options.scales.y.min;
        delete this.chart.options.scales.y.max;

        this.updateChart();
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}
