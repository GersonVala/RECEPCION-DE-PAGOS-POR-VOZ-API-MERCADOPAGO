import os
from dotenv import load_dotenv

load_dotenv()

MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "payments.db")
