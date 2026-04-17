# Notificador de Pagos Mercado Pago

Sistema que detecta pagos entrantes de Mercado Pago en tiempo real, los registra en una base de datos local y anuncia cada pago por voz.

## Requisitos

- Python 3.8 o superior
- Cuenta de Mercado Pago con Access Token



### 3. Obtener el Access Token de Mercado Pago

1. Ir a https://www.mercadopago.com.ar/developers/panel/app
2. Crear una aplicacion (o seleccionar una existente)
3. Ir a "Credenciales de produccion"
4. Copiar el **Access Token**



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

