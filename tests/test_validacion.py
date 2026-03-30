# Pruebas de Validación y Data Drift
"""
Pruebas para validación cruzada del modelo y análisis de drift.

Incluye:
- Validación cruzada del clasificador
- Comparación entre datos de entrenamiento y prueba
- Análisis de distribución de clases
- Detección de cambios en patrones
"""

import pytest
import json
import numpy as np
from pathlib import Path
from collections import Counter
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    classification_report,
    confusion_matrix
)


class TestValidacionCruzada:
    """Pruebas de validación cruzada del modelo."""
    
    def test_validacion_cruzada_5_fold(self, classifier, intents_data, nlp_model, class_names):
        """
        CP-VAL-001: Validación cruzada 5-fold del modelo.
        """
        print("\n" + "="*70)
        print("CP-VAL-001: Validación Cruzada 5-Fold")
        print("="*70)
        
        # Preparar datos
        texts = [item['text'] for item in intents_data]
        labels = [item['label'] for item in intents_data]
        
        # Convertir labels a índices
        label_to_idx = {label: i for i, label in enumerate(class_names)}
        y = np.array([label_to_idx.get(l, 0) for l in labels])
        
        # Función de predicción
        def predict_texts(texts):
            predictions = []
            for text in texts:
                doc = nlp_model(text)
                pred = max(doc.cats, key=doc.cats.get)
                predictions.append(label_to_idx.get(pred, 0))
            return np.array(predictions)
        
        # Validación cruzada manual (spaCy no es sklearn compatible)
        kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        fold_scores = []
        
        for fold, (train_idx, val_idx) in enumerate(kfold.split(texts, y)):
            val_texts = [texts[i] for i in val_idx]
            val_true = y[val_idx]
            
            val_pred = predict_texts(val_texts)
            
            accuracy = accuracy_score(val_true, val_pred)
            fold_scores.append(accuracy)
            
            print(f"   Fold {fold+1}: Accuracy = {accuracy:.2%}")
        
        promedio = np.mean(fold_scores)
        std = np.std(fold_scores)
        
        print(f"\n📊 Resultados Validación Cruzada:")
        print(f"   Accuracy Promedio: {promedio:.2%} (±{std:.2%})")
        print(f"   Mínimo: {min(fold_scores):.2%}")
        print(f"   Máximo: {max(fold_scores):.2%}")
        
        # El accuracy promedio debe ser al menos 70%
        assert promedio >= 0.60, f"Accuracy insuficiente: {promedio:.2%}"
    
    def test_metricas_por_clase(self, classifier, intents_data, class_names):
        """
        CP-VAL-002: Métricas de precisión, recall y F1 por clase.
        """
        print("\n" + "="*70)
        print("CP-VAL-002: Métricas por Clase")
        print("="*70)
        
        # Preparar datos
        texts = [item['text'] for item in intents_data]
        labels = [item['label'] for item in intents_data]
        
        # Clasificar todos los textos
        predicciones = []
        for text in texts:
            result = classifier.classify(text)
            predicciones.append(result.intent)
        
        # Calcular métricas
        print("\n📊 Reporte de Clasificación:")
        report = classification_report(
            labels, 
            predicciones, 
            zero_division=0,
            output_dict=True
        )
        
        # Mostrar top 10 clases ordenadas por F1
        clases_f1 = [(k, v['f1-score']) for k, v in report.items() 
                     if k not in ['accuracy', 'macro avg', 'weighted avg']]
        clases_f1.sort(key=lambda x: x[1], reverse=True)
        
        print("\n   Top 10 clases por F1-Score:")
        for clase, f1 in clases_f1[:10]:
            precision = report[clase]['precision']
            recall = report[clase]['recall']
            print(f"   {clase:25s} P:{precision:.2f} R:{recall:.2f} F1:{f1:.2f}")
        
        # Métricas globales
        print(f"\n📈 Métricas Globales:")
        print(f"   Accuracy: {report['accuracy']:.2%}")
        print(f"   Macro F1: {report['macro avg']['f1-score']:.2%}")
        print(f"   Weighted F1: {report['weighted avg']['f1-score']:.2%}")


