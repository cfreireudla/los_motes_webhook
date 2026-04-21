import json
import re
from typing import Dict, List, Any, Optional

MENU_URL = 'https://www.losmotesdelamagdalena.com/menu/'
ALIAS_MAP = {'menudo': 'Menudo de la Magdalena', 'menudo de la magdalena': 'Menudo de la Magdalena', 'mote': 'Mote de la Magdalena', 'mote de la magdalena': 'Mote de la Magdalena', 'hornado': 'Hornado', 'hornado completo': 'Hornado Completo', 'seco de chivo': 'Seco de Chivo', 'choclo mote con fritada': 'Choclo Mote con Fritada', 'churrasco con carne de res': 'Churrasco de Res', 'churrasco de res': 'Churrasco de Res', 'churrasco de cerdo': 'Churrasco de Cerdo', 'tortilla con caucara': 'Tortillas con Caucara', 'tortillas con caucara': 'Tortillas con Caucara', 'tortillas con fritada': 'Tortillas con Fritada', 'tortillas con chorizo': 'Tortillas con Chorizo', 'caldo de gallina': 'Caldo de Gallina', 'caldo de 31': 'Caldo de 31', 'caldo de pata': 'Caldo de Pata', 'papa con librillo': 'Papa con Librillo', 'papas con cuero': 'Papas con Cuero', 'mixto': 'Mixto', 'ambateñito': 'Ambateñito', 'guatita': 'Guatita', 'apanado de res': 'Apanado de Res', 'apanado de cerdo': 'Apanado de Cerdo', 'fritada completa': 'Fritada Completa', 'fritada tradicional': 'Fritada Tradicional', 'magdalenazo': 'Magdalenazo', 'combo ideal': 'Combo Ideal', 'combo compartir': 'Combo Compartir', 'combo dupla personal': 'Combo Dupla Personal', 'combo tradición 1': 'Combo Tradición 1', 'combo tradicion 1': 'Combo Tradición 1', 'combo tradición 2': 'Combo Tradición 2', 'combo tradicion 2': 'Combo Tradición 2', 'agua personal': 'Agua Personal', 'gaseo personal': 'Gaseo Personal', 'gaseosa personal': 'Gaseo Personal', 'fuze tea': 'Fuze Tea', 'limonada': 'Limonada Mediana', 'limonada mediana': 'Limonada Mediana', 'jugo': 'Jugo Mediano', 'jugo mediano': 'Jugo Mediano', 'magchicha mediana': 'Magchicha Mediana', 'magchicha familiar': 'Magchicha Familiar', 'chicha': 'Magchicha Mediana', 'cola': 'Gaseo Personal', 'mini hornado': 'Mini Hornado', 'mini menudo': 'Mini Menudo de la Magdalena'}
CATEGORY_MAP = {'Menudo de la Magdalena': 'sopa_especial', 'Mote de la Magdalena': 'plato_especial', 'Hornado': 'plato_tradicional', 'Hornado Completo': 'plato_especial', 'Seco de Chivo': 'plato_tradicional', 'Choclo Mote con Fritada': 'plato_especial', 'Churrasco de Res': 'plato_especial', 'Churrasco de Cerdo': 'plato_especial', 'Tortillas con Caucara': 'plato_tradicional', 'Tortillas con Fritada': 'plato_especial', 'Tortillas con Chorizo': 'plato_tradicional', 'Caldo de Gallina': 'sopa_especial', 'Caldo de 31': 'sopa_especial', 'Caldo de Pata': 'sopa_especial', 'Papa con Librillo': 'sopa_especial', 'Papas con Cuero': 'sopa_especial', 'Mixto': 'sopa_especial', 'Ambateñito': 'plato_tradicional', 'Guatita': 'plato_tradicional', 'Apanado de Res': 'plato_especial', 'Apanado de Cerdo': 'plato_especial', 'Fritada Completa': 'plato_especial', 'Fritada Tradicional': 'plato_especial', 'Magdalenazo': 'plato_especial', 'Combo Ideal': 'promocion', 'Combo Compartir': 'promocion', 'Combo Dupla Personal': 'promocion', 'Combo Tradición 1': 'promocion', 'Combo Tradición 2': 'promocion', 'Agua Personal': 'bebida', 'Gaseo Personal': 'bebida', 'Fuze Tea': 'bebida', 'Limonada Mediana': 'bebida', 'Jugo Mediano': 'bebida', 'Magchicha Mediana': 'bebida', 'Magchicha Familiar': 'bebida', 'Mini Hornado': 'mini', 'Mini Menudo de la Magdalena': 'mini'}
EXTRA_NORMALIZATION = {'aji': 'Ají', 'ají': 'Ají', 'aji de mani': 'Ají de Maní', 'ají de maní': 'Ají de Maní', 'agrio': 'Agrio', 'mapaguira': 'Mapaguira', 'chorizo': 'Chorizo', 'maduros fritos': 'Maduros Fritos', 'crujiente': 'Crujiente', 'aguacate': '½ Aguacate', '1/2 aguacate': '½ Aguacate', 'morcilla': 'Porción de Morcilla', 'arroz': 'Porción de Arroz', 'mote': 'Porción de Mote', 'choclo mote': 'Porción de Choclo Mote', 'tortillas': 'Porción de Tortillas'}
PRESA_WORDS = ['pechuga', 'muslo', 'presa', 'ala']

