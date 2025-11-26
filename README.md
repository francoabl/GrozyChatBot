# GROZY Agent — Inicio Rápido (Unificado)

Bienvenido a GROZY Agent: un asistente de compras con **observabilidad integrada**, **seguridad de producción (IL3.3)** y un **dashboard web**. Este README está pensado para alguien que descarga el proyecto por primera vez desde GitHub.

## 1. Requisitos
- Python 3.10–3.13 (recomendado)
- Dependencias del proyecto (se instalan abajo)
- Token de GitHub Models (GITHUB_TOKEN)

## 2. Instalación
```powershell
# Clonar y entrar
# git clone <repo>
# cd Evaluacion_1_caso_GROZY-main

# Crear entorno virtual (opcional)
python -m venv venv; .\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

## 3. Configuración (.env)
Crea un archivo `.env` en la raíz:
```
GITHUB_TOKEN=ghp_tu_token_real_aqui
OPENAI_BASE_URL=https://models.inference.ai.azure.com
GROZY_API_KEY=grozy_tu_api_key_opcional
SECURITY_SALT=un_salt_unico
```

## 4. Ejecutar el servidor
```powershell
python grozy_api.py
```

Verás enlaces:
- Chatbot: `http://localhost:5000/chatbot/index.html`
- Dashboard: `http://localhost:5000/dashboard/index.html`
- Health: `http://localhost:5000/api/health`

## 5. ¿Qué incluye?
- Agente LangChain con herramientas: búsqueda de productos, estadísticas y carro optimizado.
- Observabilidad: métricas (latencia, precisión, errores, CPU, memoria), trazas y reporte.
- Seguridad (IL3.3): validación/sanitización, rate limiting, API keys, anonimización, headers.
- Frontend: chatbot y dashboard integrados.

## 6. Uso rápido
- Abre el chatbot y realiza 5–10 consultas para poblar métricas.
- Abre el dashboard para ver tarjetas, gráficos y trazas.

## 7. Endpoints principales
- `POST /api/chat` — enviar mensaje (JSON: `{message, session_id}`)
- `POST /api/reset` — reiniciar sesión
- `GET /api/metrics` — métricas completas
- `GET /api/metrics/summary` — resumen
- `GET /api/metrics/traces` — trazas
- `GET /api/metrics/errors` — errores
- `GET /api/report/generate` — reporte análisis
- `GET /api/health` — estado servidor

## 8. Seguridad (IL3.3)
- Validación y sanitización de inputs.
- Rate limiting por IP (20 req/min).
- Autenticación por API Key (headers `X-API-Key`).
- Anonimización de logs y cifrado de datos sensibles.
- Headers de seguridad HTTP (CSP, HSTS, etc.).

## 9. Solución de problemas
- "Token no configurado": agrega `GITHUB_TOKEN` al `.env`.
- Dashboard vacío: genera consultas primero en el chatbot.
- 429 (rate limit): espera 60s antes de reintentar.

## 10. Licencia
MIT. Uso bajo responsabilidad del usuario. Cumplir normativas locales (GDPR, etc.).

---

Para un informe técnico listo para Word, abre `INFORME_GROZY.txt`.

```powershell
jupyter notebook agente_grozy.ipynb
```

**Características:**
- ✅ Interfaz visual en el navegador
- ✅ Ejecución celda por celda
- ✅ Documentación integrada
- ✅ Ejemplos predefinidos
- ✅ Ideal para demostración académica

**Cómo usar:**
1. Abre el notebook en Jupyter
2. Ejecuta las celdas en orden (Run All)
3. Prueba los ejemplos en las celdas 15-25
4. Modifica y experimenta

---

### Opción 3: Chatbot Web 🌐

**Requiere 2 pasos:**

#### Paso 1: Iniciar el Servidor API

```powershell
python grozy_api.py
```

Verás:
```
🔄 Inicializando GROZY Agent...
✅ GROZY Agent listo
============================================================
🚀 Servidor GROZY API iniciado
============================================================
📡 URL: http://localhost:5000
```

