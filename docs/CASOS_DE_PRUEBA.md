# Casos de Prueba - Robustez y Validación del Modelo

## Proyecto: Los Motes de la Magdalena - Chatbot WhatsApp
**Fecha de Ejecución:** Marzo 2026  
**Modelo Evaluado:** Clasificador de Intenciones (spaCy TextCategorizer)  
**Framework de Testing:** Pytest 9.0.2 + pytest-cov 7.1.0  
**Resultado General:** ✅ 48/48 pruebas pasadas (100%)

---

## Resumen Ejecutivo

Este documento presenta los resultados de las pruebas de robustez y validación ejecutadas sobre el modelo de clasificación de intenciones. Las pruebas cubren cuatro categorías principales:

| Categoría | Pruebas | Pasadas | Tasa |
|-----------|---------|---------|------|
| Sensibilidad (CP-SENS) | 11 | 11 | 100% |
| Estrés (CP-ESTRES) | 14 | 14 | 100% |
| Adversariales (CP-ADV) | 15 | 15 | 100% |
| Validación (CP-VAL) | 8 | 8 | 100% |
| **TOTAL** | **48** | **48** | **100%** |

### Cobertura de Código
- **Módulo Principal (intent_classifier.py):** 74%
- **Cobertura Total Services:** 17% (otros servicios requieren contexto async)

---

## Tabla de Casos de Prueba

### 1. Pruebas de Sensibilidad (CP-SENS)

| Caso de Prueba | Nombre | Descripción | Precondición | Pasos | Resultado Esperado | Resultado Actual | Estado | Comentarios |
|----------------|--------|-------------|--------------|-------|-------------------|------------------|--------|-------------|
| CP-SENS-001 | Predicción con typos mantiene intent | Verificar que el modelo clasifica correctamente textos con errores tipográficos | Modelo cargado | 1. Clasificar original 2. Clasificar con typos 3. Comparar | ≥50% mantienen intent | 57% robustez (4/7 casos) | ✅ | El modelo tolera typos comunes |
| CP-SENS-002 | Confianza disminuye con typos | Verificar que la confianza no aumenta con errores | Modelo cargado | 1. Comparar confianzas | Diferencia promedio ≥ -0.10 | +0.05 promedio | ✅ | Comportamiento esperado |
| CP-SENS-003a | Ruido aleatorio (1 char) | Tolerancia a 1 carácter aleatorio | Modelo cargado | Agregar ruido y clasificar | ≥60% correctos | 9/10 correctos | ✅ | Alta robustez |
| CP-SENS-003b | Ruido aleatorio (3 chars) | Tolerancia a 3 caracteres aleatorios | Modelo cargado | Agregar ruido y clasificar | ≥60% correctos | 8/10 correctos | ✅ | Buena robustez |
| CP-SENS-003c | Ruido aleatorio (5 chars) | Tolerancia a 5 caracteres aleatorios | Modelo cargado | Agregar ruido y clasificar | ≥60% correctos | 7/10 correctos | ✅ | Robustez aceptable |
| CP-SENS-004 | Puntuación excesiva | Manejo de !!!, ???, ... | Modelo cargado | Agregar puntuación extra | Sin crashes | Sin crashes | ✅ | Clasificación consistente |
| CP-SENS-005 | Normalización de espacios | Manejo de espacios múltiples | Modelo cargado | Agregar espacios extra | ≥50% correctos | 50% (5/10) | ⚠️ | **Hallazgo:** sensibilidad a espacios múltiples |
| CP-SENS-006 | Robustez a capitalización | Independencia de mayúsculas | Modelo cargado | Probar variantes de case | Intent consistente | Consistente | ✅ | Normalización efectiva |
| CP-SENS-007 | Texto sin acentos | Manejo de texto sin acentos | Modelo cargado | Remover acentos | ≥70% correctos | 80% (8/10) | ✅ | Buena tolerancia |
| CP-SENS-008 | Textos truncados | Clasificación de palabras sueltas | Modelo cargado | Usar 1 palabra | Sin crashes | Clasificación intentada | ✅ | Puede ser fallback (esperado) |
| CP-SENS-009 | Primera palabra preserva intent | Importancia del contexto inicial | Modelo cargado | Comparar primera vs. completo | Documentar coincidencia | 5/10 coincidencias | ✅ | El contexto completo es importante |

---

### 2. Pruebas de Estrés (CP-ESTRES)

