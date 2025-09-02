from fastapi import FastAPI
from app.routes import users, activities, feedback, recommend

app = FastAPI(title="KidsAdvisor API (MVP)", version="0.1.0")

# registrando rotas
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(activities.router, prefix="/activities",
                   tags=["activities"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(recommend.router, prefix="/recommend", tags=["recommend"])


@app.get("/health")
def health():
    return {"status": "ok"}
