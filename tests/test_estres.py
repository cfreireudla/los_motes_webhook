# Pruebas de Estrés del Modelo
"""
Pruebas para evaluar el comportamiento del modelo ante casos extremos:
textos muy largos, muy cortos, caracteres especiales, límites del sistema.

Objetivo: Identificar comportamientos anómalos, errores del sistema,
tiempos de procesamiento excesivos o resultados sin sentido.
"""

import pytest
import time
from typing import List


class TestCasosExtremos:
    """Pruebas con valores en los límites del dominio."""
    
    def test_texto_vacio(self, classifier):
        """
        CP-ESTRES-001: El modelo debe manejar texto vacío sin crashear.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-001: Manejo de Texto Vacío")
        print("="*70)
        
        result = classifier.classify("")
        
        print(f"Entrada: '' (texto vacío)")
        print(f"Resultado: {result.intent} ({result.confidence:.1%})")
        print(f"Es fallback: {result.is_fallback}")
        
        # Debe retornar algo válido, preferiblemente fallback
        assert result is not None
        assert result.intent is not None
        assert isinstance(result.confidence, float)
    
    def test_solo_espacios(self, classifier):
        """
        CP-ESTRES-002: El modelo debe manejar texto con solo espacios.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-002: Manejo de Solo Espacios")
        print("="*70)
        
        entradas = ["   ", "  \t  ", "\n\n", "  \n  \t  "]
        
        for entrada in entradas:
            result = classifier.classify(entrada)
            
            print(f"Entrada: {repr(entrada)}")
            print(f"Resultado: {result.intent} ({result.confidence:.1%})")
            
            assert result is not None
    
    def test_texto_muy_largo(self, classifier):
        """
        CP-ESTRES-003: El modelo debe manejar textos extremadamente largos.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-003: Manejo de Textos Muy Largos")
        print("="*70)
        
        # Diferentes longitudes
        longitudes = [100, 500, 1000, 5000]
        base_texto = "hola quiero hacer un pedido "
        
        for longitud in longitudes:
            texto_largo = (base_texto * (longitud // len(base_texto)))[:longitud]
            
            inicio = time.time()
            result = classifier.classify(texto_largo)
            tiempo = time.time() - inicio
            
            print(f"\n📏 Longitud: {len(texto_largo)} caracteres")
            print(f"   Tiempo: {tiempo:.3f}s")
            print(f"   Resultado: {result.intent} ({result.confidence:.1%})")
            
            # No debe tardar más de 5 segundos
            assert tiempo < 5.0, f"Tiempo excesivo: {tiempo:.2f}s"
            assert result is not None
    
    def test_un_solo_caracter(self, classifier):
        """
        CP-ESTRES-004: El modelo debe manejar un solo carácter.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-004: Manejo de Un Solo Carácter")
        print("="*70)
        
        caracteres = ['a', 'h', '1', '?', '!', '😀', '.']
        
        for char in caracteres:
            result = classifier.classify(char)
            
            print(f"'{char}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None


class TestCaracteresEspeciales:
    """Pruebas con caracteres especiales y símbolos."""
    
    def test_solo_numeros(self, classifier):
        """
        CP-ESTRES-005: El modelo debe manejar entradas solo numéricas.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-005: Manejo de Solo Números")
        print("="*70)
        
        entradas_numericas = [
            "123",
            "3166123456",  # Parece teléfono
            "25000",  # Parece precio
            "12:30",  # Parece hora
            "15/03/2024",  # Parece fecha
        ]
        
        for entrada in entradas_numericas:
            result = classifier.classify(entrada)
            
            print(f"'{entrada}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None
    
    def test_solo_simbolos(self, classifier):
        """
        CP-ESTRES-006: El modelo debe manejar solo símbolos.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-006: Manejo de Solo Símbolos")
        print("="*70)
        
        simbolos = [
            "!@#$%",
            "***",
            "---",
            "...",
            "???",
            "<<<>>>",
            "++--",
        ]
        
        for entrada in simbolos:
            result = classifier.classify(entrada)
            
            print(f"'{entrada}' -> {result.intent} ({result.confidence:.1%})")
            
            # Debería ser fallback en la mayoría de casos
            assert result is not None
    
    def test_emojis(self, classifier):
        """
        CP-ESTRES-007: El modelo debe manejar emojis.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-007: Manejo de Emojis")
        print("="*70)
        
        casos_emoji = [
            ("😀", "solo emoji"),
            ("👋 hola", "emoji + saludo"),
            ("quiero 🍔 pizza", "texto + emoji"),
            ("💰 cuánto cuesta", "emoji + pregunta precio"),
            ("📍 dónde", "emoji + ubicación"),
        ]
        
        for entrada, descripcion in casos_emoji:
            result = classifier.classify(entrada)
            
            print(f"{descripcion}: '{entrada}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None
    
    def test_caracteres_unicode_especiales(self, classifier):
        """
        CP-ESTRES-008: El modelo debe manejar caracteres Unicode especiales.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-008: Manejo de Unicode Especial")
        print("="*70)
        
        unicode_especial = [
            "ñoño",  # ñ
            "hëllo",  # diéresis
            "café",  # acento
            "日本語",  # japonés
            "مرحبا",  # árabe
            "привет",  # ruso
        ]
        
        for entrada in unicode_especial:
            result = classifier.classify(entrada)
            
            print(f"'{entrada}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None


class TestFormatosEspeciales:
    """Pruebas con formatos especiales de entrada."""
    
    def test_saltos_de_linea(self, classifier, textos_multilinea):
        """
        CP-ESTRES-009: El modelo debe manejar saltos de línea.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-009: Manejo de Saltos de Línea")
        print("="*70)
        
        for texto in textos_multilinea:
            result = classifier.classify(texto)
            
            texto_display = texto.replace('\n', '\\n')
            print(f"'{texto_display}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None
    
    def test_tabulaciones(self, classifier):
        """
        CP-ESTRES-010: El modelo debe manejar tabulaciones.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-010: Manejo de Tabulaciones")
        print("="*70)
        
        casos_tab = [
            "hola\tbuenas",
            "\tquiero\tpedir",
            "menú\t\t\tprecio",
        ]
        
        for texto in casos_tab:
            result = classifier.classify(texto)
            
            texto_display = texto.replace('\t', '\\t')
            print(f"'{texto_display}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None


class TestTiempoRespuesta:
    """Pruebas de rendimiento y tiempo de respuesta."""
    
    def test_tiempo_respuesta_promedio(self, classifier, textos_originales):
        """
        CP-ESTRES-011: El tiempo de respuesta debe ser aceptable.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-011: Tiempo de Respuesta Promedio")
        print("="*70)
        
        tiempos = []
        
        for texto, _ in textos_originales:
            inicio = time.time()
            result = classifier.classify(texto)
            tiempo = time.time() - inicio
            tiempos.append(tiempo)
        
        promedio = sum(tiempos) / len(tiempos)
        maximo = max(tiempos)
        minimo = min(tiempos)
        
        print(f"📊 Estadísticas de tiempo:")
        print(f"   Promedio: {promedio*1000:.2f}ms")
        print(f"   Mínimo: {minimo*1000:.2f}ms")
        print(f"   Máximo: {maximo*1000:.2f}ms")
        
        # El promedio debe ser menor a 100ms para buena UX
        assert promedio < 0.5, f"Tiempo promedio demasiado alto: {promedio:.3f}s"
    
    def test_clasificaciones_consecutivas(self, classifier, textos_originales):
        """
        CP-ESTRES-012: El modelo debe soportar clasificaciones consecutivas.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-012: Clasificaciones Consecutivas")
        print("="*70)
        
        num_iteraciones = 50
        textos = [t for t, _ in textos_originales]
        
        inicio_total = time.time()
        
        for i in range(num_iteraciones):
            texto = textos[i % len(textos)]
            result = classifier.classify(texto)
            assert result is not None
        
        tiempo_total = time.time() - inicio_total
        tiempo_por_iter = tiempo_total / num_iteraciones
        
        print(f"📊 {num_iteraciones} clasificaciones:")
        print(f"   Tiempo total: {tiempo_total:.2f}s")
        print(f"   Tiempo por clasificación: {tiempo_por_iter*1000:.2f}ms")
        
        # No debe degradarse significativamente
        assert tiempo_total < 15.0, f"Degradación de rendimiento: {tiempo_total:.2f}s"


class TestComportamientosAnomalos:
    """Pruebas para detectar comportamientos anómalos del modelo."""
    
    def test_consistencia_misma_entrada(self, classifier):
        """
        CP-ESTRES-013: El modelo debe ser determinístico (misma entrada = misma salida).
        """
        print("\n" + "="*70)
        print("CP-ESTRES-013: Consistencia Determinística")
        print("="*70)
        
        textos_prueba = [
            "hola buenos días",
            "quiero hacer un pedido",
            "cuánto cuesta",
        ]
        
        for texto in textos_prueba:
            resultados = []
            
            for _ in range(5):
                result = classifier.classify(texto)
                resultados.append((result.intent, result.confidence))
            
            # Todas las predicciones deben ser iguales
            intents = [r[0] for r in resultados]
            confianzas = [r[1] for r in resultados]
            
            assert len(set(intents)) == 1, f"Inconsistencia en: '{texto}'"
            assert len(set(confianzas)) == 1, f"Confianza variante en: '{texto}'"
            
            print(f"✅ '{texto}' -> {intents[0]} (consistente)")
    
    def test_no_excepcion_entrada_extrema(self, classifier, textos_extremos):
        """
        CP-ESTRES-014: El modelo no debe lanzar excepciones con entradas extremas.
        """
        print("\n" + "="*70)
        print("CP-ESTRES-014: Estabilidad ante Entradas Extremas")
        print("="*70)
        
        for texto, _ in textos_extremos:
            try:
                result = classifier.classify(texto)
                estado = "✅"
            except Exception as e:
                estado = "❌"
                print(f"❌ Excepción con '{texto[:30]}...': {e}")
                pytest.fail(f"Excepción no manejada: {e}")
            
            texto_display = texto[:40] + "..." if len(texto) > 40 else texto
            print(f"{estado} '{texto_display}' -> {result.intent}")
