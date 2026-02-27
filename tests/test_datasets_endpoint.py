from pathlib import Path

import app.services.datasets as datasets_service
from fastapi.testclient import TestClient

from app.main import app


def test_datasets_endpoint_returns_metadata_from_tmp_data_dir(
    monkeypatch, tmp_path: Path
):
    """
    Uses monkeypatch to redirect the service's data directory to a temp folder,
    so the test never touches the real /data (e.g., inventory.csv).
    """
    # Arrange: create a temporary "data" directory with a known CSV
    temp_data_dir = tmp_path / "data"
    temp_data_dir.mkdir(parents=True)

    (temp_data_dir / "sample.csv").write_text(
        "id,name\n" "1,Ada\n" "2,Grace\n" "3,Linus\n",
        encoding="utf-8",
    )

    # Monkeypatch _data_dir() used by list_datasets/readiness_check
    monkeypatch.setattr(datasets_service, "_data_dir", lambda: temp_data_dir)

    client = TestClient(app)

    # Act
    resp = client.get("/datasets")

    # Assert
    assert resp.status_code == 200
    payload = resp.json()

    assert "datasets" in payload
    assert isinstance(payload["datasets"], list)

    entry = next(d for d in payload["datasets"] if d["filename"] == "sample.csv")
    assert entry["id"] == "sample"
    assert entry["row_count"] == 3
    assert entry["columns"] == ["id", "name"]
    assert isinstance(entry["size_bytes"], int)
    assert entry["size_bytes"] > 0
    assert "T" in entry["modified_time"]  # basic ISO sanity check



def test_health_endpoint_returns_503_when_no_csvs(monkeypatch, tmp_path):
    """If the data directory exists but contains no CSV files,
    /health should report not ready and return HTTP 503."""

    # Arrange: create empty temp data directory
    temp_data_dir = tmp_path / "data"
    temp_data_dir.mkdir(parents=True)

    import app.services.datasets as datasets_service

    monkeypatch.setattr(datasets_service, "_data_dir", lambda: temp_data_dir)

    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # Act
    resp = client.get("/health")

    # Assert
    assert resp.status_code == 503

    payload = resp.json()
    assert payload["ready"] is False
    assert payload["status"] in ("degraded", "error")
    assert payload["checks"]["csv_count"] == 0


def test_health_endpoint_returns_200_when_csv_present(monkeypatch, tmp_path):
    """
    If the data directory exists and contains a valid CSV with a header,
    /health should report ready and return HTTP 200.
    """
    # Arrange
    temp_data_dir = tmp_path / "data"
    temp_data_dir.mkdir(parents=True)

    # Create valid CSV
    (temp_data_dir / "valid.csv").write_text(
        "id,name\n" "1,Ada\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(datasets_service, "_data_dir", lambda: temp_data_dir)

    client = TestClient(app)

    # Act
    resp = client.get("/health")

    # Assert
    assert resp.status_code == 200

    payload = resp.json()
    assert payload["ready"] is True
    assert payload["status"] == "ok"
    assert payload["datasets_found"] == 1
    assert payload["checks"]["csv_count"] == 1
    assert payload["checks"]["csv_readable"] == 1
    assert payload["checks"]["csv_unreadable"] == 0
