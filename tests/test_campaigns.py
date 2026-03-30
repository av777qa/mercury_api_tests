import pytest


class TestCampaignsHappy:

    @pytest.mark.smoke
    @pytest.mark.happy
    def test_list_campaigns(self, client):
        resp = client.get("/campaigns")
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_list_campaigns_filter_by_app(self, client, created_app):
        resp = client.get("/campaigns", params={"app_id": created_app["id"]})
        assert resp.status_code == 200

    @pytest.mark.happy
    @pytest.mark.parametrize("status", ["draft", "sending", "completed"])
    def test_list_campaigns_filter_by_status(self, client, status):
        resp = client.get("/campaigns", params={"status": status})
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_get_campaign_by_id(self, client, created_campaign):
        resp = client.get(f"/campaigns/{created_campaign['id']}")
        assert resp.status_code == 200
        body = resp.json()
        data = body.get("data", body)
        assert data.get("id") == created_campaign["id"]

    @pytest.mark.happy
    def test_get_campaign_stats(self, client, created_campaign):
        resp = client.get(f"/campaigns/{created_campaign['id']}/stats")
        assert resp.status_code == 200
        data = resp.json().get("data", resp.json())
        assert "delivery_rate" in data
        assert "open_rate" in data
        assert isinstance(data["delivery_rate"], (int, float))
        assert isinstance(data["open_rate"], (int, float))

    @pytest.mark.happy
    def test_create_campaign(self, client, created_app, created_segment, created_push_message):
        payload = {
            "app_id": created_app["id"],
            "segment_id": created_segment["id"],
            "push_message_id": created_push_message["id"],
            "name": "Temp Test Campaign",
        }
        resp = client.post("/campaigns", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        data = body.get("data", {}).get("campaign", body.get("data", body))
        assert data.get("status") == "draft"
        client.delete(f"/campaigns/{data['id']}")

    @pytest.mark.happy
    def test_update_campaign(self, client, created_campaign, fx_campaigns):
        resp = client.put(f"/campaigns/{created_campaign['id']}", json=fx_campaigns["update_valid"])
        assert resp.status_code == 200

    @pytest.mark.slow
    @pytest.mark.happy
    def test_dispatch_campaign(self, client, created_campaign):
        resp = client.post(f"/campaigns/{created_campaign['id']}/dispatch")
        assert resp.status_code == 200


class TestCampaignsNegative:

    @pytest.mark.negative
    def test_get_nonexistent_campaign(self, client, random_uuid):
        resp = client.get(f"/campaigns/{random_uuid}")
        assert resp.status_code == 404
