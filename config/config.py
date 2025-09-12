import json
from pathlib import Path


class Config:
  SUBDOMAIN: str = "cspacesales"
  BASE_URL: str = f"https://{SUBDOMAIN}.amocrm.ru"
  API_URL: str = f"{BASE_URL}/api/v4"
  TOKEN_URL: str = f"{BASE_URL}/oauth2/token"
  TOKEN_ACCESS_URL: str = f"{BASE_URL}/oauth2/access_token"
  CLIENT_ID: str = "9b06f67e-b2a0-4bea-bff2-57893bde6df5"
  CLIENT_SECRET: str = "kvcUM0di5KD4u9SwuUAHtWP8C0ntXNMccS7lknNkdcGBjvpmpIfw8skbbtzvPu94"
  REDIRECT_URI: str = "https://google.com/"
  AUTH_CODE: str = ""
  USERS: dict[int, str] = {
    10861362: "Ubaydullloh",
    10886326: "SDRs incoming call",
    10948814: "SDRs cold search",
    12805982: "SDR Sales"
  }
  TOKEN_DICT: dict[str, any] = json.loads(Path("tokens.json").read_text(encoding="utf-8"))
  # STAGES_DICT = json.loads(Path("stages.json").read_text(encoding="utf-8"))

  @classmethod
  def reload(cls):
      cls.TOKEN_DICT: dict[str, any] = json.loads(Path("tokens.json").read_text(encoding="utf-8"))
      # cls.STAGES_DICT = json.loads(Path("stages.json").read_text(encoding="utf-8"))