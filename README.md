# Recepción de Pagos por Voz — API Mercado Pago

Sistema en Python que detecta pagos recibidos a través de la API de Mercado Pago
y los anuncia por voz en el punto de venta, para comercios con alto tránsito
donde el operador no puede estar mirando la pantalla.

## Contexto del proyecto

Desarrollado para una ferretería con necesidad de confirmar pagos en tiempo real
sin depender de revisar el celular o la pantalla. Proyecto freelance — Febrero 2026.

## Características

- Detección de pagos en tiempo real mediante **Webhooks** de Mercado Pago (IPN y Webhook v2)
- **Polling** cada 60 segundos como mecanismo de respaldo ante fallas del webhook
- **Síntesis de voz** automática del estado de cada transacción (aprobada / rechazada) via `edge-tts`
- **Registro persistente** de operaciones en base de datos SQLite para trazabilidad
- **Dashboard web** con login, filtros por fecha y monto, y totales del día / mes / año
- **Exportación a Excel** (.xlsx) de ventas por día, mes o año
- Lógica para identificar correctamente al pagador real en transferencias (evita mostrar datos del cobrador)

## Stack técnico

- **Lenguaje:** Python 3.8+
- **Framework web:** Flask 3.1
- **Síntesis de voz:** edge-tts 7.2 (voz `es-AR-ElenaNeural`, requiere conexión a internet)
- **Base de datos:** SQLite (via módulo estándar `sqlite3`)
- **Exportación:** openpyxl 3.1
- **Configuración:** python-dotenv
- **API externa:** Mercado Pago REST API v1
- **Despliegue:** Windows + Cloudflare Tunnel (para recibir webhooks sin IP pública)

## Arquitectura (flujo)

\`\`\`
Mercado Pago
    │
    ├─ Webhook POST /webhook  ──► valida topic → fetch detalles → SQLite → TTS
    │
    └─ Polling (hilo daemon)  ──► cada 60s consulta /v1/payments/search → mismo flujo
\`\`\`

1. Mercado Pago notifica un pago vía Webhook al endpoint \`/webhook\`
2. El servidor responde \`200 OK\` inmediatamente y delega el procesamiento a un hilo aparte
3. Se consulta el detalle completo del pago en la API de Mercado Pago
4. Se registra la operación en SQLite (deduplicado por \`mp_payment_id\`)
5. Se encola el anuncio de voz (nombre del pagador + monto)
6. Un hilo de polling corre en paralelo como respaldo

## Instalación y uso

### Requisitos

- Python 3.8+
- Cuenta de Mercado Pago con Access Token de producción
- Windows (la reproducción de audio usa Windows Media Player vía PowerShell)
- Cloudflare Tunnel u otro método para exponer el puerto 5000 a internet (necesario para recibir webhooks)

### Pasos

\`\`\`bash
git clone https://github.com/GersonVala/RECEPCION-DE-PAGOS-POR-VOZ-API-MERCADOPAGO.git
cd RECEPCION-DE-PAGOS-POR-VOZ-API-MERCADOPAGO
pip install -r requirements.txt
\`\`\`

### Configuración

Copiar \`.env.example\` a \`.env\` y completar las variables:

\`\`\`bash
cp .env.example .env
\`\`\`

\`\`\`env
MP_ACCESS_TOKEN=tu_access_token_de_mercado_pago
FLASK_PORT=5000
FLASK_SECRET_KEY=una_clave_secreta_larga_y_aleatoria
DASHBOARD_PASSWORD=tu_contraseña_del_dashboard
\`\`\`

### Ejecución

\`\`\`bash
python app.py
\`\`\`

O usar el script incluido en Windows:

\`\`\`
iniciar_server.bat
\`\`\`

El servidor queda escuchando en \`http://localhost:5000\`. Para recibir webhooks desde Mercado Pago,
el puerto debe ser accesible desde internet (Cloudflare Tunnel, ngrok, etc.).

Configurar la URL del webhook en el panel de Mercado Pago:
\`https://tu-dominio/webhook\`

## Estructura del proyecto

\`\`\`
├── app.py              # Servidor Flask: webhook, polling, dashboard, exportación
├── config.py           # Carga de variables de entorno
├── database.py         # Capa de acceso a SQLite (init, insert, queries)
├── tts.py              # Síntesis de voz con edge-tts (cola thread-safe)
├── templates/
│   ├── index.html      # Dashboard de pagos con filtros
│   └── login.html      # Pantalla de login
├── requirements.txt
├── .env.example        # Variables de entorno requeridas (sin valores)
├── iniciar_server.bat  # Script de inicio para Windows
└── instalar.bat        # Script de instalación para Windows
\`\`\`

## Limitaciones conocidas

- **Solo Windows:** la reproducción de audio usa Windows Media Player vía PowerShell; no corre en Linux/Mac sin modificar \`tts.py\`
- **Sin tests:** no hay cobertura de pruebas automatizadas
- **Sin Docker:** requiere instalación manual de Python y dependencias
- **Dashboard sin HTTPS propio:** depende de Cloudflare Tunnel para TLS en producción
- **Credenciales hardcodeadas (pendiente):** \`FLASK_SECRET_KEY\` y \`DASHBOARD_PASSWORD\` están en \`app.py\`; deben moverse a \`.env\`

## Autor

Gerson Valashek — Estudiante de Informática (UTN)
LinkedIn: https://www.linkedin.com/in/gersonvalashek
