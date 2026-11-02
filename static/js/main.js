/**
 * Weather Data Analysis System
 * Main Frontend Application Script
 */

let currentPage = 1;
const perPage = 15;
let currentLocationsList = [];

document.addEventListener('DOMContentLoaded', () => {
    // Initialize system
    loadSystemStatus();
    loadLocations();
    loadAnalytics();
    loadRecords(1);
    loadQualityReport();

    setupEventListeners();
});

function setupEventListeners() {
    // 1. Upload Form
    const uploadForm = document.getElementById('uploadForm');
    const csvFileInput = document.getElementById('csvFileInput');
    const selectedFileText = document.getElementById('selectedFileText');

    if (csvFileInput) {
        csvFileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                selectedFileText.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            } else {
                selectedFileText.textContent = 'No file selected';
            }
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFormUpload);
    }

    // 2. Load Sample Data Button
    const btnLoadSample = document.getElementById('btnLoadSample');
    if (btnLoadSample) {
        btnLoadSample.addEventListener('click', handleLoadSample);
    }

    // 3. Reset Data Button
    const btnResetData = document.getElementById('btnResetData');
    if (btnResetData) {
        btnResetData.addEventListener('click', handleResetData);
    }

    // 4. Records Filter Controls
    const searchInput = document.getElementById('searchInput');
    const locationFilter = document.getElementById('locationFilter');
    const btnApplyFilter = document.getElementById('btnApplyFilter');
    const btnResetFilter = document.getElementById('btnResetFilter');

    if (btnApplyFilter) {
        btnApplyFilter.addEventListener('click', () => {
            loadRecords(1);
        });
    }

    if (searchInput) {
        searchInput.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') {
                loadRecords(1);
            }
        });
    }

    if (locationFilter) {
        locationFilter.addEventListener('change', () => {
            loadRecords(1);
        });
    }

    if (btnResetFilter) {
        btnResetFilter.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            if (locationFilter) locationFilter.value = 'all';
            const dateFrom = document.getElementById('filterDateFrom');
            const dateTo = document.getElementById('filterDateTo');
            if (dateFrom) dateFrom.value = '';
            if (dateTo) dateTo.value = '';
            loadRecords(1);
        });
    }

    // 5. Chart Location Filter
    const chartLocationSelect = document.getElementById('chartLocationSelect');
    if (chartLocationSelect) {
        chartLocationSelect.addEventListener('change', (e) => {
            loadAnalytics(e.target.value);
        });
    }

    // 6. Export Filtered Records Table
    const btnExportCSV = document.getElementById('btnExportCSV');
    if (btnExportCSV) {
        btnExportCSV.addEventListener('click', exportTableToCSV);
    }
}

/**
 * Check backend status and DB engine
 */
async function loadSystemStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        const badge = document.getElementById('dbEngineBadge');
        if (badge) {
            badge.textContent = `Database: ${data.database_engine}`;
        }
    } catch (err) {
        console.error("Failed to load status:", err);
    }
}

/**
 * Load available locations for dropdown filters
 */
async function loadLocations() {
    try {
        const res = await fetch('/api/locations');
        const data = await res.json();
        currentLocationsList = data.locations || [];

        const locationFilter = document.getElementById('locationFilter');
        const chartLocationSelect = document.getElementById('chartLocationSelect');

        const populateOptions = (selectElem, defaultLabel = "All Locations") => {
            if (!selectElem) return;
            const currentVal = selectElem.value;
            selectElem.innerHTML = `<option value="all">${defaultLabel}</option>`;
            currentLocationsList.forEach(loc => {
                const opt = document.createElement('option');
                opt.value = loc;
                opt.textContent = loc;
                selectElem.appendChild(opt);
            });
            if (currentVal && currentLocationsList.includes(currentVal)) {
                selectElem.value = currentVal;
            }
        };

        populateOptions(locationFilter, "All Locations");
        populateOptions(chartLocationSelect, "All Locations (Overall)");
    } catch (err) {
        console.error("Failed to load locations:", err);
    }
}

