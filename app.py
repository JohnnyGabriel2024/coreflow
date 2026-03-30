from flask import Flask, render_template, request, redirect, url_for
import os

from database import db
from models import Cliente, Interaccion, Producto, Venta, DetalleVenta

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.environ.get("DB_PATH", os.path.join(INSTANCE_DIR, 'crm.db'))

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

os.makedirs(INSTANCE_DIR, exist_ok=True)

with app.app_context():
    if not os.path.exists(DB_PATH):
        print("🆕 Creando base de datos...")
        db.create_all()
    else:
        print("📦 Base de datos existente detectada. No se modifica.")

    # Migración ligera: agregar columnas faltantes en productos (sin perder datos)
    con = db.session.connection()
    from sqlalchemy import text

    cols = {row[1] for row in con.execute(text("PRAGMA table_info(productos)"))}
    adds = [
        ("sku", "TEXT"),
        ("descripcion", "TEXT"),
        ("categoria", "TEXT"),
        ("unidad_medida", "TEXT"),
        ("stock_minimo", "INTEGER"),
        ("estado", "TEXT"),
        ("fecha_actualizacion", "DATETIME"),
    ]
    for col_name, col_type in adds:
        if col_name not in cols:
            default = "'activo'" if col_name == 'estado' else "0" if col_name == 'stock_minimo' else "'u'" if col_name == 'unidad_medida' else None
            stmt = f"ALTER TABLE productos ADD COLUMN {col_name} {col_type}"
            if default is not None:
                stmt += f" DEFAULT {default}"
            con.execute(text(stmt))
    db.session.commit()


# =========================
# 🔥 FILTROS
# =========================

@app.template_filter('clp')
def format_clp(value):
    return f"${value:,.0f}".replace(",", ".")


@app.template_filter('fecha')
def format_fecha(value):
    return value.strftime('%d-%m-%Y %H:%M')


# =========================
# ROUTES
# =========================

@app.route('/')
def index():
    clientes = Cliente.query.order_by(Cliente.fecha_creacion.desc()).all()
    return render_template('clientes.html', clientes=clientes)


@app.route('/cliente/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        cliente = Cliente(
            nombre=request.form['nombre'],
            email=request.form.get('email'),
            telefono=request.form.get('telefono'),
            empresa=request.form.get('empresa')
        )
        db.session.add(cliente)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('cliente_form.html')


@app.route('/cliente/<int:id>')
def cliente_detalle(id):
    cliente = Cliente.query.get_or_404(id)
    return render_template('cliente_detalle.html', cliente=cliente)


@app.route('/cliente/<int:id>/interaccion/nuevo', methods=['GET'])
def nueva_interaccion(id):
    cliente = Cliente.query.get_or_404(id)
    tipos = ['llamada', 'email', 'reunión', 'nota', 'otro']
    return render_template('interaccion_form.html', cliente=cliente, tipos=tipos)


@app.route('/cliente/<int:id>/interaccion', methods=['POST'])
def agregar_interaccion(id):
    cliente = Cliente.query.get_or_404(id)
    tipo = request.form.get('tipo', '').strip()
    nota = request.form.get('nota', '').strip()

    if not tipo or not nota:
        # Se puede mejorar con flash, por ahora re-envía al formulario
        return redirect(url_for('nueva_interaccion', id=id))

    interaccion = Interaccion(
        cliente_id=cliente.id,
        tipo=tipo,
        nota=nota
    )

    db.session.add(interaccion)
    db.session.commit()

    return redirect(url_for('cliente_detalle', id=id))


