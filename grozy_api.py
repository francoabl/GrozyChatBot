"""
GROZY API - Backend Flask para el Chatbot Web
CON INTEGRACIÓN DE OBSERVABILIDAD
"""

from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import json
import os
import time
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Sistema de Seguridad
try:
    from security_config import (
        security_manager,
        sanitize_input,
        validate_input,
        apply_rate_limit,
        require_api_key,
        add_security_headers
    )
    SECURITY_ENABLED = True
    print("🔒 Sistema de seguridad habilitado")
except ImportError:
    SECURITY_ENABLED = False
    print("⚠️ Sistema de seguridad no disponible")

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_agent

# Sistema de Observabilidad
try:
    from grozy_observability import metrics_system, logger
    OBSERVABILITY_ENABLED = True
    print("✅ Sistema de observabilidad habilitado")
except ImportError:
    OBSERVABILITY_ENABLED = False
    print("⚠️ Sistema de observabilidad no disponible")

# Cargar variables de entorno
load_dotenv()

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para peticiones desde el navegador

# Aplicar headers de seguridad a todas las respuestas
if SECURITY_ENABLED:
    @app.after_request
    def apply_security_headers(response):
        return add_security_headers(response)

# ============================================================================
# CONFIGURACIÓN Y CARGA DE DATOS (Una sola vez al iniciar)
# ============================================================================

print("🔄 Inicializando GROZY Agent...")

# Credenciales
github_token = os.getenv('GITHUB_TOKEN')
openai_base_url = os.getenv('OPENAI_BASE_URL')

if not github_token:
    raise ValueError("Configura GITHUB_TOKEN en el archivo .env")

# Cargar productos
file_path = os.path.join("data", "productos_unimarc_muestra.json")
with open(file_path, "r", encoding="utf-8") as f:
    productos = json.load(f)

# Convertir a documentos
docs = []
for p in productos:
    contenido = (
        f"Nombre: {p['nombre']} | "
        f"Precio: ${p['precio']} | "
        f"Categoría: {p['categoria']} | "
        f"Subcategoría: {p.get('subcategoria', 'N/A')} | "
        f"Supermercado: {p['supermercado']}"
    )
    docs.append(Document(
        page_content=contenido,
        metadata={
            "nombre": p['nombre'],
            "precio": p['precio'],
            "categoria": p['categoria'],
            "subcategoria": p.get('subcategoria', 'N/A'),
            "supermercado": p['supermercado']
        }
    ))

# Crear vector store
embeddings = OpenAIEmbeddings(
    api_key=github_token,
    base_url=openai_base_url,
    model="text-embedding-3-small"
)

vectorstore = FAISS.from_documents(docs, embeddings)

# Configurar LLM
llm = ChatOpenAI(
    api_key=github_token,
    base_url=openai_base_url,
    model="gpt-4o-mini",
    temperature=0.7
)

# ============================================================================
# DEFINICIÓN DE HERRAMIENTAS
# ============================================================================

@tool
def buscar_productos(query: str, k: int = 10) -> str:
    """Busca productos en la base de datos."""
    results = vectorstore.similarity_search(query, k=k)
    productos_encontrados = []
    
    for doc in results:
        productos_encontrados.append(
            f"- {doc.metadata['nombre']} | ${doc.metadata['precio']} | {doc.metadata['categoria']}"
        )
    
    return f"Productos encontrados ({len(productos_encontrados)}):\n" + "\n".join(productos_encontrados)


@tool
def obtener_estadisticas_categorias() -> str:
    """Obtiene estadísticas de productos por categoría."""
    categorias = {}
    precios_por_cat = {}
    
    for p in productos:
        cat = p['categoria']
        categorias[cat] = categorias.get(cat, 0) + 1
        if cat not in precios_por_cat:
            precios_por_cat[cat] = []
        precios_por_cat[cat].append(p['precio'])
    
    resultado = "📊 ESTADÍSTICAS:\n\n"
    resultado += f"Total productos: {len(productos)}\n"
    resultado += f"Categorías: {len(categorias)}\n\n"
    
    for cat, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:8]:
        precio_prom = sum(precios_por_cat[cat]) / len(precios_por_cat[cat])
        resultado += f"• {cat}: {count} productos (${precio_prom:,.0f})\n"
    
    return resultado


