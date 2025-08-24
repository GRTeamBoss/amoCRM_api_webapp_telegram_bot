import json
from pathlib import Path


class Config:
  SUBDOMAIN = "cspacesales"
  BASE_URL = f"https://{SUBDOMAIN}.amocrm.ru"
  API_URL = f"{BASE_URL}/api/v4"
  TOKEN_URL = f"{BASE_URL}/oauth2/token"
  TOKEN_ACCESS_URL = f"{BASE_URL}/oauth2/access_token"
  CLIENT_ID = "9b06f67e-b2a0-4bea-bff2-57893bde6df5"
  CLIENT_SECRET = "kvcUM0di5KD4u9SwuUAHtWP8C0ntXNMccS7lknNkdcGBjvpmpIfw8skbbtzvPu94"
  REDIRECT_URI = "https://google.com/"
  AUTH_CODE = ""
  USERS = {
    10861362: "Ubaydullloh",
    10886326: "SDRs incoming call",
    10948814: "SDRs cold search",
    12805982: "SDR Sales"
  }
  TOKEN_DICT = json.loads(Path("tokens.json").read_text(encoding="utf-8"))
  STAGES_DICT = json.loads(Path("stages.json").read_text(encoding="utf-8"))

  @classmethod
  def reload(cls):
      cls.TOKEN_DICT = json.loads(Path("tokens.json").read_text(encoding="utf-8"))
      cls.STAGES_DICT = json.loads(Path("stages.json").read_text(encoding="utf-8"))