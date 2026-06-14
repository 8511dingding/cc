#!/usr/bin/env python3
import os
import sys
import time
import signal
import threading
from datetime import datetime, timedelta
from typing import Optional

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sync_engine import SkillSyncEngine

class SkillSyncScheduler:
    def __init__(self, config_path: str = None):
        self.engine = SkillSyncEngine(config_path)
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
    def _handle_signal(self, signum, frame):
        self.engine.logger.info(f"Received signal {signum}, stopping scheduler...")
        self.stop()
        
    def start(self):
        if self.running:
            self.engine.logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.engine.logger.info("Scheduler started")
        
    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        self.engine.logger.info("Scheduler stopped")
        
    def _run_loop(self):
        last_run: Optional[datetime] = None
        
        while self.running:
            try:
                config = self.engine.config
                scheduler_config = config.get('scheduler', {})
                
                if not scheduler_config.get('enabled', True):
                    time.sleep(60)
                    continue
                
                interval_hours = scheduler_config.get('interval_hours', 24)
                now = datetime.now()
                
                should_run = False
                if last_run is None:
                    should_run = True
                else:
                    next_run = last_run + timedelta(hours=interval_hours)
                    if now >= next_run:
                        should_run = True
                
                if should_run:
                    self.engine.logger.info(f"Starting scheduled sync at {now}")
                    self._do_scheduled_sync()
                    last_run = now
                    self.engine.logger.info(f"Scheduled sync completed, next run in {interval_hours} hours")
                
                time.sleep(60)
                
            except Exception as e:
                self.engine.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
                
    def _do_scheduled_sync(self):
        try:
            config = self.engine.config
            source = config.get('default_source', 'claude')
            targets = config.get('default_targets', ['trae', 'codex'])
            
            results = self.engine.sync_all(source=source, targets=targets, dry_run=False)
            
            for target, result in results.items():
                if result.success:
                    self.engine.logger.info(
                        f"Scheduled sync {source} -> {target} succeeded: "
                        f"added={len(result.added)}, updated={len(result.updated)}, "
                        f"skipped={len(result.skipped)}"
                    )
                else:
                    self.engine.logger.error(
                        f"Scheduled sync {source} -> {target} failed: {result.errors}"
                    )
                    
        except Exception as e:
            self.engine.logger.error(f"Error in scheduled sync: {e}")

if __name__ == "__main__":
    scheduler = SkillSyncScheduler()
    
    print("Skill Sync Scheduler")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    scheduler.start()
    
    try:
        while scheduler.running:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.stop()
