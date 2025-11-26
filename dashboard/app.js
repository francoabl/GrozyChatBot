/**
 * GROZY Dashboard - Aplicación JavaScript
 * Gestión de métricas de observabilidad en tiempo real
 */

// Configuración de la API
const API_BASE_URL = 'http://localhost:5000/api';
const REFRESH_INTERVAL = 5000; // 5 segundos

// Variables globales para los gráficos
let latencyChart = null;
let toolsChart = null;
let resourcesChart = null;
let errorsChart = null;

// Estado de la aplicación
let refreshTimer = null;

/**
 * Inicialización de la aplicación
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando Dashboard GROZY...');
    
    // Inicializar gráficos
    initCharts();
    
    // Cargar datos iniciales
    loadAllMetrics();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Iniciar actualización automática
    startAutoRefresh();
    
    console.log('✅ Dashboard inicializado correctamente');
});

/**
 * Configurar event listeners
 */
function setupEventListeners() {
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadAllMetrics();
    });
    
    document.getElementById('exportBtn').addEventListener('click', exportMetrics);
    document.getElementById('reportBtn').addEventListener('click', showReport);
    document.getElementById('closeModalBtn').addEventListener('click', closeModal);
    document.getElementById('copyReportBtn').addEventListener('click', copyReport);
    document.getElementById('downloadReportBtn').addEventListener('click', downloadReport);
    document.getElementById('refreshTracesBtn').addEventListener('click', loadTraces);
    document.getElementById('refreshErrorsBtn').addEventListener('click', loadErrors);
    
    // Cerrar modal al hacer clic fuera
    document.getElementById('reportModal').addEventListener('click', (e) => {
        if (e.target.id === 'reportModal') {
            closeModal();
        }
    });
}

/**
 * Inicializar todos los gráficos
 */
