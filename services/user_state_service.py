from sqlalchemy.orm import Session
from database.models import UserState, Order, OrderItem
from datetime import datetime

def get_or_create_user(db: Session, phone_number: str) -> UserState:
    """
    Obtiene o crea un usuario en la base de datos
    """
    user = db.query(UserState).filter(UserState.phone_number == phone_number).first()
    
    if not user:
        user = UserState(
            phone_number=phone_number,
            current_state="INITIAL",
            last_interaction=datetime.now()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_interaction = datetime.now()
        db.commit()
    
    return user

def update_user_state(db: Session, phone_number: str, state: str, category_id: int = None):
    """
    Actualiza el estado del usuario
    """
    user = get_or_create_user(db, phone_number)
    user.current_state = state
    if category_id is not None:
        user.current_category_id = category_id
    user.last_interaction = datetime.now()
    db.commit()
    return user

def get_user_current_order(db: Session, user_id: int) -> Order:
    """
    Obtiene el pedido pendiente actual del usuario o crea uno nuevo
    """
    order = db.query(Order).filter(
        Order.user_id == user_id,
        Order.status == "PENDING"
    ).first()
    
    if not order:
        order = Order(user_id=user_id, status="PENDING")
        db.add(order)
        db.commit()
        db.refresh(order)
    
    return order

def add_item_to_order(db: Session, order_id: int, product_id: int, quantity: int, price: float):
    """
    Agrega un producto al pedido
    """
    # Verificar si el producto ya existe en el pedido
    existing_item = db.query(OrderItem).filter(
        OrderItem.order_id == order_id,
        OrderItem.product_id == product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += quantity
    else:
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price
        )
        db.add(item)
    
    db.commit()

def calculate_order_total(db: Session, order_id: int) -> float:
    """
    Calcula el total del pedido
    """
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    total = sum(item.price * item.quantity for item in items)
    
    # Actualizar el total en el pedido
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.total = total
        db.commit()
    
    return total

def clear_user_cart(db: Session, user_id: int):
    """
    Limpia el carrito del usuario (pedido pendiente)
    """
    order = db.query(Order).filter(
        Order.user_id == user_id,
        Order.status == "PENDING"
    ).first()
    
    if order:
        db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
        db.delete(order)
        db.commit()
