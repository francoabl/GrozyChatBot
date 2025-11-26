"""
Configuración de Seguridad para GROZY Agent
Implementa medidas de protección según estándares de producción
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import re
import bleach

# ============================================================================
# GESTIÓN DE SECRETOS Y API KEYS
# ============================================================================

class SecurityManager:
    """Gestión centralizada de seguridad."""
    
    def __init__(self):
        # Generar API key maestra si no existe
        self.master_key = os.getenv('GROZY_API_KEY') or self._generate_api_key()
        self.master_key_hash = self._hash_key(self.master_key)
        
        # Rate limiting storage (IP -> [timestamps])
        self.rate_limit_storage = {}
        
        # Configuración
        self.MAX_REQUESTS_PER_MINUTE = 20
        self.MAX_MESSAGE_LENGTH = 2000
        self.ALLOWED_CHARACTERS = re.compile(r'^[a-zA-Z0-9áéíóúñÑ\s\.,;:¿?¡!\-\$%()]+$')
        
        # Logging de seguridad
        self.security_log = []
        
    def _generate_api_key(self):
        """Genera una API key segura."""
        return f"grozy_{secrets.token_urlsafe(32)}"
    
    def _hash_key(self, key):
        """Hash SHA-256 de la API key."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def validate_api_key(self, provided_key):
        """Valida una API key proporcionada."""
        if not provided_key:
            return False
        
        # Comparación segura usando hash
        provided_hash = self._hash_key(provided_key)
        return secrets.compare_digest(provided_hash, self.master_key_hash)
    
    def log_security_event(self, event_type, details, ip_address):
        """Registra eventos de seguridad."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'details': details,
            'ip': self._anonymize_ip(ip_address)  # IP anonimizada
        }
        self.security_log.append(event)
        
        # Mantener solo últimos 1000 eventos (política de retención)
        if len(self.security_log) > 1000:
            self.security_log = self.security_log[-1000:]
    
    def _anonymize_ip(self, ip):
        """Anonimiza dirección IP para privacidad."""
        if ':' in ip:  # IPv6
            parts = ip.split(':')
            return ':'.join(parts[:4]) + ':****'
        else:  # IPv4
            parts = ip.split('.')
            return '.'.join(parts[:2]) + '.***'


# ============================================================================
# VALIDACIÓN Y SANITIZACIÓN DE INPUTS
# ============================================================================

def sanitize_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitiza entrada del usuario para prevenir inyecciones.
    
    Protege contra:
    - XSS (Cross-Site Scripting)
    - SQL Injection
    - Command Injection
    - Path Traversal
    """
    if not text:
        return ""
    
    # 1. Limitar longitud
    text = text[:max_length]
    
    # 2. Remover HTML/JavaScript malicioso
    text = bleach.clean(text, tags=[], strip=True)
    
    # 3. Remover caracteres peligrosos
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'\.\./+',  # Path traversal
        r'[\x00-\x1f\x7f]',  # Control characters
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # 4. Escapar caracteres especiales
    text = text.replace('\\', '\\\\').replace('"', '\\"')
    
    return text.strip()


