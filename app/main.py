# --------------------
# File: app/main.py
# --------------------
from fastapi import FastAPI
from app.routers import users
from app.database import client

app = FastAPI(title="KidsAdvisor API")
app.include_router(users.router, prefix="/usuarios", tags=["usuarios"])


@app.on_event("shutdown")
def shutdown_db_client():
    client.close()
