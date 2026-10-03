import os
import sys

# Configure UTF-8 stdout for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app import create_app
from app.database import init_db, check_db_connection

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    # Check for CLI commands
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command in ("init-db", "initdb"):
            print("[INFO] Initializing database from schema.sql and seed_data.sql using .env credentials...")
            success, msg = init_db(seed=True)
            if success:
                print(f"[SUCCESS] {msg}")
            else:
                print(f"[ERROR] Could not initialize database: {msg}")
            sys.exit(0 if success else 1)

        elif command in ("check-db", "checkdb"):
            print("[INFO] Checking MySQL connectivity using .env credentials...")
            success, msg = check_db_connection()
            if success:
                print(f"[SUCCESS] {msg}")
            else:
                print(f"[ERROR] Could not connect: {msg}")
            sys.exit(0 if success else 1)

    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")
    debug = os.getenv("FLASK_DEBUG", "1") == "1"

    print(f"\n[AI-Powered PG & Room Finder] Server starting on http://{host}:{port}")
    print("[TIP] You can run 'python run.py init-db' anytime to initialize your database tables.\n")
    app.run(host=host, port=port, debug=debug)
