from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.importer import build_import_preview
from app.schemas import (
    DashboardResponse,
    DataRecord,
    ImportPreviewResponse,
    ProjectSummary,
    ProjectUpsertRequest,
    RecordBrandsPatchRequest,
    RecordPatchRequest,
    RecordReportPatchRequest,
)
from app.store import create_project, dashboard, delete_project, patch_brands, patch_record, patch_report_candidate, update_project


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["DELETE", "GET", "PATCH", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(f"{settings.api_prefix}/dashboard", response_model=DashboardResponse)
    async def get_dashboard(project_id: str | None = Query(default=None)) -> DashboardResponse:
        return dashboard(project_id)

    @app.post(f"{settings.api_prefix}/projects", response_model=ProjectSummary)
    async def add_project(payload: ProjectUpsertRequest) -> ProjectSummary:
        try:
            return create_project(payload)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.patch(f"{settings.api_prefix}/projects/{{project_id}}", response_model=ProjectSummary)
    async def edit_project(project_id: str, payload: ProjectUpsertRequest) -> ProjectSummary:
        try:
            updated = update_project(project_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if updated is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return updated

    @app.delete(f"{settings.api_prefix}/projects/{{project_id}}")
    async def remove_project(project_id: str) -> dict[str, bool]:
        try:
            deleted = delete_project(project_id)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"deleted": True}

    @app.post(f"{settings.api_prefix}/imports/preview", response_model=ImportPreviewResponse)
    async def preview_import(file: UploadFile = File(...)) -> ImportPreviewResponse:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=422, detail="上传文件为空")
        if len(content) > 80 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="文件过大，单次预览建议不超过 80MB")
        try:
            return build_import_preview(file.filename or "upload.xlsx", content)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

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

    @app.patch(f"{settings.api_prefix}/records/{{record_id}}/report-candidate", response_model=DataRecord)
    async def update_report_candidate(record_id: str, payload: RecordReportPatchRequest) -> DataRecord:
        try:
            updated = patch_report_candidate(record_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if updated is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return updated

    @app.patch(f"{settings.api_prefix}/records/{{record_id}}/brands", response_model=DataRecord)
    async def update_brands(record_id: str, payload: RecordBrandsPatchRequest) -> DataRecord:
        try:
            updated = patch_brands(record_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if updated is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return updated

    return app


app = create_app()
