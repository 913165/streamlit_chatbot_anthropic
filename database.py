import sqlite3

DB_PATH = "skybook.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables and insert seed data if not already present."""
    conn = get_conn()
    cur  = conn.cursor()

    # Create tables one by one (avoid executescript issues)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(20)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS airlines (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            airline_id  INTEGER NOT NULL REFERENCES airlines(id),
            flight_no   VARCHAR(20) NOT NULL,
            origin      VARCHAR(100) NOT NULL,
            destination VARCHAR(100) NOT NULL,
            travel_date DATE NOT NULL,
            seat_class  VARCHAR(20)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            ref          VARCHAR(20) UNIQUE NOT NULL,
            passenger_id INTEGER NOT NULL REFERENCES passengers(id),
            flight_id    INTEGER NOT NULL REFERENCES flights(id),
            price        NUMERIC(10,2) NOT NULL,
            status       VARCHAR(20) DEFAULT 'pending'
        )
    """)

    conn.commit()

    # Seed only if empty
    cur.execute("SELECT COUNT(*) AS cnt FROM airlines")
    if cur.fetchone()["cnt"] == 0:
        cur.executemany("INSERT INTO airlines (name) VALUES (?)", [
            ("Philippine Airlines",),
            ("Cebu Pacific",),
            ("AirAsia",),
        ])

        cur.executemany("INSERT INTO passengers (name, email, phone) VALUES (?,?,?)", [
            ("Maria Santos",   "maria@email.com",  "09171234567"),
            ("Jose Reyes",     "jose@email.com",   "09181234567"),
            ("Ana Gonzales",   "ana@email.com",    "09191234567"),
            ("Carlos Mendoza", "carlos@email.com", "09201234567"),
            ("Luz Villanueva", "luz@email.com",    "09211234567"),
        ])

        cur.executemany(
            "INSERT INTO flights (airline_id, flight_no, origin, destination, travel_date, seat_class) VALUES (?,?,?,?,?,?)", [
            (1, "PR-101", "Metro Manila", "Bacolod",      "2026-04-12", "Economy"),
            (2, "5J-471", "Metro Manila", "Bacolod",      "2026-04-12", "Economy"),
            (3, "Z2-304", "Bacolod",      "Pampanga",     "2026-04-13", "Economy"),
            (1, "PR-103", "Bacolod",      "Metro Manila", "2026-04-19", "Economy"),
            (2, "Z2-205", "Pampanga",     "Bacolod",      "2026-04-20", "Economy"),
        ])

        cur.executemany(
            "INSERT INTO bookings (ref, passenger_id, flight_id, price, status) VALUES (?,?,?,?,?)", [
            ("SB-10021", 1, 1, 4800.00, "confirmed"),
            ("SB-10022", 2, 2, 7200.00, "confirmed"),
            ("SB-10023", 3, 3, 3800.00, "pending"),
            ("SB-10024", 4, 4, 9500.00, "cancelled"),
            ("SB-10025", 5, 5, 2500.00, "pending"),
        ])

        conn.commit()

    conn.close()


def debug_schema():
    conn = get_conn()
    for table in ["passengers", "airlines", "flights", "bookings"]:
        cur = conn.execute(f"PRAGMA table_info({table})")
        cols = [row["name"] for row in cur.fetchall()]
        print(f"{table}: {cols}")
    conn.close()


# ── READ ──────────────────────────────────────────────────────
def get_all_bookings():
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            b.id,
            b.ref,
            p.name        AS pname,
            p.email       AS email,
            p.phone       AS phone,
            f.flight_no   AS flight,
            a.name        AS airline,
            f.origin      AS origin,
            f.destination AS destination,
            f.travel_date AS travel_date,
            f.seat_class  AS cls,
            b.price,
            b.status
        FROM bookings b
        JOIN passengers p ON p.id = b.passenger_id
        JOIN flights    f ON f.id = b.flight_id
        JOIN airlines   a ON a.id = f.airline_id
        ORDER BY b.id DESC
    """).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["name"] = d.pop("pname")
        d["from"] = d.pop("origin")
        d["to"]   = d.pop("destination")
        d["date"] = d.pop("travel_date")
        result.append(d)
    return result


