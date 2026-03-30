import pytest
from clients.api_client import ApiClient

class TestAuthHappy:

    @pytest.mark.smoke
    @pytest.mark.happy
    def test_login_success_returns_token(self, fx_auth):
        anon = ApiClient()
        resp = anon.post("/auth/token", json=fx_auth["valid"])
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("success") is True
        data = body.get("data", {})
        assert "token" in data, f"Expected 'token' in data, got: {list(data.keys())}"
        assert isinstance(data["token"], str) and len(data["token"]) > 0
        assert "user" in data, f"Expected 'user' in data, got: {list(data.keys())}"

    @pytest.mark.happy
    def test_revoke_token(self, fx_auth):
        """Логінимось окремим клієнтом і видаляємо тільки його токен,
        щоб не зламати спільний client fixture для решти тестів."""
        temp = ApiClient()
        temp.login(fx_auth["valid"]["email"], fx_auth["valid"]["password"])
        resp = temp.delete("/auth/token")
        assert resp.status_code == 200
        assert "message" in resp.json()


class TestAuthNegative:

    @pytest.mark.negative
    def test_login_wrong_password(self, fx_auth):
        anon = ApiClient()
        resp = anon.post("/auth/token", json=fx_auth["invalid_password"])
        assert resp.status_code == 500

    @pytest.mark.negative
    def test_login_missing_password_field(self, fx_auth):
        anon = ApiClient()
        resp = anon.post("/auth/token", json=fx_auth["missing_password"])
        assert resp.status_code == 422

    @pytest.mark.negative
    def test_protected_endpoint_without_token(self):
        anon = ApiClient()
        resp = anon.get("/apps")
        assert resp.status_code == 500

    @pytest.mark.negative
    def test_protected_endpoint_with_broken_token(self):
        bad_client = ApiClient(token="this.is.not.a.valid.jwt.token")
        resp = bad_client.get("/apps")
        assert resp.status_code == 500
