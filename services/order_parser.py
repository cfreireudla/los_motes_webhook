# Parser de pedidos para Los Motes de la Magdalena
"""
Extrae productos, cantidades, extras y modificadores de mensajes de texto libre.
Basado en motes_chatbot_parser_v3.py
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

MENU_URL = 'https://www.losmotesdelamagdalena.com/menu/'

# Mapeo de aliases - EXACTO del parser original
ALIAS_MAP = {
    'menudo': 'Menudo de la Magdalena', 
    'menudo de la magdalena': 'Menudo de la Magdalena', 
    'mote': 'Mote de la Magdalena', 
    'mote de la magdalena': 'Mote de la Magdalena', 
    'hornado': 'Hornado', 
    'hornado completo': 'Hornado Completo', 
    'seco de chivo': 'Seco de Chivo', 
    'choclo mote con fritada': 'Choclo Mote con Fritada', 
    'churrasco con carne de res': 'Churrasco de Res', 
    'churrasco de res': 'Churrasco de Res', 
    'churrasco de cerdo': 'Churrasco de Cerdo', 
    'tortilla con caucara': 'Tortillas con Caucara', 
    'tortillas con caucara': 'Tortillas con Caucara', 
    'tortillas con fritada': 'Tortillas con Fritada', 
    'tortillas con chorizo': 'Tortillas con Chorizo', 
    'caldo de gallina': 'Caldo de Gallina', 
    'caldo de 31': 'Caldo de 31', 
    'caldo de pata': 'Caldo de Pata', 
    'papa con librillo': 'Papa con Librillo', 
    'papas con cuero': 'Papas con Cuero', 
    'mixto': 'Mixto', 
    'ambateñito': 'Ambateñito', 
    'guatita': 'Guatita', 
    'apanado de res': 'Apanado de Res', 
    'apanado de cerdo': 'Apanado de Cerdo', 
    'fritada completa': 'Fritada Completa', 
    'fritada tradicional': 'Fritada Tradicional', 
    'magdalenazo': 'Magdalenazo', 
    'combo ideal': 'Combo Ideal', 
    'combo compartir': 'Combo Compartir', 
    'combo dupla personal': 'Combo Dupla Personal', 
    'combo tradición 1': 'Combo Tradición 1', 
    'combo tradicion 1': 'Combo Tradición 1', 
    'combo tradición 2': 'Combo Tradición 2', 
    'combo tradicion 2': 'Combo Tradición 2', 
    'agua personal': 'Agua Personal', 
    'gaseo personal': 'Gaseo Personal', 
    'gaseosa personal': 'Gaseo Personal', 
    'fuze tea': 'Fuze Tea', 
    'limonada': 'Limonada Mediana', 
    'limonada mediana': 'Limonada Mediana', 
    'jugo': 'Jugo Mediano', 
    'jugo mediano': 'Jugo Mediano', 
    'magchicha mediana': 'Magchicha Mediana', 
    'magchicha familiar': 'Magchicha Familiar', 
    'chicha': 'Magchicha Mediana', 
    'cola': 'Gaseo Personal', 
    'mini hornado': 'Mini Hornado', 
    'mini menudo': 'Mini Menudo de la Magdalena'
}

# Categorías - EXACTO del parser original
CATEGORY_MAP = {
    'Menudo de la Magdalena': 'sopa_especial', 
    'Mote de la Magdalena': 'plato_especial', 
    'Hornado': 'plato_tradicional', 
    'Hornado Completo': 'plato_especial', 
    'Seco de Chivo': 'plato_tradicional', 
    'Choclo Mote con Fritada': 'plato_especial', 
    'Churrasco de Res': 'plato_especial', 
    'Churrasco de Cerdo': 'plato_especial', 
    'Tortillas con Caucara': 'plato_tradicional', 
    'Tortillas con Fritada': 'plato_especial', 
    'Tortillas con Chorizo': 'plato_tradicional', 
    'Caldo de Gallina': 'sopa_especial', 
    'Caldo de 31': 'sopa_especial', 
    'Caldo de Pata': 'sopa_especial', 
    'Papa con Librillo': 'sopa_especial', 
    'Papas con Cuero': 'sopa_especial', 
    'Mixto': 'sopa_especial', 
    'Ambateñito': 'plato_tradicional', 
    'Guatita': 'plato_tradicional', 
    'Apanado de Res': 'plato_especial', 
    'Apanado de Cerdo': 'plato_especial', 
    'Fritada Completa': 'plato_especial', 
    'Fritada Tradicional': 'plato_especial', 
    'Magdalenazo': 'plato_especial', 
    'Combo Ideal': 'promocion', 
    'Combo Compartir': 'promocion', 
    'Combo Dupla Personal': 'promocion', 
    'Combo Tradición 1': 'promocion', 
    'Combo Tradición 2': 'promocion', 
    'Agua Personal': 'bebida', 
    'Gaseo Personal': 'bebida', 
    'Fuze Tea': 'bebida', 
    'Limonada Mediana': 'bebida', 
    'Jugo Mediano': 'bebida', 
    'Magchicha Mediana': 'bebida', 
    'Magchicha Familiar': 'bebida', 
    'Mini Hornado': 'mini', 
    'Mini Menudo de la Magdalena': 'mini'
}

# Extras - EXACTO del parser original
EXTRA_NORMALIZATION = {
    'aji': 'Ají', 
    'ají': 'Ají', 
    'aji de mani': 'Ají de Maní', 
    'ají de maní': 'Ají de Maní', 
    'agrio': 'Agrio', 
    'mapaguira': 'Mapaguira', 
    'chorizo': 'Chorizo', 
    'maduros fritos': 'Maduros Fritos', 
    'crujiente': 'Crujiente', 
    'aguacate': '½ Aguacate', 
    '1/2 aguacate': '½ Aguacate', 
    'morcilla': 'Porción de Morcilla', 
    'arroz': 'Porción de Arroz', 
    'mote': 'Porción de Mote', 
    'choclo mote': 'Porción de Choclo Mote', 
    'tortillas': 'Porción de Tortillas',
    'encurtido': 'Encurtido'
}

PRESA_WORDS = ['pechuga', 'muslo', 'presa', 'ala']

# Hints del parser original
SALUDOS = ["hola", "buenas", "buenos días", "buen dia", "buen día", "buenas tardes", "buenas noches"]
MENU_HINTS = ["menu", "menú", "qué tienen", "que tienen", "qué venden", "que venden", "opciones", "carta"]
PAYMENT_HINTS = ["tarjeta", "efectivo", "transferencia"]
TRACKING_HINTS = ["ya llega", "estado del pedido", "ya sale", "demora", "cuánto tiempo", "cuanto tiempo"]
LOCATION_HINTS = ["ubicación", "ubicacion", "dirección", "direccion", "sector", "sur", "norte"]


# ========== FUNCIONES DEL PARSER ORIGINAL ==========

def normalizar(texto: str) -> str:
    """Normaliza el texto para comparaciones."""
    texto = texto.strip().lower()
    texto = re.sub(r"\s+", " ", texto)
    return texto


def detectar_saludo(texto: str) -> bool:
    """Detecta si el mensaje contiene un saludo."""
    return any(s in texto for s in SALUDOS)


# Mapeo de palabras a números
PALABRA_A_NUMERO = {
    'un': 1, 'una': 1, 'uno': 1,
    'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5,
    'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9, 'diez': 10
}


def extraer_cantidades(texto: str, total_items: int) -> List[int]:
    """Extrae cantidades numéricas del texto (función legacy)."""
    nums = [int(n) for n in re.findall(r"\d+", texto)]
    if len(nums) >= total_items and total_items > 0:
        return nums[:total_items]
    return [1] * total_items


def extraer_cantidad_para_producto(texto: str, alias: str) -> int:
    """
    Extrae la cantidad específica para un producto buscando el patrón
    'CANTIDAD + PRODUCTO' justo antes del alias.
    
    Ejemplos:
    - '2 fuze tea' → 2
    - 'un hornado' → 1
    - 'dame hornado' → 1 (default)
    """
    t = normalizar(texto)
    
    # Patrón: número + espacio(s) + alias
    pattern_num = rf'(\d+)\s+{re.escape(alias)}'
    match = re.search(pattern_num, t)
    if match:
        return int(match.group(1))
    
    # Patrón: palabra numérica + espacio(s) + alias
    for palabra, numero in PALABRA_A_NUMERO.items():
        pattern_palabra = rf'\b{palabra}\s+{re.escape(alias)}'
        if re.search(pattern_palabra, t):
            return numero
    
    # Default: 1
    return 1


def extraer_presa(texto: str) -> Optional[str]:
    """Extrae tipo de presa para Caldo de Gallina."""
    t = normalizar(texto)
    for palabra in PRESA_WORDS:
        if palabra in t:
            return palabra
    return None


def detectar_productos(texto: str) -> List[str]:
    """Detecta productos mencionados en el texto."""
    t = normalizar(texto)
    encontrados = []
    for alias in sorted(ALIAS_MAP.keys(), key=len, reverse=True):
        if alias in t:
            oficial = ALIAS_MAP[alias]
            if oficial not in encontrados:
                encontrados.append(oficial)
    # Caso especial: "caldo" sin especificar
    if "caldo" in t and not any(x in encontrados for x in ["Caldo de Gallina", "Caldo de 31", "Caldo de Pata"]):
        encontrados.append("Caldo de Gallina")
    return encontrados


def detectar_productos_con_cantidades(texto: str) -> List[Dict[str, Any]]:
    """
    Detecta productos Y sus cantidades asociadas.
    Retorna lista de {'producto': str, 'cantidad': int, 'alias_usado': str}
    """
    t = normalizar(texto)
    encontrados = []
    productos_ya_agregados = set()
    
    # Ordenar aliases por longitud (mayor primero) para evitar matches parciales
    for alias in sorted(ALIAS_MAP.keys(), key=len, reverse=True):
        if alias in t:
            oficial = ALIAS_MAP[alias]
            if oficial not in productos_ya_agregados:
                cantidad = extraer_cantidad_para_producto(texto, alias)
                encontrados.append({
                    'producto': oficial,
                    'cantidad': cantidad,
                    'alias_usado': alias
                })
                productos_ya_agregados.add(oficial)
    
    # Caso especial: "caldo" sin especificar
    if "caldo" in t and "Caldo de Gallina" not in productos_ya_agregados \
       and "Caldo de 31" not in productos_ya_agregados \
       and "Caldo de Pata" not in productos_ya_agregados:
        cantidad = extraer_cantidad_para_producto(texto, "caldo")
        encontrados.append({
            'producto': "Caldo de Gallina",
            'cantidad': cantidad,
            'alias_usado': "caldo"
        })
    
    return encontrados


def detectar_extras(texto: str) -> Dict[str, List[str]]:
    """Detecta extras, ingredientes sin y con."""
    t = normalizar(texto)
    extras, sin_items, con_items = [], [], []
    for raw in EXTRA_NORMALIZATION.keys():
        if raw in t:
            norm = EXTRA_NORMALIZATION[raw]
            if f"sin {raw}" in t or f"no {raw}" in t:
                sin_items.append(norm)
            else:
                extras.append(norm)
    presa = extraer_presa(t)
    if presa:
        con_items.append(presa.title())
    return {
        "extras": sorted(list(dict.fromkeys(extras))), 
        "sin": sorted(list(dict.fromkeys(sin_items))), 
        "con": sorted(list(dict.fromkeys(con_items)))
    }


def construir_productos_detalle(texto: str, productos: List[str], cantidades: List[int], extras_info: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """Construye el detalle de cada producto (función legacy)."""
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


def construir_productos_detalle_v2(texto: str, productos_con_cantidad: List[Dict[str, Any]], extras_info: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Construye el detalle de cada producto usando la nueva estructura con cantidades.
    """
    detalles = []
    for item in productos_con_cantidad:
        producto_oficial = item['producto']
        cantidad = item['cantidad']
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
    """Clasifica la intención basada en el texto y productos detectados."""
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
    """Decide qué tipo de respuesta dar."""
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
    """
    Función principal del parser - MEJORADA para extraer cantidades correctamente.
    Parsea un mensaje completo y retorna toda la información estructurada.
    """
    t = normalizar(texto)
    saludo = detectar_saludo(t)
    
    # Usar la nueva función que extrae productos CON cantidades
    productos_con_cantidad = detectar_productos_con_cantidades(texto)
    productos = [p['producto'] for p in productos_con_cantidad]
    cantidades = [p['cantidad'] for p in productos_con_cantidad]
    
    extras_info = detectar_extras(t)
    detalles = construir_productos_detalle_v2(t, productos_con_cantidad, extras_info)
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


