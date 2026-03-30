import pytest


class TestFunnelsHappy:

    @pytest.mark.smoke
    @pytest.mark.happy
    def test_list_funnels(self, client):
        resp = client.get("/funnels")
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_list_funnels_filter_by_app(self, client, created_app):
        resp = client.get("/funnels", params={"app_id": created_app["id"]})
        assert resp.status_code == 200

    @pytest.mark.happy
    def test_get_funnel_by_id(self, client, created_funnel):
        resp = client.get(f"/funnels/{created_funnel['id']}")
        assert resp.status_code == 200
        body = resp.json()
        assert "event_triggers" in body or "data" in body

    @pytest.mark.happy
    def test_update_funnel(self, client, created_funnel, fx_funnels):
        resp = client.put(f"/funnels/{created_funnel['id']}", json=fx_funnels["update_valid"])
        assert resp.status_code == 200
        assert resp.json().get("success") is True

    @pytest.mark.happy
    def test_get_funnel_client_progress(self, client, created_funnel):
        resp = client.get(
            f"/funnels/{created_funnel['id']}/client-progress",
            params={"page": 1, "per_page": 10},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body

    @pytest.mark.happy
    def test_track_funnel_action_clicked(self, client, created_client, created_funnel):
        resp = client.post("/funnels/track", json={
            "client_id": created_client["id"],
            "funnel_id": created_funnel["id"],
            "action": "clicked",
        })
        assert resp.status_code == 200
        assert resp.json().get("status") is None

    @pytest.mark.happy
    def test_track_funnel_action_converted(self, client, created_client, created_funnel):
        resp = client.post("/funnels/track", json={
            "client_id": created_client["id"],
            "funnel_id": created_funnel["id"],
            "action": "converted",
        })
        assert resp.status_code == 200

    @pytest.mark.slow
    @pytest.mark.happy
    def test_start_funnel_for_segment(self, client, created_funnel, created_segment):
        resp = client.post(
            f"/funnels/{created_funnel['id']}/start",
            json={"segment_id": created_segment["id"]},
        )
        assert resp.status_code == 200
        data = resp.json().get("data", resp.json())
        assert "clients_started" in data

    @pytest.mark.happy
    def test_create_funnel_step(self, client, created_funnel, created_campaign):
        payload = {
            "funnel_id": created_funnel["id"],
            "name": "Step 1 - Initial Push",
            "step_order": 1,
            "push_campaign_id": created_campaign["id"],
            "delay_minutes": 60,
            "timeout_action": "stop_funnel",
        }
        resp = client.post(f"/funnels/{created_funnel['id']}/steps", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body.get("success") is True
        step_id = body.get("data", {}).get("id")
        if step_id:
            client.delete(f"/funnels/{created_funnel['id']}/steps/{step_id}")


class TestFunnelsNegative:

    @pytest.mark.negative
    def test_create_funnel_missing_segment_id(self, client, created_app, fx_funnels):
        payload = {**fx_funnels["missing_segment_id"], "app_id": created_app["id"]}
        resp = client.post("/funnels", json=payload)
        assert resp.status_code == 201
        funnel_id = resp.json().get("data", {}).get("id")
        if funnel_id:
            client.delete(f"/funnels/{funnel_id}")
