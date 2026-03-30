
import uuid
import pytest


class TestClientsHappy:

    @pytest.mark.smoke
    @pytest.mark.happy
    def test_list_clients(self, client):
        resp = client.get("/clients")
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_register_client(self, client, created_app, created_stream, fx_clients):
        stream_uid = created_stream.get("uid") or created_stream.get("id")
        payload = {
            **fx_clients["valid"],
            "id": str(uuid.uuid4()),
            "push_token": f"TestToken_{uuid.uuid4().hex}",
            "bundle": created_app["bundle"],
            "stream_uid": stream_uid,
        }
        resp = client.post("/clients", json=payload)
        assert resp.status_code == 201
        data = resp.json().get("data", {})
        assert data.get("status") == "stored"
        assert data.get("id") == payload["id"]

    @pytest.mark.happy
    def test_get_client_by_id(self, client, created_client):
        resp = client.get(f"/clients/{created_client['id']}")
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_update_client(self, client, created_client, fx_clients):
        resp = client.put(f"/clients/{created_client['id']}", json=fx_clients["update_valid"])
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_get_client_campaign_recipients(self, client, created_client):
        resp = client.get(f"/clients/{created_client['id']}/campaign-recipients")
        assert resp.status_code == 200
        assert "data" in resp.json()

    @pytest.mark.happy
    def test_get_client_events(self, client, created_client):
        resp = client.get(f"/clients/{created_client['id']}/events")
        assert resp.status_code == 200


class TestClientsNegative:

    @pytest.mark.negative
    def test_register_client_missing_push_token(self, client, created_app, created_stream, fx_clients):
        stream_uid = created_stream.get("uid") or created_stream.get("id")
        payload = {
            **fx_clients["missing_push_token"],
            "id": str(uuid.uuid4()),
            "bundle": created_app["bundle"],
            "stream_uid": stream_uid,
        }
        resp = client.post("/clients", json=payload)
        assert resp.status_code == 422

    @pytest.mark.negative
    def test_register_client_invalid_country(self, client, created_app, created_stream, fx_clients):
        stream_uid = created_stream.get("uid") or created_stream.get("id")
        payload = {
            **fx_clients["invalid_country_too_long"],
            "id": str(uuid.uuid4()),
            "push_token": f"TestToken_{uuid.uuid4().hex}",
            "bundle": created_app["bundle"],
            "stream_uid": stream_uid,
        }
        resp = client.post("/clients", json=payload)
        assert resp.status_code == 422

    @pytest.mark.negative
    def test_get_nonexistent_client(self, client, random_uuid):
        resp = client.get(f"/clients/{random_uuid}")
        assert resp.status_code == 404
