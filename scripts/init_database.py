import sys
from pathlib import Path

# Safe UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from TextToSQL.core.database import DatabaseManager, seed_database
from TextToSQL.core.schema_manager import SchemaManager

def main():
    print("🌱 Initializing and seeding relational database...")
    db = DatabaseManager()
    seed_database(db)
    
    sm = SchemaManager(db)
    schema = sm.get_full_schema()
    
    print(f"✅ Database initialized successfully at: {db.db_path}")
    print(f"📊 Total tables: {len(schema['tables'])}")
    for t_name, t_data in schema["tables"].items():
        print(f"   - {t_name}: {t_data['row_count']} rows, {len(t_data['columns'])} columns")

if __name__ == "__main__":
    main()