**⚠️ IMPORTANTE:** Deja esta terminal abierta y ejecutándose.

#### Paso 2: Abrir el Chatbot

Abre `chatbot/index.html` en tu navegador:
- Doble clic en el archivo, o
- Arrastra el archivo al navegador, o
- En VS Code: clic derecho → "Open with Live Server"

**Características:**
- ✅ Interfaz moderna y responsive
- ✅ Botones de acceso rápido con ejemplos
- ✅ Indicador de escritura animado
- ✅ Historial de conversación
- ✅ Funciona en móvil y desktop

---

## 📚 Ejemplos de Consultas

### 🌱 Dieta Vegetariana
```
"Arma un carro vegetariano para 4 personas con presupuesto de $30,000"
```

**Resultado esperado:**
- Búsqueda de productos vegetarianos
- Validación de ausencia de carnes
- Balance entre frutas, verduras, lácteos y legumbres
- Total dentro del presupuesto

### 🩺 Dieta Diabética
```
"Necesito productos para diabético, presupuesto $15,000, valida que no tengan azúcar"
```

**Resultado esperado:**
- Productos sin azúcar añadido
- Priorizaci de carbohidratos complejos
- Advertencia sobre productos con azúcar

### 💪 Dieta Fitness
```
"Carro fitness para 2 personas, $20,000, prioriza proteínas y carbohidratos complejos"
```

**Resultado esperado:**
- Alta proporción de proteínas
- Carbohidratos complejos (arroz integral, avena)
- Frutas y verduras para balance

### 🧠 Uso de Memoria
```
Usuario: "Me llamo Franco y soy vegetariano"
Agente: "Encantado Franco, recordaré tu preferencia..."

Usuario: "Arma un carro para mí con $20,000"
Agente: "Claro Franco, prepararé un carro VEGETARIANO..." ✅ Recuerda!
```

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    USUARIO                              │
│         (CLI / Notebook / Web)                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              AGENTE GROZY (LangChain)                   │
│  ┌────────────────────────────────────────────────┐    │
│  │  🧠 LLM (GPT-4o-mini via GitHub Models)       │    │
│  │     • Razonamiento y toma de decisiones        │    │
│  │     • Planificación adaptativa                 │    │
│  │     • Selección de herramientas                │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  💾 MEMORIA                                    │    │
│  │     • Corto plazo: ConversationBufferMemory    │    │
│  │     • Largo plazo: JSON persistente            │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  🔧 HERRAMIENTAS (7 tools)                    │    │
│  │                                                 │    │
│  │  🔍 Consulta:                                  │    │
│  │     • buscar_productos                         │    │
│  │     • obtener_estadisticas_categorias          │    │
│  │                                                 │    │
│  │  🧠 Razonamiento:                              │    │
│  │     • validar_dieta                            │    │
│  │     • calcular_presupuesto                     │    │
│  │     • evaluar_balance_nutricional              │    │
│  │                                                 │    │
│  │  ✍️ Escritura:                                 │    │
│  │     • generar_carro_optimizado                 │    │
│  │     • guardar_preferencias_usuario             │    │
│  └────────────────────────────────────────────────┘    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│           BASE DE CONOCIMIENTO                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  📊 Vector Store (FAISS)                       │    │
│  │     • 495 productos                            │    │
│  │     • 9 categorías                             │    │
│  │     • Embeddings (text-embedding-3-small)      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  📁 Datos (JSON)                               │    │
│  │     • productos_unimarc_muestra.json           │    │
│  │     • preferencias_usuarios.json               │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Ejecución

```
1. Usuario ingresa consulta
   ↓
2. Agente analiza intención
   ↓
3. Planifica secuencia de herramientas
   ↓
4. Ejecuta herramientas iterativamente
   ↓
5. Valida restricciones (dieta, presupuesto, balance)
   ↓
6. ¿Hay problemas? → Ajusta estrategia (vuelve al paso 3)
   ↓
7. Integra resultados
   ↓
8. Genera respuesta final
   ↓
9. Actualiza memoria
   ↓
10. Retorna al usuario
```