SALUDOS = ["hola", "buenas", "buenos días", "buen dia", "buen día", "buenas tardes", "buenas noches"]
MENU_HINTS = ["menu", "menú", "qué tienen", "que tienen", "qué venden", "que venden", "opciones", "carta"]
PAYMENT_HINTS = ["tarjeta", "efectivo", "transferencia"]
TRACKING_HINTS = ["ya llega", "estado del pedido", "ya sale", "demora", "cuánto tiempo", "cuanto tiempo"]
LOCATION_HINTS = ["ubicación", "ubicacion", "dirección", "direccion", "sector", "sur", "norte"]

def normalizar(texto: str) -> str:
    texto = texto.strip().lower()
    texto = re.sub(r"\s+", " ", texto)
    return texto

def detectar_saludo(texto: str) -> bool:
    return any(s in texto for s in SALUDOS)

def extraer_cantidades(texto: str, total_items: int) -> List[int]:
    nums = [int(n) for n in re.findall(r"\d+", texto)]
    if len(nums) >= total_items and total_items > 0:
        return nums[:total_items]
    return [1] * total_items

def extraer_presa(texto: str) -> Optional[str]:
    t = normalizar(texto)
    for palabra in PRESA_WORDS:
        if palabra in t:
            return palabra
    return None

def detectar_productos(texto: str) -> List[str]:
    t = normalizar(texto)
    encontrados = []
    for alias in sorted(ALIAS_MAP.keys(), key=len, reverse=True):
        if alias in t:
            oficial = ALIAS_MAP[alias]
            if oficial not in encontrados:
                encontrados.append(oficial)
    if "caldo" in t and not any(x in encontrados for x in ["Caldo de Gallina", "Caldo de 31", "Caldo de Pata"]):
        encontrados.append("Caldo de Gallina")
    return encontrados

def detectar_extras(texto: str) -> Dict[str, List[str]]:
    t = normalizar(texto)
    extras, sin_items, con_items = [], [], []
    for raw in EXTRA_NORMALIZATION.keys():
        if raw in t:
            norm = EXTRA_NORMALIZATION[raw]
            if f"sin {raw}" in t:
                sin_items.append(norm)
            else:
                extras.append(norm)
    presa = extraer_presa(t)
    if presa:
        con_items.append(presa.title())
    return {"extras": sorted(list(dict.fromkeys(extras))), "sin": sorted(list(dict.fromkeys(sin_items))), "con": sorted(list(dict.fromkeys(con_items)))}