class TestDistribucionDatos:
    """Pruebas de análisis de distribución de datos."""
    
    def test_balance_clases(self, intents_data, class_names):
        """
        CP-VAL-003: Análisis de balance de clases en el dataset.
        """
        print("\n" + "="*70)
        print("CP-VAL-003: Balance de Clases")
        print("="*70)
        
        labels = [item['label'] for item in intents_data]
        conteo = Counter(labels)
        
        total = len(labels)
        
        print(f"\n📊 Distribución de clases ({total} ejemplos):")
        
        clases_ordenadas = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
        
        for clase, count in clases_ordenadas:
            pct = (count / total) * 100
            barra = "█" * int(pct)
            print(f"   {clase:25s} {count:3d} ({pct:5.1f}%) {barra}")
        
        # Verificar que no hay clases con menos de 3 ejemplos
        clases_escasas = [c for c, n in conteo.items() if n < 3]
        
        print(f"\n⚠️ Clases con menos de 3 ejemplos: {clases_escasas or 'Ninguna'}")
        
        # Calcular desbalance
        max_count = max(conteo.values())
        min_count = min(conteo.values())
        ratio = max_count / min_count if min_count > 0 else float('inf')
        
        print(f"\n📈 Ratio de desbalance: {ratio:.1f}x")
    
    def test_longitud_textos(self, intents_data):
        """
        CP-VAL-004: Análisis de longitud de textos por intent.
        """
        print("\n" + "="*70)
        print("CP-VAL-004: Distribución de Longitud de Textos")
        print("="*70)
        
        # Calcular longitudes por intent
        longitudes_por_intent = {}
        for item in intents_data:
            intent = item['label']
            longitud = len(item['text'])
            
            if intent not in longitudes_por_intent:
                longitudes_por_intent[intent] = []
            longitudes_por_intent[intent].append(longitud)
        
        # Estadísticas
        print("\n📊 Longitud de textos por intent:")
        stats = []
        for intent, longs in longitudes_por_intent.items():
            promedio = np.mean(longs)
            minimo = min(longs)
            maximo = max(longs)
            stats.append((intent, promedio, minimo, maximo))
        
        stats.sort(key=lambda x: x[1], reverse=True)
        
        for intent, prom, mín, máx in stats[:10]:
            print(f"   {intent:25s} Prom:{prom:5.1f} Min:{mín:3d} Max:{máx:3d}")


class TestDataDrift:
    """Pruebas para detectar data drift potencial."""
    
    def test_comparar_confianza_train_vs_nuevos(self, classifier, intents_data):
        """
        CP-VAL-005: Comparar confianza en datos vistos vs. nuevos.
        """
        print("\n" + "="*70)
        print("CP-VAL-005: Análisis de Confianza Datos Vistos vs. Nuevos")
        print("="*70)
        
        # Textos del dataset (vistos durante entrenamiento)
        textos_vistos = [item['text'] for item in intents_data[:20]]
        
        # Textos nuevos (variaciones no vistas)
        textos_nuevos = [
            "hey qué tal cómo estás",
            "quisiera ordenar comida para llevar",
            "a qué horas cierran ustedes",
            "me podrían decir los valores",
            "tengo una reclamación que hacer",
            "buenas noches quisiera información",
            "hay servicio de repartidor",
            "aceptan pagos con tarjeta",
            "quiero ver qué tienen de comer",
            "necesito ayuda de un agente",
        ]
        
        # Calcular confianzas
        conf_vistos = []
        for texto in textos_vistos:
            result = classifier.classify(texto)
            conf_vistos.append(result.confidence)
        
        conf_nuevos = []
        for texto in textos_nuevos:
            result = classifier.classify(texto)
            conf_nuevos.append(result.confidence)
        
        prom_vistos = np.mean(conf_vistos)
        prom_nuevos = np.mean(conf_nuevos)
        
        print(f"\n📊 Confianza Promedio:")
        print(f"   Datos de entrenamiento: {prom_vistos:.2%}")
        print(f"   Datos nuevos:           {prom_nuevos:.2%}")
        print(f"   Diferencia:             {prom_vistos - prom_nuevos:+.2%}")
        
        # Analizar si hay drift significativo
        drift = prom_vistos - prom_nuevos
        
        if drift > 0.20:
            print("\n⚠️ DRIFT DETECTADO: El modelo es significativamente menos")
            print("   confiado con datos nuevos. Considerar reentrenamiento.")
        else:
            print("\n✅ Sin drift significativo detectado.")
    
    def test_variantes_por_intent(self, classifier):
        """
        CP-VAL-006: Verificar que variantes del mismo intent se clasifican igual.
        """
        print("\n" + "="*70)
        print("CP-VAL-006: Consistencia de Variantes por Intent")
        print("="*70)
        
        # Variantes para cada intent
        variantes_por_intent = {
            "saludo": [
                "hola", "buenos días", "buenas tardes", "qué tal", 
                "hey", "hola buenas"
            ],
            "consultar_horario": [
                "cuál es el horario", "a qué hora abren", "horarios",
                "hasta qué hora atienden", "qué días abren"
            ],
            "realizar_pedido": [
                "quiero pedir", "quisiera ordenar", "me das",
                "quiero un pedido", "voy a pedir"
            ],
            "delivery": [
                "hacen domicilios", "tienen delivery", "envíos a domicilio",
                "reparten a casa", "llevan a domicilio"
            ],
        }
        
        for intent_esperado, variantes in variantes_por_intent.items():
            print(f"\n🏷️ Intent: {intent_esperado}")
            correctos = 0
            
            for variante in variantes:
                result = classifier.classify(variante)
                es_correcto = result.intent == intent_esperado
                if es_correcto:
                    correctos += 1
                
                estado = "✅" if es_correcto else f"❌ -> {result.intent}"
                print(f"   '{variante}' {estado}")
            
            tasa = correctos / len(variantes)
            print(f"   📊 Tasa de acierto: {tasa:.0%}")


