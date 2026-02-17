import sqlite3
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mp_payment_id TEXT UNIQUE,
            payer_name TEXT,
            payer_email TEXT,
            amount REAL,
            description TEXT,
            status TEXT,
            payment_type TEXT,
            bank TEXT,
            date_created TEXT,
            date_registered DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Agregar columnas si la tabla ya existia sin ellas
    for col, col_type in [("payment_type", "TEXT"), ("bank", "TEXT")]:
        try:
            conn.execute(f"ALTER TABLE payments ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()


def insert_payment(data):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO payments
            (mp_payment_id, payer_name, payer_email, amount, description, status, payment_type, bank, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(data["mp_payment_id"]),
            data.get("payer_name", "Desconocido"),
            data.get("payer_email", ""),
            data.get("amount", 0),
            data.get("description", ""),
            data.get("status", ""),
            data.get("payment_type", ""),
            data.get("bank", ""),
            data.get("date_created", ""),
        ))
        conn.commit()
        inserted = conn.total_changes > 0
    finally:
        conn.close()
    return inserted


def get_totals(dia=None, mes=None, anio=None):
    """Devuelve totales de pagos aprobados para dia, mes y año indicados."""
    conn = get_connection()
    params = []

    # Dia: comparar los primeros 10 caracteres (YYYY-MM-DD)
    if dia:
        dia_cond = "substr(date_created, 1, 10) = ?"
        params.append(dia)
    else:
        dia_cond = "substr(date_created, 1, 10) = date('now', 'localtime')"

    # Mes: comparar los primeros 7 caracteres (YYYY-MM)
    if mes:
        mes_cond = "substr(date_created, 1, 7) = ?"
        params.append(mes)
    else:
        mes_cond = "substr(date_created, 1, 7) = strftime('%Y-%m', 'now', 'localtime')"

    # Año: comparar los primeros 4 caracteres (YYYY)
    if anio:
        anio_cond = "substr(date_created, 1, 4) = ?"
        params.append(anio)
    else:
        anio_cond = "substr(date_created, 1, 4) = strftime('%Y', 'now', 'localtime')"

    row = conn.execute(f"""
        SELECT
            COALESCE(SUM(CASE WHEN {dia_cond} THEN amount END), 0) AS total_dia,
            COALESCE(SUM(CASE WHEN {mes_cond} THEN amount END), 0) AS total_mes,
            COALESCE(SUM(CASE WHEN {anio_cond} THEN amount END), 0) AS total_anio
        FROM payments
        WHERE status = 'approved'
    """, params).fetchone()
    conn.close()
    return {
        "total_dia": row["total_dia"],
        "total_mes": row["total_mes"],
        "total_anio": row["total_anio"],
    }


def get_payments_by_period(periodo, valor):
    """Devuelve pagos aprobados para un periodo (dia/mes/anio)."""
    conn = get_connection()
    if periodo == "dia":
        query = "SELECT * FROM payments WHERE status = 'approved' AND substr(date_created, 1, 10) = ? ORDER BY date_created DESC"
        params = [valor]
    elif periodo == "mes":
        query = "SELECT * FROM payments WHERE status = 'approved' AND substr(date_created, 1, 7) = ? ORDER BY date_created DESC"
        params = [valor]
    else:
        query = "SELECT * FROM payments WHERE status = 'approved' AND substr(date_created, 1, 4) = ? ORDER BY date_created DESC"
        params = [valor]
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_payments(date_from=None, date_to=None, amount_min=None, amount_max=None, page=1, per_page=15):
    where = " WHERE 1=1"
    params = []

    if date_from:
        where += " AND date_created >= ?"
        params.append(date_from)
    if date_to:
        where += " AND date_created <= ?"
        params.append(date_to + " 23:59:59")
    if amount_min:
        where += " AND amount >= ?"
        params.append(float(amount_min))
    if amount_max:
        where += " AND amount <= ?"
        params.append(float(amount_max))

    conn = get_connection()

    total = conn.execute(f"SELECT COUNT(*) FROM payments{where}", params).fetchone()[0]

    query = f"SELECT * FROM payments{where} ORDER BY date_created DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    rows = conn.execute(query, params).fetchall()
    conn.close()

    total_pages = max(1, (total + per_page - 1) // per_page)
    return [dict(row) for row in rows], total, total_pages
