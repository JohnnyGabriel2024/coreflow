#!/usr/bin/env python
"""
Script para crear usuarios en el sistema CRM
Uso: python create_user.py <username> <email> <contraseña>
"""

import sys
import os
from database import db
from models import Usuario
from app import app

def crear_usuario(username, email, contrasena, nombre_completo=None):
    """Crea un nuevo usuario en la base de datos"""
    
    with app.app_context():
        # Verificar si el usuario ya existe
        usuario_existente = Usuario.query.filter_by(username=username).first()
        if usuario_existente:
            print(f"❌ Error: El usuario '{username}' ya existe.")
            return False
        
        # Verificar si el email ya existe
        email_existente = Usuario.query.filter_by(email=email).first()
        if email_existente:
            print(f"❌ Error: El email '{email}' ya está registrado.")
            return False
        
        # Crear el usuario
        usuario = Usuario(
            username=username,
            email=email,
            nombre_completo=nombre_completo or username
        )
        usuario.establecer_contrasena(contrasena)
        
        try:
            db.session.add(usuario)
            db.session.commit()
            print(f"✅ Usuario '{username}' creado exitosamente!")
            print(f"   Email: {email}")
            print(f"   Nombre: {usuario.nombre_completo}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear el usuario: {str(e)}")
            return False


def listar_usuarios():
    """Lista todos los usuarios activos"""
    with app.app_context():
        usuarios = Usuario.query.all()
        if not usuarios:
            print("No hay usuarios registrados.")
            return
        
        print("\n📋 Usuarios del sistema:")
        print("-" * 60)
        for usuario in usuarios:
            estado = "✅ Activo" if usuario.activo else "❌ Inactivo"
            print(f"  • {usuario.username:20} | {usuario.email:25} | {estado}")
        print("-" * 60)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Sin argumentos: mostrar menú
        print("\n🔐 Gestor de Usuarios - mini CRM")
        print("=" * 50)
        print("\nUso:")
        print("  python create_user.py crear <usuario> <email> <contraseña> [nombre]")
        print("  python create_user.py listar")
        print("\nEjemplos:")
        print("  python create_user.py crear admin admin@example.com 123456")
        print("  python create_user.py crear vendor vendedor@example.com pass123 'Juan Pérez'")
        print("  python create_user.py listar")
        print()
        
    elif len(sys.argv) >= 2:
        comando = sys.argv[1].lower()
        
        if comando == "crear" and len(sys.argv) >= 5:
            username = sys.argv[2]
            email = sys.argv[3]
            contrasena = sys.argv[4]
            nombre_completo = sys.argv[5] if len(sys.argv) > 5 else None
            crear_usuario(username, email, contrasena, nombre_completo)
            
        elif comando == "listar":
            listar_usuarios()
            
        else:
            print("❌ Comando no válido o faltan argumentos.")
            print("\nUsa 'python create_user.py' sin argumentos para ver la ayuda.")