---

## 📊 Documentación Técnica

### Justificación de Decisiones Técnicas

#### 1. Framework: LangChain

**Razón de selección:**
- ✅ Framework líder en desarrollo de aplicaciones con LLM (70k+ estrellas GitHub)
- ✅ Abstracciones robustas para agentes y herramientas
- ✅ Implementación nativa de patrones ReAct (Reasoning + Acting)
- ✅ Integración directa con OpenAI y GitHub Models
- ✅ Sistema de memoria incorporado
- ✅ Gran comunidad y documentación exhaustiva

**Alternativas consideradas:**
- **Haystack:** Más orientado a búsqueda, menor flexibilidad para agentes complejos
- **Autogen:** Requiere múltiples agentes, innecesario para este caso de uso
- **Implementación custom:** Mayor control pero tiempo de desarrollo significativamente mayor

**Referencia:** Chase, H. (2022). LangChain [Software]. https://github.com/langchain-ai/langchain

---

#### 2. Vector Store: FAISS

**Razón de selección:**
- ✅ Optimizado por Facebook AI Research para búsquedas de similitud
- ✅ Excelente rendimiento para datasets medianos (<1M vectores)
- ✅ Funciona en CPU (no requiere GPU)
- ✅ Integración directa con LangChain
- ✅ Latencia < 100ms para búsquedas

**Referencia:** Johnson, J., Douze, M., & Jégou, H. (2019). Billion-scale similarity search with GPUs. IEEE Transactions on Big Data, 7(3), 535-547.

---

#### 3. LLM: GPT-4o-mini (GitHub Models)

**Razón de selección:**
- ✅ Acceso gratuito para desarrollo académico
- ✅ Balance óptimo costo-rendimiento
- ✅ Capacidad de razonamiento suficiente para el dominio
- ✅ Latencia < 3 segundos
- ✅ Soporte nativo de function calling (crítico para herramientas)
- ✅ Contexto de 128k tokens

**Referencia:** OpenAI. (2024). GPT-4 Technical Report. https://openai.com/research/gpt-4

---

#### 4. Arquitectura: Agent with Tools (ReAct Pattern)

**Razón de selección:**
- ✅ LLM decide dinámicamente qué herramientas usar
- ✅ Planificación multi-paso
- ✅ Capacidad de autocorrección
- ✅ Validación automática de argumentos
- ✅ Manejo robusto de errores

**Referencia:** Yao, S., et al. (2023). ReAct: Synergizing reasoning and acting in language models. ICLR.

---

### Sistema de Memoria Implementado

#### Memoria de Corto Plazo

**Implementación:**
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="output"
)
```

**Características:**
- Mantiene historial completo de la conversación
- Permite referencias anafóricas ("para mí", "lo anterior")
- Coherencia temática entre turnos
- Persistencia solo durante la sesión

**Ejemplo:**
```
Turno 1:
Usuario: "Me llamo Franco y soy vegetariano"
Agente: "Encantado Franco, recordaré tu preferencia"

