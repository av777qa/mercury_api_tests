import uuid
import pytest


class TestSegmentsHappy:

    @pytest.mark.smoke
    @pytest.mark.happy
    def test_list_segments(self, client):
        resp = client.get("/segments")
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_list_segments_filter_by_app(self, client, created_app):
        resp = client.get("/segments", params={"app_id": created_app["id"]})
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_list_segments_pagination(self, client):
        resp = client.get("/segments", params={"page": 1})
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_get_segment_by_id(self, client, created_segment):
        resp = client.get(f"/segments/{created_segment['id']}")
        assert resp.status_code == 200
        body = resp.json()
        assert "clients_count" in body or "clients_count" in body.get("data", {})

    @pytest.mark.happy
    def test_create_segment(self, client, created_app, fx_segments):
        payload = {
            **fx_segments["valid"],
            "app_id": created_app["id"],
            "name": f"Temp Segment {uuid.uuid4().hex[:8]}",
        }
        resp = client.post("/segments", json=payload)
        assert resp.status_code == 201
        data = resp.json().get("data", resp.json())
        assert data.get("id")
        client.delete(f"/segments/{data['id']}")

    @pytest.mark.happy
    def test_update_segment(self, client, created_segment, fx_segments):
        resp = client.put(f"/segments/{created_segment['id']}", json=fx_segments["update_valid"])
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_reassign_clients(self, client, created_segment):
        resp = client.post(f"/segments/{created_segment['id']}/reassign-clients")
        assert resp.status_code == 200


class TestSegmentsNegative:

    @pytest.mark.negative
    def test_create_segment_missing_app_id(self, client, fx_segments):
        resp = client.post("/segments", json=fx_segments["missing_app_id"])
        assert resp.status_code == 422

    @pytest.mark.negative
    def test_get_nonexistent_segment(self, client, random_uuid):
        resp = client.get(f"/segments/{random_uuid}")
        assert resp.status_code == 404
