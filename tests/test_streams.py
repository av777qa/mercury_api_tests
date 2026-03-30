import uuid
import pytest


class TestStreamsHappy:

    @pytest.mark.smoke
    @pytest.mark.happy
    def test_list_streams(self, client):
        resp = client.get("/streams")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("success") is True
        assert "data" in body

    @pytest.mark.happy
    def test_list_streams_pagination(self, client):
        resp = client.get("/streams", params={"page": 1, "per_page": 5})
        assert resp.status_code == 200
        assert resp.json().get("data", {}).get("per_page") == 5

    @pytest.mark.happy
    def test_list_streams_filter_by_bundle(self, client, created_app):
        resp = client.get("/streams", params={"app_bundle": created_app["bundle"]})
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_get_stream_by_uid(self, client, created_stream):
        uid = created_stream.get("uid") or created_stream.get("id")
        resp = client.get(f"/streams/{uid}")
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_create_stream(self, client, created_app, fx_streams):
        payload = {
            **fx_streams["valid"],
            "name": f"Temp Stream {uuid.uuid4().hex[:6]}",
            "app_bundle": created_app["bundle"],
        }
        resp = client.post("/streams", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body.get("success") is True
        data = body.get("data", {})
        uid = data.get("uid") or data.get("id")
        assert uid
        client.delete(f"/streams/{uid}")

    @pytest.mark.happy
    def test_sync_stream_creates_new(self, client, created_app):
        payload = {
            "uid": f"test-stream-{uuid.uuid4().hex[:8]}",
            "name": "Sync New Stream",
            "app_bundle": created_app["bundle"],
            "is_active": True,
        }
        resp = client.post("/streams/sync", json=payload)
        assert resp.status_code in (200, 201)
        assert resp.json().get("success") is True

    @pytest.mark.happy
    def test_update_stream(self, client, created_stream, fx_streams):
        uid = created_stream.get("uid") or created_stream.get("id")
        resp = client.put(f"/streams/{uid}", json=fx_streams["update_valid"])
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_delete_stream(self, client, created_app, fx_streams):
        payload = {
            **fx_streams["valid"],
            "name": f"Delete Me {uuid.uuid4().hex[:6]}",
            "app_bundle": created_app["bundle"],
        }
        create_resp = client.post("/streams", json=payload)
        assert create_resp.status_code == 201
        data = create_resp.json().get("data", {})
        uid = data.get("uid") or data.get("id")
        resp = client.delete(f"/streams/{uid}")
        assert resp.status_code == 204
