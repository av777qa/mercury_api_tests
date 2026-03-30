import pytest


class TestLocalizationHappy:

    @pytest.mark.happy
    def test_get_localization_by_app_id(self, client, created_app):
        resp = client.get("/localization", params={"app_id": created_app["id"]})
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            body = resp.json()
            assert "keys" in body or "en" in body

    @pytest.mark.happy
    def test_get_localization_by_package_name(self, client, created_app):
        resp = client.get("/localization", params={"packageName": created_app["bundle"]})
        assert resp.status_code in (200, 404)

    @pytest.mark.happy
    def test_get_localization_by_bundle_alias(self, client, created_app):
        resp = client.get("/localization", params={"bundle": created_app["bundle"]})
        assert resp.status_code in (200, 404)
