"""
Script para transformar los_motes_dataset_aliases_v3.jsonl al formato de intents.jsonl
y mapear las intenciones al esquema existente.
"""
import json
from pathlib import Path

# Mapeo de intenciones del dataset v3 a intents.jsonl
INTENT_MAPPING = {
    # Mapeos directos y equivalentes
    "saludo": "saludo",
    "consulta_pago": "metodos_pago",
    "pedido_directo": "realizar_pedido",
    "solicitud_menu": "consultar_menu",
    "solicitud_pedido": "realizar_pedido",  # Quiere hacer pedido sin especificar productos
    "seleccion_bebida": "realizar_pedido",  # Es un pedido de bebida
    "extra_pedido": "modificar_pedido",  # Agregar extras al pedido
    "consulta_envio": "delivery",  # Consulta costo de envío
    "consulta_tiempo_entrega": "delivery",  # Tiempo de entrega
    "compartir_ubicacion": "delivery",  # Comparte ubicación para envío
    "solicitar_sector": "delivery",  # Pregunta por cobertura
    "recomendacion": "consultar_menu",  # Pide sugerencia del menú
    "cambio_efectivo": "metodos_pago",  # Relacionado con pago en efectivo
    
    # Nuevas intenciones que necesitan crearse
    "correccion_direccion": "correccion_direccion",  # NUEVO
    "seguimiento_pedido": "seguimiento_pedido",  # NUEVO
    "datos_factura": "datos_factura",  # NUEVO
}

def transform_dataset():
    """Transforma el dataset v3 al formato compatible con spaCy."""
    
    base_path = Path(__file__).parent.parent
    input_file = base_path / "los_motes_dataset_aliases_v3.jsonl"
    output_file = base_path / "data" / "los_motes_v3_transformed.jsonl"
    
    transformed_data = []
    intent_counts = {}
    unmapped_intents = set()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                record = json.loads(line)
                
                # Extraer texto
                text = record.get("text", "")
                if not text:
                    print(f"Línea {line_num}: Sin texto, saltando.")
                    continue
                
                # Extraer intención principal del output
                output = record.get("output", {})
                original_intent = output.get("intencion_principal", "")
                
                if not original_intent:
                    print(f"Línea {line_num}: Sin intención, saltando.")
                    continue
                
                # Mapear intención
                if original_intent in INTENT_MAPPING:
                    mapped_intent = INTENT_MAPPING[original_intent]
                else:
                    unmapped_intents.add(original_intent)
                    mapped_intent = original_intent  # Mantener original si no está mapeada
                
                # Crear registro transformado
                transformed_record = {
                    "text": text,
                    "label": mapped_intent
                }
                
                transformed_data.append(transformed_record)
                
                # Contar intenciones
                intent_counts[mapped_intent] = intent_counts.get(mapped_intent, 0) + 1
                
            except json.JSONDecodeError as e:
                print(f"Línea {line_num}: Error JSON - {e}")
                continue
    
    # Eliminar duplicados
    seen = set()
    unique_data = []
    duplicates = 0
    
    for record in transformed_data:
        key = (record["text"], record["label"])
        if key not in seen:
            seen.add(key)
            unique_data.append(record)
        else:
            duplicates += 1
    
    # Guardar archivo transformado
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in unique_data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    # Mostrar estadísticas
    print("\n" + "="*60)
    print("TRANSFORMACIÓN COMPLETADA")
    print("="*60)
    print(f"\nArchivo generado: {output_file}")
    print(f"Total registros originales: {len(transformed_data)}")
    print(f"Duplicados eliminados: {duplicates}")
    print(f"Total registros únicos: {len(unique_data)}")
    
    print("\n" + "-"*40)
    print("DISTRIBUCIÓN POR INTENCIÓN:")
    print("-"*40)
    for intent, count in sorted(intent_counts.items(), key=lambda x: -x[1]):
        print(f"  {intent}: {count}")
    
    if unmapped_intents:
        print("\n" + "-"*40)
        print("INTENCIONES SIN MAPEO (se mantuvieron igual):")
        print("-"*40)
        for intent in unmapped_intents:
            print(f"  - {intent}")
    
    # Identificar nuevas intenciones
    new_intents = {"correccion_direccion", "seguimiento_pedido", "datos_factura"}
    found_new = new_intents.intersection(set(intent_counts.keys()))
    
    if found_new:
        print("\n" + "-"*40)
        print("NUEVAS INTENCIONES DETECTADAS (agregar a responses.json):")
        print("-"*40)
        for intent in found_new:
            print(f"  - {intent}: {intent_counts.get(intent, 0)} ejemplos")
    
    return unique_data, intent_counts

if __name__ == "__main__":
    transform_dataset()
