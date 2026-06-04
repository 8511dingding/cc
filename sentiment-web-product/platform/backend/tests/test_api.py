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
