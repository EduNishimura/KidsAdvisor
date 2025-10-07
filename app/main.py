from fastapi import FastAPI
from app.routers import users, events, participations, categories
from app.database import client

app = FastAPI(title="KidsAdvisor API")

app.include_router(users.router, prefix="/usuarios", tags=["usuarios"])
app.include_router(events.router, prefix="/eventos", tags=["eventos"])
app.include_router(participations.router, prefix="/eventos",
                   tags=["participações"])
app.include_router(categories.router, prefix="/categories",
                   tags=["categorias"])


@app.on_event("shutdown")
def shutdown_db_client():
    client.close()