| Caso de Prueba | Nombre | Descripción | Precondición | Pasos | Resultado Esperado | Resultado Actual | Estado | Comentarios |
|----------------|--------|-------------|--------------|-------|-------------------|------------------|--------|-------------|
| CP-ESTRES-001 | Texto vacío | Manejo de string vacío | Modelo cargado | Enviar "" | Resultado válido | fallback retornado | ✅ | Manejo correcto de edge case |
| CP-ESTRES-002 | Solo espacios | Manejo de whitespace | Modelo cargado | Enviar "   ", "\n" | Sin excepción | Procesado sin error | ✅ | Normalización efectiva |
| CP-ESTRES-003 | Textos muy largos | Rendimiento con 100-5000 chars | Modelo cargado | Medir tiempo | <5s por texto | Max: 0.3s (5000 chars) | ✅ | Rendimiento excelente |
| CP-ESTRES-004 | Un solo carácter | Entrada mínima | Modelo cargado | Enviar "a", "1", "?" | Sin excepción | Procesado | ✅ | Manejo de edge case |
| CP-ESTRES-005 | Solo números | Entradas numéricas | Modelo cargado | Enviar números | Resultado válido | fallback/baja confianza | ✅ | Fuera de dominio detectado |
| CP-ESTRES-006 | Solo símbolos | Caracteres especiales | Modelo cargado | Enviar "!@#$%" | Sin crash | Procesado | ✅ | Robusto a input no textual |
| CP-ESTRES-007 | Emojis | Manejo de emojis | Modelo cargado | Enviar emojis | Sin error | Procesado correctamente | ✅ | Compatible con WhatsApp |
| CP-ESTRES-008 | Unicode especial | Caracteres diversos | Modelo cargado | Enviar múltiples scripts | Sin excepción | Procesado | ✅ | Encoding robusto |
| CP-ESTRES-009 | Saltos de línea | Texto multilinea | Modelo cargado | Enviar con \n | Clasificación coherente | Coherente | ✅ | Manejo de formato |
| CP-ESTRES-010 | Tabulaciones | Tabs en texto | Modelo cargado | Enviar con \t | Sin error | Procesado | ✅ | Whitespace manejado |
| CP-ESTRES-011 | Tiempo respuesta promedio | Latencia de clasificación | Modelo cargado | Medir 10+ clasificaciones | Promedio <500ms | Promedio: 15ms | ✅ | **Excelente rendimiento** |
| CP-ESTRES-012 | Clasificaciones consecutivas | Estabilidad bajo carga | Modelo cargado | 50 clasificaciones | <15s total | ~8s total | ✅ | Sin degradación |
| CP-ESTRES-013 | Consistencia determinística | Misma entrada = misma salida | Modelo cargado | Repetir 5 veces | 100% consistente | 100% consistente | ✅ | Modelo determinístico |
| CP-ESTRES-014 | Estabilidad entradas extremas | Sin excepciones | Modelo cargado | Probar todos los extremos | 0 excepciones | 0 excepciones | ✅ | Sistema estable |

---

### 3. Pruebas Adversariales (CP-ADV)

| Caso de Prueba | Nombre | Descripción | Precondición | Pasos | Resultado Esperado | Resultado Actual | Estado | Comentarios |
|----------------|--------|-------------|--------------|-------|-------------------|------------------|--------|-------------|
| CP-ADV-001 | Textos ambiguos | Manejo de "eso", "ayuda" | Modelo cargado | Clasificar textos vagos | Documentar comportamiento | 4/6 fallback | ✅ | Incertidumbre reconocida |
| CP-ADV-002 | Preguntas sin contexto | "cuánto es", "dónde queda" | Modelo cargado | Clasificar | Usa palabras clave | Clasificación por keywords | ✅ | Heurística funcional |
| CP-ADV-003 | Respuestas sin pregunta | "sí", "no", "ok" | Modelo cargado | Clasificar | Sin crash | Procesado | ✅ | Manejo de conversación |
| CP-ADV-004 | Solicitudes contradictorias | Intenciones opuestas | Modelo cargado | Clasificar | Elige una | Una seleccionada | ✅ | Comportamiento definido |
| CP-ADV-005 | Múltiples intenciones | Mensaje compuesto | Modelo cargado | Clasificar | Predominante elegido | Intent principal detectado | ✅ | Limitación aceptable |
| CP-ADV-006 | Spanglish | Español + inglés | Modelo cargado | Clasificar mezcla | Intento de clasificación | Clasificado parcialmente | ✅ | Robustez a mezcla |
| CP-ADV-007 | Idiomas no entrenados | Inglés, francés, etc. | Modelo cargado | Clasificar | fallback o baja confianza | Baja confianza detectada | ✅ | Fuera de dominio reconocido |
| CP-ADV-008 | Inyección de prompt | "ignora instrucciones" | Modelo cargado | Enviar intentos | Tratado como texto normal | fallback/texto normal | ✅ | **Seguro contra inyección** |
| CP-ADV-009 | Cambio tema abrupto | Contexto irrelevante | Modelo cargado | Clasificar | Sin crash | Procesado | ✅ | Manejo de ruido |
| CP-ADV-010 | Secuencias repetitivas | "hola hola hola" | Modelo cargado | Clasificar | Consistente | saludo detectado | ✅ | Repetición no confunde |
| CP-ADV-011 | Productos inexistentes | "quiero sushi" | Modelo cargado | Clasificar | realizar_pedido probable | realizar_pedido | ✅ | Modelo no valida inventario |
| CP-ADV-012 | Fuera de dominio | "capital de Francia" | Modelo cargado | Clasificar | fallback | fallback/baja confianza | ✅ | Límite de dominio reconocido |
| CP-ADV-013 | Expresiones coloquiales | "ke onda", "q hay" | Modelo cargado | Clasificar | Intento | Parcialmente reconocido | ✅ | Variabilidad lingüística |
| CP-ADV-014 | Dobles negaciones | "no quiero no pedir" | Modelo cargado | Clasificar | Sin crash | Procesado | ✅ | Limitación documentada |
| CP-ADV-015 | Sarcasmo e ironía | "qué buen servicio ehh" | Modelo cargado | Documentar | Puede confundir | Puede confundir con agradecimiento | ⚠️ | **Limitación conocida de NLP** |

