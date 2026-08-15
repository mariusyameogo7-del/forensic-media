import pytest
from uuid import UUID


def test_anonymous_access_flow(client, sample_valid_jpeg):
    # 1. Upload anonymous image
    files = {"file": ("test.jpg", sample_valid_jpeg, "image/jpeg")}
    res = client.post("/api/v1/analyses", files=files)
    assert res.status_code == 202
    data = res.json()
    analysis_id = data["analysis_id"]
    public_id = data["public_id"]
    token = data["access_token"]
    assert token is not None

    # 2. Access with valid token -> 200 OK
    headers = {"X-Analysis-Token": token}
    res_progress = client.get(f"/api/v1/analyses/{analysis_id}/progress", headers=headers)
    assert res_progress.status_code == 200

    # 3. Access with missing token -> 401 Unauthorized
    res_no_token = client.get(f"/api/v1/analyses/{analysis_id}/progress")
    assert res_no_token.status_code == 401
    assert res_no_token.json()["error"]["code"] == "UNAUTHORIZED"

    # 4. Access with wrong token -> 401 Unauthorized
    res_bad_token = client.get(
        f"/api/v1/analyses/{analysis_id}/progress",
        headers={"X-Analysis-Token": "invalid_fake_token_12345"}
    )
    assert res_bad_token.status_code == 401

    # 5. Using public_id in header or route is never sufficient
    res_public_id_header = client.get(
        f"/api/v1/analyses/{analysis_id}/progress",
        headers={"X-Analysis-Token": public_id}
    )
    assert res_public_id_header.status_code == 401
