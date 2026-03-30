import uuid
import pytest


class TestAppsHappy:

    @pytest.mark.smoke
    @pytest.mark.happy
    def test_list_apps(self, client):
        resp = client.get("/apps")
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_list_apps_compact(self, client):
        resp = client.get("/apps", params={"compact": 1})
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_list_apps_filter_by_bundles(self, client, created_app):
        resp = client.get("/apps", params={"bundles": created_app["bundle"]})
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_get_app_by_id(self, client, created_app):
        resp = client.get(f"/apps/{created_app['id']}")
        assert resp.status_code == 200
        data = resp.json().get("data", resp.json())
        assert data["id"] == created_app["id"]
        assert "bundle" in data

    @pytest.mark.happy
    def test_get_app_with_clients(self, client, created_app):
        resp = client.get(f"/apps/{created_app['id']}", params={"with_clients": True})
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_get_app_with_segments(self, client, created_app):
        resp = client.get(f"/apps/{created_app['id']}", params={"with_segments": True})
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_sync_app_creates_new(self, client, fx_apps):
        payload = {**fx_apps["sync_new"], "bundle": f"com.test.new.{uuid.uuid4().hex[:8]}"}
        resp = client.post("/apps/sync", json=payload)
        assert resp.status_code in (200, 201)
        body = resp.json()
        assert body.get("success") is True
        app_id = body.get("data", {}).get("id")
        if app_id:
            client.delete(f"/apps/{app_id}")

    @pytest.mark.happy
    def test_sync_app_updates_existing(self, client, created_app, fx_apps):
        payload = {**fx_apps["sync_new"], "bundle": created_app["bundle"]}
        resp = client.post("/apps/sync", json=payload)
        assert resp.status_code == 200
        assert resp.json().get("meta", {}).get("created") is False

    @pytest.mark.happy
    def test_update_app(self, client, created_app, fx_apps):
        resp = client.put(f"/apps/{created_app['id']}", json=fx_apps["update_valid"])
        assert resp.status_code == 200
        data = resp.json().get("data", resp.json())
        assert data.get("display_name") == fx_apps["update_valid"]["display_name"]


class TestAppsNegative:

    @pytest.mark.negative
    def test_sync_app_missing_bundle(self, client, fx_apps):
        resp = client.post("/apps/sync", json=fx_apps["sync_invalid_no_bundle"])
        assert resp.status_code == 500

    @pytest.mark.negative
    def test_sync_app_invalid_platform(self, client, fx_apps):
        resp = client.post("/apps/sync", json=fx_apps["sync_invalid_platform"])
        assert resp.status_code == 500

    @pytest.mark.negative
    def test_get_nonexistent_app(self, client, random_uuid):
        resp = client.get(f"/apps/{random_uuid}")
        assert resp.status_code == 404
