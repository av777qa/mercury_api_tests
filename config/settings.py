import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.staging"))

BASE_URL = os.getenv("BASE_URL", "https://push-service.app-octopus.com/api")
TEST_EMAIL = os.getenv("TEST_EMAIL")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")
TIMEOUT = int(os.getenv("TIMEOUT", "10"))
