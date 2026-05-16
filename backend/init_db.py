from app.db.session import engine
from app.db.base import Base
print(f"Engine: {engine}")
if engine:
    print(f"Engine URL: {engine.url}")
    print(f"Driver: {engine.url.drivername}")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")
else:
    print("Engine is None")