/**
 * Load analytics, dashboard summary cards, and charts
 */
async function loadAnalytics(location = 'all') {
    try {
        let url = `/api/analytics?location=${encodeURIComponent(location)}`;
        const res = await fetch(url);
        const data = await res.json();

        // Update Summary Cards
        if (data.has_data) {
            document.getElementById('cardTotalRecords').textContent = data.summary.total_records.toLocaleString();
            document.getElementById('cardAvgTemp').textContent = data.summary.avg_temp;
            document.getElementById('cardAvgHumidity').textContent = data.summary.avg_humidity;
            document.getElementById('cardTotalRainfall').textContent = data.summary.total_rainfall;

            // Sub-metrics
            document.getElementById('subMinTemp').textContent = `${data.summary.min_temp} °C`;
            document.getElementById('subMaxTemp').textContent = `${data.summary.max_temp} °C`;
            document.getElementById('subLocations').textContent = `${data.summary.unique_locations} Cities`;
            document.getElementById('subDateRange').textContent = data.summary.date_range;

            // Render Tables
            renderMonthlySummaryTable(data.monthly_summary);
            renderLocationSummaryTable(data.location_summary);

            // Render Charts
            renderAllCharts(data.chart_data);
        } else {
            // Reset to zeroes
            document.getElementById('cardTotalRecords').textContent = '0';
            document.getElementById('cardAvgTemp').textContent = '0.0';
            document.getElementById('cardAvgHumidity').textContent = '0.0';
            document.getElementById('cardTotalRainfall').textContent = '0.0';
            document.getElementById('subMinTemp').textContent = 'N/A';
            document.getElementById('subMaxTemp').textContent = 'N/A';
            document.getElementById('subLocations').textContent = '0';
            document.getElementById('subDateRange').textContent = 'No records';

            renderMonthlySummaryTable([]);
            renderLocationSummaryTable([]);
        }
    } catch (err) {
        console.error("Failed to load analytics:", err);
    }
}

/**
 * Render Monthly Summary Table
 */
function renderMonthlySummaryTable(monthlyList) {
    const tbody = document.getElementById('monthlySummaryTbody');
    if (!tbody) return;

    if (!monthlyList || monthlyList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 20px; color: var(--text-muted);">No monthly data available. Please upload a weather CSV file.</td></tr>`;
        return;
    }

    let rowsHtml = '';
    monthlyList.forEach(m => {
        rowsHtml += `
            <tr>
                <td><strong>${m.month_name}</strong></td>
                <td>${m.record_count}</td>
                <td><strong>${m.avg_temp} °C</strong></td>
                <td>${m.min_temp} °C</td>
                <td>${m.max_temp} °C</td>
                <td>${m.avg_humidity} %</td>
                <td><strong>${m.total_rainfall} mm</strong></td>
            </tr>
        `;
    });
    tbody.innerHTML = rowsHtml;
}

/**
 * Render Location Comparison Table
 */
function renderLocationSummaryTable(locationsList) {
    const tbody = document.getElementById('locationSummaryTbody');
    if (!tbody) return;

    if (!locationsList || locationsList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 20px; color: var(--text-muted);">No location statistics available.</td></tr>`;
        return;
    }

    let rowsHtml = '';
    locationsList.forEach(loc => {
        rowsHtml += `
            <tr>
                <td><strong>${loc.location}</strong></td>
                <td>${loc.records}</td>
                <td><strong>${loc.avg_temp} °C</strong></td>
                <td>${loc.min_temp} °C</td>
                <td>${loc.max_temp} °C</td>
                <td>${loc.avg_humidity} %</td>
                <td>${loc.total_rainfall} mm</td>
            </tr>
        `;
    });
    tbody.innerHTML = rowsHtml;
}

/**
 * Load Weather Records with Pagination and Filters
 */
