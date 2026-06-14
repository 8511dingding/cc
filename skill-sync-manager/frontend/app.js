const API_BASE = '';

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    refreshStatus();
    loadSkills();
    loadComparison();
    loadLogs();
    loadScheduleConfig();
    
    document.getElementById('app-filter').addEventListener('change', loadSkills);
});

function initTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
        });
    });
}

async function fetchAPI(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options
    });
    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }
    return response.json();
}

function showLoading(text = '处理中...') {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

async function refreshStatus() {
    try {
        const status = await fetchAPI('/api/status');
        
        document.getElementById('status-indicator').classList.add('running');
        document.getElementById('status-text').textContent = '运行中';
        document.getElementById('timestamp').textContent = new Date(status.timestamp).toLocaleString('zh-CN');
        
        const allSkills = await fetchAPI('/api/skills');
        
        const appStatusEl = document.getElementById('app-status');
        appStatusEl.innerHTML = '';
        
        const appNames = {
            trae: 'Trae',
            claude: 'Claude Code',
            codex: 'Codex',
            central: '中央仓库'
        };
        
        for (const [app, skills] of Object.entries(allSkills)) {
            const div = document.createElement('div');
            div.className = 'app-item';
            div.innerHTML = `
                <div class="app-name">${appNames[app] || app}</div>
                <div class="app-count">${skills.length} 个技能</div>
            `;
            appStatusEl.appendChild(div);
        }
    } catch (error) {
        console.error('Status refresh failed:', error);
        document.getElementById('status-text').textContent = '连接失败';
    }
}

async function loadComparison() {
    try {
        const comparison = await fetchAPI('/api/skills/compare');
        
        const statsEl = document.getElementById('sync-stats');
        statsEl.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">唯一技能总数</span>
                <span class="stat-value">${comparison.summary.total_unique_skills}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">已完全同步</span>
                <span class="stat-value positive">${comparison.summary.fully_synced}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">需要同步</span>
                <span class="stat-value warning">${comparison.summary.needs_sync}</span>
            </div>
        `;
        
        const unsyncedEl = document.getElementById('unsynced-skills');
        const unsynced = Object.entries(comparison.sync_status)
            .filter(([_, status]) => !status.is_synced);
        
        if (unsynced.length === 0) {
            unsyncedEl.innerHTML = '<p style="color: #22c55e; text-align: center; padding: 40px;">🎉 所有技能已完全同步！</p>';
        } else {
            unsyncedEl.innerHTML = '';
            unsynced.forEach(([name, status]) => {
                const div = document.createElement('div');
                div.className = 'unsynced-item';
                div.innerHTML = `
                    <div>
                        <div class="unsynced-name">${name}</div>
                        <div class="unsynced-status">仅在: ${status.present_in.join(', ')}</div>
                    </div>
                `;
                unsyncedEl.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Comparison failed:', error);
    }
}

async function loadSkills() {
    try {
        const filter = document.getElementById('app-filter').value;
        const allSkills = await fetchAPI('/api/skills');
        
        const tableEl = document.getElementById('skills-table');
        
        if (filter === 'all') {
            const comparison = await fetchAPI('/api/skills/compare');
            const appNames = ['trae', 'claude', 'codex', 'central'];
            const appLabels = {
                trae: 'T',
                claude: 'C',
                codex: 'X',
                central: 'M'
            };
            
            let html = '<table><thead><tr><th>技能名称</th>';
            appNames.forEach(app => {
                html += `<th>${appLabels[app]}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            for (const [name, status] of Object.entries(comparison.sync_status)) {
                html += `<tr><td>${name}</td>`;
                appNames.forEach(app => {
                    const present = status.present_in.includes(app);
                    html += `<td><span class="presence-badge ${present ? 'present' : 'missing'}">${present ? '✓' : '✗'}</span></td>`;
                });
                html += '</tr>';
            }
            html += '</tbody></table>';
            tableEl.innerHTML = html;
        } else {
            const skills = allSkills[filter] || [];
            if (skills.length === 0) {
                tableEl.innerHTML = '<p class="loading">暂无技能数据</p>';
                return;
            }
            
            let html = '<table><thead><tr><th>名称</th><th>文件数</th><th>大小</th><th>有 SKILL.md</th></tr></thead><tbody>';
            skills.forEach(skill => {
                html += `
                    <tr>
                        <td><strong>${skill.name}</strong></td>
                        <td>${skill.files_count}</td>
                        <td>${formatSize(skill.size)}</td>
                        <td>${skill.has_skill_md ? '<span class="presence-badge present">✓</span>' : '<span class="presence-badge missing">✗</span>'}</td>
                    </tr>
                `;
            });
            html += '</tbody></table>';
            tableEl.innerHTML = html;
        }
    } catch (error) {
        console.error('Load skills failed:', error);
        document.getElementById('skills-table').innerHTML = `<p class="loading">加载失败: ${error.message}</p>`;
    }
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

async function doSync() {
    const source = document.getElementById('sync-source').value;
    const targets = [];
    if (document.getElementById('target-trae').checked) targets.push('trae');
    if (document.getElementById('target-claude').checked) targets.push('claude');
    if (document.getElementById('target-codex').checked) targets.push('codex');
    const dryRun = document.getElementById('dry-run').checked;
    
    if (targets.length === 0) {
        showToast('请至少选择一个目标应用', 'error');
        return;
    }
    
    const filteredTargets = targets.filter(t => t !== source);
    if (filteredTargets.length === 0) {
        showToast('目标应用不能与源应用相同', 'error');
        return;
    }
    
    showLoading(dryRun ? '预览同步中...' : '同步中...');
    
    try {
        const result = await fetchAPI('/api/sync-all', {
            method: 'POST',
            body: JSON.stringify({
                source,
                targets: filteredTargets,
                dry_run: dryRun
            })
        });
        
        displaySyncResult(result);
        showToast(dryRun ? '预览完成' : '同步完成', 'success');
        
        refreshStatus();
        loadComparison();
        loadSkills();
    } catch (error) {
        showToast('同步失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function displaySyncResult(results) {
    const resultEl = document.getElementById('sync-result');
    let html = '';
    
    for (const [target, result] of Object.entries(results)) {
        html += `\n========================================\n`;
        html += `${result.source} → ${target}\n`;
        html += `========================================\n`;
        
        if (result.added && result.added.length > 0) {
            html += '\n【新增】\n';
            result.added.forEach(s => html += `  + ${s}\n`);
        }
        if (result.updated && result.updated.length > 0) {
            html += '\n【更新】\n';
            result.updated.forEach(s => html += `  ~ ${s}\n`);
        }
        if (result.removed && result.removed.length > 0) {
            html += '\n【删除】\n';
            result.removed.forEach(s => html += `  - ${s}\n`);
        }
        if (result.skipped && result.skipped.length > 0) {
            html += '\n【跳过】\n';
            result.skipped.forEach(s => html += `  = ${s}\n`);
        }
        if (result.errors && result.errors.length > 0) {
            html += '\n【错误】\n';
            result.errors.forEach(s => html += `  ! ${s}\n`);
        }
    }
    
    resultEl.innerHTML = html;
}

async function syncAll() {
    showLoading('一键同步中...');
    try {
        const result = await fetchAPI('/api/sync-all', {
            method: 'POST',
            body: JSON.stringify({ dry_run: false })
        });
        displaySyncResult(result);
        showToast('一键同步完成', 'success');
        refreshStatus();
        loadComparison();
        loadSkills();
    } catch (error) {
        showToast('同步失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function backupToCentral() {
    showLoading('备份中...');
    try {
        await fetchAPI('/api/backup', { method: 'POST' });
        showToast('备份完成', 'success');
        refreshStatus();
        loadComparison();
    } catch (error) {
        showToast('备份失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function restoreFromCentral() {
    if (!confirm('确定要从中央仓库恢复所有技能吗？')) return;
    
    showLoading('恢复中...');
    try {
        const result = await fetchAPI('/api/restore', { method: 'POST' });
        displaySyncResult(result.results);
        showToast('恢复完成', 'success');
        refreshStatus();
        loadComparison();
        loadSkills();
    } catch (error) {
        showToast('恢复失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function loadScheduleConfig() {
    try {
        const config = await fetchAPI('/api/config');
        const scheduler = config.scheduler || {};
        
        document.getElementById('schedule-enabled').checked = scheduler.enabled !== false;
        document.getElementById('schedule-interval').value = scheduler.interval_hours || 24;
        document.getElementById('schedule-backup').checked = scheduler.auto_backup !== false;
        document.getElementById('max-backups').value = scheduler.max_backups || 7;
    } catch (error) {
        console.error('Load schedule config failed:', error);
    }
}

async function saveSchedule() {
    const config = {
        scheduler: {
            enabled: document.getElementById('schedule-enabled').checked,
            interval_hours: parseInt(document.getElementById('schedule-interval').value) || 24,
            auto_backup: document.getElementById('schedule-backup').checked,
            max_backups: parseInt(document.getElementById('max-backups').value) || 7
        }
    };
    
    try {
        await fetchAPI('/api/config', {
            method: 'PUT',
            body: JSON.stringify(config)
        });
        showToast('定时任务配置已保存', 'success');
    } catch (error) {
        showToast('保存失败: ' + error.message, 'error');
    }
}

async function loadLogs() {
    try {
        const data = await fetchAPI('/api/logs?limit=200');
        const logsEl = document.getElementById('logs-container');
        
        if (!data.logs || data.logs.length === 0) {
            logsEl.innerHTML = '<p>暂无日志</p>';
            return;
        }
        
        logsEl.innerHTML = data.logs.map(line => {
            const color = line.includes('ERROR') ? '#ef4444' :
                         line.includes('WARNING') ? '#f59e0b' :
                         line.includes('SUCCESS') || line.includes('completed') ? '#22c55e' : '#e2e8f0';
            return `<div style="color: ${color}">${escapeHtml(line)}</div>`;
        }).join('');
        
        logsEl.scrollTop = logsEl.scrollHeight;
    } catch (error) {
        console.error('Load logs failed:', error);
        document.getElementById('logs-container').innerHTML = `<p style="color: #ef4444">加载失败: ${error.message}</p>`;
    }
}

function refreshLogs() {
    loadLogs();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
