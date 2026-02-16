from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base

class Category(Base):
    """Categorías del menú (Platos Especiales, Sopas, etc.)"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    order = Column(Integer, default=0)  # Para ordenar en el menú
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    """Productos del menú"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    available = Column(Integer, default=1)  # 1 = disponible, 0 = no disponible
    
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class UserState(Base):
    """Estado de la conversación del usuario"""
    __tablename__ = "user_states"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    current_state = Column(String(50), default="INITIAL")  # INITIAL, MENU, CATEGORY, SELECTING, CONFIRMING
    current_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    last_interaction = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    orders = relationship("Order", back_populates="user")

class Order(Base):
    """Pedidos de los usuarios"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_states.id"))
    status = Column(String(20), default="PENDING")  # PENDING, CONFIRMED, COMPLETED, CANCELLED
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    notes = Column(Text, nullable=True)
    
    user = relationship("UserState", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    """Items individuales de cada pedido"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)  # Precio al momento del pedido
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
