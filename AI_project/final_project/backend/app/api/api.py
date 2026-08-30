from fastapi import APIRouter
from app.api.endpoints import (
    projects,
    tasks,
    dependencies,
    metrics,
    risk,
    health,
    deadline,
    scenario,
    recommendations,
    ai_analytics,
    auth,
    documents,
    chat,
)

api_router = APIRouter()

# Attach endpoint routers
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(tasks.router, tags=["Tasks"])
api_router.include_router(dependencies.router, tags=["Dependencies"])
api_router.include_router(metrics.router, tags=["Metrics"])
api_router.include_router(risk.router, tags=["Risk Forecasting"])
api_router.include_router(health.router, tags=["Health Assessment"])
api_router.include_router(deadline.router, tags=["Deadline Analysis"])
api_router.include_router(scenario.router, tags=["What-If Scenario Simulation"])
api_router.include_router(recommendations.router, tags=["Preventive Recommendations"])
api_router.include_router(ai_analytics.router, tags=["AI Analytics API"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(chat.router, prefix="/chats", tags=["Chat History"])


