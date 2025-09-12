import json
import os
from pathlib import Path

from dotenv import load_dotenv



class Config:
  load_dotenv()
  SUBDOMAIN: str = os.getenv("SUBDOMAIN", None)
  BASE_URL: str = f"https://{SUBDOMAIN}.amocrm.ru"
  API_URL: str = f"{BASE_URL}/api/v4"
  TOKEN_URL: str = f"{BASE_URL}/oauth2/token"
  TOKEN_ACCESS_URL: str = f"{BASE_URL}/oauth2/access_token"
  CLIENT_ID: str = os.getenv("CLIENT_ID", None)
  CLIENT_SECRET: str = os.getenv("CLIENT_SECRET", None)
  REDIRECT_URI: str = "https://google.com/"
  AUTH_CODE: str = ""
  USERS: dict[int, str] = {
    10861362: "Ubaydullloh",
    10886326: "SDRs incoming call",
    10948814: "SDRs cold search",
    12805982: "SDR Sales"
  }
  TOKEN_DICT: dict[str, any] = json.loads(Path(os.getenv("TOKENS_JSON_GET_FILE", "tokens.json")).read_text(encoding="utf-8"))
  # STAGES_DICT = json.loads(Path("stages.json").read_text(encoding="utf-8"))

  @classmethod
  def reload(cls):
      cls.TOKEN_DICT: dict[str, any] = json.loads(Path(os.getenv("TOKENS_JSON_GET_FILE", "tokens.json")).read_text(encoding="utf-8"))
      # cls.STAGES_DICT = json.loads(Path("stages.json").read_text(encoding="utf-8"))