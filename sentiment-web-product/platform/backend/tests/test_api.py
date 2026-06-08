from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_dashboard_returns_seed_workspace() -> None:
    response = client.get("/api/platform/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_project"]["id"] == "p-a2"
    assert payload["label_schema"]["fields"][0]["key"] == "sentiment_polarity"
    assert payload["records"]
    assert len(payload["rule_sets"]) >= 5
    assert len(payload["rule_definitions"]) >= 50
    assert payload["brand_rules"][0]["category"] == "母婴奶粉"
    assert payload["project_rule_status"]


def test_dashboard_switches_project_context() -> None:
    response = client.get("/api/platform/dashboard?project_id=p-risk")

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_project"]["id"] == "p-risk"
    assert payload["active_project"]["date_range"] == "2026-06-01 至 2026-06-05"
    assert payload["records"][0]["id"].startswith("risk-")
    assert payload["report"]["project_id"] == "p-risk"


def test_project_crud_keeps_new_project_isolated() -> None:
    create_response = client.post(
        "/api/platform/projects",
        json={
            "name": "测试舆情项目",
            "client": "测试客户",
            "brand": "测试品牌",
            "description": "测试项目说明",
            "objective": "测试项目目标",
            "platforms": ["小红书", "抖音"],
            "date_range": "2026-06-01 至 2026-06-05",
            "delivery_due": "2026-06-10",
            "owner_id": "u-001",
            "label_schema": "正负向 + 议题 + 品牌识别",
            "rule_version": "v1.0",
            "report_template": "默认报告模板",
            "export_pattern": "{project}_{date}_{version}_{format}",
            "selected_rule_set_ids": ["rules-brand-milk-powder-top40", "rules-cleaning-default"],
            "priority": "高",
            "status": "项目配置中",
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    project_id = created["id"]
    assert created["progress"] == 0
    assert created["platforms"] == ["小红书", "抖音"]
    assert created["priority"] == "高"
    assert created["selected_rule_set_ids"] == ["rules-brand-milk-powder-top40", "rules-cleaning-default"]
    assert created["applied_rule_set_ids"] == []

    dashboard_response = client.get(f"/api/platform/dashboard?project_id={project_id}")
    assert dashboard_response.status_code == 200
    dashboard_payload = dashboard_response.json()
    assert dashboard_payload["active_project"]["id"] == project_id
    assert dashboard_payload["records"] == []
    assert dashboard_payload["imports"] == []
    assert dashboard_payload["report"]["status"] == "待生成"

    update_response = client.patch(
        f"/api/platform/projects/{project_id}",
        json={
            "name": "测试舆情项目 v2",
            "client": "测试客户",
            "brand": "测试品牌",
            "description": "测试项目说明 v2",
            "objective": "测试项目目标 v2",
            "platforms": ["微博"],
            "date_range": "2026-06-01 至 2026-06-10",
            "delivery_due": "2026-06-12",
            "owner_id": "u-002",
            "label_schema": "正负向 + 议题 + 品牌识别",
            "rule_version": "v1.1",
            "report_template": "默认报告模板",
            "export_pattern": "{client}_{date}_{format}",
            "selected_rule_set_ids": ["rules-sentiment-a2-v9"],
            "priority": "中",
            "status": "待导入数据",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["owner"]["id"] == "u-002"
    assert update_response.json()["status"] == "待导入数据"
    assert update_response.json()["platforms"] == ["微博"]
    assert update_response.json()["delivery_due"] == "2026-06-12"
    assert update_response.json()["selected_rule_set_ids"] == ["rules-sentiment-a2-v9"]

    delete_response = client.delete(f"/api/platform/projects/{project_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True


def test_patch_record_confirms_manual_label() -> None:
    response = client.patch(
        "/api/platform/records/r-002",
        json={
            "edited_by": "u-001",
            "updates": [
                {"field_key": "sentiment_polarity", "value": "negative", "confirmed": True},
                {"field_key": "sentiment_type", "value": "panic", "confirmed": True},
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["labels"]["sentiment_polarity"]["final"] == "negative"
    assert payload["labels"]["sentiment_polarity"]["confirmed"] is True
    assert payload["labels"]["sentiment_polarity"]["confirmed_by"]["id"] == "u-001"


def test_patch_record_rejects_invalid_child_label() -> None:
    response = client.patch(
        "/api/platform/records/r-002",
        json={
            "edited_by": "u-001",
            "updates": [
                {"field_key": "sentiment_polarity", "value": "positive", "confirmed": True},
                {"field_key": "sentiment_type", "value": "panic", "confirmed": True},
            ],
        },
    )

    assert response.status_code == 422


def test_patch_record_rejects_unknown_editor() -> None:
    response = client.patch(
        "/api/platform/records/r-002",
        json={
            "edited_by": "u-missing",
            "updates": [
                {"field_key": "cognition", "value": "accurate", "confirmed": True},
            ],
        },
    )

    assert response.status_code == 422


def test_project_rule_preview_and_apply_tracks_pending_rules() -> None:
    preview_response = client.post(
        "/api/platform/projects/p-risk/rules/preview",
        json={
            "edited_by": "u-001",
            "selected_rule_set_ids": [
                "rules-brand-milk-powder-top40",
                "rules-cleaning-default",
                "rules-sentiment-a2-v9",
            ],
        },
    )

    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    assert "rules-sentiment-a2-v9" in preview_payload["newly_selected_rule_set_ids"]
    assert preview_payload["protected_records"] >= 1
    assert "before_counts" in preview_payload
    assert "after_counts" in preview_payload

    apply_response = client.post(
        "/api/platform/projects/p-risk/rules/apply",
        json={
            "edited_by": "u-001",
            "selected_rule_set_ids": [
                "rules-brand-milk-powder-top40",
                "rules-cleaning-default",
                "rules-sentiment-a2-v9",
            ],
        },
    )

    assert apply_response.status_code == 200
    dashboard_response = client.get("/api/platform/dashboard?project_id=p-risk")
    payload = dashboard_response.json()
    assert "rules-sentiment-a2-v9" in payload["active_project"]["applied_rule_set_ids"]
    assert not any(status["pending_apply"] for status in payload["project_rule_status"] if status["selected"])


def test_import_upload_registers_batch_and_downloads_file() -> None:
    create_response = client.post(
        "/api/platform/projects",
        json={
            "name": "导入闭环测试项目",
            "client": "测试客户",
            "brand": "测试品牌",
            "platforms": ["抖音"],
            "date_range": "2026-06-01 至 2026-06-30",
            "owner_id": "u-001",
            "selected_rule_set_ids": ["rules-cleaning-default"],
            "priority": "中",
            "status": "待导入数据",
        },
    )
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]
    csv_bytes = "评论ID,评论内容,平台\n1,有效内容,抖音\n2, ,抖音\n3,��乱码,抖音\n4,第二条有效,抖音\n".encode()

    upload_response = client.post(
        f"/api/platform/projects/{project_id}/imports",
        files={"file": ("import-loop.csv", csv_bytes, "text/csv")},
    )

    assert upload_response.status_code == 200
    payload = upload_response.json()
    assert payload["preview"]["total_rows"] == 4
    assert payload["preview"]["effective_rows"] == 2
    assert payload["preview"]["invalid_content_rows"] == 2
    job = payload["job"]
    assert job["filename"] == "import-loop.csv"
    assert job["valid_rows"] == 2
    assert job["invalid_rows"] == 2
    assert job["download_url"].endswith(f"/imports/{job['id']}/download")

    dashboard_response = client.get(f"/api/platform/dashboard?project_id={project_id}")
    assert dashboard_response.status_code == 200
    dashboard_payload = dashboard_response.json()
    assert dashboard_payload["active_project"]["status"] == "待字段映射"
    assert dashboard_payload["active_project"]["total_count"] == 2
    assert dashboard_payload["imports"][0]["id"] == job["id"]

    download_response = client.get(job["download_url"])
    assert download_response.status_code == 200
    assert download_response.content == csv_bytes
