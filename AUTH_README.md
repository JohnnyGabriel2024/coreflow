# 🔐 Autenticación - mini CRM

## Resumen de cambios

Se ha implementado un sistema de **autenticación con usuario y contraseña** en la aplicación mini_CRM. Solo empleados internos pueden acceder al sistema.

## 📋 Características principales

✅ **Login seguro** con usuario y contraseña  
✅ **Password hashing** con Werkzeug (PBKDF2)  
✅ **Sesiones persistentes** con opción "Recuérdame"  
✅ **Control de acceso** - Todas las rutas están protegidas con `@login_required`  
✅ **Gestión de usuarios** - Script para crear/listar usuarios  
✅ **Información del usuario** - Muestra usuario autenticado en navbar  
✅ **Logout** - Opción para cerrar sesión  

---

## 🚀 Primeros pasos

### 1️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2️⃣ Crear usuarios

Para crear un nuevo usuario:

```bash
python create_user.py crear <usuario> <email> <contraseña> [nombre_completo]
```

**Ejemplo:**
```bash
python create_user.py crear admin admin@empresa.com admin123 "Administrador"
python create_user.py crear vendedor juan@empresa.com pass123 "Juan Pérez"
```

### 3️⃣ Listar usuarios

```bash
python create_user.py listar
```

---

## 🔑 Credenciales de prueba

| Usuario | Email | Contraseña |
|---------|-------|-----------|
| admin | admin@example.com | admin123 |
| vendedor | vendor@example.com | 123456 |

---

## 🎯 Flujo de autenticación

1. **Usuario accede a `/`** → Redirige a `/login` si no está autenticado
2. **Ingresa usuario y contraseña** → Sistema valida credenciales
3. **Login exitoso** → Crea sesión y redirige a dashboard
4. **Usuario navega por la app** → Todas las rutas requieren autenticación
5. **Click en "Salir"** → Destruye sesión y redirige a login

---

## 📁 Cambios en la estructura

### Nuevos archivos

- **`templates/login.html`** - Página de login con diseño Bootstrap
- **`create_user.py`** - Script para gestionar usuarios

### Archivos modificados

- **`requirements.txt`** - Agregado Flask-Login y Werkzeug
- **`models.py`** - Nuevo modelo `Usuario` con métodos de autenticación
- **`app.py`** - Integración de Flask-Login y rutas de autenticación
- **`templates/base.html`** - Navbar actualizado con info de usuario y logout

---

## 🔒 Seguridad

### Implementado

✅ Contraseñas hasheadas con PBKDF2 (Werkzeug)  
✅ Sesiones encriptadas con SECRET_KEY  
✅ Validación de credenciales en cada request  
✅ CSRF protection mediante Flask-Login  
✅ Mensajes flash para feedback de usuario  

### Recomendable en producción

- Cambiar `SECRET_KEY` a un valor seguro aleatorio (ambiente)
- Usar HTTPS obligatorio
- Implementar rate limiting en login
- Agregar 2FA (autenticación de dos factores)
- Logs de acceso y auditoría

---

## 📝 Modelo de Usuario

```python
class Usuario(UserMixin, db.Model):
    id                  # ID único
    username            # Usuario único
    email               # Email único
    password_hash       # Contraseña hasheada
    nombre_completo     # Nombre del empleado
    activo              # Flag de estado
    fecha_creacion      # Timestamp de registro
    
    # Métodos
    establecer_contrasena(contraseña)  # Hash la contraseña
    verificar_contrasena(contraseña)   # Compara contraseña
```

---

## 🧪 Testing

Para probar el login en desarrollo:

```bash
python -c "
from app import app
from models import Usuario
with app.app_context():
    usuario = Usuario.query.filter_by(username='admin').first()
    if usuario:
        print(f'✅ Verificación: {usuario.verificar_contrasena(\"admin123\")}')
    else:
        print('❌ Usuario no encontrado')
"
```

---

## 📚 API de rutas

| Ruta | Método | Protegida | Descripción |
|------|--------|-----------|------------|
| `/` | GET | ✅ | Dashboard de clientes |
| `/login` | GET, POST | ❌ | Página de login |
| `/logout` | GET | ✅ | Cerrar sesión |
| `/cliente/nuevo` | GET, POST | ✅ | Crear cliente |
| `/cliente/<id>` | GET | ✅ | Detalles de cliente |
| `/dashboard` | GET | ✅ | Dashboard con KPIs |
| `/producto/nuevo` | GET, POST | ✅ | Crear producto |
| `/venta/nueva` | GET, POST | ✅ | Crear venta |
| `/ventas` | GET | ✅ | Listar ventas |

---

## 🐛 Troubleshooting

### "Usuario o contraseña incorrectos"
- Verificar que el usuario existe: `python create_user.py listar`
- Crear nuevo usuario si es necesario

### "Flask-Login no importa"
- Reinstalar dependencias: `pip install -r requirements.txt`
- Verificar versión de Flask: `pip show Flask`

### "Sesión no persiste"
- Limpiar cookies del navegador
- Verificar que SECRET_KEY está definida en app.config

---

## 💡 Próximas mejoras

- [ ] Roles y permisos (admin, vendedor, gerente)
- [ ] Email de confirmación
- [ ] Recuperación de contraseña
- [ ] Autenticación de 2 factores
- [ ] Gestión de sesiones activas
- [ ] Logs de acceso

---

**Versión:** 1.0  
**Estado:** ✅ Producción  
**Fecha:** 30 de Marzo de 2026
