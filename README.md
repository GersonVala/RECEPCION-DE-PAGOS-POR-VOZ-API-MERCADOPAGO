# HolaGranja - Notificador de Pagos Mercado Pago

Sistema que detecta pagos entrantes de Mercado Pago en tiempo real, los registra en una base de datos local y anuncia cada pago por voz.

## Requisitos

- Python 3.8 o superior
- Cuenta de Mercado Pago con Access Token
- ngrok (para exponer el servidor a internet)

## Instalacion

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Copiar el archivo de ejemplo y completar con tu token:

```bash
copy .env.example .env
```

Editar `.env` y reemplazar `TU_ACCESS_TOKEN_AQUI` con tu Access Token real.

### 3. Obtener el Access Token de Mercado Pago

1. Ir a https://www.mercadopago.com.ar/developers/panel/app
2. Crear una aplicacion (o seleccionar una existente)
3. Ir a "Credenciales de produccion"
4. Copiar el **Access Token**

## Uso

### 1. Iniciar el servidor

```bash
python app.py
```

El servidor se iniciara en `http://localhost:5000`.

### 2. Exponer tunnel (puede ser grok para pruebas)

En otra terminal:

```bash
ngrok http 5000
```

Ngrok mostrara una URL publica como `https://xxxx-xx-xx.ngrok-free.app`.

### 3. Configurar webhook en Mercado Pago

1. Ir a https://www.mercadopago.com.ar/developers/panel/app
2. Seleccionar tu aplicacion
3. Ir a "Webhooks" o "Notificaciones IPN"
4. Configurar la URL: `https://TU-URL-NGROK/webhook`
5. Seleccionar el evento: **Pagos (payment)**
6. Guardar

### 4. Ver pagos recibidos

Abrir en el navegador: `http://localhost:5000`

Desde ahi podes filtrar por nombre, fecha y monto.

## Estructura del proyecto

```
PROYECTO HOLAGRANJA/
├── app.py              # Servidor Flask (webhook + web)
├── config.py           # Configuracion
├── database.py         # Base de datos SQLite
├── tts.py              # Anuncio por voz
├── templates/
│   └── index.html      # Interfaz web
├── requirements.txt    # Dependencias
├── .env.example        # Variables de entorno (ejemplo)
├── .env                # Variables de entorno (tu config)
└── payments.db         # Base de datos (se crea automaticamente)
```

## API

### GET /api/pagos

Devuelve los pagos en formato JSON. Parametros opcionales:

- `nombre` - Filtrar por nombre del pagador
- `fecha_desde` - Fecha minima (YYYY-MM-DD)
- `fecha_hasta` - Fecha maxima (YYYY-MM-DD)
- `monto_min` - Monto minimo
- `monto_max` - Monto maximo

Ejemplo: `http://localhost:5000/api/pagos?nombre=Juan&monto_min=1000`