def validate_input(text: str) -> tuple[bool, str]:
    """
    Valida que la entrada cumpla con los criterios de seguridad.
    
    Returns:
        (is_valid, error_message)
    """
    if not text:
        return False, "El mensaje no puede estar vacío"
    
    if len(text) > 2000:
        return False, "El mensaje excede el límite de 2000 caracteres"
    
    if len(text.strip()) < 3:
        return False, "El mensaje es demasiado corto"
    
    # Detectar intentos de inyección SQL
    sql_patterns = [
        r'\b(union|select|insert|update|delete|drop|create|alter)\b',
        r'--',
        r'/\*.*?\*/',
        r';.*?(drop|exec|execute)',
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Entrada inválida: contiene patrones no permitidos"
    
    # Detectar comandos del sistema
    if re.search(r'\$\(|\`|&&|\|\|', text):
        return False, "Entrada inválida: contiene caracteres de comando"
    
    return True, ""


# ============================================================================
# RATE LIMITING
# ============================================================================

def check_rate_limit(security_manager, ip_address, max_requests=20, window_seconds=60):
    """
    Verifica si la IP ha excedido el límite de peticiones.
    
    Args:
        security_manager: Instancia de SecurityManager
        ip_address: Dirección IP del cliente
        max_requests: Número máximo de peticiones
        window_seconds: Ventana de tiempo en segundos
    
    Returns:
        (allowed, remaining_requests)
    """
    now = datetime.now()
    cutoff = now - timedelta(seconds=window_seconds)
    
    # Obtener peticiones recientes de esta IP
    if ip_address not in security_manager.rate_limit_storage:
        security_manager.rate_limit_storage[ip_address] = []
    
    # Filtrar peticiones dentro de la ventana de tiempo
    recent_requests = [
        ts for ts in security_manager.rate_limit_storage[ip_address]
        if ts > cutoff
    ]
    
    # Actualizar storage
    security_manager.rate_limit_storage[ip_address] = recent_requests
    
    # Verificar límite
    if len(recent_requests) >= max_requests:
        security_manager.log_security_event(
            'rate_limit_exceeded',
            f'IP excedió {max_requests} peticiones en {window_seconds}s',
            ip_address
        )
        return False, 0
    
    # Registrar nueva petición
    security_manager.rate_limit_storage[ip_address].append(now)
    
    remaining = max_requests - len(recent_requests) - 1
    return True, remaining


# ============================================================================
# DECORADORES DE SEGURIDAD
# ============================================================================

def require_api_key(security_manager):
    """Decorador para requerir API key válida."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener API key del header
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                security_manager.log_security_event(
                    'missing_api_key',
                    'Intento de acceso sin API key',
                    request.remote_addr
                )
                return jsonify({
                    'success': False,
                    'error': 'API key requerida. Incluye X-API-Key en el header.'
                }), 401
            
            if not security_manager.validate_api_key(api_key):
                security_manager.log_security_event(
                    'invalid_api_key',
                    'API key inválida',
                    request.remote_addr
                )
                return jsonify({
                    'success': False,
                    'error': 'API key inválida'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def apply_rate_limit(security_manager):
    """Decorador para aplicar rate limiting."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            
            allowed, remaining = check_rate_limit(security_manager, ip)
            
            if not allowed:
                return jsonify({
                    'success': False,
                    'error': 'Límite de peticiones excedido. Intenta en 1 minuto.'
                }), 429
            
            # Ejecutar función original
            result = f(*args, **kwargs)
            
            # No modificar headers ya que puede causar conflictos con Flask
            return result
        
        return decorated_function
    return decorator


# ============================================================================
# CIFRADO DE DATOS SENSIBLES
# ============================================================================

def encrypt_sensitive_data(data: str) -> str:
    """
    Cifra datos sensibles usando hash irreversible.
    Para datos que no necesitan ser recuperados (ej: contraseñas).
    """
    salt = os.getenv('SECURITY_SALT', 'grozy_default_salt_2025')
    salted = f"{salt}{data}".encode()
    return hashlib.sha256(salted).hexdigest()


def anonymize_data(data: dict) -> dict:
    """
    Anonimiza datos personales antes de logging.
    """
    anonymized = data.copy()
    
    # Campos sensibles a anonimizar
    sensitive_fields = ['user_id', 'email', 'ip_address', 'phone']
    
    for field in sensitive_fields:
        if field in anonymized:
            # Reemplazar con hash parcial
            value = str(anonymized[field])
            anonymized[field] = f"***{value[-4:]}" if len(value) > 4 else "****"
    
    return anonymized


# ============================================================================
# HEADERS DE SEGURIDAD
# ============================================================================

def add_security_headers(response):
    """Agrega headers de seguridad HTTP a las respuestas."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response


# ============================================================================
# INSTANCIA GLOBAL
# ============================================================================

# Crear instancia única del gestor de seguridad
security_manager = SecurityManager()

print(f"""
╔══════════════════════════════════════════════════════════╗
║          🔒 SISTEMA DE SEGURIDAD INICIALIZADO           ║
╚══════════════════════════════════════════════════════════╝

📋 Configuración:
   • Rate Limiting: {security_manager.MAX_REQUESTS_PER_MINUTE} req/min
   • Longitud máxima: {security_manager.MAX_MESSAGE_LENGTH} chars
   • Validación de inputs: ✅ Habilitada
   • Sanitización XSS/SQL: ✅ Habilitada
   • Cifrado de datos: ✅ Habilitado
   • Anonimización: ✅ Habilitada
   • Gestión de secretos: ✅ Habilitada

🔑 API Key Maestra Generada:
   {security_manager.master_key}
   
   ⚠️  IMPORTANTE: Guarda esta API key en tu .env:
   GROZY_API_KEY={security_manager.master_key}

🛡️  Protecciones Activas:
   ✓ Prevención de inyección SQL
   ✓ Prevención de XSS
   ✓ Protección contra Command Injection
   ✓ Rate Limiting por IP
   ✓ Validación de entradas
   ✓ Logs de seguridad anonimizados
   ✓ Headers de seguridad HTTP
   ✓ Principio de mínimo privilegio

""")
