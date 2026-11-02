/**
 * Weather Data Analysis System
 * Chart.js Visualizations Controller
 * 
 * Includes:
 * 1. Line chart for temperature trends (°C)
 * 2. Bar chart for monthly rainfall (mm)
 * 3. Bar chart for monthly average temperature (°C)
 * 4. Line chart for humidity trends (%)
 */

let chartTempTrends = null;
let chartMonthlyRainfall = null;
let chartMonthlyAvgTemp = null;
let chartHumidityTrends = null;

// Palette adhering to College project specifications (Light Blue, Dark Blue, Clean Slate)
const COLORS = {
    darkBlue: '#1e40af',
    darkBlueBg: 'rgba(30, 64, 175, 0.75)',
    primaryBlue: '#0284c7',
    primaryBlueBg: 'rgba(2, 132, 199, 0.7)',
    lightBlueFill: 'rgba(2, 132, 199, 0.12)',
    tealBlue: '#0d9488',
    tealBlueFill: 'rgba(13, 148, 136, 0.12)',
    gridColor: '#e2e8f0',
    textColor: '#475569'
};

function renderAllCharts(chartData) {
    if (!chartData || !chartData.dates || chartData.dates.length === 0) {
        console.warn("No chart data available to render.");
        return;
    }

    if (typeof Chart === 'undefined') {
        console.warn("Chart.js not yet initialized, retrying in 250ms...");
        setTimeout(() => renderAllCharts(chartData), 250);
        return;
    }

    try {
        renderTemperatureTrendsChart(chartData.dates, chartData.temperatures);
    } catch (e) {
        console.error("Error rendering Temperature Trends Chart:", e);
    }

    try {
        renderMonthlyRainfallChart(chartData.monthly_labels, chartData.monthly_rain);
    } catch (e) {
        console.error("Error rendering Monthly Rainfall Chart:", e);
    }

    try {
        renderMonthlyAvgTempChart(chartData.monthly_labels, chartData.monthly_avg_temp);
    } catch (e) {
        console.error("Error rendering Monthly Avg Temp Chart:", e);
    }

    try {
        renderHumidityTrendsChart(chartData.dates, chartData.humidities);
    } catch (e) {
        console.error("Error rendering Humidity Trends Chart:", e);
    }
}

/**
 * 1. Line Chart: Temperature Trends
 */
function renderTemperatureTrendsChart(labels, data) {
    const ctx = document.getElementById('chartTempTrends');
    if (!ctx) return;

    const existing = Chart.getChart(ctx);
    if (existing) {
        existing.destroy();
    }
    chartTempTrends = null;

    chartTempTrends = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Daily Temperature (°C)',
                data: data,
                borderColor: COLORS.primaryBlue,
                backgroundColor: COLORS.lightBlueFill,
                fill: true,
                tension: 0.25,
                borderWidth: 2,
                pointRadius: labels.length > 50 ? 1 : 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: COLORS.textColor, font: { size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Temperature: ${context.parsed.y} °C`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: COLORS.gridColor },
                    ticks: {
                        color: COLORS.textColor,
                        maxTicksLimit: 12
                    },
                    title: {
                        display: true,
                        text: 'Observation Date',
                        color: COLORS.textColor,
                        font: { weight: 'bold' }
                    }
                },
                y: {
                    grid: { color: COLORS.gridColor },
                    ticks: {
                        color: COLORS.textColor,
                        callback: function(value) { return value + ' °C'; }
                    },
                    title: {
                        display: true,
                        text: 'Temperature (°C)',
                        color: COLORS.textColor,
                        font: { weight: 'bold' }
                    }
                }
            }
        }
    });
}

/**
 * 2. Bar Chart: Monthly Rainfall
 */
function renderMonthlyRainfallChart(labels, data) {
    const ctx = document.getElementById('chartMonthlyRainfall');
    if (!ctx) return;

    const existing = Chart.getChart(ctx);
    if (existing) {
        existing.destroy();
    }
    chartMonthlyRainfall = null;

    chartMonthlyRainfall = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Rainfall (mm)',
                data: data,
                backgroundColor: COLORS.primaryBlueBg,
                borderColor: COLORS.primaryBlue,
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: COLORS.textColor, font: { size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Total Rain: ${context.parsed.y} mm`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: COLORS.textColor },
                    title: {
                        display: true,
                        text: 'Month',
                        color: COLORS.textColor,
                        font: { weight: 'bold' }
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: COLORS.gridColor },
                    ticks: {
                        color: COLORS.textColor,
                        callback: function(value) { return value + ' mm'; }
                    },
                    title: {
                        display: true,
                        text: 'Precipitation (mm)',
                        color: COLORS.textColor,
                        font: { weight: 'bold' }
                    }
                }
            }
        }
    });
}

/**
 * 3. Bar Chart: Monthly Average Temperature
 */
function renderMonthlyAvgTempChart(labels, data) {
    const ctx = document.getElementById('chartMonthlyAvgTemp');
    if (!ctx) return;

    const existing = Chart.getChart(ctx);
    if (existing) {
        existing.destroy();
    }
    chartMonthlyAvgTemp = null;

    chartMonthlyAvgTemp = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monthly Mean Temp (°C)',
                data: data,
                backgroundColor: COLORS.darkBlueBg,
                borderColor: COLORS.darkBlue,
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: COLORS.textColor, font: { size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Average: ${context.parsed.y} °C`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: COLORS.textColor },
                    title: {
                        display: true,
                        text: 'Month',
                        color: COLORS.textColor,
                        font: { weight: 'bold' }
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: { color: COLORS.gridColor },
                    ticks: {
                        color: COLORS.textColor,
                        callback: function(value) { return value + ' °C'; }
                    },
                    title: {
                        display: true,
                        text: 'Mean Temperature (°C)',
                        color: COLORS.textColor,
                        font: { weight: 'bold' }
                    }
                }
            }
        }
    });
}

/**
 * 4. Line Chart: Humidity Trends
 */
function renderHumidityTrendsChart(labels, data) {
    const ctx = document.getElementById('chartHumidityTrends');
    if (!ctx) return;

    const existing = Chart.getChart(ctx);
    if (existing) {
        existing.destroy();
    }
    chartHumidityTrends = null;

    chartHumidityTrends = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Relative Humidity (%)',
                data: data,
                borderColor: COLORS.tealBlue,
                backgroundColor: COLORS.tealBlueFill,
                fill: true,
                tension: 0.25,
                borderWidth: 2,
                pointRadius: labels.length > 50 ? 1 : 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: COLORS.textColor, font: { size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Humidity: ${context.parsed.y} %`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: COLORS.gridColor },
                    ticks: {
                        color: COLORS.textColor,
                        maxTicksLimit: 12
                    },
                    title: {
                        display: true,
                        text: 'Observation Date',
                        color: COLORS.textColor,
                        font: { weight: 'bold' }
                    }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: COLORS.gridColor },
                    ticks: {
                        color: COLORS.textColor,
                        callback: function(value) { return value + ' %'; }
                    },
                    title: {
                        display: true,
                        text: 'Relative Humidity (%)',
                        color: COLORS.textColor,
                        font: { weight: 'bold' }
                    }
                }
            }
        }
    });
}

