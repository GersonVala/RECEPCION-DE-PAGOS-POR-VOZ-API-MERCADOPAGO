import asyncio
import queue
import tempfile
import threading

import edge_tts

# Cola de mensajes y worker unico para evitar conflictos entre hilos
_message_queue = queue.Queue()
_worker_started = False
_worker_lock = threading.Lock()

# Voz argentina femenina (alternativa masculina: "es-AR-TomasNeural")
VOICE = "es-AR-ElenaNeural"


def _tts_worker():
    """Worker que consume la cola y reproduce mensajes uno por uno."""
    loop = asyncio.new_event_loop()

    while True:
        message = _message_queue.get()
        try:
            # Generar audio con edge-tts
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name

            loop.run_until_complete(
                edge_tts.Communicate(message, VOICE, rate="-10%").save(tmp_path)
            )

            # Reproducir con el reproductor nativo de Windows
            import winsound
            import subprocess
            # winsound no soporta mp3, usamos Windows Media Player silencioso
            subprocess.run(
                ["powershell", "-WindowStyle", "Hidden", "-Command",
                 f'(New-Object Media.SoundPlayer).Stop(); '
                 f'Add-Type -AssemblyName presentationCore; '
                 f'$player = New-Object System.Windows.Media.MediaPlayer; '
                 f'$player.Open([Uri]"{tmp_path}"); '
                 f'$player.Play(); '
                 f'Start-Sleep -Milliseconds 500; '
                 f'while ($player.Position -lt $player.NaturalDuration.TimeSpan) {{ Start-Sleep -Milliseconds 200 }}; '
                 f'$player.Close()'],
                capture_output=True, timeout=30
            )

            import os
            os.unlink(tmp_path)

        except Exception as e:
            print(f"[TTS Error] {e}")
        finally:
            _message_queue.task_done()


def _ensure_worker():
    """Inicia el worker si no esta corriendo."""
    global _worker_started
    if _worker_started:
        return
    with _worker_lock:
        if _worker_started:
            return
        t = threading.Thread(target=_tts_worker, daemon=True)
        t.start()
        _worker_started = True


def announce_payment(name, amount, rejected=False):
    """Encola un anuncio de pago. Se reproducen en orden, uno a la vez."""
    if amount == int(amount):
        amount_str = f"{int(amount):,}".replace(",", ".")
    else:
        amount_str = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    if rejected:
        if name:
            message = f"Atención. Se rechazó un pago de {name} por {amount_str} pesos"
        else:
            message = f"Atención. Se rechazó un pago por {amount_str} pesos"
    else:
        if name:
            message = f"Se recibió una transferencia de {name} por {amount_str} pesos"
        else:
            message = f"Se recibió una transferencia por {amount_str} pesos"

    _ensure_worker()
    _message_queue.put(message)