@app.route('/dashboard')
def dashboard():
    total_clientes = Cliente.query.count()
    total_interacciones = Interaccion.query.count()

    interacciones_recientes = Interaccion.query.order_by(
        Interaccion.fecha.desc()
    ).limit(5).all()

    # 📊 Ventas por cliente
    ventas = db.session.query(
        Cliente.nombre,
        db.func.sum(Venta.total)
    ).join(Venta).group_by(Cliente.nombre).all()

    clientes_labels = [v[0] for v in ventas]
    ventas_data = [float(v[1]) for v in ventas]

    # 📈 Interacciones por tipo
    interacciones = db.session.query(
        Interaccion.tipo,
        db.func.count(Interaccion.id)
    ).group_by(Interaccion.tipo).all()

    tipos_labels = [i[0] for i in interacciones]
    tipos_data = [i[1] for i in interacciones]

    # 💰 Total ventas
    total_ventas = db.session.query(db.func.sum(Venta.total)).scalar() or 0

    # 📈 Ticket promedio
    cantidad_ventas = Venta.query.count()
    ticket_promedio = total_ventas / cantidad_ventas if cantidad_ventas > 0 else 0

    # 🏆 Mejor cliente
    mejor_cliente = db.session.query(
        Cliente.nombre,
        db.func.sum(Venta.total).label('total')
    ).join(Venta).group_by(Cliente.id).order_by(db.desc('total')).first()

    nombre_mejor_cliente = mejor_cliente[0] if mejor_cliente else "N/A"

    return render_template(
        'dashboard.html',
        total_clientes=total_clientes,
        total_interacciones=total_interacciones,
        interacciones_recientes=interacciones_recientes,
        clientes_labels=clientes_labels,
        ventas_data=ventas_data,
        tipos_labels=tipos_labels,
        tipos_data=tipos_data,

        # 🔥 KPIs financieros
        total_ventas=total_ventas,
        ticket_promedio=ticket_promedio,
        mejor_cliente=nombre_mejor_cliente
    )


@app.route('/producto/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if request.method == 'POST':
        sku = request.form.get('sku', '').strip() or None
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        categoria = request.form.get('categoria', '').strip()
        unidad_medida = request.form.get('unidad_medida', 'u').strip()
        precio = float(request.form.get('precio', 0) or 0)
        stock = int(request.form.get('stock', 0) or 0)
        stock_minimo = int(request.form.get('stock_minimo', 0) or 0)

        if not nombre or precio < 0 or stock < 0:
            return redirect(url_for('nuevo_producto'))

        producto = Producto(
            sku=sku,
            nombre=nombre,
            descripcion=descripcion,
            categoria=categoria,
            unidad_medida=unidad_medida,
            precio=precio,
            stock=stock,
            stock_minimo=stock_minimo,
            estado='activo'
        )

        db.session.add(producto)
        db.session.commit()
        return redirect(url_for('nuevo_producto'))

    filtro = request.args.get('filtro', '').strip()
    if filtro:
        productos = Producto.query.filter(
            db.or_(
                Producto.nombre.ilike(f"%{filtro}%"),
                Producto.sku.ilike(f"%{filtro}%"),
                Producto.categoria.ilike(f"%{filtro}%")
            )
        ).all()
    else:
        productos = Producto.query.all()

    return render_template('producto_form.html', productos=productos, filtro=filtro)


@app.route('/venta/nueva', methods=['GET', 'POST'])
def nueva_venta():
    clientes = Cliente.query.all()
    productos = Producto.query.all()

    if request.method == 'POST':
        cliente_id = request.form['cliente_id']

        venta = Venta(cliente_id=cliente_id)
        db.session.add(venta)
        db.session.commit()

        total = 0

        productos_ids = request.form.getlist('producto_id')
        cantidades = request.form.getlist('cantidad')

        for i in range(len(productos_ids)):
            cantidad_str = cantidades[i]

            if not cantidad_str or cantidad_str.strip() == '':
                continue

            cantidad = int(cantidad_str)

            if cantidad > 0:
                producto = Producto.query.get(int(productos_ids[i]))
                if not producto or producto.estado != 'activo':
                    continue

                if cantidad > producto.stock:
                    db.session.rollback()
                    return "Stock insuficiente para {}".format(producto.nombre), 400

                producto.stock -= cantidad

                subtotal = producto.precio * cantidad
                total += subtotal

                detalle = DetalleVenta(
                    venta_id=venta.id,
                    producto_id=producto.id,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )

                db.session.add(detalle)

        venta.total = total
        db.session.commit()

        return redirect(url_for('listar_ventas'))

    return render_template(
        'venta_form.html',
        clientes=clientes,
        productos=productos
    )


@app.route('/ventas')
def listar_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template('ventas.html', ventas=ventas)


@app.route('/venta/<int:id>')
def detalle_venta(id):
    venta = Venta.query.get_or_404(id)
    return render_template('venta_detalle.html', venta=venta)


if __name__ == '__main__':
    app.run(debug=True)
