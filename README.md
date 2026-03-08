# 🌮 Los Motes de la Magdalena - WhatsApp Chatbot

Chatbot de WhatsApp para pedidos de comida, construido con FastAPI y spaCy para clasificación de intenciones con NLP.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![spaCy](https://img.shields.io/badge/spaCy-3.x-09A3D5.svg)](https://spacy.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Características

- **Flujo de pedidos interactivo** - Menús con botones y listas de WhatsApp
- **Clasificación de intenciones con IA** - Modelo spaCy entrenado con 22 intents
- **Respuestas inteligentes** - Manejo de preguntas frecuentes (horarios, ubicación, delivery, etc.)
- **Carrito de compras** - Gestión de pedidos con confirmación
- **Arquitectura modular** - Servicios separados y fácil de extender

---

## 🛠️ Stack Tecnológico

| Tecnología | Uso |
|------------|-----|
| **FastAPI** | Framework web async |
| **SQLAlchemy** | ORM para base de datos |
| **SQLite** | Base de datos local |
| **spaCy** | NLP y clasificación de intenciones |
| **httpx** | Cliente HTTP async para WhatsApp API |
| **Jupyter** | Notebooks para entrenamiento del modelo |

---

## 📁 Estructura del Proyecto

```
los_motes_webhook/
├── app.py                    # Punto de entrada FastAPI
├── requirements.txt          # Dependencias
├── .env.example              # Plantilla de variables de entorno
│
├── data/
│   ├── intents.jsonl         # Dataset de entrenamiento (388 ejemplos)
│   └── responses.json        # Respuestas por intent
│
├── database/
│   ├── database.py           # Configuración SQLAlchemy
│   ├── models.py             # Modelos (Category, Product, Order, etc.)
│   └── seed.py               # Datos iniciales del menú
│
├── models/
│   └── intent_classifier/    # Modelo spaCy entrenado (generado)
│
├── notebooks/
│   ├── 01_exploracion_datos.ipynb
│   ├── 02_entrenamiento_modelo.ipynb
│   └── 03_evaluacion_metricas.ipynb
│
├── routes/
│   └── webhook_routes.py     # Endpoints del webhook
│
└── services/
    ├── ai_service.py         # Orquestador de IA
    ├── intent_classifier.py  # Clasificador de intenciones
    ├── menu_service.py       # Lógica del menú y pedidos
    ├── message_service.py    # Procesamiento de mensajes
    ├── interactive_messages.py # Mensajes de WhatsApp
    └── user_state_service.py # Estado del usuario
```

---

## 🚀 Instalación

### 1. Clonar repositorio

```bash
git clone https://github.com/tu-usuario/los_motes_webhook.git
cd los_motes_webhook
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
WHATSAPP_TOKEN=tu_token_de_whatsapp
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
VERIFY_TOKEN=tu_token_de_verificacion
```

### 5. Entrenar el modelo de IA

Ejecutar los notebooks en orden:

```bash
# Opción 1: Jupyter Notebook
jupyter notebook notebooks/

# Opción 2: VS Code
# Abrir notebooks/ y ejecutar celdas
```

1. `01_exploracion_datos.ipynb` - Análisis del dataset
2. `02_entrenamiento_modelo.ipynb` - Entrenar y guardar modelo
3. `03_evaluacion_metricas.ipynb` - Evaluar rendimiento

### 6. Ejecutar servidor

```bash
# Desarrollo
fastapi dev

# Producción
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## 🔧 Configuración del Webhook

### 1. Exponer servidor local (desarrollo)

```bash
ngrok http 8000
```

### 2. Configurar en Meta Business

1. Ir a [Meta for Developers](https://developers.facebook.com)
2. WhatsApp > Configuration > Webhook
3. URL: `https://tu-ngrok-url.ngrok.io/webhook`
4. Verify Token: El mismo que en `.env`
5. Suscribirse a: `messages`

---

## 🤖 Intents Soportados

| Intent | Descripción | Ejemplo |
|--------|-------------|---------|
| `saludo` | Saludos iniciales | "hola", "buenas tardes" |
| `despedida` | Despedidas | "chao", "hasta luego" |
| `consultar_menu` | Ver menú | "qué tienen?", "ver carta" |
| `consultar_horario` | Horarios | "a qué hora abren?" |
| `consultar_ubicacion` | Ubicación | "dónde están?" |
| `realizar_pedido` | Iniciar pedido | "quiero pedir" |
| `delivery` | Info de envío | "hacen delivery?" |
| `metodos_pago` | Formas de pago | "aceptan nequi?" |
| `hablar_humano` | Atención humana | "quiero hablar con alguien" |
| `fallback` | No entendido | (cualquier otro mensaje) |

Ver todos los 22 intents en `data/responses.json`.

---

## 📊 Métricas del Modelo

| Métrica | Valor |
|---------|-------|
| Accuracy | ~85-90% |
| F1-Score (macro) | ~80-85% |
| Intents | 22 |
| Ejemplos | 388 |

*Ejecutar `03_evaluacion_metricas.ipynb` para métricas detalladas.*

---

## 📝 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/webhook` | Verificación de Meta |
| `POST` | `/webhook` | Recibir mensajes de WhatsApp |
| `GET` | `/` | Health check |

---

## 🗺️ Roadmap

- [ ] Pruebas unitarias con pytest
- [ ] CI/CD con GitHub Actions
- [ ] Deploy a producción (Railway/Render)
- [ ] Dashboard de métricas
- [ ] Integración con sistema POS
- [ ] Notificaciones a administrador

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Tu Nombre**

- GitHub: [@tu-usuario](https://github.com/tu-usuario)

---

<p align="center">
  Hecho con ❤️ para Los Motes de la Magdalena 🌮
</p>
