import app
import os
print(f"APP PATH: {os.path.abspath(app.__file__)}")
from app.main import app as fastapi_app
print(f"ROUTES: {[r.path for r in fastapi_app.routes]}")
