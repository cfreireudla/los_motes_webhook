# Pruebas Adversariales Ligeras
"""
Pruebas para evaluar la estabilidad del modelo ante entradas desafiantes
pero realistas: prompts ambiguos, inputs contradictorios, mezcla de idiomas.

Objetivo: Evaluar la estabilidad del modelo ante confusión, no hackear el sistema.
"""

import pytest
from typing import List


class TestPromptsAmbiguos:
    """Pruebas con entradas ambiguas o sin contexto."""
    
    def test_textos_muy_ambiguos(self, classifier, textos_ambiguos):
        """
        CP-ADV-001: El modelo debe manejar textos ambiguos de manera segura.
        """
        print("\n" + "="*70)
        print("CP-ADV-001: Manejo de Textos Ambiguos")
        print("="*70)
        
        fallbacks = 0
        
        for texto in textos_ambiguos:
            result = classifier.classify(texto)
            
            if result.is_fallback or result.confidence < 0.5:
                fallbacks += 1
                estado = "⚠️ Fallback"
            else:
                estado = f"➡️ {result.intent}"
            
            print(f"'{texto}' -> {estado} ({result.confidence:.1%})")
        
        # Es aceptable que la mayoría sean fallback por ambigüedad
        print(f"\n📊 Fallbacks por ambigüedad: {fallbacks}/{len(textos_ambiguos)}")
    
    def test_preguntas_sin_contexto(self, classifier):
        """
        CP-ADV-002: El modelo debe manejar preguntas genéricas sin contexto.
        """
        print("\n" + "="*70)
        print("CP-ADV-002: Preguntas Sin Contexto")
        print("="*70)
        
        preguntas_vagas = [
            "cuánto es",
            "dónde queda",
            "a qué hora",
            "cómo se hace",
            "por qué",
            "para qué",
        ]
        
        for pregunta in preguntas_vagas:
            result = classifier.classify(pregunta)
            
            # Intentará clasificar según palabras clave
            print(f"'{pregunta}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None
    
    def test_respuestas_sin_pregunta(self, classifier):
        """
        CP-ADV-003: El modelo debe manejar respuestas sin pregunta previa.
        """
        print("\n" + "="*70)
        print("CP-ADV-003: Respuestas Sin Pregunta Previa")
        print("="*70)
        
        respuestas = [
            "sí",
            "no",
            "tal vez",
            "no sé",
            "puede ser",
            "ok",
            "dale",
            "listo",
        ]
        
        for resp in respuestas:
            result = classifier.classify(resp)
            
            print(f"'{resp}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None


class TestInputsContradictorios:
    """Pruebas con entradas que contienen elementos contradictorios."""
    
    def test_solicitudes_contradictorias(self, classifier, textos_contradictorios):
        """
        CP-ADV-004: El modelo debe manejar solicitudes contradictorias.
        """
        print("\n" + "="*70)
        print("CP-ADV-004: Solicitudes Contradictorias")
        print("="*70)
        
        for texto in textos_contradictorios:
            result = classifier.classify(texto)
            
            print(f"'{texto[:50]}...'")
            print(f"   -> {result.intent} ({result.confidence:.1%})")
            print(f"   Fallback: {result.is_fallback}")
            
            assert result is not None
    
    def test_cambio_intencion_mismo_mensaje(self, classifier):
        """
        CP-ADV-005: El modelo debe manejar cambios de intención en un mensaje.
        """
        print("\n" + "="*70)
        print("CP-ADV-005: Cambios de Intención en Mismo Mensaje")
        print("="*70)
        
        cambios = [
            "hola quiero pedir pero antes dime el horario",
            "cuánto cuesta y también dónde están",
            "gracias pero tengo una queja",
            "voy a pedir pero primero el menú",
        ]
        
        for texto in cambios:
            result = classifier.classify(texto)
            
            print(f"'{texto}'")
            print(f"   -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None


class TestMezclaIdiomas:
    """Pruebas con textos que mezclan idiomas."""
    
    def test_spanglish(self, classifier, textos_multiidioma):
        """
        CP-ADV-006: El modelo debe intentar clasificar spanglish.
        """
        print("\n" + "="*70)
        print("CP-ADV-006: Manejo de Spanglish/Mezcla de Idiomas")
        print("="*70)
        
        for texto in textos_multiidioma:
            result = classifier.classify(texto)
            
            print(f"'{texto}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None
    
    def test_idiomas_no_entrenados(self, classifier):
        """
        CP-ADV-007: El modelo debe manejar idiomas no entrenados sin crashear.
        """
        print("\n" + "="*70)
        print("CP-ADV-007: Idiomas No Entrenados")
        print("="*70)
        
        otros_idiomas = [
            ("hello how are you", "inglés"),
            ("bonjour comment allez vous", "francés"),
            ("guten tag", "alemán"),
            ("こんにちは", "japonés"),
            ("مرحبا", "árabe"),
        ]
        
        for texto, idioma in otros_idiomas:
            result = classifier.classify(texto)
            
            print(f"[{idioma}] '{texto}' -> {result.intent} ({result.confidence:.1%})")
            
            # Esperamos fallback o baja confianza
            assert result is not None


class TestIntentosConfusion:
    """Pruebas con intentos de confundir al modelo."""
    
    def test_inyeccion_prompt(self, classifier, textos_inyeccion):
        """
        CP-ADV-008: El modelo debe ignorar intentos de inyección de prompt.
        """
        print("\n" + "="*70)
        print("CP-ADV-008: Resistencia a Inyección de Prompt")
        print("="*70)
        
        for texto in textos_inyeccion:
            result = classifier.classify(texto)
            
            # El clasificador debe tratarlo como texto normal/fallback
            print(f"'{texto[:40]}...'")
            print(f"   -> {result.intent} ({result.confidence:.1%})")
            
            # No debe crashear ni comportarse de manera inesperada
            assert result is not None
            assert isinstance(result.response, str)
    
    def test_cambio_tema_abrupto(self, classifier):
        """
        CP-ADV-009: El modelo debe manejar cambios de tema abruptos.
        """
        print("\n" + "="*70)
        print("CP-ADV-009: Cambios de Tema Abrupto")
        print("="*70)
        
        cambios = [
            "hola... por cierto, el clima está raro",
            "quiero pedir pero qué opinas de la política",
            "menú... aunque ahora que lo pienso cuál es tu color favorito",
        ]
        
        for texto in cambios:
            result = classifier.classify(texto)
            
            print(f"'{texto}'")
            print(f"   -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None
    
    def test_secuencias_repetitivas(self, classifier):
        """
        CP-ADV-010: El modelo debe manejar secuencias repetitivas.
        """
        print("\n" + "="*70)
        print("CP-ADV-010: Secuencias Repetitivas")
        print("="*70)
        
        repetitivos = [
            "hola hola hola hola hola",
            "quiero quiero quiero pedido",
            "gracias gracias gracias gracias",
            "menu menu menu menu menu",
        ]
        
        for texto in repetitivos:
            result = classifier.classify(texto)
            
            print(f"'{texto}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None


class TestCasosBorde:
    """Pruebas en los bordes del dominio del problema."""
    
    def test_productos_no_existentes(self, classifier):
        """
        CP-ADV-011: El modelo debe manejar consultas sobre productos inexistentes.
        """
        print("\n" + "="*70)
        print("CP-ADV-011: Productos No Existentes")
        print("="*70)
        
        productos_inexistentes = [
            "quiero sushi",
            "tienen hamburguesas",
            "pizza por favor",
            "me das un hot dog",
            "hay tacos de birria",
        ]
        
        for texto in productos_inexistentes:
            result = classifier.classify(texto)
            
            # Probablemente clasificará como realizar_pedido
            print(f"'{texto}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None
    
    def test_solicitudes_fuera_dominio(self, classifier):
        """
        CP-ADV-012: El modelo debe manejar solicitudes fuera del dominio.
        """
        print("\n" + "="*70)
        print("CP-ADV-012: Solicitudes Fuera de Dominio")
        print("="*70)
        
        fuera_dominio = [
            "cuál es la capital de Francia",
            "cómo se calcula una integral",
            "quién ganó el mundial 2022",
            "cuánto es 2+2",
            "cómo está el dólar hoy",
        ]
        
        for texto in fuera_dominio:
            result = classifier.classify(texto)
            
            print(f"'{texto}' -> {result.intent} ({result.confidence:.1%})")
            
            # Debería ser fallback o baja confianza
            assert result is not None
    
    def test_expresiones_coloquiales(self, classifier):
        """
        CP-ADV-013: El modelo debe manejar expresiones coloquiales/slang.
        """
        print("\n" + "="*70)
        print("CP-ADV-013: Expresiones Coloquiales")
        print("="*70)
        
        coloquiales = [
            "ke onda bro",
            "q hay de comer",
            "pss kiero algo",
            "nmms que hambre",
            "nel pastel",
            "chido gracias",
        ]
        
        for texto in coloquiales:
            result = classifier.classify(texto)
            
            print(f"'{texto}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None


class TestEstabilidadRedesAdversariales:
    """Pruebas de estabilidad ante patrones adversariales conocidos."""
    
    def test_negaciones_confusas(self, classifier):
        """
        CP-ADV-014: El modelo debe manejar dobles negaciones.
        """
        print("\n" + "="*70)
        print("CP-ADV-014: Negaciones Confusas")
        print("="*70)
        
        negaciones = [
            "no quiero no pedir",
            "no es que no me guste el menú",
            "no voy a no ir",
            "no me digas que no",
        ]
        
        for texto in negaciones:
            result = classifier.classify(texto)
            
            print(f"'{texto}' -> {result.intent} ({result.confidence:.1%})")
            
            assert result is not None
    
    def test_sarcasmo_ironia(self, classifier):
        """
        CP-ADV-015: El modelo puede no detectar sarcasmo (limitación conocida).
        """
        print("\n" + "="*70)
        print("CP-ADV-015: Sarcasmo e Ironía (Limitación Conocida)")
        print("="*70)
        
        sarcasticos = [
            "qué buen servicio tienen ehh",
            "gracias por la rapidez... NOT",
            "excelente que no contesten",
            "me encanta esperar 2 horas",
        ]
        
        for texto in sarcasticos:
            result = classifier.classify(texto)
            
            # Documentamos el comportamiento sin asegurar corrección
            tipo = "Puede confundir" if result.intent in ["agradecimiento", "opinion_comida"] else "OK"
            print(f"'{texto}'")
            print(f"   -> {result.intent} ({result.confidence:.1%}) [{tipo}]")
            
            assert result is not None
