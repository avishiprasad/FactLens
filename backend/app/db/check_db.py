from pathlib import Path
import sqlite3

from app.db.database import DATABASE_PATH


print("FactLens database:")
print(DATABASE_PATH)
print()

if not DATABASE_PATH.exists():
    print("Database does not exist yet.")
    raise SystemExit(0)


connection = sqlite3.connect(DATABASE_PATH)

tables = connection.execute(
    "SELECT name FROM sqlite_master "
    "WHERE type='table'"
).fetchall()

print("Tables:")

for table in tables:
    print("-", table[0])


print()

document_count = connection.execute(
    "SELECT COUNT(*) FROM documents"
).fetchone()[0]

fact_count = connection.execute(
    "SELECT COUNT(*) FROM facts"
).fetchone()[0]

relationship_count = connection.execute(
    "SELECT COUNT(*) FROM fact_relationships"
).fetchone()[0]


print("Documents:", document_count)
print("Facts:", fact_count)
print("Relationships:", relationship_count)


connection.close()
