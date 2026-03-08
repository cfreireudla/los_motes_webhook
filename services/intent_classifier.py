# Clasificador de intención con spaCy
"""
Servicio para clasificar la intención del usuario usando el modelo entrenado.
Carga el modelo de spaCy y las respuestas predefinidas.
"""

import json
import random
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """Resultado de la clasificación de intención."""
    intent: str
    confidence: float
    response: str
    action: Optional[str]
    is_fallback: bool


class IntentClassifier:
    """
    Clasificador de intenciones usando spaCy.
    
    Carga el modelo entrenado y las respuestas predefinidas,
    luego clasifica el texto del usuario y devuelve la respuesta apropiada.
    """
    
    # Umbral mínimo de confianza para aceptar una predicción
    CONFIDENCE_THRESHOLD = 0.5
    
    def __init__(
        self,
        model_path: str = "models/intent_classifier",
        responses_path: str = "data/responses.json"
    ):
        """
        Inicializa el clasificador.
        
        Args:
            model_path: Ruta al modelo de spaCy entrenado
            responses_path: Ruta al archivo JSON con respuestas
        """
        self.model_path = Path(model_path)
        self.responses_path = Path(responses_path)
        self.nlp: Optional[Language] = None
        self.responses: dict = {}
        self._loaded = False
    
    def load(self) -> bool:
        """
        Carga el modelo y las respuestas.
        
        Returns:
            True si la carga fue exitosa, False en caso contrario.
        """
        try:
            # Cargar modelo de spaCy
            if not self.model_path.exists():
                logger.error(f"Modelo no encontrado en: {self.model_path}")
                return False
            
            logger.info(f"Cargando modelo desde: {self.model_path}")
            self.nlp = spacy.load(self.model_path)
            logger.info(f"Modelo cargado. Pipeline: {self.nlp.pipe_names}")
            
            # Cargar respuestas
            if not self.responses_path.exists():
                logger.error(f"Respuestas no encontradas en: {self.responses_path}")
                return False
            
            with open(self.responses_path, 'r', encoding='utf-8') as f:
                self.responses = json.load(f)
            logger.info(f"Respuestas cargadas: {len(self.responses)} intents")
            
            self._loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar clasificador: {e}")
            return False
    
    @property
    def is_loaded(self) -> bool:
        """Indica si el clasificador está cargado y listo."""
        return self._loaded and self.nlp is not None
    
    def classify(self, text: str) -> IntentResult:
        """
        Clasifica el texto y retorna la intención con su respuesta.
        
        Args:
            text: Texto del usuario a clasificar
            
        Returns:
            IntentResult con la intención, confianza, respuesta y acción
        """
        if not self.is_loaded:
            logger.warning("Clasificador no cargado, usando fallback")
            return self._get_fallback_result()
        
        try:
            # Preprocesar texto
            text_clean = text.strip().lower()
            
            # Clasificar con spaCy
            doc = self.nlp(text_clean)
            
            # Obtener la categoría con mayor probabilidad
            if not doc.cats:
                logger.warning("El modelo no devolvió categorías")
                return self._get_fallback_result()
            
            predicted_intent = max(doc.cats, key=doc.cats.get)
            confidence = doc.cats[predicted_intent]
            
            logger.debug(
                f"Clasificación: '{text[:50]}...' -> {predicted_intent} "
                f"(confianza: {confidence:.2%})"
            )
            
            # Verificar umbral de confianza
            if confidence < self.CONFIDENCE_THRESHOLD:
                logger.info(
                    f"Confianza baja ({confidence:.2%}), usando fallback"
                )
                return self._get_fallback_result(
                    original_intent=predicted_intent,
                    original_confidence=confidence
                )
            
            # Obtener respuesta para el intent
            return self._build_result(predicted_intent, confidence)
            
        except Exception as e:
            logger.error(f"Error al clasificar texto: {e}")
            return self._get_fallback_result()
    
    def _build_result(self, intent: str, confidence: float) -> IntentResult:
        """
        Construye el resultado para un intent específico.
        
        Args:
            intent: Nombre del intent detectado
            confidence: Nivel de confianza de la predicción
            
        Returns:
            IntentResult con la respuesta y acción correspondiente
        """
        intent_data = self.responses.get(intent, self.responses.get("fallback", {}))
        
        # Seleccionar respuesta aleatoria de las disponibles
        responses_list = intent_data.get("responses", [])
        if responses_list:
            response = random.choice(responses_list)
        else:
            response = "¿En qué puedo ayudarte?"
        
        action = intent_data.get("action")
        
        return IntentResult(
            intent=intent,
            confidence=confidence,
            response=response,
            action=action,
            is_fallback=False
        )
    
    def _get_fallback_result(
        self,
        original_intent: Optional[str] = None,
        original_confidence: float = 0.0
    ) -> IntentResult:
        """
        Genera un resultado de fallback cuando no hay clasificación confiable.
        
        Args:
            original_intent: Intent original detectado (para logging)
            original_confidence: Confianza original
            
        Returns:
            IntentResult con respuesta de fallback
        """
        fallback_data = self.responses.get("fallback", {
            "responses": ["No entendí tu mensaje. ¿Podrías reformularlo?"],
            "action": "show_menu_button"
        })
        
        responses_list = fallback_data.get("responses", [])
        response = random.choice(responses_list) if responses_list else "¿En qué puedo ayudarte?"
        
        return IntentResult(
            intent="fallback",
            confidence=original_confidence,
            response=response,
            action=fallback_data.get("action"),
            is_fallback=True
        )
    
    def get_all_intents(self) -> list[str]:
        """Retorna la lista de todos los intents disponibles."""
        return list(self.responses.keys())
    
    def get_response_for_intent(self, intent: str) -> Optional[dict]:
        """
        Obtiene la configuración de respuesta para un intent específico.
        
        Args:
            intent: Nombre del intent
            
        Returns:
            Dict con 'responses' y 'action', o None si no existe
        """
        return self.responses.get(intent)


# Instancia global del clasificador (singleton)
_classifier_instance: Optional[IntentClassifier] = None


def get_classifier() -> IntentClassifier:
    """
    Obtiene la instancia global del clasificador.
    Crea una nueva si no existe.
    
    Returns:
        Instancia del IntentClassifier
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = IntentClassifier()
    return _classifier_instance


async def init_classifier() -> bool:
    """
    Inicializa el clasificador de forma asíncrona.
    Debe llamarse al inicio de la aplicación.
    
    Returns:
        True si la inicialización fue exitosa
    """
    classifier = get_classifier()
    if not classifier.is_loaded:
        return classifier.load()
    return True