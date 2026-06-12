from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.importer import build_import_preview
from app.schemas import (
    DashboardResponse,
    DataRecord,
    ImportPreviewResponse,
    ImportUploadResponse,
    ProjectSummary,
    ProjectRulesPatchRequest,
    RuleImpactPreview,
    ProjectUpsertRequest,
    RecordBrandsPatchRequest,
    RecordPatchRequest,
    RecordReportPatchRequest,
)
from app.store import (
    apply_project_rules,
    create_project,
    dashboard,
    delete_import_job,
    delete_project,
    import_file_path,
    import_job,
    patch_brands,
    patch_record,
    patch_report_candidate,
    preview_project_rules,
    register_import_job,
    revalidate_import_job,
    update_project,
)


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

    @app.post(f"{settings.api_prefix}/projects/{{project_id}}/rules/preview", response_model=RuleImpactPreview)
    async def preview_rules(project_id: str, payload: ProjectRulesPatchRequest) -> RuleImpactPreview:
        try:
            preview = preview_project_rules(project_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if preview is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return preview

    @app.post(f"{settings.api_prefix}/projects/{{project_id}}/rules/apply", response_model=RuleImpactPreview)
    async def apply_rules(project_id: str, payload: ProjectRulesPatchRequest) -> RuleImpactPreview:
        try:
            preview = apply_project_rules(project_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if preview is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return preview

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

    @app.post(f"{settings.api_prefix}/projects/{{project_id}}/imports", response_model=ImportUploadResponse)
    async def upload_import(project_id: str, file: UploadFile = File(...)) -> ImportUploadResponse:
        content = await file.read()
        filename = file.filename or "upload.xlsx"
        if not content:
            raise HTTPException(status_code=422, detail="上传文件为空")
        if len(content) > 80 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="文件过大，单次导入建议不超过 80MB")
        try:
            preview = build_import_preview(filename, content)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        storage_dir = Path(settings.import_storage_dir) / project_id
        storage_dir.mkdir(parents=True, exist_ok=True)
        safe_name = _safe_upload_filename(filename)
        storage_path = storage_dir / f"{uuid4().hex}-{safe_name}"
        storage_path.write_bytes(content)
        try:
            job = register_import_job(
                project_id,
                preview,
                owner_id="u-001",
                file_size_label=_format_file_size(len(content)),
                storage_path=storage_path,
            )
        except ValueError as exc:
            storage_path.unlink(missing_ok=True)
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if job is None:
            storage_path.unlink(missing_ok=True)
            raise HTTPException(status_code=404, detail="Project not found")
        return ImportUploadResponse(job=job, preview=preview)

    @app.get(f"{settings.api_prefix}/projects/{{project_id}}/imports/{{import_id}}/download")
    async def download_import(project_id: str, import_id: str) -> FileResponse:
        job = import_job(project_id, import_id)
        path = import_file_path(import_id)
        if job is None or path is None:
            raise HTTPException(status_code=404, detail="Import file not found")
        return FileResponse(path, filename=job.filename, media_type="application/octet-stream")

    @app.delete(f"{settings.api_prefix}/projects/{{project_id}}/imports/{{import_id}}")
    async def remove_import(project_id: str, import_id: str) -> dict[str, bool]:
        deleted = delete_import_job(project_id, import_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Import file not found")
        return {"deleted": True}

    @app.post(f"{settings.api_prefix}/projects/{{project_id}}/imports/{{import_id}}/revalidate", response_model=ImportUploadResponse)
    async def revalidate_import(project_id: str, import_id: str) -> ImportUploadResponse:
        job = import_job(project_id, import_id)
        path = import_file_path(import_id)
        if job is None or path is None:
            raise HTTPException(status_code=404, detail="Import file not found")
        try:
            preview = build_import_preview(job.filename, path.read_bytes())
            updated = revalidate_import_job(project_id, import_id, preview)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if updated is None:
            raise HTTPException(status_code=404, detail="Import file not found")
        return ImportUploadResponse(job=updated, preview=preview)

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


def _safe_upload_filename(filename: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in ".-_()[] " else "_" for char in filename).strip()
    return cleaned or "upload.dat"


def _format_file_size(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"