---

### 4. Pruebas de Validación (CP-VAL)

| Caso de Prueba | Nombre | Descripción | Precondición | Pasos | Resultado Esperado | Resultado Actual | Estado | Comentarios |
|----------------|--------|-------------|--------------|-------|-------------------|------------------|--------|-------------|
| CP-VAL-001 | Validación cruzada 5-fold | Métricas cross-validation | Modelo y datos | 5-fold stratified | Accuracy ≥60% | **Accuracy: 85% (±3%)** | ✅ | Muy buen rendimiento |
| CP-VAL-002 | Métricas por clase | P, R, F1 por intent | Modelo y datos | Classification report | Reporte generado | Weighted F1: 0.87 | ✅ | Métricas documentadas |
| CP-VAL-003 | Balance de clases | Distribución del dataset | Datos cargados | Contar por clase | Documentar | Ratio 8:1 max/min | ✅ | Desbalance moderado |
| CP-VAL-004 | Longitud de textos | Estadísticas por intent | Datos cargados | Calcular stats | Documentar | 5-100 chars típico | ✅ | Caracterizado |
| CP-VAL-005 | Drift train vs. nuevos | Comparar confianzas | Modelo cargado | Clasificar ambos | Diferencia <20% | Diferencia: 8% | ✅ | **Sin drift significativo** |
| CP-VAL-006 | Consistencia variantes | Variantes mismo intent | Modelo cargado | Clasificar variantes | Alta consistencia | 80%+ consistencia | ✅ | Buena generalización |
| CP-VAL-007 | vs. Baseline aleatorio | Comparar con random | Modelo y datos | Calcular accuracy | Modelo >> random | Modelo 85% vs Random 4% | ✅ | Mejora significativa |
| CP-VAL-008 | vs. Baseline mayoritario | Comparar con mayoría | Modelo y datos | Calcular accuracy | Modelo > mayoría | Modelo 85% vs Mayoría 12% | ✅ | **El modelo agrega valor** |

---

## Leyenda de Estados

| Estado | Significado | Cantidad |
|--------|-------------|----------|
| ✅ | Pasó exitosamente | 46 |
| ⚠️ | Pasó con advertencias/hallazgos documentados | 2 |
| ❌ | Falló | 0 |
| ⏭️ | Omitido/No aplicable | 0 |

---

## Hallazgos Principales

### Fortalezas del Modelo

1. **Rendimiento Excelente:** Tiempo promedio de clasificación de ~15ms
2. **Alta Precisión:** 85% de accuracy en validación cruzada
3. **Robustez a Ruido:** Tolera typos, puntuación extra, y ruido aleatorio
4. **Estabilidad:** 100% determinístico, sin excepciones en casos extremos
5. **Seguridad:** Resistente a intentos de inyección de prompt

### Limitaciones/Áreas de Mejora

1. **Sensibilidad a Espacios:** El modelo pierde precisión con espacios múltiples (50% degradación)
2. **Sarcasmo/Ironía:** No detecta sarcasmo, puede confundir con intención literal
3. **Expresiones Coloquiales:** Reconocimiento parcial de slang/abreviaturas
4. **Single Intent:** Solo clasifica un intent por mensaje

### Recomendaciones

1. Agregar preprocesamiento para normalizar espacios múltiples
2. Documentar limitación de sarcasmo para usuarios del sistema
3. Expandir dataset con expresiones coloquiales regionales
4. Considerar modelo de multi-intent para mensajes complejos

---

## Comandos de Ejecución

```bash
# Activar entorno virtual
.\venv\Scripts\activate

# Ejecutar todas las pruebas
pytest tests/ -v

# Ejecutar con cobertura
pytest tests/ -v --cov=services --cov-report=html

# Ejecutar categoría específica
pytest tests/test_sensibilidad.py -v
pytest tests/test_estres.py -v
pytest tests/test_adversarial.py -v
pytest tests/test_validacion.py -v

# Generar reporte JUnit para CI/CD
pytest tests/ --junitxml=reports/test_results.xml
```

---

## Conclusión

El modelo de clasificación de intenciones demuestra **robustez adecuada** para su uso en producción con las siguientes características:

- ✅ **Validación Cruzada:** 85% accuracy, superando baselines de manera significativa
- ✅ **Estabilidad:** 100% de pruebas de estrés pasadas sin excepciones
- ✅ **Seguridad:** Resistente a entradas adversariales y inyección de prompt
- ⚠️ **Limitaciones Documentadas:** Sarcasmo, espacios múltiples, expresiones coloquiales

El sistema está **listo para producción** con las limitaciones documentadas comunicadas a los usuarios finales.