@tool
def generar_carro_optimizado(tipo_dieta: str, presupuesto: float, personas: int) -> str:
    """Genera un carro de compras optimizado."""
    queries_dieta = {
        'vegetariana': 'frutas verduras lácteos huevos legumbres cereales',
        'diabetica': 'verduras carnes magras lácteos sin azúcar cereales integrales',
        'fitness': 'proteínas pollo pavo atún huevos avena frutas verduras',
        'familiar': 'frutas verduras carnes lácteos pan cereales snacks'
    }
    
    query = queries_dieta.get(tipo_dieta.lower(), queries_dieta['familiar'])
    num_productos = min(20, int(presupuesto / 1000))
    results = vectorstore.similarity_search(query, k=num_productos * 2)
    
    productos_seleccionados = []
    total = 0
    
    for doc in results:
        precio = doc.metadata['precio']
        if total + precio <= presupuesto:
            productos_seleccionados.append({
                'nombre': doc.metadata['nombre'],
                'precio': precio,
                'categoria': doc.metadata['categoria']
            })
            total += precio
            
            if len(productos_seleccionados) >= num_productos:
                break
    
    resultado = f"🛒 CARRO - Dieta {tipo_dieta.upper()}\n"
    resultado += f"👥 {personas} personas | 💰 ${presupuesto:,}\n\n"
    
    for i, p in enumerate(productos_seleccionados, 1):
        resultado += f"{i}. {p['nombre']} - ${p['precio']:,}\n"
    
    resultado += f"\n💰 TOTAL: ${total:,}\n"
    resultado += f"💵 Saldo: ${presupuesto - total:,}\n"
    
    return resultado


# Crear agente
tools = [buscar_productos, obtener_estadisticas_categorias, generar_carro_optimizado]

system_message = """Eres GROZY, un asistente de compras de supermercado.

Ayudas a los usuarios a:
- Buscar productos
- Ver estadísticas
- Generar carros de compra optimizados

Cuando el usuario pida un carro, usa generar_carro_optimizado directamente.
Sé breve y directo. Usa emojis moderadamente."""

agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_message,
    debug=False
)

print("✅ GROZY Agent listo")

# ============================================================================
# WRAPPER CON OBSERVABILIDAD
# ============================================================================

def invoke_agent_with_metrics(user_message: str, conversation_history: list = None) -> dict:
    """
    Invoca el agente con tracking de métricas
    """
    start_time = time.time()
    tools_used = []
    success = False
    response_content = ""
    error_msg = None
    messages_result = []
    
    try:
        # Preparar mensajes
        if conversation_history is None:
            messages = [HumanMessage(content=user_message)]
        else:
            messages = conversation_history + [HumanMessage(content=user_message)]
        
        if OBSERVABILITY_ENABLED:
            logger.info(f"🚀 Petición desde chatbot: {user_message[:100]}...")
        
        # Invocar agente
        response = agent_executor.invoke({"messages": messages})
        messages_result = response['messages']
        
        # Extraer respuesta
        response_content = response['messages'][-1].content
        
        # Detectar herramientas usadas
        for msg in response['messages']:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_name = tc.get('name', '') if isinstance(tc, dict) else getattr(tc, 'name', '')
                    if tool_name and tool_name not in tools_used:
                        tools_used.append(tool_name)
        
        success = True
        
        if OBSERVABILITY_ENABLED:
            logger.info(f"✅ Petición exitosa - Herramientas: {tools_used}")
        
    except Exception as e:
        error_msg = str(e)
        if OBSERVABILITY_ENABLED:
            logger.error(f"❌ Error en petición: {error_msg}")
            logger.error(traceback.format_exc())
        response_content = f"Error: {error_msg}"
    
    finally:
        # Calcular latencia
        latency = time.time() - start_time
        
        # Registrar métricas si está habilitado
        if OBSERVABILITY_ENABLED:
            metrics_system.record_request(
                success=success,
                latency=latency,
                tools_used=tools_used,
                error=error_msg,
                request_text=user_message
            )
            
            if success:
                metrics_system.record_trace(
                    request=user_message,
                    response=response_content,
                    tools_used=tools_used,
                    latency=latency
                )
                metrics_system.check_consistency(user_message, response_content)
    
    return {
        'success': success,
        'response': response_content,
        'latency': latency,
        'tools_used': tools_used,
        'messages': messages_result
    }


