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
            {"name": "Apanado de res", "price": 15.0, "category_id": categories["Platos Especiales"]},
            {"name": "Apanado de cerdo", "price": 14.0, "category_id": categories["Platos Especiales"]},
            {"name": "Hornado Completo", "price": 18.0, "category_id": categories["Platos Especiales"]},
            {"name": "Tortillas con Fritada", "price": 16.0, "category_id": categories["Platos Especiales"]},
            {"name": "ChocloMote con Fritada", "price": 15.0, "category_id": categories["Platos Especiales"]},
            {"name": "Fritada Completa", "price": 17.0, "category_id": categories["Platos Especiales"]},
            {"name": "Mote de la Magdalena", "price": 14.0, "category_id": categories["Platos Especiales"]},
            {"name": "Churrasco de Cerdo", "price": 16.0, "category_id": categories["Platos Especiales"]},
            {"name": "Churrasco de Res", "price": 17.0, "category_id": categories["Platos Especiales"]},
            {"name": "Fritada Tradicional", "price": 15.0, "category_id": categories["Platos Especiales"]},
            {"name": "Magdalenazo", "price": 20.0, "category_id": categories["Platos Especiales"]},
            
            # Platos Tradicionales
            {"name": "Ambateñito", "price": 12.0, "category_id": categories["Platos Tradicionales"]},
            {"name": "Guatita", "price": 11.0, "category_id": categories["Platos Tradicionales"]},
            {"name": "Tortillas con caucara", "price": 10.0, "category_id": categories["Platos Tradicionales"]},
            {"name": "Tortillas con Fritada", "price": 12.0, "category_id": categories["Platos Tradicionales"]},
            {"name": "Hornado", "price": 13.0, "category_id": categories["Platos Tradicionales"]},
            {"name": "Seco de Chivo", "price": 14.0, "category_id": categories["Platos Tradicionales"]},
            
            # Sopas Especiales
            {"name": "Papas con Librillo", "price": 8.0, "category_id": categories["Sopas Especiales"]},
            {"name": "Papas con Cuero", "price": 8.0, "category_id": categories["Sopas Especiales"]},
            {"name": "Yahuarlocro", "price": 9.0, "category_id": categories["Sopas Especiales"]},
            {"name": "Mixto", "price": 9.0, "category_id": categories["Sopas Especiales"]},
            {"name": "Menudo de la Magdalena", "price": 10.0, "category_id": categories["Sopas Especiales"]},
            {"name": "Caldo de Gallina", "price": 8.0, "category_id": categories["Sopas Especiales"]},
            {"name": "Caldo de Pata", "price": 7.0, "category_id": categories["Sopas Especiales"]},
            {"name": "Locro Tradicional", "price": 7.0, "category_id": categories["Sopas Especiales"]},
            {"name": "Caldo de 31", "price": 9.0, "category_id": categories["Sopas Especiales"]},
            
            # Mini Especiales
            {"name": "Mini Hornado", "price": 6.0, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Apanado", "price": 6.0, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Tortillas con fritada", "price": 6.0, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Mote de la Magdalena", "price": 5.0, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Seco de Chivo", "price": 7.0, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Churrasco de cerdo", "price": 7.0, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Churrasco de Res", "price": 7.0, "category_id": categories["Mini Especiales"]},
            {"name": "Mini Choclomote con Fritada", "price": 6.0, "category_id": categories["Mini Especiales"]},
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