def construir_productos_detalle(texto: str, productos: List[str], cantidades: List[int], extras_info: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    detalles = []
    for i, producto_oficial in enumerate(productos):
        cantidad = cantidades[i] if i < len(cantidades) else 1
        categoria = CATEGORY_MAP.get(producto_oficial, "producto")
        detalles.append({
            "texto_cliente": texto,
            "producto_oficial": producto_oficial,
            "categoria": categoria,
            "cantidad": cantidad,
            "modificadores": {
                "sin": extras_info["sin"],
                "con": extras_info["con"],
                "extras": extras_info["extras"],
                "tamano": "mini" if "mini" in normalizar(texto) and categoria != "bebida" else None,
                "presa": extraer_presa(texto) if producto_oficial == "Caldo de Gallina" else None,
            },
        })
    return detalles

def clasificar_intencion(texto: str, productos: List[str]) -> str:
    t = normalizar(texto)
    if productos:
        return "pedido_directo"
    if any(x in t for x in MENU_HINTS):
        return "solicitud_menu"
    if any(x in t for x in PAYMENT_HINTS):
        return "consulta_pago"
    if any(x in t for x in TRACKING_HINTS):
        return "seguimiento_pedido"
    if any(x in t for x in LOCATION_HINTS):
        return "compartir_ubicacion"
    if detectar_saludo(t):
        return "saludo"
    return "solicitud_pedido"

def decidir_respuesta(intent: str, productos: List[str]) -> str:
    if intent == "pedido_directo" and productos:
        return "confirmar_pedido"
    if intent == "solicitud_menu":
        return "enviar_menu"
    if intent == "consulta_pago":
        return "informar_metodos_pago"
    if intent == "seguimiento_pedido":
        return "revisar_estado_pedido"
    if intent == "compartir_ubicacion":
        return "validar_cobertura"
    if intent == "saludo":
        return "saludo_con_opciones"
    return "guiar_pedido"

def parsear_mensaje(texto: str) -> Dict[str, Any]:
    t = normalizar(texto)
    saludo = detectar_saludo(t)
    productos = detectar_productos(t)
    extras_info = detectar_extras(t)
    cantidades = extraer_cantidades(t, len(productos))
    detalles = construir_productos_detalle(t, productos, cantidades, extras_info)
    intent = clasificar_intencion(t, productos)
    secundarias = ["saludo"] if saludo and intent != "saludo" else []
    bebidas = [d["producto_oficial"] for d in detalles if d["categoria"] == "bebida"]
    platos = [d["producto_oficial"] for d in detalles if d["categoria"] != "bebida"]
    return {
        "empresa": "Los Motes de la Magdalena",
        "canal": "whatsapp",
        "input": texto,
        "output": {
            "intencion_principal": intent,
            "intenciones_secundarias": secundarias,
            "saludo": saludo,
            "requiere_agente": intent == "seguimiento_pedido",
            "fase_conversacion": "pedido" if intent == "pedido_directo" else "inicio",
            "entidades": {
                "productos": platos,
                "cantidades": cantidades,
                "bebidas": bebidas,
                "extras": extras_info["extras"],
                "sin_ingredientes": extras_info["sin"],
                "con_ingredientes": extras_info["con"],
                "metodo_pago": "tarjeta" if "tarjeta" in t else "efectivo" if "efectivo" in t else "transferencia" if "transferencia" in t else None,
                "direccion": None,
                "ubicacion_compartida": "ubicación" in t or "ubicacion" in t,
                "sector": "sur" if "sur" in t else "norte" if "norte" in t else None,
                "precio_mencionado": None,
                "tiempo_entrega": "consulta" if "tiempo" in t else None,
                "menu_link_requerido": intent == "solicitud_menu",
                "menu_url": MENU_URL,
                "productos_detalle": detalles,
            },
            "respuesta_esperada": decidir_respuesta(intent, productos),
        },
    }

if __name__ == "__main__":
    ejemplos = [
        "Deme un menudo por favor",
        "Un hornado y un hornado completo",
        "Caldo de gallina con pechuga",
        "Hola me comparte el menú por favor",
        "Mote con agrio y mapaguira",
    ]
    for e in ejemplos:
        print(json.dumps(parsear_mensaje(e), ensure_ascii=False, indent=2))
