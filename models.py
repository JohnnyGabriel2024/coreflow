# modelo escalable

from datetime import datetime
from database import db

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(50))
    empresa = db.Column(db.String(100))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    interacciones = db.relationship('Interaccion', backref='cliente', lazy=True)


class Interaccion(db.Model):
    __tablename__ = 'interacciones'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    tipo = db.Column(db.String(50))
    nota = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
from datetime import datetime
from database import db

# =========================
# PRODUCTOS
# =========================
class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=True)
    nombre = db.Column(db.String(100), nullable=False, index=True)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(80), index=True)
    unidad_medida = db.Column(db.String(20), default='u')
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(20), default='activo')
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def esta_bajo_stock(self):
        return self.stock <= self.stock_minimo


# =========================
# VENTAS
# =========================
class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, default=0)

    cliente = db.relationship('Cliente', backref='ventas')


# =========================
# DETALLE DE VENTA
# =========================
class DetalleVenta(db.Model):
    __tablename__ = 'detalle_ventas'

    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

    venta = db.relationship('Venta', backref='detalles')
    producto = db.relationship('Producto')