async function loadRecords(page = 1) {
    currentPage = page;
    const search = document.getElementById('searchInput')?.value.trim() || '';
    const location = document.getElementById('locationFilter')?.value || 'all';
    const dateFrom = document.getElementById('filterDateFrom')?.value || '';
    const dateTo = document.getElementById('filterDateTo')?.value || '';

    let url = `/api/records?page=${page}&per_page=${perPage}&search=${encodeURIComponent(search)}&location=${encodeURIComponent(location)}`;
    if (dateFrom) url += `&date_from=${encodeURIComponent(dateFrom)}`;
    if (dateTo) url += `&date_to=${encodeURIComponent(dateTo)}`;

    try {
        const res = await fetch(url);
        const data = await res.json();
        const tbody = document.getElementById('recordsTableBody');
        const pageInfo = document.getElementById('pageInfo');
        const btnPrev = document.getElementById('btnPrevPage');
        const btnNext = document.getElementById('btnNextPage');

        if (!data.records || data.records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 30px; color: var(--text-muted);">No records found matching criteria.</td></tr>`;
            if (pageInfo) pageInfo.textContent = 'Showing 0 records';
            if (btnPrev) btnPrev.disabled = true;
            if (btnNext) btnNext.disabled = true;
            return;
        }

        let html = '';
        data.records.forEach((r, idx) => {
            const rowNumber = (data.page - 1) * data.per_page + idx + 1;
            html += `
                <tr>
                    <td>${rowNumber}</td>
                    <td><strong>${r.date}</strong></td>
                    <td>${r.location}</td>
                    <td>${r.temperature.toFixed(1)} °C</td>
                    <td>${r.humidity.toFixed(1)} %</td>
                    <td>${r.rainfall.toFixed(1)} mm</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;

        // Pagination info
        if (pageInfo) {
            const start = (data.page - 1) * data.per_page + 1;
            const end = Math.min(data.page * data.per_page, data.total);
            pageInfo.textContent = `Showing ${start}-${end} of ${data.total} records (Page ${data.page} of ${data.total_pages})`;
        }

        if (btnPrev) {
            btnPrev.disabled = data.page <= 1;
            btnPrev.onclick = () => loadRecords(data.page - 1);
        }
        if (btnNext) {
            btnNext.disabled = data.page >= data.total_pages;
            btnNext.onclick = () => loadRecords(data.page + 1);
        }

    } catch (err) {
        console.error("Failed to load records:", err);
    }
}

/**
 * Load Data Quality Report
 */
async function loadQualityReport() {
    try {
        const res = await fetch('/api/quality-report');
        const data = await res.json();

        // Update cards
        document.getElementById('reportValidCount').textContent = data.total_valid_records.toLocaleString();
        document.getElementById('reportInvalidCount').textContent = data.total_invalid_records.toLocaleString();
        document.getElementById('reportTotalUploads').textContent = data.uploads.length;

        // Populate detailed rejected rows table
        const tbody = document.getElementById('qualityLogsTbody');
        if (!tbody) return;

        if (!data.detailed_logs || data.detailed_logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 20px; color: var(--success-color); font-weight: 500;">✓ No invalid records found. All processed rows satisfied quality checks!</td></tr>`;
            return;
        }

        let html = '';
        data.detailed_logs.forEach(log => {
            html += `
                <tr>
                    <td><strong>Row ${log.row_number}</strong></td>
                    <td><span class="badge" style="background-color: #fee2e2; color: #991b1b; border-color: #fca5a5;">${log.issue_type}</span></td>
                    <td style="font-family: monospace; font-size: 0.85rem;">${escapeHtml(log.raw_data || 'N/A')}</td>
                    <td>${log.description}</td>
                    <td><span style="color: #b91c1c; font-weight: 600;">${log.action_taken}</span></td>
                </tr>
            `;
        });
        tbody.innerHTML = html;

    } catch (err) {
        console.error("Failed to load quality report:", err);
    }
}

/**
 * Handle CSV File Upload via AJAX
 */
async function handleFormUpload(e) {
    e.preventDefault();
    const fileInput = document.getElementById('csvFileInput');
    const alertBox = document.getElementById('uploadAlert');
    const uploadResultBox = document.getElementById('uploadResultInfo');

    if (!fileInput.files || fileInput.files.length === 0) {
        showAlert(alertBox, 'Please choose a CSV file to upload.', 'danger');
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    showAlert(alertBox, 'Uploading and validating CSV dataset... Please wait.', 'info');

    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showAlert(alertBox, data.message, 'success');

            // Show uploaded file details card
            if (uploadResultBox && data.upload_info) {
                const info = data.upload_info;
                uploadResultBox.style.display = 'block';
                document.getElementById('resFilename').textContent = info.filename;
                document.getElementById('resFileSize').textContent = info.file_size_formatted;
                document.getElementById('resTotalRows').textContent = info.total_rows;
                document.getElementById('resValidRows').textContent = info.valid_count;
                document.getElementById('resInvalidRows').textContent = info.invalid_count;

                // Missing values per column
                const missList = document.getElementById('resMissingList');
                if (missList && info.missing_counts) {
                    missList.innerHTML = Object.entries(info.missing_counts)
                        .map(([col, cnt]) => `<li>${col}: <strong>${cnt}</strong> missing</li>`)
                        .join('');
                }
            }

            // Refresh app sections
            await loadSystemStatus();
            await loadLocations();
            await loadAnalytics();
            await loadRecords(1);
            await loadQualityReport();

            // Clear file input
            fileInput.value = '';
            document.getElementById('selectedFileText').textContent = 'Upload complete';
        } else {
            showAlert(alertBox, data.message || 'Error uploading file.', 'danger');
            if (uploadResultBox) uploadResultBox.style.display = 'none';
        }
    } catch (err) {
        console.error("Upload error:", err);
        showAlert(alertBox, 'Network or server error during upload.', 'danger');
    }
}

