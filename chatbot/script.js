// ============================================
// GROZY Chatbot - JavaScript
// ============================================

// Configuración
const API_URL = 'http://localhost:5000/api';
let sessionId = generateSessionId();

// Generar ID de sesión único
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Elementos del DOM
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const statusElement = document.getElementById('status');

// Auto-resize del textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Enviar mensaje al presionar Enter (sin Shift)
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Agregar mensaje al chat
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = isUser ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Formatear contenido (convertir saltos de línea a HTML)
    const formattedContent = formatMessage(content);
    contentDiv.innerHTML = formattedContent;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return messageDiv;
}

// Formatear mensaje (básico)
function formatMessage(text) {
    // Convertir URLs en links
    text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    
    // Convertir saltos de línea en <br>
    text = text.replace(/\n/g, '<br>');
    
    // Detectar listas (líneas que empiezan con • o -)
    const lines = text.split('<br>');
    let inList = false;
    let result = [];
    
    for (let line of lines) {
        const trimmed = line.trim();
        if (trimmed.match(/^[•\-\*]\s/)) {
            if (!inList) {
                result.push('<ul>');
                inList = true;
            }
            result.push('<li>' + trimmed.substring(2) + '</li>');
        } else {
            if (inList) {
                result.push('</ul>');
                inList = false;
            }
            result.push(line);
        }
    }
    
    if (inList) {
        result.push('</ul>');
    }
    
    return result.join('<br>');
}

// Mostrar indicador de escritura
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content typing-indicator';
    contentDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(contentDiv);
    
    chatContainer.appendChild(typingDiv);
    scrollToBottom();
}

// Ocultar indicador de escritura
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Scroll automático al final
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Actualizar estado
function setStatus(message, type = 'normal') {
    statusElement.textContent = message;
    statusElement.className = 'status ' + type;
}

// Enviar mensaje
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Deshabilitar input
    userInput.disabled = true;
    sendButton.disabled = true;
    
    // Agregar mensaje del usuario
    addMessage(message, true);
    
    // Limpiar input
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Mostrar indicador de escritura
    showTypingIndicator();
    setStatus('● GROZY está pensando...', 'connected');
    
    try {
        // Enviar a la API
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Ocultar indicador
        hideTypingIndicator();
        
        // Agregar respuesta del bot
        addMessage(data.response, false);
        
        setStatus('● Listo', 'connected');
        
    } catch (error) {
        console.error('Error:', error);
        hideTypingIndicator();
        
        addMessage(
            '❌ Lo siento, ocurrió un error al comunicarme con el servidor.\n\n' +
            'Verifica que el servidor esté ejecutándose en http://localhost:5000\n\n' +
            'Error: ' + error.message,
            false
        );
        
        setStatus('● Error de conexión', 'error');
    } finally {
        // Rehabilitar input
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }
}

// Enviar mensaje rápido
function sendQuickMessage(message) {
    userInput.value = message;
    sendMessage();
}

// Reiniciar conversación
async function resetChat() {
    if (!confirm('¿Deseas iniciar una nueva conversación?')) {
        return;
    }
    
    try {
        // Llamar al endpoint de reset
        await fetch(`${API_URL}/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        // Generar nuevo ID de sesión
        sessionId = generateSessionId();
        
        // Limpiar chat (mantener mensaje de bienvenida)
        const messages = chatContainer.querySelectorAll('.message');
        messages.forEach((msg, index) => {
            if (index > 0) { // Mantener el primer mensaje (bienvenida)
                msg.remove();
            }
        });
        
        setStatus('● Nueva conversación iniciada', 'connected');
        
        // Pequeño delay para mostrar el mensaje
        setTimeout(() => {
            setStatus('● Listo', 'connected');
        }, 2000);
        
    } catch (error) {
        console.error('Error al reiniciar:', error);
        alert('Error al reiniciar la conversación');
    }
}

// Verificar estado del servidor al cargar
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('Servidor conectado:', data);
            setStatus('● Conectado', 'connected');
        } else {
            throw new Error('Servidor no responde');
        }
    } catch (error) {
        console.error('Error de conexión:', error);
        setStatus('● Desconectado - Inicia el servidor', 'error');
        
        // Mostrar mensaje de error en el chat
        addMessage(
            '⚠️ No se pudo conectar al servidor.\n\n' +
            'Para usar el chatbot:\n' +
            '1. Abre una terminal\n' +
            '2. Navega a la carpeta del proyecto\n' +
            '3. Ejecuta: python grozy_api.py\n' +
            '4. Recarga esta página',
            false
        );
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    checkServerHealth();
    userInput.focus();
    
    console.log('🤖 GROZY Chatbot inicializado');
    console.log('Session ID:', sessionId);
});

// Manejar errores globales
window.addEventListener('error', (event) => {
    console.error('Error global:', event.error);
});
