"""
Script de prueba para generar métricas del sistema de observabilidad GROZY
Ejecuta múltiples consultas al agente y genera datos para el dashboard
"""

import time
from grozy_agent_v2 import invoke_agent_with_metrics
from grozy_observability import metrics_system

print("="*70)
print("🧪 GENERADOR DE MÉTRICAS DE PRUEBA - GROZY")
print("="*70)
print("Este script ejecutará consultas de prueba para generar métricas\n")

# Consultas de prueba variadas
test_queries = [
    # Consultas simples
    {
        "query": "¿Qué productos tienes disponibles?",
        "expected_tools": ["obtener_estadisticas_categorias"]
    },
    {
        "query": "Dame estadísticas de productos",
        "expected_tools": ["obtener_estadisticas_categorias"]
    },
    
    # Búsquedas
    {
        "query": "Busca productos lácteos",
        "expected_tools": ["buscar_productos"]
    },
    {
        "query": "¿Tienes frutas frescas?",
        "expected_tools": ["buscar_productos"]
    },
    {
        "query": "Muéstrame productos de desayuno",
        "expected_tools": ["buscar_productos"]
    },
    
    # Generación de carros
    {
        "query": "Genera un carro vegetariano para 2 personas con $20000",
        "expected_tools": ["generar_carro_optimizado"]
    },
    {
        "query": "Crea un carro fitness para 3 personas con presupuesto de $30000",
        "expected_tools": ["generar_carro_optimizado"]
    },
    {
        "query": "Arma un carro familiar para 4 personas con $40000",
        "expected_tools": ["generar_carro_optimizado"]
    },
    
    # Validaciones
    {
        "query": "Valida si manzana,pan,leche son aptos para dieta vegetariana",
        "expected_tools": ["validar_dieta"]
    },
    {
        "query": "¿El pollo y huevos son compatibles con dieta vegetariana?",
        "expected_tools": ["validar_dieta"]
    },
    
    # Cálculos de presupuesto
    {
        "query": "Calcula el costo de pan,leche,huevos con presupuesto de 10000",
        "expected_tools": ["calcular_presupuesto"]
    },
    
    # Balance nutricional
    {
        "query": "Evalúa el balance nutricional de manzana,pollo,arroz,leche",
        "expected_tools": ["evaluar_balance_nutricional"]
    },
    
    # Consultas complejas (múltiples herramientas)
    {
        "query": "Genera un carro vegetariano para 2 personas con $25000 y valida que sea compatible con la dieta",
        "expected_tools": ["generar_carro_optimizado", "validar_dieta"]
    },
]

print(f"📋 Total de consultas a ejecutar: {len(test_queries)}\n")
print("Iniciando pruebas...\n")

successful = 0
failed = 0
total_latency = 0

for i, test in enumerate(test_queries, 1):
    query = test['query']
    expected_tools = test.get('expected_tools', [])
    
    print(f"{i}/{len(test_queries)} - Ejecutando: {query[:60]}...")
    
    try:
        # Invocar agente con métricas
        result = invoke_agent_with_metrics(query)
        
        # Calcular precisión si hay herramientas esperadas
        if expected_tools:
            precision = metrics_system.calculate_precision(
                expected_tools, 
                result['tools_used']
            )
            precision_str = f"Precisión: {precision:.1%}"
        else:
            precision_str = ""
        
        # Mostrar resultado
        if result['success']:
            successful += 1
            status = "✅"
            print(f"   {status} Latencia: {result['latency']:.2f}s | "
                  f"Herramientas: {', '.join(result['tools_used']) if result['tools_used'] else 'Ninguna'} | "
                  f"{precision_str}")
        else:
            failed += 1
            status = "❌"
            print(f"   {status} Falló")
        
        total_latency += result['latency']
        
    except Exception as e:
        failed += 1
        print(f"   ❌ Error: {str(e)}")
    
    # Pequeña pausa entre consultas
    time.sleep(0.5)
    print()

# Generar reporte
print("="*70)
print("📊 RESUMEN DE PRUEBAS")
print("="*70)
print(f"Total ejecutadas: {len(test_queries)}")
print(f"Exitosas: {successful} ({successful/len(test_queries)*100:.1f}%)")
print(f"Fallidas: {failed} ({failed/len(test_queries)*100:.1f}%)")
print(f"Latencia promedio: {total_latency/len(test_queries):.2f}s")
print()

# Exportar métricas
print("💾 Exportando métricas...")
summary = metrics_system.export_metrics()
print(f"✅ Métricas exportadas a data/metrics.json")
print()

# Generar reporte de análisis
print("📄 Generando reporte de análisis...")
report = metrics_system.generate_analysis_report()
print("✅ Reporte generado")
print()

# Mostrar resumen de métricas
print("="*70)
print("📈 MÉTRICAS DEL SISTEMA")
print("="*70)
print(f"Total de peticiones: {summary['total_requests']}")
print(f"Tasa de éxito: {summary['success_rate']:.1f}%")
print(f"Tasa de error: {summary['error_rate']:.1f}%")
print(f"Latencia promedio: {summary['avg_latency']:.3f}s")
print(f"Latencia P95: {summary['p95_latency']:.3f}s")
print(f"Latencia P99: {summary['p99_latency']:.3f}s")
print(f"Precisión promedio: {summary['avg_precision']:.1%}")
print(f"CPU promedio: {summary['avg_cpu_percent']:.1f}%")
print(f"Memoria promedio: {summary['avg_memory_percent']:.1f}%")
print()

print("🔧 USO DE HERRAMIENTAS:")
for tool, count in sorted(summary['tool_usage'].items(), key=lambda x: x[1], reverse=True):
    percentage = (count / summary['total_tool_calls'] * 100) if summary['total_tool_calls'] > 0 else 0
    print(f"  • {tool}: {count} veces ({percentage:.1f}%)")
print()

print("="*70)
print("✅ PRUEBA COMPLETADA")
print("="*70)
print("Ahora puedes:")
print("  1. Iniciar la API: python grozy_observability_api.py")
print("  2. Abrir el dashboard: http://localhost:5001")
print("  3. Ver las métricas en tiempo real")
print("="*70)
