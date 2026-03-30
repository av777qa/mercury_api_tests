import requests
from config.settings import BASE_URL, TIMEOUT



class ApiClient:
    def __init__(self, token: str = None):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        if token:
            self.set_token(token)

    # ------------------------------------------------------------------
    # AUTH
    # ------------------------------------------------------------------

    def set_token(self, token: str) -> None:
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def clear_token(self) -> None:
        self.session.headers.pop("Authorization", None)

    def login(self, email: str, password: str) -> str:
        response = self.post(
            "/auth/token",
            json={"email": email, "password": password},
        )
        response.raise_for_status()
        token = response.json().get("data", {}).get("token")
        if not token:
            raise ValueError(f"Token not found in response: {response.json()}")
        self.set_token(token)
        return token

    # ------------------------------------------------------------------
    # HTTP-methods
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_params(kwargs: dict) -> dict:
        if "params" in kwargs and kwargs["params"]:
            kwargs["params"] = {
                k: int(v) if isinstance(v, bool) else v
                for k, v in kwargs["params"].items()
            }
        return kwargs

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(f"{self.base_url}{path}", timeout=TIMEOUT, **self._normalize_params(kwargs))

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.session.post(f"{self.base_url}{path}", timeout=TIMEOUT, **self._normalize_params(kwargs))

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.session.put(f"{self.base_url}{path}", timeout=TIMEOUT, **self._normalize_params(kwargs))

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.session.delete(f"{self.base_url}{path}", timeout=TIMEOUT, **self._normalize_params(kwargs))

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clone_without_token(self) -> "ApiClient":
        return ApiClient()

    def clone_with_token(self, token: str) -> "ApiClient":
        return ApiClient(token=token)
