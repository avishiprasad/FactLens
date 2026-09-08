from app.db.database import Base, engine
from app.db import models


def reset_database():
    print("Resetting FactLens database...")
    print(f"Database: {engine.url}")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("FactLens database reset successfully.")


if __name__ == "__main__":
    reset_database()