# ========== FUNCIONES ADAPTADAS PARA EL SERVICIO ==========

@dataclass
class ParseResult:
    """Resultado del parsing simplificado para uso en ai_service."""
    productos: List[Dict[str, Any]]
    extras: List[str]
    sin_ingredientes: List[str]
    con_ingredientes: List[str]
    tiene_productos: bool
    mensaje_original: str
    cantidades: List[int]
    bebidas: List[str]
    platos: List[str]
    intencion: str
    full_output: Dict[str, Any]
    
    def to_confirmation_text(self) -> str:
        """Genera texto de confirmación del pedido."""
        if not self.productos:
            return ""
        
        lines = ["📝 *Tu pedido:*\n"]
        
        for p in self.productos:
            line = f"• {p['cantidad']}x {p['producto_oficial']}"
            
            # Agregar presa si es Caldo de Gallina
            if p.get('modificadores', {}).get('presa'):
                line += f" (con {p['modificadores']['presa']})"
            
            lines.append(line)
        
        # Agregar extras
        if self.extras:
            lines.append(f"\n➕ Extras: {', '.join(self.extras)}")
        
        # Agregar "sin" ingredientes
        if self.sin_ingredientes:
            lines.append(f"🚫 Sin: {', '.join(self.sin_ingredientes)}")
        
        return "\n".join(lines)


def parsear_pedido(texto: str) -> ParseResult:
    """
    Wrapper que usa parsear_mensaje y retorna ParseResult.
    """
    resultado = parsear_mensaje(texto)
    entidades = resultado["output"]["entidades"]
    
    return ParseResult(
        productos=entidades["productos_detalle"],
        extras=entidades["extras"],
        sin_ingredientes=entidades["sin_ingredientes"],
        con_ingredientes=entidades["con_ingredientes"],
        tiene_productos=len(entidades["productos_detalle"]) > 0,
        mensaje_original=texto,
        cantidades=entidades["cantidades"],
        bebidas=entidades["bebidas"],
        platos=entidades["productos"],
        intencion=resultado["output"]["intencion_principal"],
        full_output=resultado
    )


# Alias para compatibilidad
parse = parsear_pedido
