from database.database import SessionLocal, init_db
from database.models import Category, Product

def seed_database():
    """Puebla la base de datos con categorías y productos"""
    
    # Inicializar tablas
    init_db()
    
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        if db.query(Category).count() > 0:
            print("La base de datos ya tiene datos")
            return
        
        # Crear categorías
        categories_data = [
            {"name": "Platos Especiales", "order": 1},
            {"name": "Platos Tradicionales", "order": 2},
            {"name": "Sopas Especiales", "order": 3},
            {"name": "Mini Especiales", "order": 4},
            {"name": "Mini Tradicionales", "order": 5},
            {"name": "Mini Sopas", "order": 6},
            {"name": "Extras", "order": 7},
            {"name": "Bebidas", "order": 8},
            {"name": "Postres", "order": 9},
            {"name": "Promociones", "order": 10},
            {"name": "Antonjitos Tradicionales", "order": 11},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.add(category)
            db.flush()
            categories[cat_data["name"]] = category.id
        
        # Productos por categoría
        products_data = [
            # Platos Especiales
            {"name": "Apanado de Res", "price": 7.99, "category_id": categories["Platos Especiales"]},
            {"name": "Apanado de Cerdo", "price": 7.99, "category_id": categories["Platos Especiales"]},
            {"name": "Hornado Completo", "price": 10.50, "category_id": categories["Platos Especiales"]},
            {"name": "Tortillas con Fritada", "price": 8.75, "category_id": categories["Platos Especiales"]},
            {"name": "Choclo Mote con Fritada", "price": 6.99, "category_id": categories["Platos Especiales"]},
            {"name": "Fritada Completa", "price": 9.99, "category_id": categories["Platos Especiales"]},
            {"name": "Mote de la Magdalena", "price": 6.99, "category_id": categories["Platos Especiales"]},
            {"name": "Churrasco de Cerdo", "price": 7.99, "category_id": categories["Platos Especiales"]},
            {"name": "Churrasco de Res", "price": 7.99, "category_id": categories["Platos Especiales"]},
            {"name": "Fritada Tradicional", "price": 8.50, "category_id": categories["Platos Especiales"]},
            {"name": "Magdalenazo", "price": 9.50, "category_id": categories["Platos Especiales"]},
            {"name": "Mote con Chicharrón", "price": 6.25, "category_id": categories["Platos Especiales"]},
            
            # Platos Tradicionales
            {"name": "Ambateñito", "price": 6.5, "category_id": categories["Platos Tradicionales"]},
            {"name": "Guatita", "price": 5.99, "category_id": categories["Platos Tradicionales"]},
            {"name": "Tortillas con Caucara", "price": 5.99, "category_id": categories["Platos Tradicionales"]},
            {"name": "Tortillas con Chorizo", "price": 5.99, "category_id": categories["Platos Tradicionales"]},
            {"name": "Hornado", "price": 9.75, "category_id": categories["Platos Tradicionales"]},
            {"name": "Seco de Chivo", "price": 9.99, "category_id": categories["Platos Tradicionales"]},
            
            # Sopas Especiales
            {"name": "Papa con Librillo", "price": 5.99, "category_id": categories["Sopas Especiales"]},
            {"name": "Papas con Cuero", "price": 5.99, "category_id": categories["Sopas Especiales"]},
            {"name": "Yahuarlocro", "price": 7.5, "category_id": categories["Sopas Especiales"]},
            {"name": "Mixto", "price": 6.50, "category_id": categories["Sopas Especiales"]},
            {"name": "Menudo de la Magdalena", "price": 6.75, "category_id": categories["Sopas Especiales"]},
            {"name": "Caldo de Gallina", "price": 6.50, "category_id": categories["Sopas Especiales"]},
            {"name": "Caldo de Pata", "price": 6.50, "category_id": categories["Sopas Especiales"]},
            {"name": "Locro Tradicional", "price": 5.25, "category_id": categories["Sopas Especiales"]},
            {"name": "Caldo de 31", "price": 5.99, "category_id": categories["Sopas Especiales"]},
            
            # Mini Especiales
            {"name": "Mini Hornado", "price": 6.99, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Apanado", "price": 6.99, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Tortillas con Fritada", "price": 6.50, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Mote de la Magdalena", "price": 5.99, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Seco de Chivo", "price": 6.99, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Churrasco de Cerdo", "price": 6.99, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Churrasco de Res", "price": 6.99, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Choclo Mote con Fritada", "price": 5.99, "category_id": categories["Mini Especiales"]},

            # Mini Tradicionales
            {"name": "Mini Ambateñito", "price": 5.50, "category_id": categories["Mini Tradicionales"]},
            {"name": "Mini Tortillas con Caucara", "price": 4.99, "category_id": categories["Mini Tradicionales"]},
            {"name": "Mini Tortillas con Chorizo", "price": 4.99, "category_id": categories["Mini Tradicionales"]},
            {"name": "Mini Guatita", "price": 4.99, "category_id": categories["Mini Tradicionales"]},

            # Mini Sopas
            {"name": "Mini Menudo de la Magdalena", "price": 5.50, "category_id": categories["Mini Sopas"]},
            {"name": "Mini Papa con Librillo", "price": 4.99, "category_id": categories["Mini Sopas"]},
            {"name": "Mini Yahuarlocro", "price": 5.99, "category_id": categories["Mini Sopas"]},
            {"name": "Mini Papas con Cuero", "price": 4.99, "category_id": categories["Mini Sopas"]},
            {"name": "Mini Caldo de Pata", "price": 5.25, "category_id": categories["Mini Sopas"]},
            {"name": "Mini Mixto", "price": 4.99, "category_id": categories["Mini Sopas"]},

            # Extras
            {"name": "Empanada Grande de Morocho", "price": 1.99, "category_id": categories["Extras"]},
            {"name": "Chorizo", "price": 1.75, "category_id": categories["Extras"]},
            {"name": "Empanadas de Morocho 3 Grandes", "price": 5.25, "category_id": categories["Extras"]},
            {"name": "Maduros Fritos", "price": 1.50, "category_id": categories["Extras"]},
            {"name": "Empanadas de Morocho 3 Pequeñas", "price": 3.50, "category_id": categories["Extras"]},
            {"name": "Crujiente", "price": 3.50, "category_id": categories["Extras"]},
            {"name": "½ Aguacate", "price": 1.00, "category_id": categories["Extras"]},
            {"name": "Carita Feliz", "price": 1.75, "category_id": categories["Extras"]},
            {"name": "Choclo, Habas y Queso", "price": 3.75, "category_id": categories["Extras"]},
            {"name": "Porción de Morcilla", "price": 3.99, "category_id": categories["Extras"]},
            {"name": "Mix Tradicional", "price": 4.99, "category_id": categories["Extras"]},
            {"name": "Choclo con Queso", "price": 2.99, "category_id": categories["Extras"]},
            {"name": "Porción de Arroz", "price": 1.75, "category_id": categories["Extras"]},
            {"name": "Porción de Mote", "price": 1.99, "category_id": categories["Extras"]},
            {"name": "Porción de Choclo Mote", "price": 2.25, "category_id": categories["Extras"]},
            {"name": "Porción de Tortillas", "price": 2.25, "category_id": categories["Extras"]},

            # Bebidas (nombres exactos del parser)
            {"name": "Agua Personal", "price": 0.99, "category_id": categories["Bebidas"]},
            {"name": "Gaseo Personal", "price": 1.50, "category_id": categories["Bebidas"]},
            {"name": "Fuze Tea", "price": 1.60, "category_id": categories["Bebidas"]},
            {"name": "Limonada Mediana", "price": 1.50, "category_id": categories["Bebidas"]},
            {"name": "Jugo Mediano", "price": 1.99, "category_id": categories["Bebidas"]},
            {"name": "Magchicha Familiar", "price": 3.25, "category_id": categories["Bebidas"]},
            {"name": "Magchicha Mediana", "price": 1.50, "category_id": categories["Bebidas"]},

            # Postres
            {"name": "Mousse de Chocolate", "price": 1.99, "category_id": categories["Postres"]},
            {"name": "Mousse de Maracuyá", "price": 1.99, "category_id": categories["Postres"]},
            {"name": "Mousse de Mora", "price": 1.99, "category_id": categories["Postres"]},

            # Promociones (nombres exactos del parser)
            {"name": "Combo Dupla Personal", "price": 13.99, "category_id": categories["Promociones"]},
            {"name": "Combo Compartir", "price": 12.99, "category_id": categories["Promociones"]},
            {"name": "Combo Ideal", "price": 8.50, "category_id": categories["Promociones"]},
            {"name": "Combo Tradición 2", "price": 6.99, "category_id": categories["Promociones"]},
            {"name": "Combo Tradición 1", "price": 6.99, "category_id": categories["Promociones"]},

            # Antojitos Tradicionales
            {"name": "Morocho + 2 Empanadas de Viento", "price": 3.25, "category_id": categories["Antonjitos Tradicionales"]},
            {"name": "Morocho Solo", "price": 2.50, "category_id": categories["Antonjitos Tradicionales"]},
            {"name": "Combo Empanada de Viento", "price": 2.25, "category_id": categories["Antonjitos Tradicionales"]},
            {"name": "Empanada de Viento", "price": 0.99, "category_id": categories["Antonjitos Tradicionales"]},
            {"name": "Quimbolito + Café", "price": 2.25, "category_id": categories["Antonjitos Tradicionales"]},
            {"name": "Quimbolito", "price": 1.99, "category_id": categories["Antonjitos Tradicionales"]},
            {"name": "Humita + Café", "price": 2.25, "category_id": categories["Antonjitos Tradicionales"]},
            {"name": "Humita", "price": 1.99, "category_id": categories["Antonjitos Tradicionales"]},
            {"name": "Bolón + Café", "price": 2.25, "category_id": categories["Antonjitos Tradicionales"]},
            {"name": "Bolón", "price": 1.99, "category_id": categories["Antonjitos Tradicionales"]},
        ]
        
        for prod_data in products_data:
            product = Product(**prod_data)
            db.add(product)
        
        db.commit()
        print("✅ Base de datos poblada exitosamente")
        print(f"   - {len(categories_data)} categorías")
        print(f"   - {len(products_data)} productos")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al poblar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
