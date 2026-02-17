import queue
import threading
import pyttsx3

# Cola de mensajes y worker unico para evitar conflictos entre hilos
_message_queue = queue.Queue()
_worker_started = False
_worker_lock = threading.Lock()


def _tts_worker():
    """Worker que consume la cola y reproduce mensajes uno por uno."""
    engine = pyttsx3.init()
    engine.setProperty("rate", 120)

    while True:
        message = _message_queue.get()
        try:
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print(f"[TTS Error] {e}")
            # Reiniciar engine si falla
            try:
                engine.stop()
                engine = pyttsx3.init()
                engine.setProperty("rate", 120)
            except Exception:
                pass
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
