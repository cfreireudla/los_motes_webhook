from sqlalchemy.orm import Session
from database.models import Category, Product, Order, OrderItem
from services.interactive_messages import send_button_message, send_list_message, send_text_message
from services.user_state_service import (
    get_or_create_user, 
    update_user_state, 
    get_user_current_order,
    add_item_to_order,
    calculate_order_total
)

async def send_welcome_message(phone_number: str, name: str, db: Session):
    """
    Paso 1: Mensaje de bienvenida con botón de Menú
    """
    update_user_state(db, phone_number, "WELCOME")
    
    welcome_text = f"Hola {name}, ¡Bienvenido a Los Motes de la Magdalena! 🎉\n\nSelecciona una de las siguientes opciones para continuar 👇"
    
    buttons = [
        {"id": "show_menu", "title": "📋 Menú"}
    ]
    
    await send_button_message(phone_number, welcome_text, buttons)

async def send_main_menu(phone_number: str, db: Session, page: int = 1):
    """
    Paso 2: Muestra el menú principal con categorías
    """
    update_user_state(db, phone_number, "MENU")
    
    # Obtener categorías de la BD
    categories = db.query(Category).order_by(Category.order).all()
    
    if not categories:
        await send_text_message(phone_number, "Lo siento, el menú no está disponible en este momento.")
        return
    
    # WhatsApp permite maximo 10 filas por lista
    # Usamos 9 filas para categorias y 1 fila para paginacion
    page_size = 9
    total_pages = max(1, (len(categories) + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))

    start = (page - 1) * page_size
    end = start + page_size
    page_categories = categories[start:end]

    rows = [
        {
            "id": f"cat_{cat.id}",
            "title": cat.name,
            "description": cat.description or ""
        }
        for cat in page_categories
    ]

    if total_pages > 1:
        if page < total_pages:
            rows.append({
                "id": f"menu_page_{page + 1}",
                "title": f"➡️ Siguiente ({page + 1}/{total_pages})",
                "description": ""
            })
        if page > 1 and len(rows) < 10:
            rows.append({
                "id": f"menu_page_{page - 1}",
                "title": f"⬅️ Anterior ({page - 1}/{total_pages})",
                "description": ""
            })

    sections = [
        {
            "title": "Menú",
            "rows": rows
        }
    ]

    if total_pages > 1:
        menu_text = f"Menú (página {page}/{total_pages})\n\nSelecciona una categoría:"
    else:
        menu_text = "Menú\n\nSelecciona una categoría para ver los productos disponibles:"

    await send_list_message(phone_number, menu_text, "Ver opciones", sections)