def get_airlines():
    conn = get_conn()
    rows = conn.execute("SELECT id, name FROM airlines ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_flights():
    conn = get_conn()
    rows = conn.execute("""
        SELECT f.id, f.flight_no, f.origin, f.destination,
               f.travel_date, f.seat_class AS cls, a.name AS airline
        FROM flights f JOIN airlines a ON a.id = f.airline_id
        ORDER BY f.travel_date
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── CREATE ────────────────────────────────────────────────────
def add_booking(name, email, phone, flight_no, airline_name,
                origin, destination, travel_date, cls, price, status):
    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("SELECT id FROM passengers WHERE email=?", (email,))
    row = cur.fetchone()
    if row:
        passenger_id = row["id"]
        cur.execute("UPDATE passengers SET name=?, phone=? WHERE id=?", (name, phone, passenger_id))
    else:
        cur.execute("INSERT INTO passengers (name, email, phone) VALUES (?,?,?)", (name, email, phone))
        passenger_id = cur.lastrowid

    cur.execute("SELECT id FROM airlines WHERE name=?", (airline_name,))
    row = cur.fetchone()
    if row:
        airline_id = row["id"]
    else:
        cur.execute("INSERT INTO airlines (name) VALUES (?)", (airline_name,))
        airline_id = cur.lastrowid

    cur.execute(
        "INSERT INTO flights (airline_id, flight_no, origin, destination, travel_date, seat_class) VALUES (?,?,?,?,?,?)",
        (airline_id, flight_no, origin, destination, travel_date, cls)
    )
    flight_id = cur.lastrowid

    cur.execute("SELECT COUNT(*) AS cnt FROM bookings")
    cnt = cur.fetchone()["cnt"]
    ref = f"SB-{10021 + cnt}"

    cur.execute(
        "INSERT INTO bookings (ref, passenger_id, flight_id, price, status) VALUES (?,?,?,?,?)",
        (ref, passenger_id, flight_id, price, status)
    )
    conn.commit()
    conn.close()


# ── UPDATE ────────────────────────────────────────────────────
def update_booking(booking_id, name, email, phone, flight_no, airline_name,
                   origin, destination, travel_date, cls, price, status):
    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("SELECT passenger_id, flight_id FROM bookings WHERE id=?", (booking_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return

    passenger_id = row["passenger_id"]
    flight_id    = row["flight_id"]

    cur.execute("UPDATE passengers SET name=?, email=?, phone=? WHERE id=?",
                (name, email, phone, passenger_id))

    cur.execute("SELECT id FROM airlines WHERE name=?", (airline_name,))
    arow = cur.fetchone()
    if arow:
        airline_id = arow["id"]
    else:
        cur.execute("INSERT INTO airlines (name) VALUES (?)", (airline_name,))
        airline_id = cur.lastrowid

    cur.execute("""
        UPDATE flights
        SET airline_id=?, flight_no=?, origin=?, destination=?, travel_date=?, seat_class=?
        WHERE id=?
    """, (airline_id, flight_no, origin, destination, travel_date, cls, flight_id))

    cur.execute("UPDATE bookings SET price=?, status=? WHERE id=?",
                (price, status, booking_id))

    conn.commit()
    conn.close()


def update_booking_status(ref: str, new_status: str):
    conn = get_conn()
    conn.execute("UPDATE bookings SET status=? WHERE ref=?", (new_status, ref))
    conn.commit()
    conn.close()


# ── DELETE ────────────────────────────────────────────────────
def delete_booking(booking_id: int = None, ref: str = None):
    conn = get_conn()
    if booking_id:
        conn.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
    elif ref:
        conn.execute("DELETE FROM bookings WHERE ref=?", (ref,))
    conn.commit()
    conn.close()