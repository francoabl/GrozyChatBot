"""
API Flask para Dashboard de Observabilidad GROZY
Expone métricas del agente vía REST API
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from pathlib import Path
from grozy_observability import metrics_system, logger

app = Flask(__name__, static_folder='dashboard', static_url_path='')
CORS(app)  # Habilitar CORS para el dashboard

# Directorio de datos
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


@app.route('/')
def index():
    """Servir el dashboard principal"""
    return send_from_directory('dashboard', 'index.html')


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Obtiene resumen completo de métricas
    
    Returns:
        JSON con todas las métricas del sistema
    """
    try:
        summary = metrics_system.get_summary()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        logger.error(f"Error al obtener métricas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics/summary', methods=['GET'])
def get_metrics_summary():
    """
    Obtiene solo las métricas principales para el dashboard
    
    Returns:
        JSON con métricas resumidas
    """
    try:
        full_summary = metrics_system.get_summary()
        
        summary = {
            'total_requests': full_summary['total_requests'],
            'success_rate': full_summary['success_rate'],
            'error_rate': full_summary['error_rate'],
            'avg_latency': full_summary['avg_latency'],
            'avg_precision': full_summary['avg_precision'],
            'avg_cpu': full_summary['avg_cpu_percent'],
            'avg_memory': full_summary['avg_memory_percent'],
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        logger.error(f"Error al obtener resumen: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics/latency', methods=['GET'])
def get_latency_metrics():
    """
    Obtiene métricas de latencia para gráficos
    
    Returns:
        JSON con historial de latencia
    """
    try:
        summary = metrics_system.get_summary()
        return jsonify({
            'success': True,
            'data': {
                'avg_latency': summary['avg_latency'],
                'p95_latency': summary['p95_latency'],
                'p99_latency': summary['p99_latency'],
                'history': summary['latency_history']
            }
        })
    except Exception as e:
        logger.error(f"Error al obtener latencia: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics/tools', methods=['GET'])
def get_tool_metrics():
    """
    Obtiene métricas de uso de herramientas
    
    Returns:
        JSON con estadísticas de herramientas
    """
    try:
        summary = metrics_system.get_summary()
        return jsonify({
            'success': True,
            'data': {
                'tool_usage': summary['tool_usage'],
                'total_calls': summary['total_tool_calls']
            }
        })
    except Exception as e:
        logger.error(f"Error al obtener métricas de herramientas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics/errors', methods=['GET'])
def get_error_metrics():
    """
    Obtiene métricas de errores
    
    Returns:
        JSON con errores recientes y estadísticas
    """
    try:
        summary = metrics_system.get_summary()
        return jsonify({
            'success': True,
            'data': {
                'error_count': summary['error_count'],
                'error_rate': summary['error_rate'],
                'recent_errors': summary['recent_errors']
            }
        })
    except Exception as e:
        logger.error(f"Error al obtener métricas de errores: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics/resources', methods=['GET'])
def get_resource_metrics():
    """
    Obtiene métricas de uso de recursos
    
    Returns:
        JSON con CPU y memoria
    """
    try:
        summary = metrics_system.get_summary()
        return jsonify({
            'success': True,
            'data': {
                'avg_cpu': summary['avg_cpu_percent'],
                'avg_memory': summary['avg_memory_percent'],
                'history': summary['resource_usage']
            }
        })
    except Exception as e:
        logger.error(f"Error al obtener recursos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics/traces', methods=['GET'])
def get_execution_traces():
    """
    Obtiene trazas de ejecución
    
    Returns:
        JSON con trazas de ejecución recientes
    """
    try:
        summary = metrics_system.get_summary()
        return jsonify({
            'success': True,
            'data': summary['execution_traces']
        })
    except Exception as e:
        logger.error(f"Error al obtener trazas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/report/generate', methods=['GET'])
def generate_report():
    """
    Genera reporte de análisis
    
    Returns:
        JSON con reporte en texto
    """
    try:
        report = metrics_system.generate_analysis_report()
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        logger.error(f"Error al generar reporte: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics/export', methods=['GET'])
def export_metrics():
    """
    Exporta métricas a archivo JSON
    
    Returns:
        JSON con confirmación y datos exportados
    """
    try:
        summary = metrics_system.export_metrics()
        return jsonify({
            'success': True,
            'message': 'Métricas exportadas a data/metrics.json',
            'data': summary
        })
    except Exception as e:
        logger.error(f"Error al exportar métricas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check
    
    Returns:
        JSON con estado del servicio
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'GROZY Observability API',
        'version': '1.0.0'
    })


if __name__ == '__main__':
    print("="*60)
    print("🚀 Servidor API de Observabilidad GROZY")
    print("="*60)
    print("📡 API REST: http://localhost:5001/api")
    print("📊 Dashboard: http://localhost:5001")
    print("="*60)
    print("\nEndpoints disponibles:")
    print("  GET  /api/metrics          - Métricas completas")
    print("  GET  /api/metrics/summary  - Resumen de métricas")
    print("  GET  /api/metrics/latency  - Métricas de latencia")
    print("  GET  /api/metrics/tools    - Uso de herramientas")
    print("  GET  /api/metrics/errors   - Errores y fallos")
    print("  GET  /api/metrics/resources - Uso de recursos")
    print("  GET  /api/metrics/traces   - Trazas de ejecución")
    print("  GET  /api/report/generate  - Generar reporte")
    print("  GET  /api/metrics/export   - Exportar métricas")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
