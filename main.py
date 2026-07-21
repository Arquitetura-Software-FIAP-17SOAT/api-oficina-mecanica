from fastapi import FastAPI

from infrastructure.database.database import create_tables
from presentation.api.routes.users import router as users_router

app = FastAPI(
    title="API Oficina Mecânica",
    version="1.0.0",
)

create_tables()

app.include_router(users_router)


@app.get("/health")
def health():
    return {"status": "UP"}