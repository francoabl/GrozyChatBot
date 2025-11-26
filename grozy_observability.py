"""
Sistema de Observabilidad para Agente GROZY
Métricas: Precisión, Latencia, Errores, Uso de Recursos, Consistencia
"""

import time
import logging
import traceback
import json
import psutil
import threading
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Configurar logging estructurado
LOG_DIR = Path("data/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'grozy_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GROZY_Observability')


class AgentMetrics:
    """
    Sistema de métricas de observabilidad para el agente GROZY
    
    Métricas implementadas:
    1. Precisión: Exactitud en selección de herramientas
    2. Latencia: Tiempo de respuesta
    3. Frecuencia de errores: Tasa de fallos
    4. Uso de recursos: CPU y memoria
    5. Consistencia: Variabilidad en respuestas similares
    """
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_latency': 0,
            'tool_calls': defaultdict(int),
            'errors': [],
            'latency_history': [],
            'precision_scores': [],
            'resource_usage': [],
            'execution_traces': [],
            'consistency_checks': []
        }
        self.lock = threading.Lock()
        logger.info("✅ Sistema de métricas inicializado")
    
    def record_request(self, success: bool, latency: float, tools_used: list, 
                      error: str = None, request_text: str = ""):
        """
        Registra una petición al agente
        
        Args:
            success: Si la petición fue exitosa
            latency: Tiempo de respuesta en segundos
            tools_used: Lista de herramientas utilizadas
            error: Mensaje de error si hubo fallo
            request_text: Texto de la petición del usuario
        """
        with self.lock:
            self.metrics['total_requests'] += 1
            timestamp = datetime.now().isoformat()
            
            if success:
                self.metrics['successful_requests'] += 1
                logger.info(f"✅ Petición exitosa - Latencia: {latency:.2f}s - Herramientas: {tools_used}")
            else:
                self.metrics['failed_requests'] += 1
                error_entry = {
                    'timestamp': timestamp,
                    'error': str(error),
                    'tools_used': tools_used,
                    'request': request_text[:200]
                }
                self.metrics['errors'].append(error_entry)
                logger.error(f"❌ Petición fallida - Error: {error}")
            
            # Registrar latencia
            self.metrics['total_latency'] += latency
            self.metrics['latency_history'].append({
                'timestamp': timestamp,
                'latency': latency,
                'success': success
            })
            
            # Limitar historial a últimos 100 registros
            if len(self.metrics['latency_history']) > 100:
                self.metrics['latency_history'] = self.metrics['latency_history'][-100:]
            
            # Registrar uso de herramientas
            for tool in tools_used:
                self.metrics['tool_calls'][tool] += 1
            
            # Registrar uso de recursos del sistema
            self._record_resource_usage()
    
    def _record_resource_usage(self):
        """Registra uso de CPU y memoria"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            resource_entry = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': memory.used / (1024 * 1024)
            }
            
            self.metrics['resource_usage'].append(resource_entry)
            
            # Limitar a últimos 50 registros
            if len(self.metrics['resource_usage']) > 50:
                self.metrics['resource_usage'] = self.metrics['resource_usage'][-50:]
                
        except Exception as e:
            logger.warning(f"⚠️ Error al registrar recursos: {e}")
    
    def record_trace(self, request: str, response: str, tools_used: list, 
                    latency: float, success: bool = True):
        """
        Registra traza completa de ejecución
        
        Args:
            request: Petición del usuario
            response: Respuesta del agente
            tools_used: Herramientas utilizadas
            latency: Tiempo de respuesta
            success: Si fue exitosa
        """
        with self.lock:
            trace = {
                'timestamp': datetime.now().isoformat(),
                'request': request[:300],
                'response': response[:500],
                'tools_used': tools_used,
                'latency': latency,
                'success': success
            }
            self.metrics['execution_traces'].append(trace)
            
            # Mantener solo las últimas 50 trazas
            if len(self.metrics['execution_traces']) > 50:
                self.metrics['execution_traces'] = self.metrics['execution_traces'][-50:]
            
            logger.info(f"📝 Traza registrada - Herramientas: {len(tools_used)}, Latencia: {latency:.2f}s")
    
    def calculate_precision(self, expected_tools: list, actual_tools: list) -> float:
        """
        Calcula precisión de selección de herramientas
        
        Precisión = Herramientas correctas / Total esperadas
        
        Args:
            expected_tools: Herramientas que deberían usarse
            actual_tools: Herramientas realmente usadas
        
        Returns:
            Score de precisión (0-1)
        """
        if not expected_tools:
            return 1.0
        
        correct = len(set(expected_tools) & set(actual_tools))
        total = len(set(expected_tools) | set(actual_tools))
        precision = correct / total if total > 0 else 0
        
        with self.lock:
            self.metrics['precision_scores'].append({
                'timestamp': datetime.now().isoformat(),
                'precision': precision,
                'expected': expected_tools,
                'actual': actual_tools
            })
            
            # Limitar historial
            if len(self.metrics['precision_scores']) > 50:
                self.metrics['precision_scores'] = self.metrics['precision_scores'][-50:]
        
        logger.info(f"🎯 Precisión calculada: {precision:.2%}")
        return precision
    
    def check_consistency(self, query: str, response: str):
        """
        Verifica consistencia en respuestas similares
        
        Args:
            query: Consulta del usuario
            response: Respuesta del agente
        """
        with self.lock:
            # Buscar consultas similares previas
            similar_count = 0
            for check in self.metrics['consistency_checks']:
                if self._similarity(query.lower(), check['query'].lower()) > 0.7:
                    similar_count += 1
            
            self.metrics['consistency_checks'].append({
                'timestamp': datetime.now().isoformat(),
                'query': query[:200],
                'response': response[:200],
                'similar_previous': similar_count
            })
            
            # Limitar historial
            if len(self.metrics['consistency_checks']) > 30:
                self.metrics['consistency_checks'] = self.metrics['consistency_checks'][-30:]
    
    def _similarity(self, str1: str, str2: str) -> float:
        """Calcula similitud simple entre dos strings"""
        words1 = set(str1.split())
        words2 = set(str2.split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0
    
    def get_summary(self) -> dict:
        """
        Obtiene resumen completo de métricas
        
        Returns:
            Diccionario con todas las métricas calculadas
        """
        with self.lock:
            # Calcular promedios
            avg_latency = (self.metrics['total_latency'] / self.metrics['total_requests'] 
                          if self.metrics['total_requests'] > 0 else 0)
            
            success_rate = (self.metrics['successful_requests'] / self.metrics['total_requests'] * 100 
                           if self.metrics['total_requests'] > 0 else 0)
            
            error_rate = (self.metrics['failed_requests'] / self.metrics['total_requests'] * 100 
                         if self.metrics['total_requests'] > 0 else 0)
            
            avg_precision = (sum(p['precision'] for p in self.metrics['precision_scores']) / 
                            len(self.metrics['precision_scores']) 
                            if self.metrics['precision_scores'] else 0)
            
            # Calcular latencia P95 y P99
            latencies = [l['latency'] for l in self.metrics['latency_history']]
            p95_latency = 0
            p99_latency = 0
            if latencies:
                sorted_latencies = sorted(latencies)
                p95_idx = int(len(sorted_latencies) * 0.95)
                p99_idx = int(len(sorted_latencies) * 0.99)
                p95_latency = sorted_latencies[p95_idx] if p95_idx < len(sorted_latencies) else sorted_latencies[-1]
                p99_latency = sorted_latencies[p99_idx] if p99_idx < len(sorted_latencies) else sorted_latencies[-1]
            
            # Recursos promedio
            avg_cpu = 0
            avg_memory = 0
            if self.metrics['resource_usage']:
                avg_cpu = sum(r['cpu_percent'] for r in self.metrics['resource_usage']) / len(self.metrics['resource_usage'])
                avg_memory = sum(r['memory_percent'] for r in self.metrics['resource_usage']) / len(self.metrics['resource_usage'])
            
            return {
                # Métricas generales
                'total_requests': self.metrics['total_requests'],
                'successful_requests': self.metrics['successful_requests'],
                'failed_requests': self.metrics['failed_requests'],
                'success_rate': round(success_rate, 2),
                'error_rate': round(error_rate, 2),
                
                # Latencia
                'avg_latency': round(avg_latency, 3),
                'p95_latency': round(p95_latency, 3),
                'p99_latency': round(p99_latency, 3),
                'latency_history': self.metrics['latency_history'][-30:],
                
                # Precisión
                'avg_precision': round(avg_precision, 3),
                'precision_history': self.metrics['precision_scores'][-20:],
                
                # Uso de herramientas
                'tool_usage': dict(self.metrics['tool_calls']),
                'total_tool_calls': sum(self.metrics['tool_calls'].values()),
                
                # Errores
                'recent_errors': self.metrics['errors'][-10:],
                'error_count': len(self.metrics['errors']),
                
                # Recursos
                'avg_cpu_percent': round(avg_cpu, 2),
                'avg_memory_percent': round(avg_memory, 2),
                'resource_usage': self.metrics['resource_usage'][-20:],
                
                # Trazabilidad
                'execution_traces': self.metrics['execution_traces'][-10:],
                'consistency_checks': len(self.metrics['consistency_checks']),
                
                # Timestamp
                'generated_at': datetime.now().isoformat()
            }
    
    def export_metrics(self, filepath: str = 'data/metrics.json'):
        """
        Exporta métricas a archivo JSON
        
        Args:
            filepath: Ruta del archivo de salida
        """
        summary = self.get_summary()
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Métricas exportadas a {filepath}")
        return summary
    
    def generate_analysis_report(self) -> str:
        """
        Genera reporte de análisis de puntos críticos
        
        Returns:
            Reporte en formato texto con hallazgos
        """
        summary = self.get_summary()
        
        report = []
        report.append("="*70)
        report.append("📊 REPORTE DE ANÁLISIS - SISTEMA GROZY")
        report.append("="*70)
        report.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Sección 1: Resumen General
        report.append("1️⃣ RESUMEN GENERAL")
        report.append("-" * 70)
        report.append(f"Total de peticiones: {summary['total_requests']}")
        report.append(f"Peticiones exitosas: {summary['successful_requests']}")
        report.append(f"Peticiones fallidas: {summary['failed_requests']}")
        report.append(f"Tasa de éxito: {summary['success_rate']:.2f}%")
        report.append(f"Tasa de error: {summary['error_rate']:.2f}%\n")
        
        # Sección 2: Métricas de Rendimiento
        report.append("2️⃣ MÉTRICAS DE RENDIMIENTO")
        report.append("-" * 70)
        report.append(f"Latencia promedio: {summary['avg_latency']:.3f}s")
        report.append(f"Latencia P95: {summary['p95_latency']:.3f}s")
        report.append(f"Latencia P99: {summary['p99_latency']:.3f}s")
        report.append(f"Precisión promedio: {summary['avg_precision']:.2%}\n")
        
        # Sección 3: Uso de Recursos
        report.append("3️⃣ USO DE RECURSOS")
        report.append("-" * 70)
        report.append(f"CPU promedio: {summary['avg_cpu_percent']:.2f}%")
        report.append(f"Memoria promedio: {summary['avg_memory_percent']:.2f}%\n")
        
        # Sección 4: Análisis de Herramientas
        report.append("4️⃣ USO DE HERRAMIENTAS")
        report.append("-" * 70)
        for tool, count in sorted(summary['tool_usage'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / summary['total_tool_calls'] * 100) if summary['total_tool_calls'] > 0 else 0
            report.append(f"  • {tool}: {count} veces ({percentage:.1f}%)")
        report.append("")
        
        # Sección 5: Puntos Críticos y Hallazgos
        report.append("5️⃣ PUNTOS CRÍTICOS Y HALLAZGOS")
        report.append("-" * 70)
        
        # Análisis de latencia
        if summary['avg_latency'] > 5.0:
            report.append("⚠️ CRÍTICO: Latencia promedio alta (>5s)")
            report.append("   Recomendación: Optimizar consultas al vector store o reducir k")
        elif summary['avg_latency'] > 3.0:
            report.append("⚠️ ADVERTENCIA: Latencia moderada (>3s)")
            report.append("   Recomendación: Revisar eficiencia de herramientas")
        else:
            report.append("✅ Latencia dentro de rangos aceptables (<3s)")
        
        # Análisis de errores
        if summary['error_rate'] > 10:
            report.append("⚠️ CRÍTICO: Tasa de errores alta (>10%)")
            report.append("   Recomendación: Revisar logs y manejo de excepciones")
        elif summary['error_rate'] > 5:
            report.append("⚠️ ADVERTENCIA: Tasa de errores moderada (>5%)")
        else:
            report.append("✅ Tasa de errores baja (<5%)")
        
        # Análisis de precisión
        if summary['avg_precision'] < 0.6:
            report.append("⚠️ CRÍTICO: Precisión baja (<60%)")
            report.append("   Recomendación: Revisar prompt del sistema y selección de herramientas")
        elif summary['avg_precision'] < 0.8:
            report.append("⚠️ ADVERTENCIA: Precisión moderada (<80%)")
        else:
            report.append("✅ Precisión alta (>80%)")
        
        # Análisis de recursos
        if summary['avg_cpu_percent'] > 80:
            report.append("⚠️ ADVERTENCIA: Uso de CPU alto (>80%)")
        if summary['avg_memory_percent'] > 80:
            report.append("⚠️ ADVERTENCIA: Uso de memoria alto (>80%)")
        
        report.append("")
        
        # Sección 6: Errores Recientes
        if summary['recent_errors']:
            report.append("6️⃣ ERRORES RECIENTES")
            report.append("-" * 70)
            for i, error in enumerate(summary['recent_errors'][-5:], 1):
                report.append(f"{i}. [{error['timestamp']}]")
                report.append(f"   Error: {error['error'][:100]}")
                report.append(f"   Herramientas: {error.get('tools_used', [])}")
                report.append("")
        
        report.append("="*70)
        
        report_text = "\n".join(report)
        
        # Guardar reporte
        report_path = LOG_DIR / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info(f"📄 Reporte generado: {report_path}")
        
        return report_text


# Instancia global del sistema de métricas
metrics_system = AgentMetrics()


if __name__ == "__main__":
    print("✅ Sistema de Observabilidad GROZY inicializado")
    print("📊 Métricas activas:")
    print("   1. Precisión - Exactitud en selección de herramientas")
    print("   2. Latencia - Tiempo de respuesta (avg, P95, P99)")
    print("   3. Frecuencia de errores - Tasa de fallos")
    print("   4. Uso de recursos - CPU y Memoria")
    print("   5. Consistencia - Variabilidad en respuestas")
