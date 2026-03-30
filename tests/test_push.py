import pytest


class TestPushHappy:

    @pytest.mark.happy
    def test_track_push_opened(self, client):
        resp = client.post("/push/opened", json={"message_id": "test-message-id-001"})
        assert resp.status_code == 200
        data = resp.json().get("data", resp.json())
        assert "status" in data

    @pytest.mark.happy
    def test_send_push_to_segment(self, client, created_app, created_segment):
        resp = client.post("/push/segment", json={
            "app_id": created_app["id"],
            "segment_id": created_segment["id"],
            "name": "Test Segment Push",
            "payload": {
                "notification": {
                    "title": "Test Notification",
                    "body": "Hello from automated tests!",
                }
            },
        })
        assert resp.status_code == 200
        data = resp.json().get("data", resp.json())
        assert "campaign" in data
        assert "id" in data["campaign"]


class TestPushNegative:

    @pytest.mark.negative
    def test_send_push_missing_message_id(self, client, created_client):
        resp = client.post("/push/send", json={"client_ids": [created_client["id"]]})
        assert resp.status_code == 422
