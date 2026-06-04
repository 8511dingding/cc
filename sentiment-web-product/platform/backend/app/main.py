from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import DashboardResponse, DataRecord, RecordPatchRequest
from app.store import dashboard, patch_record


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "PATCH", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(f"{settings.api_prefix}/dashboard", response_model=DashboardResponse)
    async def get_dashboard() -> DashboardResponse:
        return dashboard()

    @app.patch(f"{settings.api_prefix}/records/{{record_id}}", response_model=DataRecord)
    async def update_record(record_id: str, payload: RecordPatchRequest) -> DataRecord:
        try:
            updated = patch_record(
                record_id,
                [item.model_dump() for item in payload.updates],
                payload.edited_by,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if updated is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return updated

    return app


app = create_app()
