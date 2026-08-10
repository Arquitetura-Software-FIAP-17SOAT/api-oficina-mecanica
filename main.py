from fastapi import FastAPI

from infrastructure.database.database import create_tables
from presentation.api.routes.clientes import router as clientes_router
from presentation.api.routes.insumos import router as insumos_router
from presentation.api.routes.servicos import router as servicos_router
from presentation.api.routes.users import router as users_router
from presentation.api.routes.ordens_servico import router as ordens_servico_router
from presentation.api.routes.veiculos import router as veiculos_router

app = FastAPI(
    title="API Oficina Mecânica",
    version="1.0.0",
)

create_tables()

app.include_router(users_router)
app.include_router(ordens_servico_router)
app.include_router(insumos_router)
app.include_router(servicos_router)
app.include_router(clientes_router)
app.include_router(veiculos_router)


@app.get("/health")
def health():
    return {"status": "UP"}