async def send_category_products(phone_number: str, category_id: int, db: Session, page: int = 1):
    """
    Paso 3: Muestra productos de una categoría específica con paginación
    """
    update_user_state(db, phone_number, "CATEGORY", category_id)
    
    # Obtener productos de la categoría
    products = db.query(Product).filter(
        Product.category_id == category_id,
        Product.available == 1
    ).all()
    
    if not products:
        await send_text_message(phone_number, "No hay productos disponibles en esta categoría.")
        return
    
    category = db.query(Category).filter(Category.id == category_id).first()
    
    # WhatsApp max 10 filas: usamos 8 para productos, 1 para volver, 1 para paginación
    page_size = 8
    total_pages = max(1, (len(products) + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    
    start = (page - 1) * page_size
    end = start + page_size
    page_products = products[start:end]
    
    rows = [
        {
            "id": f"prod_{prod.id}",
            "title": prod.name[:24],  # WhatsApp max 24 chars
            "description": f"${prod.price:.2f}"
        }
        for prod in page_products
    ]
    
    # Agregar paginación si hay múltiples páginas
    if total_pages > 1:
        if page < total_pages:
            rows.append({
                "id": f"cat_{category_id}_page_{page + 1}",
                "title": f"➡️ Siguiente ({page + 1}/{total_pages})",
                "description": ""
            })
        if page > 1 and len(rows) < 9:
            rows.append({
                "id": f"cat_{category_id}_page_{page - 1}",
                "title": f"⬅️ Anterior ({page - 1}/{total_pages})",
                "description": ""
            })
    
    # Agregar opción de volver al menú
    rows.append({
        "id": "back_to_menu",
        "title": "🔙 Volver al Menú",
        "description": ""
    })
    
    sections = [
        {
            "title": category.name[:24],  # WhatsApp max 24 chars
            "rows": rows
        }
    ]
    
    if total_pages > 1:
        category_text = f"{category.name} (página {page}/{total_pages})\n\nSelecciona los productos que deseas agregar:"
    else:
        category_text = f"{category.name}\n\nSelecciona los productos que deseas agregar:"
    
    await send_list_message(
        phone_number, 
        category_text,
        "Seleccionar",
        sections
    )

async def add_product_to_cart(phone_number: str, product_id: int, db: Session):
    """
    Paso 4: Agrega producto al carrito y permite seguir comprando
    """
    user = get_or_create_user(db, phone_number)
    update_user_state(db, phone_number, "SELECTING")
    
    # Obtener el pedido actual
    order = get_user_current_order(db, user.id)
    
    # Obtener el producto
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        await send_text_message(phone_number, "Producto no encontrado.")
        return
    
    # Agregar al pedido
    add_item_to_order(db, order.id, product.id, 1, product.price)
    
    # Calcular total actual
    total = calculate_order_total(db, order.id)
    
    # Mensaje de confirmación con opciones
    message = f"✅ {product.name} agregado a tu pedido\n\nTotal actual: ${total:.2f}\n\n¿Qué deseas hacer?"
    
    buttons = [
        {"id": "continue_shopping", "title": "➕ Agregar más"},
        {"id": "view_cart", "title": "🛒 Ver carrito"},
        {"id": "confirm_order", "title": "✔️ Confirmar"}
    ]
    
    await send_button_message(phone_number, message, buttons)

async def show_cart_and_confirm(phone_number: str, db: Session):
    """
    Paso 5: Muestra el resumen del pedido y confirma
    """
    user = get_or_create_user(db, phone_number)
    order = get_user_current_order(db, user.id)
    
    # Obtener items del pedido
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    
    if not items:
        await send_text_message(phone_number, "Tu carrito está vacío. Selecciona productos del menú.")
        await send_main_menu(phone_number, db)
        return
    
    # Construir resumen del pedido
    summary = "🛒 *Resumen de tu pedido:*\n\n"
    
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        subtotal = item.price * item.quantity
        summary += f"• {product.name} x{item.quantity} - ${subtotal:.2f}\n"
    
    total = calculate_order_total(db, order.id)
    summary += f"\n*Total: ${total:.2f}*"
    
    await send_text_message(phone_number, summary)
    
    # Botones de confirmación
    buttons = [
        {"id": "confirm_final", "title": "✅ Confirmar pedido"},
        {"id": "continue_shopping", "title": "➕ Agregar más"},
        {"id": "cancel_order", "title": "❌ Cancelar"}
    ]
    
    await send_button_message(
        phone_number,
        "¿Deseas confirmar tu pedido?",
        buttons
    )

async def confirm_order(phone_number: str, db: Session):
    """
    Confirma el pedido y actualiza el estado
    """
    user = get_or_create_user(db, phone_number)
    order = get_user_current_order(db, user.id)
    
    # Cambiar estado del pedido
    order.status = "CONFIRMED"
    db.commit()
    
    # Resetear estado del usuario
    update_user_state(db, phone_number, "INITIAL")
    
    confirmation_msg = (
        f"✅ *¡Pedido confirmado!*\n\n"
        f"Número de pedido: #{order.id}\n"
        f"Total: ${order.total:.2f}\n\n"
        f"Gracias por tu compra. En breve nos comunicaremos contigo para coordinar la entrega. 🚀"
    )
    
    await send_text_message(phone_number, confirmation_msg)
