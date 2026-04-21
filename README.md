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

## 🏗️ Arquitectura End-to-End

```text
┌──────────────────────┐
│       USUARIO        │
│ (WhatsApp App móvil) │
└──────────┬───────────┘
     │ 1) Mensaje
     ▼
┌──────────────────────────────┐
│   WHATSAPP CLOUD / META API  │
│ (eventos webhook entrantes)  │
└──────────┬───────────────────┘
     │ 2) POST /webhook
     ▼
┌──────────────────────────────────────────┐
│ FastAPI App (app.py + webhook_routes.py)│
│ - Verifica token (GET /webhook)          │
│ - Recibe payload WhatsApp (POST /webhook)│
└──────────┬───────────────────────────────┘
     │ 3) process_message(...)
     ▼
┌──────────────────────────────┐
│ message_service.py           │
│ - Detecta tipo de mensaje    │
│ - Crea sesión DB             │
│ - Ruta a IA o interactivos   │
└───────┬──────────────────────┘
  │
  ├───────────────────────────────┐
  │                               │
  ▼                               ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│ ai_service.py            │   │ interactive/list buttons │
│ (texto libre)            │   │ (menu_service.py)        │
└──────────┬───────────────┘   └──────────┬───────────────┘
     │ 4) classify(text)            │
     ▼                              │
┌──────────────────────────┐              │
│ intent_classifier.py     │              │
│ spaCy model local        │              │
│ + data/responses.json    │              │
└──────────┬───────────────┘              │
     │                              │
     ├── if intent=realizar_pedido ─────► order_parser.py
     │                                   (productos, cantidades,
     │                                    extras, modificadores)
     │
     ├── if fallback + baja confianza ──► gemini_service.py
     │                                   (respuesta generativa)
     │
     ▼
┌────────────────────────────────────────────────┐
│ Acción final                                   │
│ - send_menu_link / show_cart / cancel / etc.  │
│ - Construcción de respuesta al usuario         │
└──────────┬─────────────────────────────────────┘
     │ 5) enviar mensaje
     ▼
┌──────────────────────────────┐
│ interactive_messages.py /    │
│ send_message_service.py      │
└──────────┬───────────────────┘
     │ 6) WhatsApp API
     ▼
┌──────────────────────┐
│       USUARIO        │
│ recibe respuesta     │
└──────────────────────┘


Persistencia y artefactos de IA (cross-cutting):

  database/database.py + database/models.py
    ▲
    │ (estado usuario, carrito, pedidos, productos)
    │
  services/user_state_service.py + services/menu_service.py

  data/intents.jsonl + notebooks/* + models/intent_classifier/
    ▲
    │ (entrenamiento offline spaCy y modelo desplegado)
    │
  services/intent_classifier.py
```

Flujo resumido:

1. Usuario escribe en WhatsApp.
2. Meta envía webhook a FastAPI.
3. Se procesa el mensaje y se consulta IA/estado.
4. Se decide acción: parser de pedido, respuesta por intent o fallback Gemini.
5. Se envía la respuesta por WhatsApp y se actualiza estado/pedido en base de datos.

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
WEBHOOK_VERIFY_TOKEN=tu_token_de_verificacion
API_TOKEN=tu_token_de_whatsapp
BUSINESS_PHONE=tu_phone_number_id
API_VERSION=version_api_whatsapp
BASE_URL=webhook_url_base
DATABASE_URL=path_database
GEMINI_API_KEY=token_de_gemini_fallback
GEMINI_MODEL=modelo_gemini_fallback
GEMINI_CONFIDENCE_THRESHOLD=umbral_confianza
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

Ver todos los 25 intents en `data/responses.json`.

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

<p align="center">
  Hecho con ❤️ para Los Motes de la Magdalena 🌮
</p>
