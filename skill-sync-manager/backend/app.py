#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import json
from datetime import datetime

backend_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(backend_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sync_engine import SkillSyncEngine, SyncResult

app = FastAPI(
    title="Skill Sync Manager",
    description="管理 Trae、Claude Code 和 Codex 之间的技能同步",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SkillSyncEngine()

frontend_dir = os.path.join(project_dir, "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

class SyncRequest(BaseModel):
    source: str
    target: str
    skill_names: Optional[List[str]] = None
    dry_run: bool = False

class SyncAllRequest(BaseModel):
    source: Optional[str] = None
    targets: Optional[List[str]] = None
    dry_run: bool = False

class ScheduleConfig(BaseModel):
    enabled: bool = True
    interval_hours: int = 24
    auto_backup: bool = True
    max_backups: int = 7

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/api/status")
async def get_status():
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "skill_dirs": engine.get_skill_dirs()
    }

@app.get("/api/skills")
async def get_skills(app: Optional[str] = None):
    try:
        if app:
            skills = engine.list_skills(app)
            return {
                "app": app,
                "count": len(skills),
                "skills": [s.__dict__ for s in skills]
            }
        else:
            return engine.get_all_skills_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skills/compare")
async def compare_skills():
    try:
        all_skills = engine.get_all_skills_status()
        comparison = {}
        
        for app_name, skills in all_skills.items():
            comparison[app_name] = {
                "count": len(skills),
                "skill_names": [s["name"] for s in skills]
            }
        
        all_names = set()
        for app_data in comparison.values():
            all_names.update(app_data["skill_names"])
        
        sync_status = {}
        for name in sorted(all_names):
            present_in = []
            for app_name, app_data in comparison.items():
                if name in app_data["skill_names"]:
                    present_in.append(app_name)
            sync_status[name] = {
                "present_in": present_in,
                "is_synced": len(present_in) == len(comparison)
            }
        
        return {
            "comparison": comparison,
            "sync_status": sync_status,
            "summary": {
                "total_unique_skills": len(all_names),
                "fully_synced": sum(1 for s in sync_status.values() if s["is_synced"]),
                "needs_sync": sum(1 for s in sync_status.values() if not s["is_synced"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync")
async def sync_skills(request: SyncRequest):
    try:
        result = engine.sync_skills(
            source=request.source,
            target=request.target,
            skill_names=request.skill_names,
            dry_run=request.dry_run
        )
        return result.__dict__
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync-all")
async def sync_all(request: SyncAllRequest):
    try:
        results = engine.sync_all(
            source=request.source,
            targets=request.targets,
            dry_run=request.dry_run
        )
        return {
            target: result.__dict__
            for target, result in results.items()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backup")
async def backup_to_central(dry_run: bool = False):
    try:
        result = engine.backup_to_central(dry_run=dry_run)
        return {"message": "Backup completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/restore")
async def restore_from_central(dry_run: bool = False):
    try:
        results = engine.restore_from_central(dry_run=dry_run)
        return {
            "message": "Restore completed",
            "results": {
                target: result.__dict__
                for target, result in results.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    return engine.config

@app.put("/api/config")
async def update_config(new_config: Dict[str, Any]):
    try:
        config_path = engine.config_path
        current_config = engine.config
        
        current_config.update(new_config)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=2, ensure_ascii=False)
        
        engine.config = current_config
        return {"message": "Config updated", "config": current_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def get_logs(limit: int = 100):
    try:
        log_dir = os.path.join(project_dir, "logs")
        if not os.path.exists(log_dir):
            return {"logs": []}
        
        log_files = sorted(
            [f for f in os.listdir(log_dir) if f.startswith("sync_") and f.endswith(".log")],
            reverse=True
        )
        
        if not log_files:
            return {"logs": []}
        
        latest_log = os.path.join(log_dir, log_files[0])
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return {
                "log_file": latest_log,
                "logs": lines[-limit:]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