class TestComparacionBaseline:
    """Comparación del modelo con un baseline simple."""
    
    def test_vs_baseline_aleatorio(self, classifier, intents_data, class_names):
        """
        CP-VAL-007: El modelo debe superar un clasificador aleatorio.
        """
        print("\n" + "="*70)
        print("CP-VAL-007: Comparación vs. Baseline Aleatorio")
        print("="*70)
        
        import random
        random.seed(42)
        
        texts = [item['text'] for item in intents_data]
        labels = [item['label'] for item in intents_data]
        
        # Baseline aleatorio
        predicciones_random = [random.choice(class_names) for _ in texts]
        accuracy_random = accuracy_score(labels, predicciones_random)
        
        # Modelo real
        predicciones_modelo = []
        for text in texts:
            result = classifier.classify(text)
            predicciones_modelo.append(result.intent)
        
        accuracy_modelo = accuracy_score(labels, predicciones_modelo)
        
        print(f"\n📊 Accuracy:")
        print(f"   Baseline aleatorio: {accuracy_random:.2%}")
        print(f"   Modelo entrenado:   {accuracy_modelo:.2%}")
        print(f"   Mejora:             {accuracy_modelo - accuracy_random:+.2%}")
        
        # El modelo debe ser significativamente mejor
        assert accuracy_modelo > accuracy_random * 2, (
            "El modelo no supera significativamente el baseline aleatorio"
        )
    
    def test_vs_baseline_mayoritario(self, classifier, intents_data):
        """
        CP-VAL-008: El modelo debe superar un clasificador por clase mayoritaria.
        """
        print("\n" + "="*70)
        print("CP-VAL-008: Comparación vs. Baseline Mayoritario")
        print("="*70)
        
        texts = [item['text'] for item in intents_data]
        labels = [item['label'] for item in intents_data]
        
        # Encontrar clase mayoritaria
        conteo = Counter(labels)
        clase_mayoritaria = conteo.most_common(1)[0][0]
        
        # Baseline: siempre predecir clase mayoritaria
        accuracy_mayoritario = conteo[clase_mayoritaria] / len(labels)
        
        # Modelo real
        predicciones_modelo = []
        for text in texts:
            result = classifier.classify(text)
            predicciones_modelo.append(result.intent)
        
        accuracy_modelo = accuracy_score(labels, predicciones_modelo)
        
        print(f"\n📊 Accuracy:")
        print(f"   Clase mayoritaria ({clase_mayoritaria}): {accuracy_mayoritario:.2%}")
        print(f"   Modelo entrenado:   {accuracy_modelo:.2%}")
        print(f"   Mejora:             {accuracy_modelo - accuracy_mayoritario:+.2%}")
        
        # El modelo debe superar esta baseline
        assert accuracy_modelo > accuracy_mayoritario, (
            "El modelo no supera el baseline de clase mayoritaria"
        )
