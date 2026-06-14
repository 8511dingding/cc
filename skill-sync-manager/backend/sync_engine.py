#!/usr/bin/env python3
import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class SkillInfo:
    name: str
    path: str
    size: int
    modified_time: float
    files_count: int
    has_skill_md: bool

@dataclass
class SyncResult:
    source: str
    target: str
    added: List[str]
    updated: List[str]
    removed: List[str]
    skipped: List[str]
    errors: List[str]
    timestamp: str
    success: bool

class SkillSyncEngine:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "sync_config.json"
        )
        self.config = self._load_config()
        self._setup_logging()
        
    def _load_config(self) -> Dict:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _setup_logging(self):
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "logs"
        )
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"sync_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=getattr(logging, self.config.get('logging', {}).get('level', 'INFO')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_skill_dirs(self) -> Dict[str, str]:
        return self.config.get('skill_dirs', {})
    
    def list_skills(self, app_name: str) -> List[SkillInfo]:
        skill_dirs = self.get_skill_dirs()
        if app_name not in skill_dirs:
            raise ValueError(f"Unknown app: {app_name}")
        
        base_path = Path(skill_dirs[app_name])
        if not base_path.exists():
            return []
        
        exclude_dirs = self.config.get('exclude_dirs', ['.system', '.git'])
        skills = []
        
        for item in base_path.iterdir():
            if item.is_dir() and item.name not in exclude_dirs:
                skill_info = self._get_skill_info(item)
                if skill_info:
                    skills.append(skill_info)
        
        return sorted(skills, key=lambda s: s.name)
    
    def _get_skill_info(self, skill_path: Path) -> Optional[SkillInfo]:
        try:
            size = 0
            files_count = 0
            has_skill_md = False
            
            for root, dirs, files in os.walk(skill_path):
                for f in files:
                    file_path = Path(root) / f
                    size += file_path.stat().st_size
                    files_count += 1
                    if f == 'SKILL.md':
                        has_skill_md = True
            
            return SkillInfo(
                name=skill_path.name,
                path=str(skill_path),
                size=size,
                modified_time=skill_path.stat().st_mtime,
                files_count=files_count,
                has_skill_md=has_skill_md
            )
        except Exception as e:
            self.logger.warning(f"Failed to get skill info for {skill_path}: {e}")
            return None
    
    def get_all_skills_status(self) -> Dict[str, List[Dict]]:
        result = {}
        for app_name in self.get_skill_dirs().keys():
            skills = self.list_skills(app_name)
            result[app_name] = [asdict(skill) for skill in skills]
        return result
    
    def _create_backup(self, target_path: Path) -> Optional[str]:
        if not self.config.get('scheduler', {}).get('auto_backup', True):
            return None
        
        try:
            backup_dir = target_path.parent / f"{target_path.name}.backup"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{target_path.name}_{timestamp}"
            
            if target_path.exists():
                shutil.copytree(target_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
                
                max_backups = self.config.get('scheduler', {}).get('max_backups', 7)
                backups = sorted(backup_dir.iterdir(), key=lambda p: p.stat().st_mtime)
                while len(backups) > max_backups:
                    old_backup = backups.pop(0)
                    shutil.rmtree(old_backup)
                    self.logger.info(f"Removed old backup: {old_backup}")
            
            return str(backup_path)
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
    
    def sync_skills(
        self,
        source: str,
        target: str,
        skill_names: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> SyncResult:
        result = SyncResult(
            source=source,
            target=target,
            added=[],
            updated=[],
            removed=[],
            skipped=[],
            errors=[],
            timestamp=datetime.now().isoformat(),
            success=False
        )
        
        try:
            skill_dirs = self.get_skill_dirs()
            if source not in skill_dirs or target not in skill_dirs:
                raise ValueError(f"Invalid source/target: {source} -> {target}")
            
            source_path = Path(skill_dirs[source])
            target_path = Path(skill_dirs[target])
            
            if not source_path.exists():
                raise ValueError(f"Source directory does not exist: {source_path}")
            
            target_path.mkdir(parents=True, exist_ok=True)
            
            if not dry_run:
                self._create_backup(target_path)
            
            source_skills = {s.name: s for s in self.list_skills(source)}
            target_skills = {s.name: s for s in self.list_skills(target)}
            
            if skill_names:
                source_skills = {k: v for k, v in source_skills.items() if k in skill_names}
            
            exclude_dirs = self.config.get('exclude_dirs', ['.system', '.git'])
            strategy = self.config.get('sync_strategy', 'merge')
            
            for skill_name, skill_info in source_skills.items():
                if skill_name in exclude_dirs:
                    result.skipped.append(f"{skill_name} (excluded)")
                    continue
                
                src_skill_path = source_path / skill_name
                tgt_skill_path = target_path / skill_name
                
                try:
                    if skill_name not in target_skills:
                        if dry_run:
                            result.added.append(f"{skill_name} (new)")
                        else:
                            shutil.copytree(src_skill_path, tgt_skill_path)
                            result.added.append(skill_name)
                            self.logger.info(f"Added skill: {skill_name}")
                    else:
                        src_hash = self._hash_skill(src_skill_path)
                        tgt_hash = self._hash_skill(tgt_skill_path)
                        
                        if src_hash != tgt_hash:
                            if dry_run:
                                result.updated.append(f"{skill_name} (needs update)")
                            else:
                                shutil.rmtree(tgt_skill_path)
                                shutil.copytree(src_skill_path, tgt_skill_path)
                                result.updated.append(skill_name)
                                self.logger.info(f"Updated skill: {skill_name}")
                        else:
                            result.skipped.append(f"{skill_name} (up to date)")
                except Exception as e:
                    result.errors.append(f"{skill_name}: {str(e)}")
                    self.logger.error(f"Error syncing skill {skill_name}: {e}")
            
            if strategy == 'mirror' and not dry_run:
                for skill_name in target_skills:
                    if skill_name not in source_skills and skill_name not in exclude_dirs:
                        try:
                            tgt_skill_path = target_path / skill_name
                            shutil.rmtree(tgt_skill_path)
                            result.removed.append(skill_name)
                            self.logger.info(f"Removed skill: {skill_name}")
                        except Exception as e:
                            result.errors.append(f"Remove {skill_name}: {str(e)}")
            
            result.success = len(result.errors) == 0
            
        except Exception as e:
            result.errors.append(f"Fatal error: {str(e)}")
            self.logger.error(f"Sync failed: {e}")
        
        return result
    
    def sync_all(
        self,
        source: Optional[str] = None,
        targets: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, SyncResult]:
        source = source or self.config.get('default_source', 'claude')
        targets = targets or self.config.get('default_targets', ['trae', 'codex'])
        
        results = {}
        for target in targets:
            if target != source:
                results[target] = self.sync_skills(source, target, dry_run=dry_run)
        
        return results
    
    def _hash_skill(self, skill_path: Path) -> str:
        hasher = hashlib.sha256()
        for root, dirs, files in os.walk(skill_path):
            for f in sorted(files):
                file_path = Path(root) / f
                hasher.update(file_path.name.encode())
                with open(file_path, 'rb') as fp:
                    for chunk in iter(lambda: fp.read(8192), b''):
                        hasher.update(chunk)
        return hasher.hexdigest()
    
    def backup_to_central(self, dry_run: bool = False) -> SyncResult:
        results = self.sync_all(
            source='central',
            targets=['trae', 'claude', 'codex'],
            dry_run=dry_run
        )
        return results
    
    def restore_from_central(self, dry_run: bool = False) -> Dict[str, SyncResult]:
        return self.sync_all(
            source='central',
            targets=['trae', 'claude', 'codex'],
            dry_run=dry_run
        )