# ============================================================================
# ALMACENAMIENTO DE SESIONES (En memoria - simple)
# ============================================================================

# Diccionario para almacenar conversaciones por sesión
sessions = {}

# ============================================================================
# ENDPOINTS DE LA API
# ============================================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint para enviar mensajes al agente CON MÉTRICAS Y SEGURIDAD."""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        # SEGURIDAD: Validar y sanitizar entrada
        if SECURITY_ENABLED:
            is_valid, error_msg = validate_input(user_message)
            if not is_valid:
                security_manager.log_security_event(
                    'invalid_input',
                    f'Validación fallida: {error_msg}',
                    request.remote_addr
                )
                return jsonify({
                    'success': False,
                    'error': f'⚠️ {error_msg}',
                    'response': f'⚠️ {error_msg}'
                }), 400
            
            user_message = sanitize_input(user_message)
            security_manager.log_security_event(
                'chat_request',
                f'Mensaje procesado (longitud: {len(user_message)})',
                request.remote_addr
            )
        
        if not user_message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Obtener o crear historial de sesión
        if session_id not in sessions:
            sessions[session_id] = []
        
        conversation_messages = sessions[session_id]
        
        # Invocar agente CON MÉTRICAS
        result = invoke_agent_with_metrics(user_message, conversation_messages)
        
        # Actualizar historial
        if result['success']:
            sessions[session_id] = result['messages']
        
        return jsonify({
            'response': result['response'],
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'latency': result['latency'],
            'tools_used': result['tools_used'],
            'success': result['success']
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if OBSERVABILITY_ENABLED:
            logger.error(f"Error en endpoint /api/chat: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
@apply_rate_limit(security_manager) if SECURITY_ENABLED else lambda f: f
def reset():
    """Endpoint para reiniciar una sesión."""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in sessions:
            del sessions[session_id]
        
        return jsonify({'message': 'Sesión reiniciada', 'session_id': session_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
@apply_rate_limit(security_manager) if SECURITY_ENABLED else lambda f: f
def health():
    """Endpoint para verificar el estado del servidor."""
    return jsonify({
        'status': 'ok',
        'agent': 'GROZY',
        'version': '1.0',
        'products': len(productos),
        'tools': len(tools),
        'observability': OBSERVABILITY_ENABLED,
        'security': SECURITY_ENABLED
    })


# ============================================================================
# ENDPOINTS DE OBSERVABILIDAD (para el dashboard)
# ============================================================================

@app.route('/api/metrics', methods=['GET'])
@apply_rate_limit(security_manager) if SECURITY_ENABLED else lambda f: f
def get_metrics():
    """Obtiene todas las métricas del sistema."""
    if not OBSERVABILITY_ENABLED:
        return jsonify({'success': False, 'error': 'Observabilidad no habilitada'}), 503
    
    try:
        summary = metrics_system.get_summary()
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metrics/summary', methods=['GET'])
@apply_rate_limit(security_manager) if SECURITY_ENABLED else lambda f: f
def get_metrics_summary():
    """Obtiene resumen de métricas principales."""
    if not OBSERVABILITY_ENABLED:
        return jsonify({'success': False, 'error': 'Observabilidad no habilitada'}), 503
    
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
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metrics/traces', methods=['GET'])
def get_execution_traces():
    """Obtiene trazas de ejecución."""
    if not OBSERVABILITY_ENABLED:
        return jsonify({'success': False, 'error': 'Observabilidad no habilitada'}), 503
    
    try:
        summary = metrics_system.get_summary()
        return jsonify({'success': True, 'data': summary['execution_traces']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metrics/errors', methods=['GET'])
def get_error_metrics():
    """Obtiene métricas de errores."""
    if not OBSERVABILITY_ENABLED:
        return jsonify({'success': False, 'error': 'Observabilidad no habilitada'}), 503
    
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
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/report/generate', methods=['GET'])
def generate_report():
    """Genera reporte de análisis."""
    if not OBSERVABILITY_ENABLED:
        return jsonify({'success': False, 'error': 'Observabilidad no habilitada'}), 503
    
    try:
        report = metrics_system.generate_analysis_report()
        return jsonify({'success': True, 'report': report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metrics/export', methods=['GET'])
def export_metrics():
    """Exporta métricas a archivo JSON."""
    if not OBSERVABILITY_ENABLED:
        return jsonify({'success': False, 'error': 'Observabilidad no habilitada'}), 503
    
    try:
        summary = metrics_system.export_metrics()
        return jsonify({
            'success': True,
            'message': 'Métricas exportadas a data/metrics.json',
            'data': summary
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ENDPOINTS DE SEGURIDAD
# ============================================================================

@app.route('/api/security/status', methods=['GET'])
def security_status():
    """Obtiene el estado del sistema de seguridad."""
    if not SECURITY_ENABLED:
        return jsonify({
            'enabled': False,
            'message': 'Sistema de seguridad no habilitado'
        })
    
    return jsonify({
        'enabled': True,
        'features': {
            'rate_limiting': True,
            'input_validation': True,
            'input_sanitization': True,
            'xss_protection': True,
            'sql_injection_protection': True,
            'api_key_authentication': True,
            'data_encryption': True,
            'data_anonymization': True,
            'security_headers': True,
            'audit_logging': True
        },
        'config': {
            'max_requests_per_minute': security_manager.MAX_REQUESTS_PER_MINUTE,
            'max_message_length': security_manager.MAX_MESSAGE_LENGTH,
            'log_retention_limit': 1000
        },
        'active_protections': [
            'Prevención de inyección SQL',
            'Prevención de XSS',
            'Protección contra Command Injection',
            'Rate Limiting por IP',
            'Validación de entradas',
            'Logs de seguridad anonimizados',
            'Headers de seguridad HTTP',
            'Principio de mínimo privilegio'
        ]
    })


@app.route('/api/security/logs', methods=['GET'])
@require_api_key(security_manager) if SECURITY_ENABLED else lambda f: f
def security_logs():
    """Obtiene los logs de seguridad (requiere autenticación)."""
    if not SECURITY_ENABLED:
        return jsonify({'success': False, 'error': 'Seguridad no habilitada'}), 503
    
    try:
        # Limitar a últimos 100 eventos
        recent_logs = security_manager.security_log[-100:]
        
        return jsonify({
            'success': True,
            'total_events': len(security_manager.security_log),
            'events': recent_logs
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# RUTAS PARA SERVIR ARCHIVOS ESTÁTICOS (Chatbot y Dashboard)
# ============================================================================

@app.route('/chatbot/')
@app.route('/chatbot/<path:filename>')
def serve_chatbot(filename='index.html'):
    """Sirve los archivos del chatbot."""
    return send_from_directory('chatbot', filename)


@app.route('/dashboard/')
@app.route('/dashboard/<path:filename>')
def serve_dashboard(filename='index.html'):
    """Sirve los archivos del dashboard."""
    return send_from_directory('dashboard', filename)


# ============================================================================
# PÁGINA DE INICIO
# ============================================================================

@app.route('/')
def index():
    """Página de inicio."""
    observability_status = "✅ Habilitada" if OBSERVABILITY_ENABLED else "⚠️ Deshabilitada"
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GROZY - API Principal</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                padding: 40px;
                line-height: 1.6;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background: #334155;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }}
            h1 {{ color: #6366f1; margin-bottom: 10px; }}
            h2 {{ color: #8b5cf6; margin-top: 30px; border-bottom: 2px solid #475569; padding-bottom: 10px; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ 
                background: #1e293b;
                margin: 8px 0;
                padding: 12px;
                border-radius: 6px;
                border-left: 4px solid #6366f1;
            }}
            a {{
                color: #60a5fa;
                text-decoration: none;
                font-weight: 600;
            }}
            a:hover {{ color: #93c5fd; }}
            .status {{ 
                display: inline-block;
                padding: 6px 12px;
                border-radius: 6px;
                background: #10b981;
                color: white;
                font-size: 0.9em;
            }}
            .button {{
                display: inline-block;
                padding: 15px 30px;
                background: #6366f1;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                margin: 10px 10px 10px 0;
                font-weight: 600;
                transition: all 0.3s;
            }}
            .button:hover {{
                background: #4f46e5;
                transform: translateY(-2px);
            }}
            .button.secondary {{
                background: #8b5cf6;
            }}
            .button.secondary:hover {{
                background: #7c3aed;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 GROZY API</h1>
            <p class="status">API funcionando correctamente</p>
            
            <h2>📊 Estado del Sistema</h2>
            <ul>
                <li>Productos cargados: <strong>{len(productos)}</strong></li>
                <li>Herramientas disponibles: <strong>{len(tools)}</strong></li>
                <li>Observabilidad: <strong>{observability_status}</strong></li>
            </ul>
            
            <h2>🚀 Aplicaciones</h2>
            <div>
                <a href="/chatbot/index.html" class="button">💬 Abrir Chatbot</a>
                <a href="/dashboard/index.html" class="button secondary">📊 Dashboard de Métricas</a>
            </div>
            
            <h2>📡 Endpoints - Chatbot</h2>
            <ul>
                <li><code>POST /api/chat</code> - Enviar mensaje al agente</li>
                <li><code>POST /api/reset</code> - Reiniciar sesión</li>
                <li><code>GET /api/health</code> - Estado del servidor</li>
            </ul>
            
            <h2>📊 Endpoints - Observabilidad</h2>
            <ul>
                <li><code>GET /api/metrics</code> - Métricas completas del sistema</li>
                <li><code>GET /api/metrics/summary</code> - Resumen de métricas principales</li>
                <li><code>GET /api/metrics/traces</code> - Trazas de ejecución</li>
                <li><code>GET /api/metrics/errors</code> - Registro de errores</li>
                <li><code>GET /api/report/generate</code> - Generar reporte de análisis</li>
                <li><code>GET /api/metrics/export</code> - Exportar métricas a JSON</li>
            </ul>
            
            <h2>📚 Documentación</h2>
            <p>Para más información, consulta los archivos:</p>
            <ul>
                <li><strong>QUICKSTART.md</strong> - Guía de inicio rápido</li>
                <li><strong>OBSERVABILIDAD_GROZY.md</strong> - Documentación técnica completa</li>
                <li><strong>INDEX.md</strong> - Índice de documentación</li>
            </ul>
        </div>
    </body>
    </html>
    '''


# ============================================================================
# EJECUTAR SERVIDOR
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Servidor GROZY API iniciado")
    print("="*60)
    print("📡 API: http://localhost:5000")
    print("📖 Documentación: http://localhost:5000")
    print("💬 Chatbot: http://localhost:5000/chatbot/index.html")
    if OBSERVABILITY_ENABLED:
        print("📊 Dashboard con métricas integradas")
    else:
        print("⚠️  Observabilidad deshabilitada (instala: pip install psutil)")
    print("\nPresiona Ctrl+C para detener el servidor\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