function initCharts() {
    // Configuración común
    Chart.defaults.color = '#cbd5e1';
    Chart.defaults.borderColor = '#475569';
    
    // Gráfico de Latencia
    const latencyCtx = document.getElementById('latencyChart').getContext('2d');
    latencyChart = new Chart(latencyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Latencia (s)',
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Segundos'
                    }
                }
            }
        }
    });
    
    // Gráfico de Herramientas
    const toolsCtx = document.getElementById('toolsChart').getContext('2d');
    toolsChart = new Chart(toolsCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Uso de Herramientas',
                data: [],
                backgroundColor: [
                    '#6366f1', '#8b5cf6', '#10b981', '#f59e0b', 
                    '#ef4444', '#06b6d4', '#ec4899'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
    
    // Gráfico de Recursos
    const resourcesCtx = document.getElementById('resourcesChart').getContext('2d');
    resourcesChart = new Chart(resourcesCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'CPU %',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Memoria %',
                    data: [],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Porcentaje %'
                    }
                }
            }
        }
    });
    
    // Gráfico de Errores
    const errorsCtx = document.getElementById('errorsChart').getContext('2d');
    errorsChart = new Chart(errorsCtx, {
        type: 'doughnut',
        data: {
            labels: ['Exitosas', 'Fallidas'],
            datasets: [{
                data: [0, 0],
                backgroundColor: ['#10b981', '#ef4444']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Cargar todas las métricas
 */
async function loadAllMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics`);
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            updateMainMetrics(data);
            updateLatencyChart(data);
            updateToolsChart(data);
            updateResourcesChart(data);
            updateErrorsChart(data);
            updateAnalysis(data);
            updateLastUpdate();
        }
    } catch (error) {
        console.error('Error al cargar métricas:', error);
        showError('Error al conectar con la API');
    }
    
    // Cargar trazas y errores
    loadTraces();
    loadErrors();
}

/**
 * Actualizar métricas principales
 */
function updateMainMetrics(data) {
    document.getElementById('totalRequests').textContent = data.total_requests || 0;
    document.getElementById('successRate').textContent = `${data.success_rate?.toFixed(1) || 0}%`;
    document.getElementById('avgLatency').textContent = `${data.avg_latency?.toFixed(2) || 0}s`;
    document.getElementById('avgPrecision').textContent = `${(data.avg_precision * 100)?.toFixed(1) || 0}%`;
    document.getElementById('avgCpu').textContent = `${data.avg_cpu_percent?.toFixed(1) || 0}%`;
    document.getElementById('avgMemory').textContent = `${data.avg_memory_percent?.toFixed(1) || 0}%`;
    
    document.getElementById('p95Latency').textContent = `${data.p95_latency?.toFixed(2) || 0}s`;
    document.getElementById('p99Latency').textContent = `${data.p99_latency?.toFixed(2) || 0}s`;
    document.getElementById('totalToolCalls').textContent = data.total_tool_calls || 0;
    document.getElementById('errorCount').textContent = data.error_count || 0;
}

/**
 * Actualizar gráfico de latencia
 */
function updateLatencyChart(data) {
    const history = data.latency_history || [];
    const labels = history.map(h => new Date(h.timestamp).toLocaleTimeString());
    const latencies = history.map(h => h.latency);
    
    latencyChart.data.labels = labels;
    latencyChart.data.datasets[0].data = latencies;
    latencyChart.update();
}

/**
 * Actualizar gráfico de herramientas
 */
function updateToolsChart(data) {
    const toolUsage = data.tool_usage || {};
    const labels = Object.keys(toolUsage);
    const values = Object.values(toolUsage);
    
    toolsChart.data.labels = labels;
    toolsChart.data.datasets[0].data = values;
    toolsChart.update();
}

/**
 * Actualizar gráfico de recursos
 */
function updateResourcesChart(data) {
    const history = data.resource_usage || [];
    const labels = history.map(h => new Date(h.timestamp).toLocaleTimeString());
    const cpu = history.map(h => h.cpu_percent);
    const memory = history.map(h => h.memory_percent);
    
    resourcesChart.data.labels = labels;
    resourcesChart.data.datasets[0].data = cpu;
    resourcesChart.data.datasets[1].data = memory;
    resourcesChart.update();
}

/**
 * Actualizar gráfico de errores
 */
function updateErrorsChart(data) {
    const successful = data.successful_requests || 0;
    const failed = data.failed_requests || 0;
    
    errorsChart.data.datasets[0].data = [successful, failed];
    errorsChart.update();
}

/**
 * Cargar trazas de ejecución
 */
async function loadTraces() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics/traces`);
        const result = await response.json();
        
        if (result.success) {
            const container = document.getElementById('tracesContainer');
            const traces = result.data || [];
            
            if (traces.length === 0) {
                container.innerHTML = '<p class="empty-state">No hay trazas disponibles</p>';
                return;
            }
            
            container.innerHTML = traces.map(trace => `
                <div class="trace-item">
                    <div class="trace-header">
                        <span class="trace-timestamp">${new Date(trace.timestamp).toLocaleString()}</span>
                        <span class="trace-latency">${trace.latency.toFixed(2)}s</span>
                    </div>
                    <div class="trace-content">
                        <div class="trace-request">
                            <strong>Petición:</strong>
                            <p>${trace.request}</p>
                        </div>
                        <div class="trace-response">
                            <strong>Respuesta:</strong>
                            <p>${trace.response}</p>
                        </div>
                    </div>
                    <div class="trace-tools">
                        ${trace.tools_used.map(tool => 
                            `<span class="tool-badge">${tool}</span>`
                        ).join('')}
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error al cargar trazas:', error);
    }
}

/**
 * Cargar errores recientes
 */
async function loadErrors() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics/errors`);
        const result = await response.json();
        
        if (result.success) {
            const container = document.getElementById('errorsContainer');
            const errors = result.data.recent_errors || [];
            
            if (errors.length === 0) {
                container.innerHTML = '<p class="empty-state">No hay errores registrados</p>';
                return;
            }
            
            container.innerHTML = errors.map(error => `
                <div class="error-item">
                    <div class="error-header">
                        <span class="error-timestamp">${new Date(error.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="error-content">
                        <strong>Error:</strong>
                        <p>${error.error}</p>
                        ${error.request ? `<p><strong>Petición:</strong> ${error.request}</p>` : ''}
                    </div>
                    ${error.tools_used?.length ? `
                        <div class="error-tools">
                            ${error.tools_used.map(tool => 
                                `<span class="tool-badge">${tool}</span>`
                            ).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error al cargar errores:', error);
    }
}

/**
 * Actualizar análisis y recomendaciones
 */
function updateAnalysis(data) {
    const container = document.getElementById('analysisContainer');
    const analyses = [];
    
    // Análisis de latencia
    if (data.avg_latency > 5.0) {
        analyses.push({
            type: 'critical',
            icon: '⚠️',
            title: 'Latencia Alta Detectada',
            message: `Latencia promedio de ${data.avg_latency.toFixed(2)}s excede el límite recomendado de 5s. Considere optimizar las consultas al vector store.`
        });
    } else if (data.avg_latency > 3.0) {
        analyses.push({
            type: 'warning',
            icon: '⚡',
            title: 'Latencia Moderada',
            message: `Latencia promedio de ${data.avg_latency.toFixed(2)}s. Revise la eficiencia de las herramientas utilizadas.`
        });
    } else {
        analyses.push({
            type: 'success',
            icon: '✅',
            title: 'Latencia Óptima',
            message: `Latencia promedio de ${data.avg_latency.toFixed(2)}s está dentro de rangos aceptables.`
        });
    }
    
    // Análisis de errores
    if (data.error_rate > 10) {
        analyses.push({
            type: 'critical',
            icon: '❌',
            title: 'Tasa de Errores Crítica',
            message: `Tasa de errores de ${data.error_rate.toFixed(1)}% excede el 10%. Revise los logs y manejo de excepciones.`
        });
    } else if (data.error_rate > 5) {
        analyses.push({
            type: 'warning',
            icon: '⚠️',
            title: 'Tasa de Errores Elevada',
            message: `Tasa de errores de ${data.error_rate.toFixed(1)}% está por encima del 5%.`
        });
    } else {
        analyses.push({
            type: 'success',
            icon: '✅',
            title: 'Tasa de Errores Baja',
            message: `Tasa de errores de ${data.error_rate.toFixed(1)}% está dentro de límites aceptables.`
        });
    }
    
    // Análisis de precisión
    if (data.avg_precision < 0.6) {
        analyses.push({
            type: 'critical',
            icon: '🎯',
            title: 'Precisión Baja',
            message: `Precisión promedio de ${(data.avg_precision * 100).toFixed(1)}% es baja. Revise el prompt del sistema y la selección de herramientas.`
        });
    } else if (data.avg_precision < 0.8) {
        analyses.push({
            type: 'warning',
            icon: '🎯',
            title: 'Precisión Moderada',
            message: `Precisión promedio de ${(data.avg_precision * 100).toFixed(1)}%. Hay margen de mejora.`
        });
    } else {
        analyses.push({
            type: 'success',
            icon: '🎯',
            title: 'Precisión Alta',
            message: `Precisión promedio de ${(data.avg_precision * 100).toFixed(1)}% es excelente.`
        });
    }
    
    // Análisis de recursos
    if (data.avg_cpu_percent > 80 || data.avg_memory_percent > 80) {
        analyses.push({
            type: 'warning',
            icon: '💻',
            title: 'Uso Elevado de Recursos',
            message: `CPU: ${data.avg_cpu_percent.toFixed(1)}%, Memoria: ${data.avg_memory_percent.toFixed(1)}%. Monitoree el rendimiento del sistema.`
        });
    }
    
    container.innerHTML = analyses.map(analysis => `
        <div class="analysis-item ${analysis.type}">
            <div class="analysis-icon">${analysis.icon}</div>
            <div class="analysis-content">
                <h3>${analysis.title}</h3>
                <p>${analysis.message}</p>
            </div>
        </div>
    `).join('');
}

/**
 * Exportar métricas
 */
async function exportMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics/export`);
        const result = await response.json();
        
        if (result.success) {
            showSuccess('Métricas exportadas correctamente a data/metrics.json');
        }
    } catch (error) {
        console.error('Error al exportar métricas:', error);
        showError('Error al exportar métricas');
    }
}

/**
 * Mostrar reporte
 */
async function showReport() {
    const modal = document.getElementById('reportModal');
    const content = document.getElementById('reportContent');
    
    modal.classList.add('active');
    content.textContent = 'Generando reporte...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/report/generate`);
        const result = await response.json();
        
        if (result.success) {
            content.textContent = result.report;
        }
    } catch (error) {
        console.error('Error al generar reporte:', error);
        content.textContent = 'Error al generar el reporte';
    }
}

/**
 * Cerrar modal
 */
function closeModal() {
    document.getElementById('reportModal').classList.remove('active');
}

/**
 * Copiar reporte
 */
function copyReport() {
    const content = document.getElementById('reportContent').textContent;
    navigator.clipboard.writeText(content);
    showSuccess('Reporte copiado al portapapeles');
}

/**
 * Descargar reporte
 */
function downloadReport() {
    const content = document.getElementById('reportContent').textContent;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `grozy_report_${new Date().toISOString()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Actualizar timestamp
 */
function updateLastUpdate() {
    document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
}

/**
 * Iniciar actualización automática
 */
function startAutoRefresh() {
    refreshTimer = setInterval(() => {
        loadAllMetrics();
    }, REFRESH_INTERVAL);
}

/**
 * Detener actualización automática
 */
function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
}

/**
 * Mostrar mensaje de éxito
 */
function showSuccess(message) {
    console.log('✅', message);
    // Aquí podrías agregar un toast notification
}

/**
 * Mostrar mensaje de error
 */
function showError(message) {
    console.error('❌', message);
    // Aquí podrías agregar un toast notification
}