Turno 2:
Usuario: "Arma un carro para mí"
Agente: "Por supuesto Franco, prepararé un carro VEGETARIANO"
```

#### Memoria de Largo Plazo

**Implementación:**
- Archivo JSON local: `data/preferencias_usuarios.json`
- Herramienta: `guardar_preferencias_usuario`
- Persistencia entre sesiones

**Estructura:**
```json
{
  "Franco": {
    "preferencias": "vegetariano, presupuesto 30000, 2 personas",
    "fecha": "2025-10-29T14:30:00"
  }
}
```

---

### Planificación Adaptativa

El agente implementa un proceso de 5 fases:

#### FASE 1: Análisis de Intención
- Parsea solicitud del usuario
- Identifica información faltante
- Decide si solicitar más datos

#### FASE 2: Planificación de Acciones
- Determina secuencia de herramientas
- Prioriza según criticidad
- Considera dependencias entre tools

#### FASE 3: Ejecución Iterativa
- Ejecuta herramientas secuencialmente
- Observa resultados
- Decide siguiente acción

#### FASE 4: Validación y Ajuste
- Verifica restricciones (dieta, presupuesto, balance)
- Si hay problemas → AJUSTA ESTRATEGIA
- Si todo OK → FINALIZA

#### FASE 5: Síntesis de Respuesta
- Integra resultados de todas las herramientas
- Genera respuesta coherente
- Actualiza memoria

### Ejemplos de Adaptación

#### Ejemplo 1: Presupuesto Insuficiente

**Input:** "Carro fitness para 4 personas con $5,000"

**Proceso adaptativo:**
1. Detecta que $5,000 / 4 ≈ $1,250/persona es insuficiente
2. Reduce cantidad de productos de 20 a 10
3. Prioriza categorías económicas (cereales, legumbres)
4. Comunica limitación de forma transparente:
   ```
   "Con $5,000 para 4 personas, el presupuesto es limitado.
   He preparado un carro básico con 10 productos esenciales.
   Recomiendo aumentar el presupuesto a $15,000 para mayor variedad."
   ```

#### Ejemplo 2: Balance Nutricional Deficiente

**Input:** "Carro con: pan, galletas, dulces, bebidas, snacks"

**Proceso adaptativo:**
1. Genera carro inicial con productos solicitados
2. Evalúa balance con `evaluar_balance_nutricional`
3. Detecta carencia de: proteínas, frutas/verduras, lácteos
4. Interviene proactivamente:
   ```
   "He notado que el carro actual carece de:
   ⚠️ Proteínas (carnes, huevos, legumbres)
   ⚠️ Frutas y verduras
   ⚠️ Lácteos
   
   ¿Deseas que agregue estos grupos para un balance adecuado?"
   ```

#### Ejemplo 3: Violación de Restricción Dietética

**Input (usuario vegetariano):** "Arma carro con pollo, pescado y verduras"

**Proceso adaptativo:**
1. Consulta memoria: usuario es vegetariano
2. Detecta contradicción
3. Advierte y sugiere:
   ```
   "He notado que solicitaste pollo y pescado, pero según
   tus preferencias guardadas eres vegetariano.
   
   ¿Deseas que:
   A) Omita las carnes y priorice proteínas vegetales
   B) Actualice tus preferencias para incluir carnes?"
   ```

---

## 📈 Métricas y Rendimiento

| Métrica | Valor |
|---------|-------|
| **Herramientas disponibles** | 7 especializadas |
| **Productos en base de datos** | 495 |
| **Categorías** | 9 |
| **Tiempo de respuesta promedio** | 5-8 segundos |
| **Iteraciones por consulta** | 4-6 |
| **Tasa de éxito** | >95% en casos válidos |
| **Memoria conversacional** | Ilimitada (en sesión) |

---

## 📁 Estructura del Proyecto

```
Evaluacion_1_caso_GROZY-main/
│
├── 🐍 Scripts Python
│   ├── grozy_agent_v2.py          ⭐ Terminal interactiva (recomendado)
│   ├── grozy_api.py               🌐 API Flask para chatbot web
│   ├── grozy_agent.py             📝 Script base
│   └── crear_muestra_productos.py 🔧 Utilidad de datos
│
├── 📓 Notebooks
│   ├── agente_grozy.ipynb         ⭐ Notebook principal del agente
│   ├── Main.ipynb                 📚 Sistema RAG original
│   └── conexion.ipynb             🔌 Tests de conectividad
│
├── 🌐 Chatbot Web
│   └── chatbot/
│       ├── index.html             💻 Interfaz principal
│       ├── styles.css             🎨 Estilos
│       ├── script.js              ⚡ Lógica cliente
│       ├── demo.html              📖 Guía de uso
│       └── README.md              📄 Documentación
│
├── 📊 Datos
│   └── data/
│       ├── productos_unimarc_muestra.json  ⭐ 495 productos (usado)
│       ├── productos_unimarc.json          📦 Dataset completo
│       └── preferencias_usuarios.json      💾 Memoria persistente
│
├── 📄 Documentación
│   ├── README.md                  📘 Este archivo
│   └── requirements.txt           📦 Dependencias Python
│
└── 🔑 Configuración
    └── .env                       🔐 Variables de entorno (crear)
