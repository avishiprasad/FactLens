from app.db.database import Base, engine
from app.db import models


def init_database():
    Base.metadata.create_all(bind=engine)

    print("FactLens database initialized successfully.")


if __name__ == "__main__":
    init_database()