import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "hvac_booking.db")

def init_db():
    """Initializes the SQLite database with the required schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        price_base REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS available_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        is_booked INTEGER DEFAULT 0,
        service_type TEXT -- Optional: if slots are restricted to types
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        slot_id INTEGER,
        service_name TEXT,
        issue_description TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (slot_id) REFERENCES available_slots (id)
    )
    """)

    # Seed initial data if empty
    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        services = [
            ('AC Repair', 'Fixing cooling issues', 150.0),
            ('Furnace Maintenance', 'Annual heating checkup', 120.0),
            ('Installation', 'New system setup', 500.0),
            ('Duct Cleaning', 'Cleaning air ducts', 200.0)
        ]
        cursor.executemany("INSERT INTO services (name, description, price_base) VALUES (?, ?, ?)", services)

    # Seed some slots for the next few days
    cursor.execute("SELECT COUNT(*) FROM available_slots")
    if cursor.fetchone()[0] == 0:
        import datetime
        today = datetime.date.today()
        slots = []
        for i in range(1, 8):  # Next 7 days
            day = today + datetime.timedelta(days=i)
            # Morning slot
            slots.append((f"{day} 09:00", f"{day} 12:00"))
            # Afternoon slot
            slots.append((f"{day} 13:00", f"{day} 16:00"))
        cursor.executemany("INSERT INTO available_slots (start_time, end_time) VALUES (?, ?)", slots)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    init_db()