/**
 * Load Sample Data
 */
async function handleLoadSample() {
    const alertBox = document.getElementById('uploadAlert');
    showAlert(alertBox, 'Loading sample weather dataset...', 'info');

    try {
        const res = await fetch('/api/load-sample', { method: 'POST' });
        const data = await res.json();

        if (res.ok && data.success) {
            showAlert(alertBox, data.message, 'success');
            await loadSystemStatus();
            await loadLocations();
            await loadAnalytics();
            await loadRecords(1);
            await loadQualityReport();
        } else {
            showAlert(alertBox, data.message || 'Failed to load sample dataset.', 'danger');
        }
    } catch (err) {
        showAlert(alertBox, 'Error communicating with server.', 'danger');
    }
}

/**
 * Reset all database tables
 */
async function handleResetData() {
    if (!confirm('Are you sure you want to clear all weather records and logs? This will reset the database for a clean demonstration.')) {
        return;
    }

    try {
        const res = await fetch('/api/reset', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            alert(data.message);
            const uploadResultBox = document.getElementById('uploadResultInfo');
            if (uploadResultBox) uploadResultBox.style.display = 'none';
            await loadSystemStatus();
            await loadLocations();
            await loadAnalytics();
            await loadRecords(1);
            await loadQualityReport();
        }
    } catch (err) {
        alert('Failed to reset database.');
    }
}

/**
 * Export currently loaded records to CSV directly in browser
 */
async function exportTableToCSV() {
    try {
        const res = await fetch('/api/records?page=1&per_page=10000');
        const data = await res.json();
        if (!data.records || data.records.length === 0) {
            alert('No records available to export.');
            return;
        }

        let csvContent = "data:text/csv;charset=utf-8,Date,Location,Temperature,Humidity,Rainfall\n";
        data.records.forEach(r => {
            csvContent += `${r.date},"${r.location}",${r.temperature},${r.humidity},${r.rainfall}\n`;
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `weather_records_export_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (err) {
        alert('Export failed.');
    }
}

/**
 * Utility: Show alert message
 */
function showAlert(elem, msg, type = 'info') {
    if (!elem) return;
    elem.className = `alert-box alert-${type}`;
    elem.textContent = msg;
    elem.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => {
            elem.style.display = 'none';
        }, 6000);
    }
}

function escapeHtml(string) {
    if (!string) return '';
    return String(string)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