```

---

## 🔮 Mejoras Futuras

### Corto Plazo (1-2 meses)
- [ ] Tests unitarios con pytest
- [ ] Base de datos SQL para escalabilidad
- [ ] ConversationSummaryMemory para sesiones largas
- [ ] Logging estructurado

### Mediano Plazo (3-6 meses)
- [ ] Información nutricional detallada (calorías, macros, micronutrientes)
- [ ] Comparación de precios entre supermercados
- [ ] Sistema de alertas de ofertas y descuentos
- [ ] Recomendaciones basadas en historial

### Largo Plazo (6-12 meses)
- [ ] Fine-tuning de modelo específico para retail chileno
- [ ] Integración con APIs de supermercados en tiempo real
- [ ] Aplicación móvil (iOS/Android)
- [ ] Sistema de recomendaciones colaborativas
- [ ] Análisis predictivo de compras

---

## 🛠️ Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'langchain'"
**Solución:** 
```powershell
pip install -r requirements.txt
```

### Error: "Authentication failed" o "Invalid token"
**Solución:** 
1. Verifica que el archivo `.env` existe en la raíz
2. Verifica que `GITHUB_TOKEN` tiene un token válido
3. Regenera el token en https://github.com/settings/tokens

### El chatbot web no se conecta al servidor
**Solución:**
1. Verifica que `grozy_api.py` está ejecutándose
2. Verifica que el servidor muestra "Servidor GROZY API iniciado"
3. Abre la consola del navegador (F12) para ver errores
4. Verifica que la URL en `script.js` es `http://localhost:5000`

### El agente no encuentra productos
**Solución:**
1. Verifica que `data/productos_unimarc_muestra.json` existe
2. El vector store se genera en la primera ejecución (toma ~30 segundos)
3. Revisa que las consultas sean en español

### Respuestas muy lentas (>15 segundos)
**Solución:**
- Primera ejecución es más lenta (generación de embeddings)
- Ejecuciones posteriores son más rápidas (~5-8 segundos)
- Verifica tu conexión a internet (requiere acceso a GitHub Models)

---

## 📖 Referencias (Formato APA)

Chase, H. (2022). *LangChain* [Software]. GitHub. https://github.com/langchain-ai/langchain

Johnson, J., Douze, M., & Jégou, H. (2019). Billion-scale similarity search with GPUs. *IEEE Transactions on Big Data*, 7(3), 535-547. https://doi.org/10.1109/TBDATA.2019.2921572

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*, 33, 9459-9474.

OpenAI. (2023). *Function Calling*. OpenAI Documentation. https://platform.openai.com/docs/guides/function-calling

OpenAI. (2024). *GPT-4 Technical Report*. https://openai.com/research/gpt-4

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. *Advances in Neural Information Processing Systems*, 30.

Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., Chen, Z., Tang, J., Chen, X., Lin, Y., Zhao, W. X., Wei, Z., & Liu, T. Y. (2023). A survey on large language model based autonomous agents. *arXiv preprint arXiv:2308.11432*.

Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). ReAct: Synergizing reasoning and acting in language models. *International Conference on Learning Representations (ICLR)*.

---

## 👨‍💻 Autores y Contacto

**Franco Alarcón** - Desarrollo e implementación  
**Agustín Aceval** - Desarrollo e implementación

**Curso:** Ingeniería de Soluciones con IA   
**Fecha:** noviembre 2025

---



---

<div align="center">

**⭐ Proyecto GROZY - Agente Inteligente con IA ⭐**

*Optimización de compras mediante planificación adaptativa y memoria contextual*

</div>
